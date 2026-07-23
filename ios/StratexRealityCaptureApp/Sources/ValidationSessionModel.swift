import Foundation
import Combine
import StratexRealityCapture
#if canImport(UIKit)
import UIKit
#endif

/// Thin host-session model. Reuses package types only — no second state machine.
@MainActor
final class ValidationSessionModel: ObservableObject {
    static let appBuild = "H014B3/0.1.0"

    @Published var capability: DeviceCapabilityReport = DeviceCapability.evaluate(appBuild: appBuild)
    @Published var apiBaseURL: String = ""
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var authTokenPresent: Bool = false
    @Published var propertyId: String = ""
    @Published var roomId: String = "room-living-1"
    @Published var operatorName: String = "pilot-operator"
    @Published var commitSha: String = "UNKNOWN"
    @Published var statusMessage: String = "Configure API and verify device readiness."
    @Published var captureState: CaptureState = .idle
    @Published var latestReport: QualityReport?
    @Published var latestGuardian: GuardianResult?
    @Published var coachingMessages: [GuardianCoaching.Message] = []
    @Published var primaryCoaching: String = ""
    @Published var uploadFraction: Double = 0
    @Published var uploadMissingIndexes: [Int] = []
    @Published var outcomeSummary: String = ""
    @Published var evidence: ValidationEvidenceRun?
    @Published var evidenceExportPath: String = ""
    @Published var errorMessage: String = ""

    let fallbackCoordinator = RoomCaptureCoordinator()
    @Published var captureCoordinator: RoomCaptureCoordinator?

    private var activeCoordinator: RoomCaptureCoordinator {
        captureCoordinator ?? fallbackCoordinator
    }

    private var api: HabitatAPIClient?
    private var store: SecureLocalStore?
    private var token: String?

    init() {
        wireCoordinator(fallbackCoordinator)
        refreshCapability()
    }

    func bindCaptureCoordinator(_ coordinator: RoomCaptureCoordinator) {
        captureCoordinator = coordinator
        wireCoordinator(coordinator)
    }

    private func wireCoordinator(_ coordinator: RoomCaptureCoordinator) {
        coordinator.onStateChange = { [weak self] state in
            Task { @MainActor in
                self?.captureState = state
            }
        }
        coordinator.onProgress = { [weak self] report in
            Task { @MainActor in
                self?.ingest(report: report)
            }
        }
    }

    func refreshCapability() {
        capability = DeviceCapability.evaluate(appBuild: Self.appBuild)
    }

    func requestCamera() async {
        _ = await DeviceCapability.requestCameraAccess()
        refreshCapability()
    }

    func configureAPI() throws {
        guard let url = URL(string: apiBaseURL), !apiBaseURL.isEmpty else {
            throw HabitatAPIError.http(0, "API base URL required (non-production Habitat endpoint).")
        }
        api = HabitatAPIClient(baseURL: url)
        store = try SecureLocalStore(subdirectory: "H014B3Validation")
        statusMessage = "API client configured."
    }

    func login() async {
        errorMessage = ""
        do {
            try configureAPI()
            guard let api else { return }
            // Token is held in memory only — never written to the evidence export.
            token = try await api.login(email: email, password: password)
            authTokenPresent = token != nil
            password = "" // clear from UI state after use
            statusMessage = "Authenticated. Select property and begin capture."
            beginEvidenceIfNeeded()
        } catch {
            errorMessage = String(describing: error)
            authTokenPresent = false
        }
    }

    func beginEvidenceIfNeeded() {
        if evidence != nil { return }
        evidence = ValidationEvidenceRun(
            commitSha: commitSha,
            applicationBuild: Self.appBuild,
            deviceModel: capability.deviceModel,
            osVersion: capability.osVersion,
            lidarAvailable: capability.lidarAvailable,
            roomPlanAvailable: capability.roomPlanAvailable,
            testOperator: operatorName,
            pseudonymousPropertyId: propertyId.isEmpty ? "prop-unset" : propertyId,
            pseudonymousRoomId: roomId)
    }

    func startCapture() {
        errorMessage = ""
        beginEvidenceIfNeeded()
        guard capability.lidarAvailable, capability.roomPlanAvailable else {
            errorMessage = capability.blockingReasons.joined(separator: " ")
            return
        }
        activeCoordinator.requestAuthorizationAndStart()
        statusMessage = "Capture started. Follow Guardian coaching. Finish explicitly when ready."
    }

    func pauseCapture() { activeCoordinator.pause() }
    func resumeCapture() { activeCoordinator.resume() }
    func cancelCapture() {
        activeCoordinator.cancel()
        evidence?.observedDefects.append("Capture cancelled by operator.")
        statusMessage = "Capture cancelled."
    }

    func finishCapture() {
        activeCoordinator.finish()
        statusMessage = "Finalizing capture — preparing governed upload."
    }

    func handleAppInterruption(reason: String) {
        activeCoordinator.handleInterruption()
        evidence?.interruptionEvents.append(reason)
        statusMessage = "Interrupted (\(reason)). Capture paused if it was active."
    }

    func ingest(report: QualityReport) {
        latestReport = report
        let result = ScanQualityGuardian.evaluate(report)
        latestGuardian = result
        coachingMessages = GuardianCoaching.messages(for: result)
        primaryCoaching = GuardianCoaching.primaryInstruction(for: result)
        evidence?.guardianInterventions.append(
            "\(result.verdict.rawValue):\(result.findings.map(\.code).joined(separator: ","))"
        )
        evidence?.guardianFinalVerdict = result.verdict.rawValue
    }

    /// Run the accepted CaptureFlowController pipeline after finish.
    func uploadAndGenerateCandidate() async {
        errorMessage = ""
        guard let api, let store else {
            errorMessage = "Configure API before upload."
            return
        }
        guard !propertyId.isEmpty else {
            errorMessage = "Pseudonymous property ID required."
            return
        }
        guard let report = activeCoordinator.currentReport() ?? latestReport else {
            errorMessage = "No quality report available."
            return
        }
        guard let structure = activeCoordinator.currentStructure() else {
            errorMessage = "No derived structure available."
            return
        }
        guard let artifact = activeCoordinator.currentArtifactData(), !artifact.isEmpty else {
            errorMessage = "No capture artifact available to upload."
            return
        }
        beginEvidenceIfNeeded()
        evidence?.declaredChecksumSha256 = Checksum.sha256Hex(artifact)
        do {
            let flow = CaptureFlowController(api: api, store: store)
            let outcome = try await flow.run(
                propertyId: propertyId,
                artifactData: artifact,
                artifactType: "POINT_CLOUD",
                report: report,
                structure: structure)
            latestGuardian = outcome.localGuardian
            evidence?.guardianFinalVerdict = outcome.localGuardian.verdict.rawValue
            evidence?.verifiedChecksumSha256 = evidence?.declaredChecksumSha256
            if let cand = try? JSONSerialization.jsonObject(with: outcome.candidateResponse) as? [String: Any] {
                let model = cand["existing_model_version"] as? [String: Any]
                evidence?.candidateModelId = model?["id"] as? String ?? cand["id"] as? String
                evidence?.candidateModelState = model?["model_state"] as? String ?? "DRAFT_CANDIDATE"
            } else {
                evidence?.candidateModelState = "DRAFT_CANDIDATE"
            }
            if let up = try? JSONSerialization.jsonObject(with: outcome.uploadResponse) as? [String: Any] {
                evidence?.chunkCount = up["total_chunks"] as? Int
            }
            evidence?.completedAt = ISO8601DateFormatter().string(from: Date())
            evidence?.passFailStatus = outcome.localGuardian.verdict == .fail ? "FAIL" : "PENDING_MANUAL_GATES"
            outcomeSummary =
                "Scan \(outcome.scanSessionId) · Guardian \(outcome.localGuardian.verdict.rawValue) · " +
                "Candidate \(evidence?.candidateModelState ?? "DRAFT_CANDIDATE") · NOT property truth"
            statusMessage = "Upload complete. Review in Habitat Capture Review (read-only)."
            exportEvidence()
        } catch {
            errorMessage = String(describing: error)
            evidence?.observedDefects.append(scrubError(error))
            evidence?.networkLossEvents.append("upload_or_pipeline_error")
            evidence?.retryCount += 1
        }
    }

    func exportEvidence() {
        guard var run = evidence else { return }
        run.recomputeMeasurementErrors()
        evidence = run
        do {
            let json = try ValidationEvidenceRedactor.jsonExport(run)
            let md = ValidationEvidenceRedactor.markdownSummary(run)
            let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
                .appendingPathComponent("h014b3-evidence", isDirectory: true)
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let base = "\(run.validationRunId)-scan\(run.scanIndex)"
            let jsonURL = dir.appendingPathComponent("\(base).json")
            let mdURL = dir.appendingPathComponent("\(base).md")
            try json.write(to: jsonURL, options: .atomic)
            try md.data(using: .utf8)?.write(to: mdURL, options: .atomic)
            evidenceExportPath = jsonURL.lastPathComponent
            statusMessage = "Redacted evidence exported: \(jsonURL.lastPathComponent)"
        } catch {
            errorMessage = "Evidence export failed: \(error)"
        }
    }

    private func scrubError(_ error: Error) -> String {
        let s = String(describing: error)
        return ValidationEvidenceRedactor.containsProhibitedContent(s) ? "[redacted-error]" : String(s.prefix(160))
    }
}
