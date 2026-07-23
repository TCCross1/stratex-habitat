import Foundation

/// Governed H-014B.3 physical-device validation evidence.
///
/// Runtime instances are written under `test_reports/h014b3-device/` (gitignored).
/// Exports MUST be redacted — never include addresses, tokens, photos of people,
/// or raw credentials. Evidence is never uploaded to Passport automatically.
public struct ValidationEvidenceRun: Codable, Equatable {
    public var validationRunId: String
    public var commitSha: String
    public var applicationBuild: String
    public var deviceModel: String
    public var osVersion: String
    public var lidarAvailable: Bool
    public var roomPlanAvailable: Bool
    public var testOperator: String
    public var pseudonymousPropertyId: String
    public var pseudonymousRoomId: String
    public var startedAt: String
    public var completedAt: String?
    public var interruptionEvents: [String]
    public var networkLossEvents: [String]
    public var guardianInterventions: [String]
    public var guardianFinalVerdict: String?
    public var guardianVersion: String?
    public var coachingVersion: String?
    public var chunkCount: Int?
    public var retryCount: Int
    public var resumedChunkIndexes: [Int]
    public var declaredChecksumSha256: String?
    public var verifiedChecksumSha256: String?
    public var candidateModelId: String?
    public var candidateModelState: String?
    public var manualReferenceMeasurements: [String: Double]
    public var scanDerivedMeasurements: [String: Double]
    public var absoluteMeasurementError: [String: Double]
    public var percentageMeasurementError: [String: Double]
    public var repeatabilityResults: [String: Double]
    public var screenshotReferences: [String]
    public var passFailStatus: String
    public var observedDefects: [String]
    public var requiredRecaptureNotes: [String]
    public var scanIndex: Int
    public var truthBoundaryNote: String

    public init(validationRunId: String = UUID().uuidString,
                commitSha: String,
                applicationBuild: String,
                deviceModel: String,
                osVersion: String,
                lidarAvailable: Bool,
                roomPlanAvailable: Bool,
                testOperator: String,
                pseudonymousPropertyId: String,
                pseudonymousRoomId: String,
                startedAt: String = ISO8601DateFormatter().string(from: Date()),
                scanIndex: Int = 1) {
        self.validationRunId = validationRunId
        self.commitSha = commitSha
        self.applicationBuild = applicationBuild
        self.deviceModel = deviceModel
        self.osVersion = osVersion
        self.lidarAvailable = lidarAvailable
        self.roomPlanAvailable = roomPlanAvailable
        self.testOperator = testOperator
        self.pseudonymousPropertyId = pseudonymousPropertyId
        self.pseudonymousRoomId = pseudonymousRoomId
        self.startedAt = startedAt
        self.completedAt = nil
        self.interruptionEvents = []
        self.networkLossEvents = []
        self.guardianInterventions = []
        self.guardianFinalVerdict = nil
        self.guardianVersion = ScanQualityGuardian.version
        self.coachingVersion = GuardianCoaching.version
        self.chunkCount = nil
        self.retryCount = 0
        self.resumedChunkIndexes = []
        self.declaredChecksumSha256 = nil
        self.verifiedChecksumSha256 = nil
        self.candidateModelId = nil
        self.candidateModelState = nil
        self.manualReferenceMeasurements = [:]
        self.scanDerivedMeasurements = [:]
        self.absoluteMeasurementError = [:]
        self.percentageMeasurementError = [:]
        self.repeatabilityResults = [:]
        self.screenshotReferences = []
        self.passFailStatus = "IN_PROGRESS"
        self.observedDefects = []
        self.requiredRecaptureNotes = []
        self.scanIndex = scanIndex
        self.truthBoundaryNote =
            "DRAFT_CANDIDATE only — no automatic VERIFIED_EXISTING or Passport promotion."
    }

    /// Compute absolute and percentage errors from manual vs scan-derived meters.
    public mutating func recomputeMeasurementErrors() {
        var absErr: [String: Double] = [:]
        var pctErr: [String: Double] = [:]
        for (k, manual) in manualReferenceMeasurements {
            guard let scanned = scanDerivedMeasurements[k] else { continue }
            let a = abs(scanned - manual)
            absErr[k] = a
            if manual != 0 { pctErr[k] = (a / abs(manual)) * 100.0 }
        }
        absoluteMeasurementError = absErr
        percentageMeasurementError = pctErr
    }
}

public enum ValidationEvidenceRedactor {
    /// Keys / substrings that must never appear in exported evidence payloads.
    public static let prohibitedSubstrings: [String] = [
        "password", "token", "authorization", "bearer", "api_key", "apikey",
        "signed_url", "public_url", "bucket", "street", "address", "ssn",
        "email@", "phone", "lat=", "lon=", "gps"
    ]

    /// Return a copy safe for repository-adjacent export / operator share-out.
    public static func redacted(_ run: ValidationEvidenceRun) -> ValidationEvidenceRun {
        var r = run
        r.testOperator = sanitizeOperator(r.testOperator)
        r.pseudonymousPropertyId = sanitizeId(r.pseudonymousPropertyId, prefix: "prop")
        r.pseudonymousRoomId = sanitizeId(r.pseudonymousRoomId, prefix: "room")
        r.screenshotReferences = r.screenshotReferences.map { sanitizePath($0) }
        r.observedDefects = r.observedDefects.map { scrub($0) }
        r.requiredRecaptureNotes = r.requiredRecaptureNotes.map { scrub($0) }
        r.interruptionEvents = r.interruptionEvents.map { scrub($0) }
        r.networkLossEvents = r.networkLossEvents.map { scrub($0) }
        r.guardianInterventions = r.guardianInterventions.map { scrub($0) }
        return r
    }

    public static func jsonExport(_ run: ValidationEvidenceRun, pretty: Bool = true) throws -> Data {
        let enc = JSONEncoder()
        if pretty {
            enc.outputFormatting = [.prettyPrinted, .sortedKeys]
        }
        enc.dateEncodingStrategy = .iso8601
        return try enc.encode(redacted(run))
    }

    public static func markdownSummary(_ run: ValidationEvidenceRun) -> String {
        let r = redacted(run)
        var lines: [String] = []
        lines.append("# H-014B.3 Device Validation Evidence (Redacted)")
        lines.append("")
        lines.append("- Validation run ID: `\(r.validationRunId)`")
        lines.append("- Commit SHA: `\(r.commitSha)`")
        lines.append("- App build: `\(r.applicationBuild)`")
        lines.append("- Device: `\(r.deviceModel)` / `\(r.osVersion)`")
        lines.append("- LiDAR: \(r.lidarAvailable) · RoomPlan: \(r.roomPlanAvailable)")
        lines.append("- Operator: `\(r.testOperator)`")
        lines.append("- Property (pseudonymous): `\(r.pseudonymousPropertyId)`")
        lines.append("- Room (pseudonymous): `\(r.pseudonymousRoomId)`")
        lines.append("- Scan index: \(r.scanIndex)")
        lines.append("- Started: \(r.startedAt)")
        lines.append("- Completed: \(r.completedAt ?? "—")")
        lines.append("- Guardian verdict: \(r.guardianFinalVerdict ?? "—") (v\(r.guardianVersion ?? "?"))")
        lines.append("- Candidate: \(r.candidateModelId ?? "—") / \(r.candidateModelState ?? "—")")
        lines.append("- Checksums declared/verified: \(r.declaredChecksumSha256 ?? "—") / \(r.verifiedChecksumSha256 ?? "—")")
        lines.append("- Chunks / retries / resumed: \(r.chunkCount.map(String.init) ?? "—") / \(r.retryCount) / \(r.resumedChunkIndexes)")
        lines.append("- Pass/fail: **\(r.passFailStatus)**")
        lines.append("- Truth boundary: \(r.truthBoundaryNote)")
        lines.append("")
        lines.append("## Measurement errors")
        if r.absoluteMeasurementError.isEmpty {
            lines.append("_No paired manual/scan measurements recorded._")
        } else {
            for (k, v) in r.absoluteMeasurementError.sorted(by: { $0.key < $1.key }) {
                let pct = r.percentageMeasurementError[k].map { String(format: "%.2f%%", $0) } ?? "—"
                lines.append("- \(k): abs=\(String(format: "%.4f", v)) m · pct=\(pct)")
            }
        }
        lines.append("")
        lines.append("## Defects / recapture notes")
        for d in r.observedDefects { lines.append("- Defect: \(d)") }
        for n in r.requiredRecaptureNotes { lines.append("- Recapture: \(n)") }
        if r.observedDefects.isEmpty && r.requiredRecaptureNotes.isEmpty {
            lines.append("_None recorded._")
        }
        lines.append("")
        lines.append("_This export is redacted. Do not attach real addresses, tokens, or private photos._")
        return lines.joined(separator: "\n")
    }

    public static func containsProhibitedContent(_ text: String) -> Bool {
        let lower = text.lowercased()
        return prohibitedSubstrings.contains { lower.contains($0) }
    }

    private static func sanitizeOperator(_ name: String) -> String {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return "operator-redacted" }
        if containsProhibitedContent(trimmed) { return "operator-redacted" }
        return trimmed
    }

    private static func sanitizeId(_ raw: String, prefix: String) -> String {
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "-_"))
        let filtered = String(raw.unicodeScalars.filter { allowed.contains($0) })
        if filtered.isEmpty { return "\(prefix)-redacted" }
        if containsProhibitedContent(filtered) { return "\(prefix)-redacted" }
        return filtered
    }

    private static func sanitizePath(_ path: String) -> String {
        // Keep only basename-like references; strip home directories / absolute paths.
        let base = (path as NSString).lastPathComponent
        return base.isEmpty ? "screenshot-redacted" : base
    }

    private static func scrub(_ text: String) -> String {
        containsProhibitedContent(text) ? "[redacted]" : text
    }
}
