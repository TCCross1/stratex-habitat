import Foundation

/// Orchestrates the end-to-end governed capture flow on device:
///   authenticate → select property → create scan session → (RoomPlan capture) →
///   on-device Guardian pre-flight → secure-stage artifact → resumable upload →
///   backend Guardian evaluate → governed transition to QUALITY_REVIEW →
///   generate DRAFT_CANDIDATE (never VERIFIED_EXISTING).
///
/// The backend is always the authority: the app never claims acceptance or a
/// truth class beyond MEASURED_EXISTING/DRAFT_CANDIDATE.
public final class CaptureFlowController {
    public struct Outcome {
        public let scanSessionId: String
        public let localGuardian: GuardianResult
        public let uploadResponse: Data
        public let candidateResponse: Data
    }

    private let api: HabitatAPIClient
    private let store: SecureLocalStore
    private let uploader: ResumableUploader

    public init(api: HabitatAPIClient, store: SecureLocalStore) {
        self.api = api
        self.store = store
        self.uploader = ResumableUploader(api: api)
    }

    /// Run the governed pipeline for an already-captured artifact + derived report.
    public func run(propertyId: String,
                    artifactData: Data,
                    artifactType: String,
                    report: QualityReport,
                    structure: DerivedStructure) async throws -> Outcome {
        // 1) On-device deterministic Guardian pre-flight (instant feedback).
        let local = ScanQualityGuardian.evaluate(report)
        guard local.verdict != .fail else {
            throw HabitatAPIError.http(0, "On-device Guardian FAIL — recapture before upload: \(local.missingAreas)")
        }

        // 2) Create the governed scan session.
        let device = DeviceInfo(model: deviceModel(), osVersion: osVersion())
        let scan = try await api.createScanSession(
            propertyId: propertyId,
            ScanSessionCreate(device: device, idempotencyKey: UUID().uuidString))

        // 3) Governed capture-state walk (backend enforces legality).
        try await api.transition(scanSessionId: scan.id, to: CaptureState.ready.backendScanState)
        try await api.transition(scanSessionId: scan.id, to: CaptureState.capturing.backendScanState)
        try await api.reportCaptureProgress(scanSessionId: scan.id, nativeState: .capturing, report: report)
        try await api.transition(scanSessionId: scan.id, to: CaptureState.finalizing.backendScanState)

        // 4) Secure-stage + resumable upload into governed object storage.
        let staged = try store.write(artifactData, scanSessionId: scan.id, filename: "capture.pointcloud")
        try await api.transition(scanSessionId: scan.id, to: CaptureState.uploading.backendScanState)
        let uploadResp = try await uploader.upload(fileURL: staged, artifactType: artifactType, scanSessionId: scan.id)
        try await api.transition(scanSessionId: scan.id, to: CaptureState.uploaded.backendScanState)
        store.purge(scanSessionId: scan.id)   // no lingering sensitive interior data

        // 5) Backend processing + authoritative Guardian evaluation.
        try await api.transition(scanSessionId: scan.id, to: "PROCESSING_PENDING")
        try await api.transition(scanSessionId: scan.id, to: CaptureState.processing.backendScanState)
        try await api.transition(scanSessionId: scan.id, to: CaptureState.complete.backendScanState) // -> QUALITY_REVIEW
        _ = try await api.evaluateGuardian(scanSessionId: scan.id, report: report)

        // 6) Generate the DRAFT_CANDIDATE (never auto VERIFIED_EXISTING).
        let artifactId = extractArtifactId(from: uploadResp)
        let candidateResp = try await api.generateCandidate(
            scanSessionId: scan.id, structure: structure,
            artifactIds: artifactId.map { [$0] } ?? [])

        return Outcome(scanSessionId: scan.id, localGuardian: local,
                       uploadResponse: uploadResp, candidateResponse: candidateResp)
    }

    private func extractArtifactId(from data: Data) -> String? {
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        if let artifact = obj["artifact"] as? [String: Any], let id = artifact["id"] as? String { return id }
        return obj["artifact_id"] as? String
    }

    private func deviceModel() -> String {
        #if canImport(UIKit)
        return UIDevice.current.model
        #else
        return "iOS Device"
        #endif
    }
    private func osVersion() -> String {
        #if canImport(UIKit)
        return "iOS \(UIDevice.current.systemVersion)"
        #else
        return "iOS"
        #endif
    }
}

#if canImport(UIKit)
import UIKit
#endif
