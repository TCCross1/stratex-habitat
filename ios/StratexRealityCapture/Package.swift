// swift-tools-version:5.9
// StratexRealityCapture — thin native LiDAR capture client for STRATEX Habitat.
//
// NOTE: This package targets iOS/iPadOS and depends on Apple's RoomPlan + ARKit
// (LiDAR). It is authored as reviewable source; it can only be BUILT and RUN on
// macOS with Xcode against a LiDAR-equipped device (iPhone 12 Pro+/iPad Pro).
// See docs/h014b/H014B_ENVIRONMENT_AND_REPOSITORY_RECON.md for the environment
// classification (native build/run BLOCKED in the Linux CI/dev container).
import PackageDescription

let package = Package(
    name: "StratexRealityCapture",
    // iOS 16+ is the product target (RoomPlan). macOS 13+ is declared so the
    // portable (non-RoomPlan) sources + Guardian unit tests can compile under
    // `swift build`/`swift test` on GitHub Actions macOS runners. RoomPlan/ARKit
    // remain excluded via `#if canImport` on non-iOS hosts.
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [
        .library(name: "StratexRealityCapture", targets: ["StratexRealityCapture"])
    ],
    targets: [
        .target(
            name: "StratexRealityCapture",
            path: "Sources/StratexRealityCapture"
        ),
        .testTarget(
            name: "StratexRealityCaptureTests",
            dependencies: ["StratexRealityCapture"],
            path: "Tests/StratexRealityCaptureTests"
        )
    ]
)
