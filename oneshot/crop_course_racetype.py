from pathlib import Path
import cv2
import numpy as np

path = Path(
    r"C:\Users\furag\Documents\prog\python\mk8dx_tools\mirror_200cc_analyzer\data\person0"
)


race_type_roi = [0.16, 0.85, 0.24, 0.98]
course_roi = [0.73, 0.87, 0.82, 0.96]


def imread_safe(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def crop_img(img, roi):
    h, w = img.shape[:2]
    img = img[
        max(0, int(h * roi[1])) : min(h, int(h * roi[3])),
        max(0, int(w * roi[0])) : min(w, int(w * roi[2])),
    ]
    return img


cnt = 0
for img_path in path.glob("*/*.png"):
    if "_frame" in str(img_path):
        continue
    cnt += 1
    img = imread_safe(str(img_path))
    if img is None:
        continue
    race_type_img = crop_img(img, race_type_roi)
    course_img = crop_img(img, course_roi)
    cv2.imwrite(f"race_type/{cnt:05d}.png", race_type_img)
    cv2.imwrite(f"course/{cnt:05d}.png", course_img)
