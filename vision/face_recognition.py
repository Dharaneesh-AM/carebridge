import cv2
import numpy as np

CAMERA_DEVICE = "/dev/video0"

DETECTOR_MODEL = "models/face/face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = "models/face/face_recognition_sface_2021dec.onnx"
REFERENCE_FILE = "data/face/patient_embedding.npy"

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

# Conservative threshold based on our initial patient/other-person measurements.
PATIENT_THRESHOLD = 0.48

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

reference = np.load(REFERENCE_FILE).astype(np.float32)
reference /= np.linalg.norm(reference)

detector.setInputSize((IMAGE_WIDTH, IMAGE_HEIGHT))


def recognize_frame(frame):
    """
    Return the recognition state for one camera frame.

    Possible results:
        patient
        other_person
        no_face
        multiple_faces
    """

    if frame is None:
        return "no_face", None

    _, faces = detector.detect(frame)

    if faces is None or len(faces) == 0:
        return "no_face", None

    if len(faces) > 1:
        return "multiple_faces", None

    face = faces[0]

    aligned = recognizer.alignCrop(frame, face)
    feature = recognizer.feature(aligned).reshape(-1).astype(np.float32)

    norm = np.linalg.norm(feature)

    if norm == 0:
        return "other_person", 0.0

    feature /= norm

    score = float(
        recognizer.match(
            reference,
            feature,
            cv2.FaceRecognizerSF_FR_COSINE,
        )
    )

    if score >= PATIENT_THRESHOLD:
        return "patient", score

    return "other_person", score


def recognize_from_camera():
    """Capture one frame from the USB C270 and recognize the person."""

    camera = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)

    if not camera.isOpened():
        print("CAMERA ERROR: could not open", CAMERA_DEVICE)
        return "no_face", None

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))

    frame = None

    # C270 needs a short warm-up before reliable frames arrive.
    for _ in range(30):
        ok, current = camera.read()
        if ok and current is not None and current.size > 0:
            frame = current

    camera.release()

    if frame is None:
        print("CAMERA ERROR: no valid frame received")
        return "no_face", None

    return recognize_frame(frame)


if __name__ == "__main__":
    print("CareBridge USB camera face recognition test")
    print("Camera:", CAMERA_DEVICE)
    print("Threshold:", PATIENT_THRESHOLD)

    result, score = recognize_from_camera()

    print("RESULT:", result)
    print("SCORE:", score)
