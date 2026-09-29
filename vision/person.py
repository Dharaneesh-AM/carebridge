import cv2
import numpy as np
import onnxruntime as ort


MODEL_PATH = "models/vision/yolox_nano.onnx"
INPUT_SIZE = 416
PERSON_CLASS = 0
CONFIDENCE_THRESHOLD = 0.50


_session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)


def detect_person(frame):
    """
    Detect whether a person is present in the camera frame.

    Returns:
        True  -> person detected above threshold
        False -> no person detected
    """
    if frame is None:
        return False

    image = cv2.resize(frame, (INPUT_SIZE, INPUT_SIZE))

    # YOLOX export expects pixel values in the 0-255 range.
    blob = image[:, :, ::-1].transpose(2, 0, 1)
    blob = blob.astype(np.float32)[None, ...]

    output = _session.run(
        None,
        {"images": blob}
    )[0][0]

    objectness = output[:, 4:5]
    class_scores = output[:, 5:]

    scores = objectness * class_scores

    person_score = float(scores[:, PERSON_CLASS].max())

    return person_score >= CONFIDENCE_THRESHOLD


if __name__ == "__main__":
    print("PERSON DETECTION TEST:", detect_person(None))
