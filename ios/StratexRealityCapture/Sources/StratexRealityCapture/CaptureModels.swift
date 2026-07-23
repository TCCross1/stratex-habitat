import Foundation

// MARK: - Capture state machine (mirrors backend enums.NATIVE_TO_SCAN_STATE)

/// The native capture states surfaced by the device. Each maps to EXACTLY ONE
/// canonical backend scan-session state; the backend remains the source of truth.
public enum CaptureState: String, Codable, CaseIterable {
    case idle        = "IDLE"
    case authorized  = "AUTHORIZED"
    case ready       = "READY"
    case capturing   = "CAPTURING"
    case paused      = "PAUSED"
    case finalizing  = "FINALIZING"
    case uploading   = "UPLOADING"
    case uploaded    = "UPLOADED"
    case processing  = "PROCESSING"
    case complete    = "COMPLETE"
    case failed      = "FAILED"
    case cancelled   = "CANCELLED"

    /// The canonical backend scan-session state this native state maps to.
    public var backendScanState: String {
        switch self {
        case .idle, .authorized: return "CREATED"
        case .ready:             return "CAPTURE_READY"
        case .capturing:         return "CAPTURE_IN_PROGRESS"
        case .paused:            return "CAPTURE_PAUSED"
        case .finalizing:        return "UPLOAD_PENDING"
        case .uploading:         return "UPLOAD_IN_PROGRESS"
        case .uploaded:          return "UPLOAD_COMPLETE"
        case .processing:        return "PROCESSING_IN_PROGRESS"
        case .complete:          return "QUALITY_REVIEW"
        case .failed:            return "FAILED_RECOVERABLE"
        case .cancelled:         return "CANCELLED"
        }
    }

    /// Legal client-side transitions. The backend independently enforces its own
    /// legal-transition map; this only prevents obviously-invalid local moves.
    public var allowedNext: Set<CaptureState> {
        switch self {
        case .idle:       return [.authorized, .cancelled, .failed]
        case .authorized: return [.ready, .cancelled, .failed]
        case .ready:      return [.capturing, .cancelled, .failed]
        case .capturing:  return [.paused, .finalizing, .cancelled, .failed]
        case .paused:     return [.capturing, .cancelled, .failed]
        case .finalizing: return [.uploading, .cancelled, .failed]
        case .uploading:  return [.uploaded, .failed, .cancelled]
        case .uploaded:   return [.processing, .complete, .failed]
        case .processing: return [.complete, .failed]
        case .complete:   return []
        case .failed:     return [.ready, .finalizing, .cancelled]
        case .cancelled:  return []
        }
    }

    public func canTransition(to next: CaptureState) -> Bool { allowedNext.contains(next) }
}

// MARK: - Codable contracts (match backend reality/schemas.py)

public struct DeviceInfo: Codable {
    public let model: String
    public let osVersion: String
    public let sensor: String
    public let framework: String
    public init(model: String, osVersion: String, sensor: String = "LiDAR Scanner",
                framework: String = "RoomPlan + ARKit") {
        self.model = model; self.osVersion = osVersion
        self.sensor = sensor; self.framework = framework
    }
    enum CodingKeys: String, CodingKey {
        case model, sensor, framework
        case osVersion = "os_version"
    }
}

public struct ScanSessionCreate: Codable {
    public let captureType: String
    public let coordinateFrameId: String?
    public let device: DeviceInfo?
    public let sensors: [String]?
    public let appVersion: String?
    public let captureMode: String?
    public let privacyClassification: String
    public let idempotencyKey: String?
    enum CodingKeys: String, CodingKey {
        case device, sensors
        case captureType = "capture_type"
        case coordinateFrameId = "coordinate_frame_id"
        case appVersion = "app_version"
        case captureMode = "capture_mode"
        case privacyClassification = "privacy_classification"
        case idempotencyKey = "idempotency_key"
    }
    public init(captureType: String = "INTERIOR_LIDAR", coordinateFrameId: String? = nil,
                device: DeviceInfo? = nil, sensors: [String]? = ["lidar", "camera", "imu"],
                appVersion: String? = "StratexRealityCapture/0.1.0", captureMode: String? = "ROOMPLAN",
                privacyClassification: String = "SENSITIVE_INTERIOR", idempotencyKey: String? = nil) {
        self.captureType = captureType; self.coordinateFrameId = coordinateFrameId
        self.device = device; self.sensors = sensors; self.appVersion = appVersion
        self.captureMode = captureMode; self.privacyClassification = privacyClassification
        self.idempotencyKey = idempotencyKey
    }
}

public struct ScanSession: Codable {
    public let id: String
    public let currentState: String
    public let propertyId: String
    enum CodingKeys: String, CodingKey {
        case id
        case currentState = "current_state"
        case propertyId = "property_id"
    }
}

public struct UploadInit: Codable {
    public let artifactType: String
    public let checksumSha256: String
    public let totalSize: Int
    public let chunkSize: Int
    public let contentType: String?
    public let truthClassification: String
    public let idempotencyKey: String?
    enum CodingKeys: String, CodingKey {
        case artifactType = "artifact_type"
        case checksumSha256 = "checksum_sha256"
        case totalSize = "total_size"
        case chunkSize = "chunk_size"
        case contentType = "content_type"
        case truthClassification = "truth_classification"
        case idempotencyKey = "idempotency_key"
    }
    public init(artifactType: String, checksumSha256: String, totalSize: Int, chunkSize: Int,
                contentType: String? = "application/octet-stream",
                truthClassification: String = "UNKNOWN", idempotencyKey: String? = nil) {
        self.artifactType = artifactType; self.checksumSha256 = checksumSha256
        self.totalSize = totalSize; self.chunkSize = chunkSize; self.contentType = contentType
        self.truthClassification = truthClassification; self.idempotencyKey = idempotencyKey
    }
}

public struct UploadSession: Codable {
    public let id: String
    public let totalChunks: Int
    public let chunkSize: Int
    public let state: String
    public let missingIndexes: [Int]?
    enum CodingKeys: String, CodingKey {
        case id, state
        case totalChunks = "total_chunks"
        case chunkSize = "chunk_size"
        case missingIndexes = "missing_indexes"
    }
}

public struct UploadStatus: Codable {
    public let state: String
    public let totalChunks: Int
    public let receivedIndexes: [Int]
    public let missingIndexes: [Int]
    public let complete: Bool
    enum CodingKeys: String, CodingKey {
        case state, complete
        case totalChunks = "total_chunks"
        case receivedIndexes = "received_indexes"
        case missingIndexes = "missing_indexes"
    }
}

/// The deterministic capture-quality report sent to the backend Guardian (and
/// evaluated locally by `ScanQualityGuardian` for on-device pre-flight).
public struct QualityReport: Codable {
    public var capturedAreaM2: Double
    public var expectedAreaM2: Double?
    public var surfaceCoverage: [String: Double]
    public var wallCountDetected: Int
    public var wallCountExpected: Int
    public var trackingQuality: [String: Double]
    public var driftEstimateM: Double
    public var frameCount: Int
    public var lowQualityFrameFraction: Double
    public var dimensionsM: [String: Double]
    public var openingsDetected: Int
    enum CodingKeys: String, CodingKey {
        case capturedAreaM2 = "captured_area_m2"
        case expectedAreaM2 = "expected_area_m2"
        case surfaceCoverage = "surface_coverage"
        case wallCountDetected = "wall_count_detected"
        case wallCountExpected = "wall_count_expected"
        case trackingQuality = "tracking_quality"
        case driftEstimateM = "drift_estimate_m"
        case frameCount = "frame_count"
        case lowQualityFrameFraction = "low_quality_frame_fraction"
        case dimensionsM = "dimensions_m"
        case openingsDetected = "openings_detected"
    }
    public init(capturedAreaM2: Double = 0, expectedAreaM2: Double? = nil,
                surfaceCoverage: [String: Double] = [:], wallCountDetected: Int = 0,
                wallCountExpected: Int = 4, trackingQuality: [String: Double] = [:],
                driftEstimateM: Double = 0, frameCount: Int = 0,
                lowQualityFrameFraction: Double = 0, dimensionsM: [String: Double] = [:],
                openingsDetected: Int = 0) {
        self.capturedAreaM2 = capturedAreaM2; self.expectedAreaM2 = expectedAreaM2
        self.surfaceCoverage = surfaceCoverage; self.wallCountDetected = wallCountDetected
        self.wallCountExpected = wallCountExpected; self.trackingQuality = trackingQuality
        self.driftEstimateM = driftEstimateM; self.frameCount = frameCount
        self.lowQualityFrameFraction = lowQualityFrameFraction; self.dimensionsM = dimensionsM
        self.openingsDetected = openingsDetected
    }
}

/// A single opening/door/window derived by RoomPlan for candidate generation.
public struct DerivedOpening: Codable {
    public let type: String   // DOOR | WINDOW | OPENING
    public let wall: String   // North | East | South | West
    public let label: String?
    public init(type: String, wall: String, label: String? = nil) {
        self.type = type; self.wall = wall; self.label = label
    }
}

public struct DerivedStructure: Codable {
    public let roomLabel: String?
    public let dimensionsM: [String: Double]
    public let hasFloor: Bool
    public let hasCeiling: Bool
    public let openings: [DerivedOpening]
    public let unknowns: [String]
    enum CodingKeys: String, CodingKey {
        case openings, unknowns
        case roomLabel = "room_label"
        case dimensionsM = "dimensions_m"
        case hasFloor = "has_floor"
        case hasCeiling = "has_ceiling"
    }
    public init(roomLabel: String? = nil, dimensionsM: [String: Double],
                hasFloor: Bool, hasCeiling: Bool,
                openings: [DerivedOpening] = [], unknowns: [String] = []) {
        self.roomLabel = roomLabel; self.dimensionsM = dimensionsM
        self.hasFloor = hasFloor; self.hasCeiling = hasCeiling
        self.openings = openings; self.unknowns = unknowns
    }
}
