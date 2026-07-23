import SwiftUI
import StratexRealityCapture
#if canImport(UIKit)
import UIKit
#endif

@main
struct StratexRealityCaptureAppApp: App {
    @StateObject private var session = ValidationSessionModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(session)
                #if canImport(UIKit)
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
                    session.handleAppInterruption(reason: "willResignActive")
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.didEnterBackgroundNotification)) { _ in
                    session.handleAppInterruption(reason: "didEnterBackground")
                }
                #endif
        }
    }
}
