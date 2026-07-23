import XCTest
@testable import StratexRealityCapture

/// These tests mirror the backend `tests/test_h014b_capture.py::TestGuardianDeterminism`.
/// They lock the on-device Guardian to the SAME deterministic verdicts as the
/// authoritative backend Guardian (guardian_version 1.0.0). Run on macOS with:
///   `swift test`  (see docs/h014b/H014B_CI_AND_TESTING.md).
final class ScanQualityGuardianTests: XCTestCase {

    private func goodReport() -> QualityReport {
        var r = QualityReport()
        r.capturedAreaM2 = 29.77; r.expectedAreaM2 = 29.77
        r.surfaceCoverage = ["WALL": 0.96, "FLOOR": 0.93, "CEILING": 0.88]
        r.wallCountDetected = 4; r.wallCountExpected = 4
        r.trackingQuality = ["mean": 0.94, "min": 0.71, "limited_fraction": 0.04]
        r.driftEstimateM = 0.021; r.frameCount = 812; r.lowQualityFrameFraction = 0.06
        r.dimensionsM = ["width": 4.88, "length": 6.10, "height": 2.74]; r.openingsDetected = 3
        return r
    }

    private func badReport() -> QualityReport {
        var r = QualityReport()
        r.capturedAreaM2 = 2.0; r.expectedAreaM2 = 30.0
        r.surfaceCoverage = ["WALL": 0.3, "FLOOR": 0.2, "CEILING": 0.1]
        r.wallCountDetected = 1; r.wallCountExpected = 4
        r.trackingQuality = ["mean": 0.4, "min": 0.1, "limited_fraction": 0.7]
        r.driftEstimateM = 0.4; r.frameCount = 30; r.lowQualityFrameFraction = 0.6
        r.dimensionsM = ["width": 4.0, "length": 5.0, "height": 2.6]; r.openingsDetected = 0
        return r
    }

    func testPassIsDeterministicAndFull() {
        let a = ScanQualityGuardian.evaluate(goodReport())
        let b = ScanQualityGuardian.evaluate(goodReport())
        XCTAssertEqual(a.verdict, .pass)
        XCTAssertEqual(a.score, 100)
        XCTAssertEqual(a.coverageState, .complete)
        XCTAssertEqual(a.recommendation, "ACCEPT_CANDIDATE")
        XCTAssertEqual(a, b)   // identical inputs → identical output
    }

    func testFailSurfacesFindingsAndRecapture() {
        let r = ScanQualityGuardian.evaluate(badReport())
        XCTAssertEqual(r.verdict, .fail)
        XCTAssertEqual(r.recommendation, "RECAPTURE")
        let codes = Set(r.findings.map { $0.code })
        XCTAssertTrue(codes.contains("WALL_COVERAGE_LOW"))
        XCTAssertTrue(codes.contains("MISSING_WALL"))
        XCTAssertTrue(codes.contains("DRIFT_EXCEEDED"))
        XCTAssertTrue(codes.contains("INSUFFICIENT_AREA"))
        XCTAssertFalse(r.missingAreas.isEmpty)
    }

    func testNativeStateMappingMatchesBackend() {
        XCTAssertEqual(CaptureState.capturing.backendScanState, "CAPTURE_IN_PROGRESS")
        XCTAssertEqual(CaptureState.uploaded.backendScanState, "UPLOAD_COMPLETE")
        XCTAssertEqual(CaptureState.complete.backendScanState, "QUALITY_REVIEW")
    }
}
