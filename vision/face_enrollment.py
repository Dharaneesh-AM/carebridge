import time
from pathlib import Path

import cv2
import numpy as np

CAMERA_DEVICE = "/dev/video0"

DETECTOR_MODEL = "models/face/face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = "models/face/face_recognition_sface_2021dec.onnx"
OUTPUT_FILE = Path("data/face/patient_embedding.npy")

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

detector = cv2.FaceDetectorYN_create(
    DETECTOR_MODEL,
    "",
    (IMAGE_WIDTH, IMAGE_HEIGHT),
    0.7,
    0.3,
    5000,
)

recognizer = cv2.FaceRecognizerSF_create(
    RECOGNIZER_MODEL,
    "",
)

camera = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)

if not camera.isOpened():
    raise RuntimeError(f"Could not open USB camera: {CAMERA_DEVICE}")

detector.setInputSize((IMAGE_WIDTH, IMAGE_HEIGHT))

embeddings = []

print("CareBridge patient enrollment started.")
print("Camera source: Logitech C270")
print("Look directly at the camera.")
print("Keep your face visible and reasonably still.")
print("Collecting 5 good samples...")

# Configure the C270 for the same resolution used by the face models.
camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))

try:
    while len(embeddings) < 5:
        ok, frame = camera.read()

        if not ok or frame is None:
            print("C270 camera frame failed.")
            time.sleep(0.5)
            continue

        _, faces = detector.detect(frame)

        if faces is None or len(faces) != 1:
            print(
                f"Waiting for exactly one face... "
                f"detected={0 if faces is None else len(faces)}"
            )
            time.sleep(0.5)
            continue

        face = faces[0]

        aligned = recognizer.alignCrop(frame, face)
        feature = recognizer.feature(aligned).reshape(-1).astype(np.float32)

        norm = np.linalg.norm(feature)

        if norm == 0:
            print("Invalid embedding. Retrying.")
            continue

        embeddings.append(feature / norm)

        print(f"Sample {len(embeddings)}/5 captured.")
        time.sleep(1.0)

finally:
    camera.release()

reference = np.mean(np.stack(embeddings), axis=0)

norm = np.linalg.norm(reference)

if norm == 0:
    raise RuntimeError("Could not create a valid patient reference.")

reference = reference / norm

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

np.save(OUTPUT_FILE, reference)

print("PATIENT ENROLLMENT: COMPLETE")
print("REFERENCE:", OUTPUT_FILE)
print("EMBEDDING SHAPE:", reference.shape)
