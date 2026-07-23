import Foundation
#if canImport(CryptoKit)
import CryptoKit
#endif

public enum HabitatAPIError: Error, LocalizedError {
    case http(Int, String)
    case notAuthenticated
    case decoding(String)
    public var errorDescription: String? {
        switch self {
        case .http(let c, let m): return "HTTP \(c): \(m)"
        case .notAuthenticated: return "Not authenticated"
        case .decoding(let m): return "Decoding failed: \(m)"
        }
    }
}

/// Thin async client for the STRATEX Habitat governed capture APIs (mounted at
/// `/api/reality/v1`). Authenticates against the same JWT-cookie/Bearer scheme
/// used by the web app. No object-store URLs are ever handled on-device — the
/// client only talks to the governed backend.
public final class HabitatAPIClient {
    private let baseURL: URL
    private let session: URLSession
    private var bearerToken: String?

    public init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    // MARK: Auth
    @discardableResult
    public func login(email: String, password: String) async throws -> String {
        let body = try JSONSerialization.data(withJSONObject: ["email": email, "password": password])
        var req = URLRequest(url: baseURL.appendingPathComponent("api/auth/login"))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        let (data, resp) = try await session.data(for: req)
        try Self.check(resp, data)
        // The web login sets an httpOnly cookie; a native token endpoint may also
        // return a bearer token. Capture whichever is available.
        if let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let token = (obj["token"] ?? obj["access_token"]) as? String {
            bearerToken = token
        }
        return bearerToken ?? ""
    }

    // MARK: Scan sessions
    public func createScanSession(propertyId: String, _ body: ScanSessionCreate) async throws -> ScanSession {
        try await post("api/reality/v1/properties/\(propertyId)/scan-sessions", body: body)
    }

    public func transition(scanSessionId: String, to state: String,
                           expectedVersion: Int? = nil, idempotencyKey: String? = nil) async throws {
        var payload: [String: Any] = ["to_state": state]
        if let v = expectedVersion { payload["expected_version"] = v }
        if let k = idempotencyKey { payload["idempotency_key"] = k }
        _ = try await postRaw("api/reality/v1/scan-sessions/\(scanSessionId)/transition", json: payload)
    }

    public func reportCaptureProgress(scanSessionId: String, nativeState: CaptureState,
                                      report: QualityReport) async throws {
        let payload: [String: Any] = [
            "native_state": nativeState.rawValue,
            "captured_area_m2": report.capturedAreaM2,
            "surface_coverage": report.surfaceCoverage,
            "tracking_quality": report.trackingQuality,
            "frame_count": report.frameCount,
        ]
        _ = try await postRaw("api/reality/v1/scan-sessions/\(scanSessionId)/capture-progress", json: payload)
    }

    public func evaluateGuardian(scanSessionId: String, report: QualityReport) async throws -> Data {
        let body = try JSONEncoder().encode(report)
        return try await postRaw("api/reality/v1/scan-sessions/\(scanSessionId)/guardian/evaluate", rawBody: body)
    }

    // MARK: Resumable upload
    public func initUpload(scanSessionId: String, _ body: UploadInit) async throws -> UploadSession {
        try await post("api/reality/v1/scan-sessions/\(scanSessionId)/uploads", body: body)
    }

    public func uploadStatus(uploadId: String) async throws -> UploadStatus {
        try await get("api/reality/v1/uploads/\(uploadId)")
    }

    @discardableResult
    public func putChunk(uploadId: String, index: Int, data: Data, sha256Hex: String?) async throws -> Data {
        var req = try request("api/reality/v1/uploads/\(uploadId)/chunks/\(index)", method: "PUT")
        req.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        if let s = sha256Hex { req.setValue(s, forHTTPHeaderField: "X-Chunk-SHA256") }
        req.httpBody = data
        let (respData, resp) = try await session.data(for: req)
        try Self.check(resp, respData)
        return respData
    }

    @discardableResult
    public func completeUpload(uploadId: String) async throws -> Data {
        try await postRaw("api/reality/v1/uploads/\(uploadId)/complete", json: [:])
    }

    public func abortUpload(uploadId: String) async throws {
        _ = try await postRaw("api/reality/v1/uploads/\(uploadId)/abort", json: [:])
    }

    // MARK: Candidate generation
    @discardableResult
    public func generateCandidate(scanSessionId: String, structure: DerivedStructure,
                                  artifactIds: [String]) async throws -> Data {
        var payload: [String: Any] = ["artifact_ids": artifactIds]
        payload["derived_structure"] = try JSONSerialization.jsonObject(with: JSONEncoder().encode(structure))
        return try await postRaw("api/reality/v1/scan-sessions/\(scanSessionId)/candidate", json: payload)
    }

    // MARK: - Helpers
    private func request(_ path: String, method: String) throws -> URLRequest {
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = method
        if let t = bearerToken { req.setValue("Bearer \(t)", forHTTPHeaderField: "Authorization") }
        return req
    }

    private func get<T: Decodable>(_ path: String) async throws -> T {
        let req = try request(path, method: "GET")
        let (data, resp) = try await session.data(for: req)
        try Self.check(resp, data)
        return try decode(data)
    }

    private func post<Body: Encodable, T: Decodable>(_ path: String, body: Body) async throws -> T {
        var req = try request(path, method: "POST")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(body)
        let (data, resp) = try await session.data(for: req)
        try Self.check(resp, data)
        return try decode(data)
    }

    @discardableResult
    private func postRaw(_ path: String, json: [String: Any] = [:], rawBody: Data? = nil) async throws -> Data {
        var req = try request(path, method: "POST")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = rawBody ?? (json.isEmpty ? "{}".data(using: .utf8) : try JSONSerialization.data(withJSONObject: json))
        let (data, resp) = try await session.data(for: req)
        try Self.check(resp, data)
        return data
    }

    private func decode<T: Decodable>(_ data: Data) throws -> T {
        do { return try JSONDecoder().decode(T.self, from: data) }
        catch { throw HabitatAPIError.decoding("\(error)") }
    }

    private static func check(_ resp: URLResponse, _ data: Data) throws {
        guard let http = resp as? HTTPURLResponse else { return }
        guard (200..<300).contains(http.statusCode) else {
            let msg = String(data: data, encoding: .utf8) ?? ""
            if http.statusCode == 401 { throw HabitatAPIError.notAuthenticated }
            throw HabitatAPIError.http(http.statusCode, msg)
        }
    }
}

// MARK: - Checksum helper
public enum Checksum {
    /// SHA-256 hex digest, matching the backend's lowercase hex contract.
    public static func sha256Hex(_ data: Data) -> String {
        #if canImport(CryptoKit)
        return SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        #else
        return ""  // CryptoKit unavailable at review time on Linux; present on iOS.
        #endif
    }
}
