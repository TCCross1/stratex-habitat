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
    platforms: [.iOS(.v16)],   // RoomPlan requires iOS 16+
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
