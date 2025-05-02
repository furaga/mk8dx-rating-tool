from pathlib import Path

import cv2
import numpy as np

path = Path(r"C:\Users\furag\Documents\prog\python\mk8dx-rating-tool\data\tmp")


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


def imwrite_safe(filename, img, params=None):
    try:
        import os

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode="w+b") as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def crop_img(img, roi):
    h, w = img.shape[:2]
    img = img[
        max(0, int(h * roi[1])) : min(h, int(h * roi[3])),
        max(0, int(w * roi[0])) : min(w, int(w * roi[2])),
    ]
    return img


cnt = 30000
for img_path in path.glob("*.png"):
    if "_frame" in str(img_path):
        continue
    cnt += 1
    img = imread_safe(str(img_path))
    if img is None:
        continue
    race_type_img = crop_img(img, race_type_roi)
    course_img = crop_img(img, course_roi)

    race_type, course = img_path.stem.split("_")
    imwrite_safe(f"data/battle_courses/{course}/{cnt:05d}.png", course_img)
    imwrite_safe(f"data/battle_race_type/{race_type}/{cnt:05d}.png", race_type_img)
