import Foundation
#if canImport(AVFoundation)
import AVFoundation
#endif
#if canImport(UIKit)
import UIKit
#endif

/// Device readiness probes for the H-014B.3 validation host.
///
/// These checks never grant property truth and never bypass Guardian or backend
/// authorization. They only inform the operator whether a physical LiDAR capture
/// can be attempted on this device.
public struct DeviceCapabilityReport: Equatable, Codable {
    public let lidarAvailable: Bool
    public let roomPlanAvailable: Bool
    public let cameraAuthorization: String
    public let deviceModel: String
    public let osVersion: String
    public let appBuild: String
    public let readyForCapture: Bool
    public let blockingReasons: [String]
}

public enum DeviceCapability {
    public static func evaluate(appBuild: String = "H014B3/0.1.0") -> DeviceCapabilityReport {
        let lidar = lidarAvailable()
        let roomPlan = roomPlanAvailable()
        let camera = cameraAuthorizationStatus()
        let model = deviceModel()
        let os = osVersion()
        var blockers: [String] = []
        if !lidar { blockers.append("LiDAR sensor not available on this device.") }
        if !roomPlan { blockers.append("RoomPlan framework not available or unsupported.") }
        if camera == "denied" || camera == "restricted" {
            blockers.append("Camera permission denied — open Settings to grant access.")
        }
        let ready = blockers.isEmpty && (camera == "authorized" || camera == "notDetermined")
        return DeviceCapabilityReport(
            lidarAvailable: lidar,
            roomPlanAvailable: roomPlan,
            cameraAuthorization: camera,
            deviceModel: model,
            osVersion: os,
            appBuild: appBuild,
            readyForCapture: ready && camera == "authorized",
            blockingReasons: blockers)
    }

    public static func roomPlanAvailable() -> Bool {
        #if canImport(RoomPlan)
        if #available(iOS 16.0, *) {
            return RoomCaptureCoordinator.isSupported
        }
        return false
        #else
        return false
        #endif
    }

    public static func lidarAvailable() -> Bool {
        // RoomPlan.isSupported is the authoritative Apple gate for LiDAR RoomPlan.
        roomPlanAvailable()
    }

    public static func cameraAuthorizationStatus() -> String {
        #if canImport(AVFoundation)
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: return "authorized"
        case .denied: return "denied"
        case .restricted: return "restricted"
        case .notDetermined: return "notDetermined"
        @unknown default: return "unknown"
        }
        #else
        return "unavailable"
        #endif
    }

    public static func requestCameraAccess() async -> Bool {
        #if canImport(AVFoundation)
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        if status == .authorized { return true }
        if status == .notDetermined {
            return await withCheckedContinuation { cont in
                AVCaptureDevice.requestAccess(for: .video) { granted in
                    cont.resume(returning: granted)
                }
            }
        }
        return false
        #else
        return false
        #endif
    }

    private static func deviceModel() -> String {
        #if canImport(UIKit)
        return UIDevice.current.model
        #else
        return "simulator-or-host"
        #endif
    }

    private static func osVersion() -> String {
        #if canImport(UIKit)
        return "iOS \(UIDevice.current.systemVersion)"
        #else
        return ProcessInfo.processInfo.operatingSystemVersionString
        #endif
    }
}
