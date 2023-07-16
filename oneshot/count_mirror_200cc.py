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
        self.rates_after: List[int] = [0 for _ in range(12)]
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
    parser.add_argument("--video_dir", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    args = parser.parse_args()
    return args


history = []


def is_pre_race_screen(img):
    return True
    # is_pre_race = RaceAnalyzer.is_pre_race_screen(img)
    # history[-1].update({"is_pre_race": is_pre_race})
    # if len(history) >= 3 and np.all(
    #     [
    #         item["is_pre_race"] if "is_pre_race" in item else False
    #         for item in history[-3:]
    #     ]
    # ):
    #     return True
    # return False


def crop_img(img, roi):
    h, w = img.shape[:2]
    img = img[
        max(0, int(h * roi[1])) : min(h, int(h * roi[3])),
        max(0, int(w * roi[0])) : min(w, int(w * roi[2])),
    ]
    return img


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


def detect_rates_before(img):
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
    # imwrite_safe(f"data/tmp/courses/{best_course}_{_cnt:05d}.png", course_img)
    # imwrite_safe(f"data/tmp/race_type/{best_course}_{_cnt:05d}.png", race_type_img)
    _cnt += 1

    return best_course, best_race_type


def parse_frame(img, ts, status, race_info):
    history.append({})
    while len(history) > 10:
        history.pop(0)

    is_pre_race = is_pre_race_screen(img)
    if is_pre_race:
        rates = detect_rates_before(img)
        # 左半分にレートが写っていれば
        n_valid = len([x for x in rates[:6] if x > 500])
        if n_valid >= 3:
            history[-1].update({"rates": rates})
            race_info.rates = rates
            course, race_type = detect_course(img)
            race_info.course = course
            race_info.race_type = race_type
            return "race", race_info

    return "", race_info


def main(args):
    import time

    all_video_path = list(args.video_dir.glob("*.mp4"))

    crop_dict = {}
    with open(args.video_dir / "crop.txt", mode="r", encoding="utf8") as f:
        for line in f:
            tokens = line.split(",")
            if len(tokens) != 5:
                continue
            crop_dict[tokens[0]] = [int(x) for x in tokens[1:]]

    out_csv_path = args.out_dir / "race_info.csv"

    # 1Frameだけ取り出す
    print("Extracting middle frames...")
    for vi, video_path in enumerate(all_video_path):
        cap = cv2.VideoCapture(str(video_path))
        out_path = args.out_dir / "middle_frames" / f"{video_path.stem}.jpg"
        out_path.parent.mkdir(exist_ok=True, parents=True)
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) // 3)

        img = cap.read()[1]
        H, W = img.shape[:2]
        if video_path.stem in crop_dict:
            x1, y1, x2, y2 = crop_dict[video_path.stem]
            img = crop_img(img, (x1 / W, y1 / H, x2 / W, y2 / H))

        imwrite_safe(str(out_path), img)
        cap.release()
    return 

    for vi, video_path in enumerate(all_video_path):
        print(f"{vi+1}/{len(all_video_path)}: {video_path}")

        history.clear()
        status = "none"
        ts = 0
        race_info = RaceInfo()

        cap = cv2.VideoCapture(str(video_path))
        current_time = 0
        while True:
            cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)
            ret, frame = cap.read()
            if not ret:
                break

            H, W = frame.shape[:2]
            if video_path.stem in crop_dict:
                x1, y1, x2, y2 = crop_dict[video_path.stem]
                frame = crop_img(frame, (x1 / W, y1 / H, x2 / W, y2 / H))

            cv2.imshow("frame1", frame)
            cv2.waitKey(1)
            status, race_info = parse_frame(frame, 0, status, race_info)
            history[-1].update({"status": status})

            if (
                len(history) >= 3
                and history[-1]["status"]
                == history[-2]["status"]
                == history[-3]["status"]
                == "race"
            ):
                # TODO: save
                out_img_path = (
                    args.out_dir / f"{video_path.stem}/{current_time:05d}s.jpg"
                )

                out_img_path.parent.mkdir(parents=True, exist_ok=True)
                imwrite_safe(str(out_img_path), frame)
                with open(out_csv_path, "a", encoding="utf8") as f:
                    text = video_path.stem + "@" + str(current_time) + ","
                    text += race_info.course + ","
                    text += race_info.race_type + ","
                    text += ",".join([str(r) for r in race_info.rates]) + "\n"
                    print(text, end="", flush=True)
                    f.write(text)
                    f.flush()

                current_time += 100
            current_time += 1

            if current_time % 100 == 0:
                cap_length_sec = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(
                    cv2.CAP_PROP_FPS
                )
                print(
                    f"*[{100 * current_time / cap_length_sec:.1f}%] current_time={current_time}s"
                )
        cap.release()


if __name__ == "__main__":
    main(parse_args())
