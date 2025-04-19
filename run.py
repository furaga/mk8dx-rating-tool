import argparse
from pathlib import Path
from typing import List, Optional

import cv2
import mk8dx_digit_ocr
import numpy as np

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
        self.delta_rate: Optional[int] = None

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
    parser.add_argument("--max_my_rate", type=int, default=99999)
    parser.add_argument("--min_my_rate", type=int, default=94900)
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
    #  imwrite_safe(f"data/tmp/courses/{best_course}_{_cnt:05d}.png", course_img)
    # imwrite_safe(f"data/tmp/race_type/{best_course}_{_cnt:05d}.png", race_type_img)
    _cnt += 1

    return best_course, best_race_type


def detect_rates_after(img):
    inv_img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for i, roi in enumerate(result_rates_rois):
        crop = crop_img(inv_img, roi)
        ret, my_rate = mk8dx_digit_ocr.digit_ocr.detect_white_digit(
            crop
        )  # , verbose=True)
        if ret and min_my_rate <= my_rate <= max_my_rate:
            rates_after = []
            for roi in result_rates_rois:
                crop = crop_img(inv_img, roi)
                ret, rate = mk8dx_digit_ocr.digit_ocr.detect_digit(crop)
                if not ret:
                    rate = 0
                if not (500 <= rate <= 99999):
                    rate = 0
                rates_after.append(rate)

            return True, my_rate, i + 1, rates_after

    return False, 0, 0, []


def OBS_apply_rate(race_info):
    OBS.set_text("現在レート", f"{race_info.my_rate}")
    OBS.set_text("前回順位", f"前回{race_info.place}位")

    if race_info.place <= 3:
        OBS.set_color("前回順位", (100, 255, 100))
    elif race_info.place >= 9:
        OBS.set_color("前回順位", (255, 100, 100))
    else:
        OBS.set_color("前回順位", (255, 255, 255))

    text = OBS.get_text("最高レート")
    cur_max_rate = int(text.split(" ")[1].replace(",", ""))
    if cur_max_rate < race_info.my_rate:
        text = OBS.set_text("最高レート", f"最高 {race_info.my_rate}")


is_item_table_visible = False
prev_item_table = "", ""


def OBS_show_item_table(visible, cource, race_type, n_lap):
    pass
    global is_item_table_visible, prev_item_table
    if visible:
        path = Path("data/item_table") / f"{cource}_{n_lap}.png"
        if not path.exists():
            path = Path("data/item_table") / f"{cource}.png"
        if not path.exists():
            return
        if prev_item_table != (str(path), race_type):
            img = imread_safe(str(path), cv2.IMREAD_UNCHANGED)
            if race_type == "ミラー":
                img = cv2.flip(img, 1)
            # TODO: no hard coding
            cv2.imwrite(
                "C:/Users/furag/Dropbox/GALLERIA_XF/Documents/doc/OBS/texture/item_table.png",
                img,
            )
            prev_item_table = str(path), race_type
    if visible != is_item_table_visible:
        is_item_table_visible = visible
        OBS.set_visible("アイテムテーブル", visible)


is_timer_visible = False


def OBS_show_timer(visible):
    global is_timer_visible
    if visible != is_timer_visible:
        is_timer_visible = visible
        OBS.set_visible("timer.mp4", visible)


def parse_frame(img, ts, status, race_info: RaceInfo):
    history.append({"ts": ts, "status": status, "visible_coin_lap": False})
    while len(history) > 10:
        history.pop(0)

    is_pre_race = is_pre_race_screen(img)
    if is_pre_race:
        rates = detect_rates_before(img)
        n_valid = len([x for x in rates if x > 0])
        if n_valid >= 3:
            history[-1].update({"rates": rates})
            prev_n_valid = len([x for x in race_info.rates if x > 0])
            if prev_n_valid <= n_valid:
                race_info.rates = rates
            course, race_type = detect_course(img)
            race_info.course = course
            race_info.race_type = race_type
            if enable_OBS:
                OBS.set_text("コース情報", f"{course}, {race_type}")
            return "race", race_info

    if enable_OBS:
        ret_coin, _ = RaceAnalyzer.detect_coin(img)
        ret_lap, n_lap = RaceAnalyzer.detect_lap(
            img, 7 if race_info.course == "ベビィパーク" else 3
        )
        history[-1].update({"visible_coin_lap": ret_coin and ret_lap})

    if status == "race":
        # アイテムテーブルの表示・非表示きりかえ
        if enable_OBS:
            if len(history) >= 3:
                if np.all([x["visible_coin_lap"] for x in history[-3:]]):
                    OBS_show_item_table(
                        True, race_info.course, race_info.race_type, n_lap
                    )
                # if np.all([not x["visible_coin_lap"] for x in history[-3:]]):
                #     OBS_show_item_table(
                #         False, race_info.course, race_info.race_type, n_lap
                #     )
            # タイマーオン
            # if len(history) >= 3:
            #     if np.all([x["visible_coin_lap"] for x in history[-3:]]):
            #         OBS_show_timer(True)

        # 結果表のパース
        ret, my_rate, place, rates_after = detect_rates_after(img)
        if ret:
            if enable_OBS:
                OBS_show_item_table(False, race_info.course, race_info.race_type, n_lap)
                # OBS_show_timer(False)
            history[-1].update({"my_rate": my_rate})
            race_info.my_rate = my_rate
            if len(history) >= 2 and "my_rate" in history[-2]:
                race_info.delta_rate = my_rate - history[-2]["my_rate"]
            else:
                race_info.delta_rate = None
            race_info.place = place
            n_valid = len([x for x in rates_after if x > 0])
            prev_n_valid = len([x for x in race_info.rates_after if x > 0])
            if prev_n_valid <= n_valid:
                race_info.rates_after = rates_after
            if enable_OBS:
                OBS_apply_rate(race_info)
            return "result", race_info

    if status == "result":
        # 結果表のパース
        ret, my_rate, place, rates_after = detect_rates_after(img)
        if ret:
            if enable_OBS:
                OBS_show_item_table(False, race_info.course, race_info.race_type, n_lap)
                # OBS_show_timer(False)
            history[-1].update({"my_rate": my_rate})
            race_info.my_rate = my_rate
            race_info.place = place
            n_valid = len([x for x in rates_after if x > 0])
            prev_n_valid = len([x for x in race_info.rates_after if x > 0])
            if prev_n_valid <= n_valid:
                race_info.rates_after = rates_after
            if enable_OBS:
                OBS_apply_rate(race_info)
            return "", race_info
        else:
            return "none", race_info

    return "", race_info


def save_race_info(out_csv_path, ts, race_info):
    header = ["ts", "course", "race_type", "place", "my_rate"]
    header += [f"rates_{i}" for i in range(12)]
    header += [f"rates_after_{i}" for i in range(12)]

    if not out_csv_path.exists():
        with open(out_csv_path, "w", encoding="utf8") as f:
            f.write(",".join(header) + "\n")

    with open(out_csv_path, "a", encoding="utf8") as f:
        text = str(ts) + ","
        text += race_info.course + ","
        text += race_info.race_type + ","
        text += str(race_info.place) + ","
        text += str(race_info.my_rate) + ","
        text += ",".join([str(r) for r in race_info.rates]) + ","
        text += ",".join([str(r) for r in race_info.rates_after]) + "\n"
        f.write(text)
        f.flush()

    valid_rates = [v for v in race_info.rates if v > 0]
    mid_rate = np.median(valid_rates)
    min_rate = np.min(valid_rates)
    max_rate = np.max(valid_rates)
    print(
        f"[{race_info.course} ({race_info.race_type})] Place={race_info.place}, VR={race_info.my_rate}, {len(valid_rates)} players, {mid_rate} ({min_rate}-{max_rate})",
        flush=True,
    )


min_my_rate, max_my_rate = 0, 100000
enable_OBS = False


def main(args):
    global min_my_rate, max_my_rate, enable_OBS
    min_my_rate = args.min_my_rate
    max_my_rate = args.max_my_rate

    if len(args.obs_pass) > 0:
        print("OBS Mode")
        enable_OBS = True
        OBS.init(args.obs_pass)
    else:
        print("Video Mode:", str(args.video_path))
        cap = cv2.VideoCapture(str(args.video_path))

    status = "none"
    ts = 0
    race_info = RaceInfo()
    import time

    since = time.time()
    browser_show_time = -10000
    browser_visible = True
    ts_str = ""
    while True:
        if browser_visible and time.time() - browser_show_time > 10:
            if enable_OBS:
                OBS.set_visible("ブラウザ_レート遷移", False)
            browser_visible = False

        if enable_OBS:
            frame = OBS.capture_game_screen()
            import datetime

            now = datetime.datetime.now()
            ts_str = now.strftime("%Y-%m-%d@%H:%M:%S")
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
                save_race_info(args.out_csv_path, ts_str, race_info)
                if enable_OBS:
                    OBS.set_visible("ブラウザ_レート遷移", True)
                browser_visible = True
                browser_show_time = time.time()
                race_info = RaceInfo()

            if next_status != "":
                status = next_status
                if next_status == "race":
                    ts += 100 * 1000

        if args.imshow:
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) == ord("q"):
                break

        if enable_OBS:
            time_to_sleep = 100 - int((time.time() - since) * 1000)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep / 1000)
            since = time.time()
        #  print("xxx")


if __name__ == "__main__":
    main(parse_args())
