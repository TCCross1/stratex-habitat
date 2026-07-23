import Foundation

/// Deterministic coaching copy derived from Guardian findings / RoomPlan instructions.
///
/// The Guardian verdict remains the sole PASS/WARN/FAIL authority. This module only
/// translates existing findings into restrained operator guidance. It never invents
/// measurements, never auto-finishes a scan, and never approves property truth.
///
/// Versioned independently of Guardian thresholds so coaching wording can evolve
/// without changing the verdict algorithm (`ScanQualityGuardian.version`).
public enum GuardianCoaching {
    public static let version = "1.0.0"

    public struct Message: Equatable, Codable {
        public let code: String
        public let severity: GuardianVerdict
        public let instruction: String
    }

    /// Map a Guardian result into live coaching instructions.
    public static func messages(for result: GuardianResult) -> [Message] {
        var out: [Message] = []
        for f in result.findings {
            out.append(Message(code: f.code, severity: f.severity, instruction: instruction(for: f)))
        }
        for area in result.missingAreas where !out.contains(where: { $0.instruction.lowercased().contains(area.lowercased()) }) {
            out.append(Message(code: "MISSING_AREA", severity: result.verdict,
                               instruction: "Revisit: \(area)."))
        }
        if result.verdict == .pass {
            out.append(Message(code: "READY_FOR_REVIEW", severity: .pass,
                               instruction: "Scan quality is ready for review. Finish when the room looks complete."))
        }
        return out
    }

    /// Primary headline for the overlay (most severe finding, else ready message).
    public static func primaryInstruction(for result: GuardianResult) -> String {
        let msgs = messages(for: result)
        if let fail = msgs.first(where: { $0.severity == .fail }) { return fail.instruction }
        if let warn = msgs.first(where: { $0.severity == .warn }) { return warn.instruction }
        return msgs.last?.instruction ?? "Continue scanning."
    }

    private static func instruction(for finding: GuardianFinding) -> String {
        switch finding.code {
        case "WALL_COVERAGE_LOW", "MISSING_WALL":
            return "Revisit this wall. Sweep slowly until the wall is fully captured."
        case "FLOOR_COVERAGE_LOW":
            return "More floor coverage is required. Point the device downward and continue the sweep."
        case "CEILING_COVERAGE_LOW":
            return "Capture the upper corner and ceiling line. Tilt the device upward briefly."
        case "TRACKING_DEGRADED", "TRACKING_LIMITED_FRACTION", "DRIFT_EXCEEDED":
            return "Tracking quality has degraded. Move more slowly and keep textured surfaces in view."
        case "LOW_FRAME_QUALITY":
            return "Move more slowly. Improve lighting if the room is dark or low-texture."
        case "FRAME_COUNT_LOW":
            return "Additional sweep recommended. Continue until the frame count is adequate."
        case "INSUFFICIENT_AREA", "AREA_INCOMPLETE":
            return "More of the room is required. Complete a full perimeter before finishing."
        case "OPENING_CONFIDENCE_LOW":
            return "Opening confidence is low. Pause at each door and window for a clear view."
        default:
            return finding.message
        }
    }
}
