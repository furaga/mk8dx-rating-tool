import argparse
from pathlib import Path
from typing import List

import cv2
import mk8dx_digit_ocr
import numpy as np

DEBUG_MODE = False
start_time = 480 + 14

corr_x = 0
corr_y = 0
# # 【マリオカート8DX】参加型🟡ゲリラ配信！【成瀬_Vtuber】
# # 【マリオカート8DX】参加型🟡初見さん歓迎！一緒に走ろう🤜🤛卍【成瀬_Vtuber
# # 【マリオカート8DX】参加型🟣初見さん歓迎！一緒に走ろう【成瀬_Vtuber】 (1)
# corr_x = - 17 / 1920

# 怒りのゲリラ配信💢【成瀬_Vtuber
# corr_x = - 0 / 1920


race_type_roi = [0.16 + corr_x, 0.85, 0.24, 0.98]
course_roi = [0.73 + corr_x, 0.87, 0.82, 0.96]

players_roi_base = [
    93 / 1920 + corr_x,
    84 / 1080,
    1827 / 1920,
    870 / 1080,
]

# race_type_roi = [0.16 + 0.002, 0.85 + 0.01, 0.24 + 0.0025, 0.98 + 0.01]
# course_roi = [0.73 + 0.002, 0.87 + 0.01, 0.82 + 0.0025, 0.96 + 0.01]
# players_roi_base = [
#     93 / 1920 + 0.002,
#     84 / 1080 + 0.01,
#     1827 / 1920 + 0.0025,
#     870 / 1080 + 0.01,
# ]


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
    if DEBUG_MODE:
        cv2.imshow("players_roi", cv2.resize(players_img, None, fx=0.5, fy=0.5))

    players = []
    for x in range(2):
        for y in range(6):
            players.append(
                crop_img(players_img, [x / 2, y / 6, (x + 1) / 2, (y + 1) / 6])
            )

    rates = []
    for i, p in enumerate(players):
        rate_img = crop_img(p, [0.75, 0.5, 0.995, 0.995])
        if DEBUG_MODE:
            cv2.imshow(f"rate_img {i}", rate_img)

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
        if DEBUG_MODE:
            print("RATES", rates)
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
    all_video_path = list(args.video_dir.glob("*.mp4"))

    crop_dict = {}
    with open(args.video_dir / "crop.txt", mode="r", encoding="utf8") as f:
        # with open("crop.txt", mode="r", encoding="utf8") as f:
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
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) // 2)

        img = cap.read()[1]
        if img is None:
            print("INVALID:", video_path)
            continue
        H, W = img.shape[:2]
        if video_path.stem in crop_dict:
            x1, y1, x2, y2 = crop_dict[video_path.stem]
            img = crop_img(img, (x1 / W, y1 / H, x2 / W, y2 / H))

        imwrite_safe(str(out_path), img)
        cap.release()
    # return

    for vi, video_path in enumerate(all_video_path):
        print(f"{vi+1}/{len(all_video_path)}: {video_path}")

        if (args.out_dir / f"{video_path.stem}").exists():
            print("  skipped")
            continue

        history.clear()
        status = "none"
        race_info = RaceInfo()

        cap = cv2.VideoCapture(str(video_path))
        current_time = 0  # 23 * 60 # 0
        if DEBUG_MODE:
            current_time = start_time

        while True:
            cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)
            ret, frame = cap.read()
            if not ret:
                break

            H, W = frame.shape[:2]
            if video_path.stem in crop_dict:
                x1, y1, x2, y2 = crop_dict[video_path.stem]
                frame = crop_img(frame, (x1 / W, y1 / H, x2 / W, y2 / H))

            cv2.imshow("frame1", cv2.resize(frame, None, fx=0.5, fy=0.5))
            status, race_info = parse_frame(frame, 0, status, race_info)
            history[-1].update({"status": status})

            if DEBUG_MODE:
                cv2.imshow("cource", crop_img(frame, course_roi))
                cv2.imshow("type", crop_img(frame, race_type_roi))
                if ord("q") == cv2.waitKey(0):
                    exit(0)
            else:
                cv2.waitKey(1)

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


def main_only_with_images(args):
    out_csv_path = "count_mirror_200cc.csv"
    with open(out_csv_path, "w", encoding="utf8") as f:
        all_img_paths = list(args.out_dir.glob("*/*.jpg"))
        all_img_paths = [
            img_path
            for img_path in all_img_paths
            if img_path.parent.stem != "middle_frames"
        ]
        for i, img_path in enumerate(all_img_paths):
            if i % 100 == 0:
                print(f"{i+1}/{len(all_img_paths)}: {img_path}")
            img = imread_safe(str(img_path))
            rates = detect_rates_before(img)
            course, race_type = detect_course(img)
            text = img_path.parent.stem + "@" + img_path.stem + ","
            text += course + ","
            text += race_type + ","
            text += ",".join([str(r) for r in rates]) + "\n"
            #            print(text, end="", flush=True)
            f.write(text)
            f.flush()


def show_classification(args):
    out_csv_path = "output_wave5/race_info.csv"
    with open(out_csv_path, "r", encoding="utf8") as f:
        for line in f:
            try:
                tokens = line.split(",")
                cnt = 0
                name = ""
                while "@" not in name:
                    name += "," + tokens[cnt]
                    cnt += 1
                name = name.strip(",")
                type = tokens[cnt + 1]
                dname, ts = name.split("@")
                img_path = f"output_wave5/{dname}/{int(ts):05d}s.jpg"
                img = imread_safe(img_path)
                race_type_img = crop_img(img, race_type_roi)
                course_img = crop_img(img, course_roi)
                course_img = cv2.resize(
                    course_img, (race_type_img.shape[1], race_type_img.shape[0])
                )
                out_img = cv2.hconcat([race_type_img, course_img])
                out_img_path = f"output/{type}/{name}.jpg"
                Path(out_img_path).parent.mkdir(parents=True, exist_ok=True)
                imwrite_safe(out_img_path, out_img)
            except Exception as e:
                print(line)
                print(e)


def summarize(args):
    race_info_paths = [
        Path("output_wave5/race_info_part1.csv"),
        Path("output_wave5/race_info_part2.csv"),
        Path("output_wave5/race_info_part3.csv"),
    ]
    for p in race_info_paths:
        print("=======" + str(p) + "=======")
        part = p.stem.split("_")[-1]
        with open(p, "r", encoding="utf8") as f:
            for line in f:
                try:
                    tokens = line.split(",")
                    cnt = 0
                    name = ""
                    while "@" not in name:
                        name += "," + tokens[cnt]
                        cnt += 1
                    name = name.strip(",")
                    row = [name] + tokens[cnt:]

                    rates = [int(r) for r in row[3:]]
                    rates = [int(r) for r in rates if r > 0]
                    mean_rate = np.mean(rates)
                    if mean_rate <= 3000:
                        continue

                    dname, ts = name.split("@")

                    race_type = None
                    for t in ["150cc", "ミラー", "200cc"]:
                        #   print(f"output/{part}/{t}/{name}.jpg")
                        p1 = Path(f"output/{part}/{t}/{name}.jpg")
                        p2 = Path(f"output/{part}/{t}/{dname}@{int(ts[:-1])}.jpg")
                        if p1.exists() or p2.exists():
                            race_type = t
                            break

                    assert race_type is not None, "NOT FOUND " + (
                        f"output/{part}/{t}/{name}.jpg"
                    )

                    if race_type is not None:
                        row[2] = race_type
                        with open("count_mirror_200cc.csv", "a", encoding="utf8") as f:
                            f.write(",".join(row))
                except Exception as e:
                    print(line)
                    print(e)


if __name__ == "__main__":
    #    main(parse_args())
    #    main_only_with_images(parse_args())
    # show_classification(parse_args())
    summarize(parse_args())
    summarize(parse_args())
