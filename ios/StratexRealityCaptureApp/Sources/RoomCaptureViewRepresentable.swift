import SwiftUI
import StratexRealityCapture

#if canImport(RoomPlan) && canImport(UIKit)
import RoomPlan
import UIKit

/// UIKit bridge presenting Apple's `RoomCaptureView` bound to the package coordinator session.
struct RoomCaptureViewRepresentable: UIViewRepresentable {
    let coordinator: RoomCaptureCoordinator

    func makeUIView(context: Context) -> RoomCaptureView {
        let view = RoomCaptureView(frame: .zero)
        view.captureSession = coordinator.session
        return view
    }

    func updateUIView(_ uiView: RoomCaptureView, context: Context) {
        uiView.captureSession = coordinator.session
    }
}
#else
struct RoomCaptureViewRepresentable: View {
    let coordinator: RoomCaptureCoordinator
    var body: some View {
        ZStack {
            Color.black.opacity(0.85)
            VStack(spacing: 8) {
                Text("RoomPlan preview unavailable")
                    .foregroundStyle(.white)
                Text(RoomCaptureCoordinator.isSupported
                     ? "Attach a LiDAR device to preview."
                     : "LiDAR / RoomPlan not supported on this destination.")
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.7))
                    .multilineTextAlignment(.center)
            }
            .padding()
        }
    }
}
#endif
