import cv2
import pandas as pd

from utils import OBS

def get_black_ratio(img):
    h, w = img.shape[:2]
    thr = 25
    black = cv2.inRange(img, (0, 0, 0), (thr, thr, thr))
    br = cv2.countNonZero(black) / (h * w)
    return br


def get_white_ratio(img):
    h, w = img.shape[:2]
    thr = 190
    white = cv2.inRange(img, (thr, thr, thr), (255, 255, 255))
    wr = cv2.countNonZero(white) / (h * w)
    return wr


def is_pre_race_screen(img):
    black_ratio = get_black_ratio(img)
    # print("black_ratio", black_ratio)
    if black_ratio < 0.22:
        return False

    white_ratio = get_white_ratio(img)
    # print("white_ratio", white_ratio)
    if white_ratio < 0.13:
        return False

    return True



def save_race_info(out_csv_path, race_info):
    header = ["video_path", "time", "cource", "race_type", "place"]
    header += [f"rate_start_{i}" for i in range(12)]
    header += [f"rates_end_{i}" for i in range(12)]

    if not out_csv_path.exists():
        with open(out_csv_path, "w") as f:
            f.write(",".join(header) + "\n")

    with open(out_csv_path, "a") as f:
        f.write(race_info.cource + ",")
        f.write(race_info.race_type + ",")
        f.write(race_info.place + ",")
        f.write(",".join([r for r in race_info.rates_start]) + ",")
        f.write(",".join([r for r in race_info.rates_end]) + "\n")
        f.flush()

    rows = []

    df = pd.DataFrame(rows)
    df.to_csv(out_csv_path, header=header, index=False, encoding="utf-8")
    pass

