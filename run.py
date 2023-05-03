import argparse
import cv2
from pathlib import Path
from typing import NamedTuple, List
import pandas as pd
import numpy as np
import mk8dx_digit_ocr

from utils import OBS, RaceAnalyzer


game_screen_roi = [0, 0, 1655 / 1920, 929 / 1080]
race_type_roi = [0.16, 0.85, 0.24, (0.85 + 0.98) / 2]  # 上半分を使用
course_roi = [0.72, 0.85, 0.84, 0.98]

players_roi_base = [
    93 / 1920,
    84 / 1080,
    1827 / 1920,
    870 / 1080,
]

result_rates_rois = [
    [
        1120 / 1280,
        (50 + 52 * i) / 720,
        1224 / 1280,
        (95 + 52 * i) / 720,
    ]
    for i in range(12)
]


class RaceInfo(NamedTuple):
    cource: str = ""
    race_type: str = "150cc"
    place: str = 0
    rates_start: List[int] = [0 for _ in range(12)]
    rates_end: List[int] = [0 for _ in range(12)]


cap = None


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--obs_pass", type=str, default="")
    parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--out_csv_path", type=Path, required=True)
    parser.add_argument("--imshow", action="store_true")
    parser.add_argument("--max_my_rate", type=int, default=30000)
    parser.add_argument("--min_my_rate", type=int, default=20000)
    args = parser.parse_args()
    return args


history = []


def is_pre_race_screen(img):
    is_pre_race = RaceAnalyzer.is_pre_race_screen(img)
    history[-1].update({"is_pre_race": is_pre_race})
    if len(history) >= 3 and np.all(
        [
            item["is_pre_race"] if "is_pre_race" in item else False
            for item in history[-3:]
        ]
    ):
        return True
    return False


def crop_img(img, roi):
    h, w = img.shape[:2]
    img = img[
        max(0, int(h * roi[1])) : min(h, int(h * roi[3])),
        max(0, int(w * roi[0])) : min(w, int(w * roi[2])),
    ]
    return img


def detect_rates(img):
    players_roi = players_roi_base

    players_img = crop_img(img, players_roi)

    players = []
    for x in range(2):
        for y in range(6):
            players.append(
                crop_img(players_img, [x / 2, y / 6, (x + 1) / 2, (y + 1) / 6])
            )

    rates = []
    for i, p in enumerate(players):
        rate_img = crop_img(p, [0.75, 0.5, 0.995, 0.995])
        rate_img = cv2.cvtColor(rate_img, cv2.COLOR_BGR2GRAY)
        ret, rate = mk8dx_digit_ocr.detect_digit(rate_img)
        if not ret:
            rate = 0
        if not (500 <= rate <= 99999):
            rate = 0
        rates.append(rate)

    return rates


def detect_final_rates(img):
    inv_img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    num = 0
    for i, roi in enumerate(result_rates_rois):
        crop = crop_img(inv_img, roi)
        # cv2.imshow(f"roi{i}", crop)
        ret, rate = mk8dx_digit_ocr.digit_ocr.detect_white_digit(crop)
        if ret and min_my_rate <= rate <= max_my_rate:
            return True, rate

    return False, 0


def parse_frame(img, ts, status):
    history.append({"ts": ts, "status": status})
    while len(history) > 10:
        history.pop(0)

    if status == "none":
        is_pre_race = is_pre_race_screen(img)
        if is_pre_race:
            rates = detect_rates(img)
            history[-1].update({"rates": rates})
            return "race", RaceInfo(rates_start=rates)

    if status == "race":
        ret, next_rate = detect_final_rates(img)
        if ret:
            history[-1].update({"next_rate": next_rate})
            return "result", RaceInfo()

    if status == "result":
        ret, next_rate = detect_final_rates(img)
        if ret:
            history[-1].update({"next_rate": next_rate})
            return "", RaceInfo()
        else:
            print("next_rate =", history[-2]["next_rate"])
            return "none", RaceInfo()

    return "", RaceInfo()


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


min_my_rate, max_my_rate = 0, 100000


def main(args):
    global min_my_rate, max_my_rate
    min_my_rate = args.min_my_rate
    max_my_rate = args.max_my_rate

    if len(args.obs_pass) > 0:
        OBS.init(args.obs_pass)

    cap = cv2.VideoCapture(str(args.video_path))

    status = "race"
    ts = 200 * 1000
    while True:
        ts += 500
        cap.set(cv2.CAP_PROP_POS_MSEC, ts)
        ret, frame = cap.read()
        if not ret:
            break

        next_status, race_info = parse_frame(frame, 0, status)
        if next_status != status:
            # if status == "race":
            # レース終了
            #     save_race_info(args.out_csv_path, race_info)
            if next_status != "":
                status = next_status

        cv2.imshow("frame", frame)
        # if cv2.waitKey(0 if history[-1]["is_pre_race"] else 1) == ord("q"):
        if cv2.waitKey(1) == ord("q"):
            break


if __name__ == "__main__":
    main(parse_args())
