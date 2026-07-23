import Foundation

/// On-device deterministic mirror of the backend `reality/scan_guardian.py`.
///
/// IMPORTANT: The thresholds below MUST stay in lock-step with the backend
/// (guardian_version). This lets the app give the homeowner instant, identical
/// pre-flight feedback ("recapture the ceiling") before uploading, while the
/// backend re-runs the SAME deterministic checks as the authoritative gate.
public enum GuardianVerdict: String, Codable { case pass = "PASS", warn = "WARN", fail = "FAIL" }
public enum CoverageState: String, Codable { case complete = "COMPLETE", partial = "PARTIAL", incomplete = "INCOMPLETE" }

public struct GuardianFinding: Codable, Equatable {
    public let code: String
    public let severity: GuardianVerdict
    public let message: String
    public init(code: String, severity: GuardianVerdict, message: String) {
        self.code = code; self.severity = severity; self.message = message
    }
}

public struct GuardianResult: Codable, Equatable {
    public let guardianVersion: String
    public let verdict: GuardianVerdict
    public let coverageState: CoverageState
    public let score: Int
    public let findings: [GuardianFinding]
    public let missingAreas: [String]
    public let recommendation: String
    public init(guardianVersion: String, verdict: GuardianVerdict, coverageState: CoverageState,
                score: Int, findings: [GuardianFinding], missingAreas: [String],
                recommendation: String) {
        self.guardianVersion = guardianVersion; self.verdict = verdict
        self.coverageState = coverageState; self.score = score
        self.findings = findings; self.missingAreas = missingAreas
        self.recommendation = recommendation
    }
}

public enum ScanQualityGuardian {
    public static let version = "1.0.0"

    // Fixed thresholds — MUST match backend THRESHOLDS.
    struct T { let pass: Double; let warn: Double; let lowerIsBetter: Bool }
    static let thresholds: [String: T] = [
        "wall_coverage":         T(pass: 0.85, warn: 0.60, lowerIsBetter: false),
        "floor_coverage":        T(pass: 0.80, warn: 0.50, lowerIsBetter: false),
        "ceiling_coverage":      T(pass: 0.70, warn: 0.40, lowerIsBetter: false),
        "tracking_mean":         T(pass: 0.80, warn: 0.60, lowerIsBetter: false),
        "tracking_limited_frac": T(pass: 0.10, warn: 0.30, lowerIsBetter: true),
        "drift_m":               T(pass: 0.05, warn: 0.15, lowerIsBetter: true),
        "low_quality_frac":      T(pass: 0.15, warn: 0.35, lowerIsBetter: true),
        "area_ratio":            T(pass: 0.90, warn: 0.70, lowerIsBetter: false),
    ]
    static let minCapturedAreaM2 = 4.0
    static let minFrameCount = 120
    static let warnFrameCount = 240
    static let severityWeight: [GuardianVerdict: Int] = [.warn: 8, .fail: 25]

    static func grade(_ measured: Double, _ key: String) -> GuardianVerdict {
        guard let t = thresholds[key] else { return .pass }
        if t.lowerIsBetter {
            if measured <= t.pass { return .pass }
            if measured <= t.warn { return .warn }
            return .fail
        } else {
            if measured >= t.pass { return .pass }
            if measured >= t.warn { return .warn }
            return .fail
        }
    }

    public static func evaluate(_ r: QualityReport) -> GuardianResult {
        var findings: [GuardianFinding] = []
        var missing: [String] = []

        for (name, cov, key) in [("wall", r.surfaceCoverage["WALL"] ?? 0, "wall_coverage"),
                                 ("floor", r.surfaceCoverage["FLOOR"] ?? 0, "floor_coverage"),
                                 ("ceiling", r.surfaceCoverage["CEILING"] ?? 0, "ceiling_coverage")] {
            let sev = grade(cov, key)
            if sev != .pass {
                findings.append(.init(code: "\(name.uppercased())_COVERAGE_LOW", severity: sev,
                                      message: "\(name.capitalized) coverage is below target."))
                missing.append("\(name) surfaces (partial coverage)")
            }
        }

        if r.wallCountDetected < r.wallCountExpected {
            let n = r.wallCountExpected - r.wallCountDetected
            let sev: GuardianVerdict = n >= 2 ? .fail : .warn
            findings.append(.init(code: "MISSING_WALL", severity: sev,
                                  message: "\(n) of \(r.wallCountExpected) walls were not captured."))
            missing.append("\(n) uncaptured wall(s)")
        }

        if let m = r.trackingQuality["mean"], grade(m, "tracking_mean") != .pass {
            findings.append(.init(code: "TRACKING_DEGRADED", severity: grade(m, "tracking_mean"),
                                  message: "Mean tracking quality indicates degraded tracking."))
        }
        if let lf = r.trackingQuality["limited_fraction"], grade(lf, "tracking_limited_frac") != .pass {
            findings.append(.init(code: "TRACKING_LIMITED_FRACTION", severity: grade(lf, "tracking_limited_frac"),
                                  message: "Tracking was limited for too much of the capture."))
        }
        if grade(r.driftEstimateM, "drift_m") != .pass {
            findings.append(.init(code: "DRIFT_EXCEEDED", severity: grade(r.driftEstimateM, "drift_m"),
                                  message: "Estimated drift exceeds the PLANNING tolerance."))
        }
        if r.capturedAreaM2 < minCapturedAreaM2 {
            findings.append(.init(code: "INSUFFICIENT_AREA", severity: .fail,
                                  message: "Captured area is below the minimum for a valid room."))
        }
        if let exp = r.expectedAreaM2, exp > 0 {
            let ratio = r.capturedAreaM2 / exp
            if grade(ratio, "area_ratio") != .pass {
                findings.append(.init(code: "AREA_INCOMPLETE", severity: grade(ratio, "area_ratio"),
                                      message: "Captured only part of the expected floor area."))
            }
        }
        if grade(r.lowQualityFrameFraction, "low_quality_frac") != .pass {
            findings.append(.init(code: "LOW_FRAME_QUALITY", severity: grade(r.lowQualityFrameFraction, "low_quality_frac"),
                                  message: "Too many low-quality frames."))
        }
        if r.frameCount < minFrameCount {
            findings.append(.init(code: "FRAME_COUNT_LOW", severity: .fail, message: "Too few frames captured."))
        } else if r.frameCount < warnFrameCount {
            findings.append(.init(code: "FRAME_COUNT_LOW", severity: .warn, message: "Frame count below recommended."))
        }

        let hasFail = findings.contains { $0.severity == .fail }
        let hasWarn = findings.contains { $0.severity == .warn }
        let verdict: GuardianVerdict = hasFail ? .fail : (hasWarn ? .warn : .pass)
        let coverage: CoverageState = hasFail ? .incomplete : (hasWarn ? .partial : .complete)
        let recommendation = hasFail ? "RECAPTURE" : (hasWarn ? "REVIEW" : "ACCEPT_CANDIDATE")
        var score = 100
        for f in findings { score -= (severityWeight[f.severity] ?? 0) }
        score = max(0, min(100, score))

        return GuardianResult(guardianVersion: version, verdict: verdict, coverageState: coverage,
                              score: score, findings: findings, missingAreas: missing,
                              recommendation: recommendation)
    }
}
