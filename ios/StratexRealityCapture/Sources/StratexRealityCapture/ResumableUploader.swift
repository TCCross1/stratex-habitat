import Foundation

/// Resumable, integrity-checked chunked uploader for heavy capture artifacts.
///
/// Behaviour:
///  * Splits the artifact into fixed-size chunks (default 4 MiB, < 8 MiB backend cap).
///  * Uploads each chunk with a per-chunk SHA-256 header; retries with backoff.
///  * On interruption/relaunch, queries `uploadStatus` and resends ONLY the
///    missing indexes (true resume).
///  * Completes by asking the backend to assemble + verify the whole-file SHA-256.
public actor ResumableUploader {
    public struct Progress: Sendable {
        public let sent: Int
        public let total: Int
        public var fraction: Double { total == 0 ? 1 : Double(sent) / Double(total) }
    }

    private let api: HabitatAPIClient
    private let chunkSize: Int
    private let maxAttemptsPerChunk: Int

    public init(api: HabitatAPIClient, chunkSize: Int = 4 * 1024 * 1024, maxAttemptsPerChunk: Int = 5) {
        self.api = api
        self.chunkSize = chunkSize
        self.maxAttemptsPerChunk = maxAttemptsPerChunk
    }

    /// Upload the file at `fileURL` as an artifact of `artifactType` for `scanSessionId`.
    /// Returns the completion response bytes (artifact manifest public view).
    @discardableResult
    public func upload(fileURL: URL, artifactType: String, scanSessionId: String,
                       onProgress: (@Sendable (Progress) -> Void)? = nil) async throws -> Data {
        let attributes = try FileManager.default.attributesOfItem(atPath: fileURL.path)
        let totalSize = (attributes[.size] as? Int) ?? 0
        guard totalSize > 0 else { throw HabitatAPIError.http(422, "empty artifact") }

        let fileData = try Data(contentsOf: fileURL, options: .mappedIfSafe)
        let checksum = Checksum.sha256Hex(fileData)

        let session = try await api.initUpload(
            scanSessionId: scanSessionId,
            UploadInit(artifactType: artifactType, checksumSha256: checksum,
                       totalSize: totalSize, chunkSize: chunkSize))

        let total = session.totalChunks
        // Determine which chunks still need sending (resume support).
        var missing = Set(session.missingIndexes ?? Array(0..<total))
        if missing.isEmpty { missing = Set(0..<total) }

        for index in 0..<total {
            guard missing.contains(index) else { continue }
            let start = index * chunkSize
            let end = min(start + chunkSize, totalSize)
            let chunk = fileData.subdata(in: start..<end)
            try await sendChunk(uploadId: session.id, index: index, chunk: chunk)
            onProgress?(Progress(sent: index + 1, total: total))
        }

        // Verify remotely-known completeness before asking to finalize.
        let status = try await api.uploadStatus(uploadId: session.id)
        if !status.missingIndexes.isEmpty {
            for index in status.missingIndexes {
                let start = index * chunkSize
                let end = min(start + chunkSize, totalSize)
                try await sendChunk(uploadId: session.id, index: index, chunk: fileData.subdata(in: start..<end))
            }
        }
        return try await completeWithRetry(uploadId: session.id)
    }

    private func sendChunk(uploadId: String, index: Int, chunk: Data) async throws {
        var attempt = 0
        while true {
            do {
                _ = try await api.putChunk(uploadId: uploadId, index: index, data: chunk,
                                           sha256Hex: Checksum.sha256Hex(chunk))
                return
            } catch {
                attempt += 1
                if attempt >= maxAttemptsPerChunk { throw error }
                try await Task.sleep(nanoseconds: UInt64(pow(2.0, Double(attempt)) * 250_000_000))
            }
        }
    }

    private func completeWithRetry(uploadId: String) async throws -> Data {
        var attempt = 0
        while true {
            do { return try await api.completeUpload(uploadId: uploadId) }
            catch HabitatAPIError.http(let code, _) where code == 502 && attempt < 3 {
                attempt += 1
                try await Task.sleep(nanoseconds: UInt64(attempt) * 1_000_000_000)
            }
        }
    }
}
