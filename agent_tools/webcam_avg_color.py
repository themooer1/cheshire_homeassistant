#!/usr/bin/env python3
import sys
import cv2
import numpy as np


def get_average_rgb(camera=0, num_frames=10):
    if isinstance(camera, str):
        cap = cv2.VideoCapture(camera)
    else:
        backends = [cv2.CAP_V4L2, cv2.CAP_ANY, cv2.CAP_GSTREAMER]
        cap = None

        for backend in backends:
            cap = cv2.VideoCapture(camera, backend)
            if cap.isOpened():
                break
            cap.release()
            cap = None

    if cap is None or not cap.isOpened():
        print(f"Error: Could not open camera {camera} with any backend", file=sys.stderr)
        sys.exit(1)

    for _ in range(5):
        cap.read()

    frames = []
    for _ in range(num_frames):
        ret, frame = cap.read()
        if ret and frame is not None:
            frames.append(frame)

    cap.release()

    if not frames:
        print("Error: Could not read frames from camera", file=sys.stderr)
        sys.exit(1)

    avg_frame = np.mean(frames, axis=0)
    bgr_avg = np.mean(avg_frame, axis=(0, 1))
    r, g, b = int(bgr_avg[2]), int(bgr_avg[1]), int(bgr_avg[0])

    print(f"R:{r} G:{g} B:{b}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            camera = int(sys.argv[1])
        except ValueError:
            camera = sys.argv[1]
    else:
        camera = 0
    get_average_rgb(camera)
