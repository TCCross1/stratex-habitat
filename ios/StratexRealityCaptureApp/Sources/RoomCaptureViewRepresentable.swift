import SwiftUI
import StratexRealityCapture

#if canImport(RoomPlan) && canImport(UIKit)
import RoomPlan
import UIKit

/// UIKit bridge presenting Apple's `RoomCaptureView`.
/// `RoomCaptureView.captureSession` is get-only; the host binds the package
/// coordinator to that session on first layout.
struct RoomCaptureViewRepresentable: UIViewRepresentable {
    @Binding var coordinator: RoomCaptureCoordinator?

    func makeCoordinator() -> Bridge {
        Bridge()
    }

    func makeUIView(context: Context) -> RoomCaptureView {
        let view = RoomCaptureView(frame: .zero)
        // Bind package coordinator to the view-owned session (no second state machine).
        let bound = RoomCaptureCoordinator(captureSession: view.captureSession)
        context.coordinator.bound = bound
        DispatchQueue.main.async {
            self.coordinator = bound
        }
        return view
    }

    func updateUIView(_ uiView: RoomCaptureView, context: Context) {
        // Session is owned by the view; coordinator already observes it.
    }

    final class Bridge {
        var bound: RoomCaptureCoordinator?
    }
}
#else
struct RoomCaptureViewRepresentable: View {
    @Binding var coordinator: RoomCaptureCoordinator?
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
        .onAppear {
            if coordinator == nil {
                coordinator = RoomCaptureCoordinator()
            }
        }
    }
}
#endif
