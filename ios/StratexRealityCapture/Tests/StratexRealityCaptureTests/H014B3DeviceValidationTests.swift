import XCTest
@testable import StratexRealityCapture

final class H014B3DeviceValidationTests: XCTestCase {

    func testGuardianMissingInputFails() {
        let empty = QualityReport()
        let r = ScanQualityGuardian.evaluate(empty)
        XCTAssertEqual(r.verdict, .fail)
        XCTAssertTrue(r.findings.contains { $0.severity == .fail })
        XCTAssertEqual(r.recommendation, "RECAPTURE")
    }

    func testGuardianPassParityFixture() {
        var good = QualityReport()
        good.capturedAreaM2 = 20
        good.surfaceCoverage = ["WALL": 0.95, "FLOOR": 0.9, "CEILING": 0.85]
        good.wallCountDetected = 4
        good.wallCountExpected = 4
        good.trackingQuality = ["mean": 0.95, "limited_fraction": 0.02]
        good.driftEstimateM = 0.02
        good.frameCount = 300
        good.lowQualityFrameFraction = 0.05
        let r = ScanQualityGuardian.evaluate(good)
        XCTAssertEqual(r.verdict, .pass)
        XCTAssertEqual(r.score, 100)
        XCTAssertEqual(r.guardianVersion, "1.0.0")
    }

    func testCoachingNeverInventPassFromFail() {
        var bad = QualityReport()
        bad.capturedAreaM2 = 1
        bad.frameCount = 10
        let result = ScanQualityGuardian.evaluate(bad)
        XCTAssertEqual(result.verdict, .fail)
        let msgs = GuardianCoaching.messages(for: result)
        XCTAssertFalse(msgs.contains { $0.code == "READY_FOR_REVIEW" })
        XCTAssertFalse(GuardianCoaching.primaryInstruction(for: result).lowercased().contains("ready for review"))
    }

    func testCoachingMapsWallCoverage() {
        let finding = GuardianFinding(code: "WALL_COVERAGE_LOW", severity: .warn, message: "Wall coverage is below target.")
        let result = GuardianResult(guardianVersion: "1.0.0", verdict: .warn, coverageState: .partial,
                                    score: 80, findings: [finding], missingAreas: [], recommendation: "REVIEW")
        let primary = GuardianCoaching.primaryInstruction(for: result)
        XCTAssertTrue(primary.lowercased().contains("wall"))
    }

    func testEvidenceRedactionStripsSecretsAndPaths() {
        var run = ValidationEvidenceRun(
            commitSha: "abc123",
            applicationBuild: "H014B3/0.1.0",
            deviceModel: "iPhone",
            osVersion: "iOS 17",
            lidarAvailable: true,
            roomPlanAvailable: true,
            testOperator: "operator-a",
            pseudonymousPropertyId: "prop-demo-1",
            pseudonymousRoomId: "room-living-1")
        run.observedDefects = ["token=supersecret bearer leaked"]
        run.screenshotReferences = ["/Users/homeowner/Desktop/private-room.jpg"]
        run.requiredRecaptureNotes = ["password was visible on screen"]
        let redacted = ValidationEvidenceRedactor.redacted(run)
        XCTAssertEqual(redacted.observedDefects, ["[redacted]"])
        XCTAssertEqual(redacted.screenshotReferences, ["private-room.jpg"])
        XCTAssertEqual(redacted.requiredRecaptureNotes, ["[redacted]"])
        XCTAssertTrue(redacted.truthBoundaryNote.contains("DRAFT_CANDIDATE"))
        let json = try! ValidationEvidenceRedactor.jsonExport(run)
        let text = String(data: json, encoding: .utf8)!
        XCTAssertFalse(text.lowercased().contains("supersecret"))
        XCTAssertFalse(text.contains("/Users/homeowner"))
    }

    func testEvidenceMarkdownExportIsRedacted() {
        var run = ValidationEvidenceRun(
            commitSha: "deadbeef",
            applicationBuild: "H014B3/0.1.0",
            deviceModel: "iPad",
            osVersion: "iPadOS 17",
            lidarAvailable: true,
            roomPlanAvailable: true,
            testOperator: "pilot",
            pseudonymousPropertyId: "prop-x",
            pseudonymousRoomId: "room-y")
        run.guardianFinalVerdict = "PASS"
        run.candidateModelState = "DRAFT_CANDIDATE"
        run.passFailStatus = "PENDING_MANUAL_GATES"
        let md = ValidationEvidenceRedactor.markdownSummary(run)
        XCTAssertTrue(md.contains("DRAFT_CANDIDATE"))
        XCTAssertTrue(md.contains("redacted"))
        XCTAssertFalse(ValidationEvidenceRedactor.containsProhibitedContent(md.replacingOccurrences(of: "redacted", with: "")))
    }

    func testNoAutomaticTruthAcceptanceInEvidenceDefaults() {
        let run = ValidationEvidenceRun(
            commitSha: "sha",
            applicationBuild: "H014B3/0.1.0",
            deviceModel: "iPhone",
            osVersion: "iOS 16",
            lidarAvailable: false,
            roomPlanAvailable: false,
            testOperator: "op",
            pseudonymousPropertyId: "prop",
            pseudonymousRoomId: "room")
        XCTAssertNil(run.candidateModelState)
        XCTAssertTrue(run.truthBoundaryNote.contains("no automatic VERIFIED_EXISTING"))
        XCTAssertEqual(run.passFailStatus, "IN_PROGRESS")
    }

    func testDeviceCapabilityReportCodable() {
        let report = DeviceCapability.evaluate(appBuild: "H014B3/test")
        let data = try! JSONEncoder().encode(report)
        let decoded = try! JSONDecoder().decode(DeviceCapabilityReport.self, from: data)
        XCTAssertEqual(decoded.appBuild, "H014B3/test")
        // On macOS/Linux CI hosts RoomPlan is unavailable.
        #if !canImport(RoomPlan)
        XCTAssertFalse(decoded.roomPlanAvailable)
        XCTAssertFalse(decoded.lidarAvailable)
        #endif
    }

    func testStubCoordinatorDoesNotClaimSupportWithoutRoomPlan() {
        #if !canImport(RoomPlan)
        XCTAssertFalse(RoomCaptureCoordinator.isSupported)
        let c = RoomCaptureCoordinator()
        c.requestAuthorizationAndStart()
        XCTAssertEqual(c.state, .failed)
        XCTAssertNil(c.currentReport())
        XCTAssertNil(c.currentArtifactData())
        #endif
    }

    func testPendingUploadRecoveryRoundTrip() throws {
        let store = try SecureLocalStore(subdirectory: "H014B3Test-\(UUID().uuidString)")
        let manifest = PendingUploadManifest(
            scanSessionId: "scan-1",
            propertyId: "prop-1",
            artifactFilename: "capture.pointcloud",
            declaredChecksumSha256: "abc",
            missingIndexes: [2, 4])
        try PendingUploadRecovery.save(manifest, store: store)
        let loaded = try PendingUploadRecovery.load(scanSessionId: "scan-1", store: store)
        XCTAssertEqual(loaded, manifest)
        let resumed = PendingUploadRecovery.withMissingIndexes(
            manifest, missing: [4], uploadSessionId: "up-1", received: [0, 1, 2, 3])
        XCTAssertEqual(resumed.missingIndexes, [4])
        XCTAssertEqual(resumed.uploadSessionId, "up-1")
        store.purge(scanSessionId: "scan-1")
    }

    func testCoachingVersionIndependentOfGuardianVersion() {
        XCTAssertEqual(ScanQualityGuardian.version, "1.0.0")
        XCTAssertEqual(GuardianCoaching.version, "1.0.0")
        // Coaching may evolve; Guardian thresholds remain the verdict authority.
        XCTAssertFalse(GuardianCoaching.version.isEmpty)
    }
}
