import SwiftUI
import StratexRealityCapture

struct RootView: View {
    @EnvironmentObject private var session: ValidationSessionModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    readinessCard
                    apiCard
                    captureCard
                    coachingCard
                    outcomeCard
                    evidenceCard
                }
                .padding()
            }
            .navigationTitle("H-014B.3 Device Pilot")
            .background(Color(.systemGroupedBackground))
        }
    }

    private var readinessCard: some View {
        GroupBox("Device readiness") {
            VStack(alignment: .leading, spacing: 6) {
                labeled("LiDAR", session.capability.lidarAvailable ? "available" : "unavailable")
                labeled("RoomPlan", session.capability.roomPlanAvailable ? "available" : "unavailable")
                labeled("Camera", session.capability.cameraAuthorization)
                labeled("Device", "\(session.capability.deviceModel) · \(session.capability.osVersion)")
                labeled("Build", session.capability.appBuild)
                if !session.capability.blockingReasons.isEmpty {
                    Text(session.capability.blockingReasons.joined(separator: "\n"))
                        .foregroundStyle(.orange)
                        .font(.footnote)
                }
                HStack {
                    Button("Refresh") { session.refreshCapability() }
                    Button("Request camera") {
                        Task { await session.requestCamera() }
                    }
                }
                .buttonStyle(.bordered)
            }
        }
    }

    private var apiCard: some View {
        GroupBox("Non-production API") {
            VStack(alignment: .leading, spacing: 8) {
                TextField("API base URL (https://…)", text: $session.apiBaseURL)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .keyboardType(.URL)
                TextField("Email", text: $session.email)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                SecureField("Password (memory only)", text: $session.password)
                TextField("Pseudonymous property ID", text: $session.propertyId)
                    .textInputAutocapitalization(.never)
                TextField("Pseudonymous room ID", text: $session.roomId)
                    .textInputAutocapitalization(.never)
                TextField("Operator label", text: $session.operatorName)
                TextField("Commit SHA", text: $session.commitSha)
                    .textInputAutocapitalization(.never)
                labeled("Auth token present", session.authTokenPresent ? "yes (memory)" : "no")
                Button("Sign in") { Task { await session.login() } }
                    .buttonStyle(.borderedProminent)
                Text("Credentials are never written into evidence exports.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var captureCard: some View {
        GroupBox("Capture lifecycle") {
            VStack(alignment: .leading, spacing: 8) {
                labeled("Native state", session.captureState.rawValue)
                labeled("Backend map", session.captureState.backendScanState)
                RoomCaptureViewRepresentable(coordinator: Binding(
                    get: { session.captureCoordinator },
                    set: { newValue in
                        if let newValue { session.bindCaptureCoordinator(newValue) }
                    }
                ))
                    .frame(height: 280)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                HStack {
                    Button("Start") { session.startCapture() }
                    Button("Pause") { session.pauseCapture() }
                    Button("Resume") { session.resumeCapture() }
                }
                HStack {
                    Button("Finish") { session.finishCapture() }
                    Button("Cancel") { session.cancelCapture() }
                    Button("Upload → DRAFT_CANDIDATE") {
                        Task { await session.uploadAndGenerateCandidate() }
                    }
                }
                .buttonStyle(.bordered)
                Text(session.statusMessage).font(.footnote)
                if !session.errorMessage.isEmpty {
                    Text(session.errorMessage).foregroundStyle(.red).font(.footnote)
                }
            }
        }
    }

    private var coachingCard: some View {
        GroupBox("Live Guardian coaching") {
            VStack(alignment: .leading, spacing: 6) {
                if let g = session.latestGuardian {
                    labeled("Verdict", "\(g.verdict.rawValue) · score \(g.score) · v\(g.guardianVersion)")
                    labeled("Recommendation", g.recommendation)
                }
                Text(session.primaryCoaching.isEmpty ? "Coaching appears during capture." : session.primaryCoaching)
                    .font(.body.weight(.semibold))
                ForEach(Array(session.coachingMessages.enumerated()), id: \.offset) { _, msg in
                    Text("• \(msg.instruction)")
                        .font(.footnote)
                        .foregroundStyle(msg.severity == .fail ? .red : (msg.severity == .warn ? .orange : .primary))
                }
                Text("Guardian remains the verdict authority. Coaching never auto-finishes or promotes truth.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var outcomeCard: some View {
        GroupBox("Completion / DRAFT_CANDIDATE") {
            VStack(alignment: .leading, spacing: 6) {
                Text(session.outcomeSummary.isEmpty
                     ? "No candidate yet. Finish capture and upload to generate DRAFT_CANDIDATE only."
                     : session.outcomeSummary)
                Text("Handoff: open Habitat Capture Review (read-only). This app cannot approve VERIFIED_EXISTING.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var evidenceCard: some View {
        GroupBox("Validation evidence") {
            VStack(alignment: .leading, spacing: 6) {
                labeled("Run", session.evidence?.validationRunId ?? "—")
                labeled("Export", session.evidenceExportPath.isEmpty ? "not yet" : session.evidenceExportPath)
                Button("Export redacted evidence") { session.exportEvidence() }
                    .buttonStyle(.bordered)
                Text("Copy JSON/Markdown from the app Documents/h014b3-evidence folder. Do not commit real addresses or tokens.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func labeled(_ k: String, _ v: String) -> some View {
        HStack {
            Text(k).foregroundStyle(.secondary)
            Spacer()
            Text(v).font(.body.monospaced())
        }
        .font(.footnote)
    }
}
