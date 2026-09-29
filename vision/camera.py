import cv2
import time


CAMERA_DEVICE = "/dev/video0"
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 5


def get_camera_source():
    return CAMERA_DEVICE


def open_camera():
    camera = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)

    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera device: {CAMERA_DEVICE}")

    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    # C270 needs a short warm-up before valid frames arrive.
    time.sleep(2)

    for _ in range(10):
        ok, frame = camera.read()

        if ok and frame is not None and frame.mean() > 5:
            return camera

    camera.release()
    raise RuntimeError("Camera opened but did not produce a valid image frame")


if __name__ == "__main__":
    camera = open_camera()

    ok, frame = camera.read()

    print("FRAME RECEIVED:", ok)

    if ok:
        print("FRAME SHAPE:", frame.shape)
        print("FRAME MEAN:", frame.mean())
        print("FRAME MIN:", frame.min())
        print("FRAME MAX:", frame.max())

    camera.release()
