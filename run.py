import argparse
import cv2
from pathlib import Path
from typing import NamedTuple, List
import pandas as pd
import numpy as np
import mk8dx_digit_ocr

from utils import OBS, RaceAnalyzer


race_type_roi = [0.16, 0.85, 0.24, (0.85 + 0.98) / 2]  # 上半分を使用
course_roi = [0.72, 0.85, 0.84, 0.98]

race_type_roi = [0.16, 0.85, 0.24, 0.98]
course_roi = [0.73, 0.87, 0.82, 0.96]

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


class RaceInfo:
    def __init__(self):
        self.course: str = ""
        self.race_type: str = ""
        self.place: int = 0
        self.rates: List[int] = [0 for _ in range(12)]
        self.my_rate: int = 0

    def __repr__(self) -> str:
        return (
            self.course
            + ","
            + self.race_type
            + ","
            + str(self.place)
            + ","
            + str(self.my_rate)
            + " | "
            + ",".join([str(r) for r in self.rates])
        )


cap = None


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--obs_pass", type=str, default="")
    parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--out_csv_path", type=Path, required=True)
    parser.add_argument("--imshow", action="store_true")
    parser.add_argument("--max_my_rate", type=int, default=40000)
    parser.add_argument("--min_my_rate", type=int, default=30000)
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


_cnt = 10000
course_dict = {}
race_type_dict = {}


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


def detect_course(img):
    global _cnt

    # 初回ならデータ読み込む
    if len(course_dict) <= 0:
        for d in Path("data/courses").glob("*"):
            for img_path in d.glob("*.png"):
                tmpl = imread_safe(str(img_path))
                tmpl = cv2.resize(tmpl, (173, 97))
                course_dict.setdefault(d.stem, []).append(tmpl)

    if len(race_type_dict) <= 0:
        for d in Path("data/race_type").glob("*"):
            for img_path in d.glob("*.png"):
                tmpl = imread_safe(str(img_path))
                tmpl = cv2.resize(tmpl, (103, 93))
                race_type_dict.setdefault(d.stem, []).append(tmpl)

    best_score = 0
    best_course = ""
    course_img = crop_img(img, course_roi)
    course_img = cv2.resize(course_img, (173, 97))
    for k, v in course_dict.items():
        for i, template in enumerate(v):
            result = cv2.matchTemplate(course_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if best_score < max_val:
                best_score = max_val
                best_course = k
    # print(best_course, "| score =", best_score)

    best_score = 0
    best_race_type = ""
    race_type_img = crop_img(img, race_type_roi)
    race_type_img = cv2.resize(race_type_img, (103, 93))
    for k, v in race_type_dict.items():
        for i, template in enumerate(v):
            result = cv2.matchTemplate(race_type_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if best_score < max_val:
                best_score = max_val
                best_race_type = k

    # save
    imwrite_safe(f"data/tmp/courses/{best_course}_{_cnt:05d}.png", course_img)
    imwrite_safe(f"data/tmp/race_type/{best_course}_{_cnt:05d}.png", race_type_img)
    _cnt += 1

    return best_course, best_race_type


def detect_final_rates(img):
    inv_img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    num = 0
    for i, roi in enumerate(result_rates_rois):
        crop = crop_img(inv_img, roi)
        # cv2.imshow(f"roi{i}", crop)
        ret, rate = mk8dx_digit_ocr.digit_ocr.detect_white_digit(
            crop
        )  # , verbose=True)
        if ret and min_my_rate <= rate <= max_my_rate:
            imwrite_safe(f"rate_{_cnt:05d}.png", crop)
            return True, rate, i + 1

    return False, 0, 0


def parse_frame(img, ts, status, race_info):
    history.append({"ts": ts, "status": status})
    while len(history) > 10:
        history.pop(0)

    is_pre_race = is_pre_race_screen(img)
    if is_pre_race:
        rates = detect_rates(img)
        if len([x for x in rates if x > 0]) >= 3:
            history[-1].update({"rates": rates})
            race_info.rates = rates
            course, race_type = detect_course(img)
            race_info.course = course
            race_info.race_type = race_type
            OBS.set_text("コース情報", f"{course}, {race_type}")
            return "race", race_info

    if status == "race":
        ret, my_rate, place = detect_final_rates(img)
        if ret:
            history[-1].update({"my_rate": my_rate})
            race_info.my_rate = my_rate
            race_info.place = place
            OBS.set_text(
                "現在レート・前回順位", f"(現在 {race_info.my_rate}, 前回{race_info.place}位)"
            )
            return "result", race_info

    if status == "result":
        ret, my_rate, place = detect_final_rates(img)
        if ret:
            history[-1].update({"my_rate": my_rate})
            race_info.my_rate = my_rate
            race_info.place = place
            OBS.set_text(
                "現在レート・前回順位", f"(現在 {race_info.my_rate}, 前回{race_info.place}位)"
            )
            return "", race_info
        else:
            return "none", race_info

    return "", race_info


def save_race_info(out_csv_path, ts, race_info):
    header = ["ts", "course", "race_type", "place", "my_rate"]
    header += [f"rates_{i}" for i in range(12)]

    if not out_csv_path.exists():
        with open(out_csv_path, "w", encoding="sjis") as f:
            f.write(",".join(header) + "\n")

    with open(out_csv_path, "a", encoding="sjis") as f:
        f.write(str(ts) + ",")
        f.write(race_info.course + ",")
        f.write(race_info.race_type + ",")
        f.write(str(race_info.place) + ",")
        f.write(str(race_info.my_rate) + ",")
        f.write(",".join([str(r) for r in race_info.rates]) + "\n")
        f.flush()


min_my_rate, max_my_rate = 0, 100000


def main(args):
    global min_my_rate, max_my_rate
    min_my_rate = args.min_my_rate
    max_my_rate = args.max_my_rate

    if len(args.obs_pass) > 0:
        OBS.init(args.obs_pass)
    else:
        cap = cv2.VideoCapture(str(args.video_path))

    status = "none"
    ts = 0
    race_info = RaceInfo()
    import time

    since1 = time.time()
    since = time.time()
    browser_show_time = -10000
    browser_visible = True
    ts_str = ""
    while True:
        if browser_visible and time.time() - browser_show_time > 10:
            OBS.set_visible("ブラウザ_レート遷移", False)
            browser_visible = False

        if len(args.obs_pass) > 0:
            frame = OBS.capture_game_screen()
            import datetime
            now = datetime.datetime.now()
            ts_str = now.strftime('%Y-%m-%d %H:%M:%S')
        else:
            ts += 500
            ts_str = str(args.video_path) + "@" + str(ts)
            cap.set(cv2.CAP_PROP_POS_MSEC, ts)
            ret, frame = cap.read()
            if not ret:
                break

        next_status, race_info = parse_frame(frame, 0, status, race_info)
        if next_status != status:
            if next_status == "none":
                save_race_info(
                    args.out_csv_path, ts_str, race_info
                )
                OBS.set_visible("ブラウザ_レート遷移", True)
                browser_visible = True
                browser_show_time = time.time()
                print("Saved Race Information.")
                race_info = RaceInfo()

            if next_status != "":
                status = next_status
                if next_status == "race":
                    ts += 100 * 1000

        cv2.imshow("frame", frame)
        # if cv2.waitKey(0 if history[-1]["is_pre_race"] else 1) == ord("q"):
        if cv2.waitKey(1) == ord("q"):
            break

        if len(args.obs_pass) > 0:
            time_to_sleep = 100 - int((time.time() - since) * 1000)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep / 1000)
            since = time.time()
        #  print("xxx")


if __name__ == "__main__":
    main(parse_args())
