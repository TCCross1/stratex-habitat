import Foundation

/// On-device secure staging for capture artifacts (Phase 10 — local data security).
///
/// Governance:
///  * All capture files are written with `.completeFileProtection` (encrypted at
///    rest, unavailable while the device is locked).
///  * Files live in a dedicated Application-Support subdirectory excluded from
///    iCloud/iTunes backup.
///  * `purge(...)` deletes the local copy immediately after the governed upload
///    completes, so sensitive interior imagery/geometry does not linger.
public final class SecureLocalStore {
    public enum StoreError: Error { case notFound, ioError(String) }

    private let root: URL
    private let fm = FileManager.default

    public init(subdirectory: String = "StratexRealityCapture") throws {
        let base = try fm.url(for: .applicationSupportDirectory, in: .userDomainMask,
                              appropriateFor: nil, create: true)
        root = base.appendingPathComponent(subdirectory, isDirectory: true)
        if !fm.fileExists(atPath: root.path) {
            try fm.createDirectory(at: root, withIntermediateDirectories: true,
                                   attributes: Self.directoryProtectionAttributes)
        }
        try excludeFromBackup(root)
    }

    public func stagingURL(scanSessionId: String, filename: String) -> URL {
        let dir = root.appendingPathComponent(scanSessionId, isDirectory: true)
        try? fm.createDirectory(at: dir, withIntermediateDirectories: true,
                                attributes: Self.directoryProtectionAttributes)
        return dir.appendingPathComponent(filename)
    }

    @discardableResult
    public func write(_ data: Data, scanSessionId: String, filename: String) throws -> URL {
        let url = stagingURL(scanSessionId: scanSessionId, filename: filename)
        do {
            try data.write(to: url, options: Self.writeOptions)
            try excludeFromBackup(url)
            return url
        } catch { throw StoreError.ioError("\(error)") }
    }

    /// iOS: complete file protection. macOS CI / review hosts: atomic write only
    /// (FileProtectionType is an iOS data-protection concept).
    private static var directoryProtectionAttributes: [FileAttributeKey: Any]? {
        #if os(iOS)
        return [.protectionKey: FileProtectionType.complete]
        #else
        return nil
        #endif
    }

    private static var writeOptions: Data.WritingOptions {
        #if os(iOS)
        return [.completeFileProtection, .atomic]
        #else
        return [.atomic]
        #endif
    }

    /// Delete all locally staged files for a scan session (call after upload completes).
    public func purge(scanSessionId: String) {
        let dir = root.appendingPathComponent(scanSessionId, isDirectory: true)
        try? fm.removeItem(at: dir)
    }

    /// Purge stale staging older than `maxAge` (e.g. abandoned captures).
    public func purgeStale(olderThan maxAge: TimeInterval = 72 * 3600) {
        guard let items = try? fm.contentsOfDirectory(at: root, includingPropertiesForKeys: [.contentModificationDateKey]) else { return }
        let cutoff = Date().addingTimeInterval(-maxAge)
        for item in items {
            if let date = (try? item.resourceValues(forKeys: [.contentModificationDateKey]))?.contentModificationDate,
               date < cutoff {
                try? fm.removeItem(at: item)
            }
        }
    }

    private func excludeFromBackup(_ url: URL) throws {
        var mutable = url
        var values = URLResourceValues()
        values.isExcludedFromBackup = true
        try mutable.setResourceValues(values)
    }
}
