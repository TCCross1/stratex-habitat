import Foundation

/// Local pending-upload manifest for H-014B.3 interruption recovery.
/// Stores only non-secret metadata beside staged artifact bytes in SecureLocalStore.
public struct PendingUploadManifest: Codable, Equatable {
    public let scanSessionId: String
    public let propertyId: String
    public let artifactFilename: String
    public let declaredChecksumSha256: String
    public let artifactType: String
    public let createdAt: String
    public let uploadSessionId: String?
    public let receivedIndexes: [Int]
    public let missingIndexes: [Int]

    public init(scanSessionId: String, propertyId: String, artifactFilename: String,
                declaredChecksumSha256: String, artifactType: String = "POINT_CLOUD",
                createdAt: String = ISO8601DateFormatter().string(from: Date()),
                uploadSessionId: String? = nil, receivedIndexes: [Int] = [],
                missingIndexes: [Int] = []) {
        self.scanSessionId = scanSessionId
        self.propertyId = propertyId
        self.artifactFilename = artifactFilename
        self.declaredChecksumSha256 = declaredChecksumSha256
        self.artifactType = artifactType
        self.createdAt = createdAt
        self.uploadSessionId = uploadSessionId
        self.receivedIndexes = receivedIndexes
        self.missingIndexes = missingIndexes
    }
}

public enum PendingUploadRecovery {
    public static let manifestFilename = "pending-upload.json"

    public static func save(_ manifest: PendingUploadManifest, store: SecureLocalStore) throws {
        let data = try JSONEncoder().encode(manifest)
        _ = try store.write(data, scanSessionId: manifest.scanSessionId, filename: manifestFilename)
    }

    public static func load(scanSessionId: String, store: SecureLocalStore) throws -> PendingUploadManifest? {
        let url = store.stagingURL(scanSessionId: scanSessionId, filename: manifestFilename)
        guard FileManager.default.fileExists(atPath: url.path) else { return nil }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(PendingUploadManifest.self, from: data)
    }

    /// Merge server missing indexes into a recovered manifest (precise resume).
    public static func withMissingIndexes(_ manifest: PendingUploadManifest,
                                          missing: [Int],
                                          uploadSessionId: String?,
                                          received: [Int]) -> PendingUploadManifest {
        PendingUploadManifest(
            scanSessionId: manifest.scanSessionId,
            propertyId: manifest.propertyId,
            artifactFilename: manifest.artifactFilename,
            declaredChecksumSha256: manifest.declaredChecksumSha256,
            artifactType: manifest.artifactType,
            createdAt: manifest.createdAt,
            uploadSessionId: uploadSessionId ?? manifest.uploadSessionId,
            receivedIndexes: received,
            missingIndexes: missing.sorted())
    }
}
