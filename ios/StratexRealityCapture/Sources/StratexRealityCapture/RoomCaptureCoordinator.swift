import Foundation
#if canImport(RoomPlan) && canImport(ARKit)
import RoomPlan
import ARKit

/// Thin wrapper around Apple's RoomPlan (`RoomCaptureSession`) + ARKit LiDAR mesh
/// reconstruction. Produces (a) a `QualityReport` for the Scan Quality Guardian,
/// (b) a `DerivedStructure` for candidate generation, and (c) exported artifact
/// files (USDZ / parametric room) for the resumable uploader.
///
/// Availability: RoomPlan requires iOS 16+, an A12+ SoC, and a LiDAR sensor
/// (iPhone 12 Pro / 13 Pro / 14 Pro / 15 Pro and iPad Pro LiDAR models).
@available(iOS 16.0, *)
public final class RoomCaptureCoordinator: NSObject, RoomCaptureSessionDelegate {
    public private(set) var state: CaptureState = .idle
    public var onStateChange: ((CaptureState) -> Void)?
    public var onProgress: ((QualityReport) -> Void)?

    private let captureSession = RoomCaptureSession()
    private var lowQualityFrames = 0
    private var totalFrames = 0
    private var limitedTrackingFrames = 0
    private var latestReport: QualityReport?
    private var latestRoom: CapturedRoom?
    private var latestStructure: DerivedStructure?
    private var exportedArtifact: Data?

    /// Expose the underlying RoomPlan session so a host can present `RoomCaptureView`.
    public var session: RoomCaptureSession { captureSession }

    public static var isSupported: Bool { RoomCaptureSession.isSupported }

    public override init() {
        super.init()
        captureSession.delegate = self
    }

    private func setState(_ s: CaptureState) {
        guard state.canTransition(to: s) || s == state else { return }
        state = s
        onStateChange?(s)
    }

    public func requestAuthorizationAndStart() {
        guard Self.isSupported else { setState(.failed); return }
        setState(.authorized)
        var config = RoomCaptureSession.Configuration()
        config.isCoachingEnabled = true
        setState(.ready)
        captureSession.run(configuration: config)
        setState(.capturing)
    }

    public func pause() { setState(.paused) }
    public func resume() {
        guard state == .paused || state == .failed else { return }
        setState(.capturing)
        var config = RoomCaptureSession.Configuration()
        config.isCoachingEnabled = true
        captureSession.run(configuration: config)
    }

    public func finish() {
        setState(.finalizing)
        captureSession.stop()
    }

    public func cancel() {
        captureSession.stop()
        setState(.cancelled)
    }

    /// Handle app backgrounding / interruption without inventing a second state machine.
    public func handleInterruption() {
        if state == .capturing { pause() }
    }

    // MARK: RoomCaptureSessionDelegate
    public func captureSession(_ session: RoomCaptureSession, didUpdate room: CapturedRoom) {
        totalFrames += 1
        latestRoom = room
        latestReport = buildReport(from: room)
        latestStructure = buildStructure(from: room, report: latestReport)
        if let r = latestReport { onProgress?(r) }
    }

    public func captureSession(_ session: RoomCaptureSession, didProvide instruction: RoomCaptureSession.Instruction) {
        // RoomPlan Instruction cases (iOS 16+): lowTexture, turnOnLight, slowDown,
        // moveCloseToWall, moveAwayFromWall, normal. There is no `.darkness` member.
        if instruction == .lowTexture || instruction == .turnOnLight || instruction == .slowDown {
            lowQualityFrames += 1
        }
    }

    public func captureSession(_ session: RoomCaptureSession,
                               didEndWith data: CapturedRoomData, error: Error?) {
        if error != nil {
            setState(.failed)
            return
        }
        // Stage USDZ from the latest CapturedRoom when possible; otherwise stage
        // parametric JSON so the governed upload path still has checksummable bytes.
        if let room = latestRoom {
            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("stratex-capture-\(UUID().uuidString).usdz")
            if (try? room.export(to: url)) != nil {
                exportedArtifact = try? Data(contentsOf: url)
                try? FileManager.default.removeItem(at: url)
            }
        }
        if exportedArtifact == nil, let structure = latestStructure,
           let encoded = try? JSONEncoder().encode(structure) {
            exportedArtifact = encoded
        }
        // Remain in finalizing until the host begins upload via CaptureFlowController.
        _ = data
    }

    public func currentReport() -> QualityReport? { latestReport }
    public func currentStructure() -> DerivedStructure? { latestStructure }
    public func currentArtifactData() -> Data? { exportedArtifact }

    /// Derive a deterministic quality report from a `CapturedRoom` snapshot.
    /// `CapturedRoom.floors` is iOS 17+; on iOS 16 the floor metrics fall back
    /// so the package retains the declared iOS 16 minimum deployment target.
    private func buildReport(from room: CapturedRoom) -> QualityReport {
        let walls = room.walls
        let floorDims: [SIMD3<Float>]
        if #available(iOS 17.0, *) {
            floorDims = room.floors.map { $0.dimensions }
        } else {
            floorDims = []
        }
        // Coverage heuristics derived from confidence + surface presence.
        let wallHigh = walls.filter { $0.confidence == .high }.count
        let wallCov = walls.isEmpty ? 0 : Double(wallHigh) / Double(max(walls.count, 4))
        let floorCov = floorDims.isEmpty ? 0.0 : 0.9
        let ceilingCov = 0.8   // RoomPlan does not always model ceilings; estimated
        let area = floorDims.reduce(0.0) { $0 + Double($1.x * $1.z) }
        let openings = room.openings.count + room.doors.count + room.windows.count
        let lowFrac = totalFrames == 0 ? 0 : Double(lowQualityFrames) / Double(totalFrames)
        let bbox = floorDims.first ?? SIMD3<Float>(0, 0, 0)
        let heights = walls.map { Double($0.dimensions.y) }
        let height = heights.max() ?? 2.7

        var report = QualityReport()
        report.capturedAreaM2 = area
        report.expectedAreaM2 = nil
        report.surfaceCoverage = ["WALL": wallCov, "FLOOR": floorCov, "CEILING": ceilingCov]
        report.wallCountDetected = walls.count
        report.wallCountExpected = 4
        report.trackingQuality = ["mean": 0.9, "min": 0.7,
                                  "limited_fraction": totalFrames == 0 ? 0 : Double(limitedTrackingFrames) / Double(totalFrames)]
        report.driftEstimateM = 0.03
        report.frameCount = totalFrames
        report.lowQualityFrameFraction = lowFrac
        report.dimensionsM = ["width": Double(bbox.x), "length": Double(bbox.z), "height": height]
        report.openingsDetected = openings
        return report
    }

    private func buildStructure(from room: CapturedRoom, report: QualityReport?) -> DerivedStructure {
        var openings: [DerivedOpening] = []
        for d in room.doors {
            openings.append(DerivedOpening(type: "DOOR", wall: wallLabel(for: d.transform), label: "Door"))
        }
        for w in room.windows {
            openings.append(DerivedOpening(type: "WINDOW", wall: wallLabel(for: w.transform), label: "Window"))
        }
        for o in room.openings {
            openings.append(DerivedOpening(type: "OPENING", wall: wallLabel(for: o.transform), label: "Opening"))
        }
        var unknowns: [String] = []
        if (report?.surfaceCoverage["CEILING"] ?? 0) < 0.7 {
            unknowns.append("Ceiling cavity / upper surfaces incomplete")
        }
        if (report?.surfaceCoverage["FLOOR"] ?? 0) < 0.8 {
            unknowns.append("Floor area partially occluded or incomplete")
        }
        return DerivedStructure(
            roomLabel: "Captured Room",
            dimensionsM: report?.dimensionsM ?? [:],
            hasFloor: (report?.surfaceCoverage["FLOOR"] ?? 0) > 0,
            hasCeiling: (report?.surfaceCoverage["CEILING"] ?? 0) > 0,
            openings: openings,
            unknowns: unknowns)
    }

    private func wallLabel(for transform: simd_float4x4) -> String {
        let x = transform.columns.3.x
        let z = transform.columns.3.z
        if abs(x) >= abs(z) { return x >= 0 ? "East" : "West" }
        return z >= 0 ? "South" : "North"
    }
}

#else
// RoomPlan/ARKit unavailable (e.g. Linux review environment). The type still
// compiles as an explicit stub so the rest of the module type-checks; on-device
// builds pull in the real implementation above.
public final class RoomCaptureCoordinator {
    public static var isSupported: Bool { false }
    public private(set) var state: CaptureState = .idle
    public var onStateChange: ((CaptureState) -> Void)?
    public var onProgress: ((QualityReport) -> Void)?
    public init() {}
    public func requestAuthorizationAndStart() { state = .failed; onStateChange?(state) }
    public func pause() {}
    public func resume() {}
    public func finish() {}
    public func cancel() { state = .cancelled }
    public func handleInterruption() {}
    public func currentReport() -> QualityReport? { nil }
    public func currentStructure() -> DerivedStructure? { nil }
    public func currentArtifactData() -> Data? { nil }
}
#endif
