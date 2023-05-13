"""
最下位のレースのshorts動画を自動生成したい
"""

import argparse
import cv2
from pathlib import Path
from typing import NamedTuple, List
import pandas as pd
import numpy as np
import mk8dx_digit_ocr

from utils import OBS, RaceAnalyzer


def parse_args():
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--race_info_path", type=Path, default="out.csv")
    parser.add_argument("--imshow", action="store_true")
    args = parser.parse_args()
    return args


# def

# def parse_frame(img, ts, status, race_info):
#     history.append({"ts": ts, "status": status, "visible_coin_lap": False})
#     while len(history) > 10:
#         history.pop(0)

#     is_pre_race = is_pre_race_screen(img)
#     if is_pre_race:
#         rates = detect_rates_before(img)
#         n_valid = len([x for x in rates if x > 0])
#         if n_valid >= 3:
#             history[-1].update({"rates": rates})
#             prev_n_valid = len([x for x in race_info.rates if x > 0])
#             if prev_n_valid <= n_valid:
#                 race_info.rates = rates
#             course, race_type = detect_course(img)
#             race_info.course = course
#             race_info.race_type = race_type
#             if enable_OBS:
#                 OBS.set_text("コース情報", f"{course}, {race_type}")
#             return "race", race_info

#     return "", race_info


def collect_last_place_races(df):
    indexes = []
    for i, row in df.iterrows():
#        print(row)
        n_players = np.sum([1 for i in range(12) if 0 < row[f"rates_{i}"] <= 99999])
        n_players = max(
            n_players,
            np.sum([1 for i in range(12) if 0 < row[f"rates_after_{i}"] <= 99999]),
        )
        if row["place"] >= n_players:
            indexes.append(i)
            print(row["ts"], row["course"], row["place"], row["my_rate"], n_players)
    return indexes


def main(args):
    #    cap = cv2.VideoCapture(str(args.video_path))

    import pandas as pd

    df = pd.read_csv(
        args.race_info_path,
        encoding="utf8",
        engine="python",
        on_bad_lines="skip",
        # usecols=[
        #     "ts",
        #     "course",
        #     "race_type",
        #     "place",
        #     "my_rate",
        #     "rates_0",
        #     "rates_1",
        #     "rates_2",
        #     "rates_3",
        #     "rates_4",
        #     "rates_5",
        #     "rates_6",
        #     "rates_7",
        #     "rates_8",
        #     "rates_9",
        #     "rates_10",
        #     "rates_11",
        # ],
    )

    indexes = collect_last_place_races(df)

    # while True:
    #     ret, img = cap.read()
    #     if not ret:
    #         break
    #     cv2.imshow("img", img)
    #     cv2.waitKey(1)


if __name__ == "__main__":
    main(parse_args())
