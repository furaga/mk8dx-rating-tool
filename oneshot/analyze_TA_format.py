import argparse
import cv2
from pathlib import Path
import numpy as np

from utils import RaceAnalyzer


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--video_dir", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--imshow", action="store_true")
    args = parser.parse_args()
    return args


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


import time


def main(args):
    all_video_paths = list(args.video_dir.glob("*.mp4"))

    video_ids = [
        "JZSGG7gt0Q4",
        "C4I08_ie3rI",
        "GoU7HwoDPlY",
        "OFiipst3jqo",
        "dM3cSMgrMnI",
        "ayOPuf7tC7c",
        "DCqPWLRZbZ8",
        "9e3tjbfO8p4",
        "fI9vkzI8uTk",
        "-vbeAA72NkI",
        "wnT0-vmEHAo",
        "c_UqtKGcG4I",
        "p23XXDPmXG8",
        "XwY20lHcjEg",
        "bCGcWq9lA_g",
        "pqCeX2R_IW4",
        "9N6fZH-2kZw",
        "w7lESAP8nBA",
        "0PFd_lNqFxg",
        "--juyTU3WYE",
        "p0JOJxMIc54",
        "l18Psarq1bY",
        "WbUXSQHNLVQ",
        "UL25ZswdXEc",
        "9R7wq24QmYE",
        "YzFW_96G3JI",
    ]

    n_lap = 0
    out_rows = []
    for vi, vid in enumerate(video_ids):
        csv_path = list(args.out_dir.glob(f"*{vid}.csv"))[0]
        laps_path = f"output/{csv_path.name}"

        import pandas as pd

        df = pd.read_csv(laps_path)

        for row in df.values:
            _, _, timer = row
            is_lap0 = "0:00.000" == timer
            is_lap3 = timer[0] != "0"
            if is_lap0:
                out_rows.append([])
            else:
                if len(out_rows[-1]) > 2 and not is_lap3:
                    out_rows.append([])

                tokens = timer.split(":")
                ts = (
                    +float(tokens[0]) * 60
                    + float(tokens[1].split(".")[0])
                    + float(tokens[1].split(".")[1]) / 1000
                )
                timer_float = ts

                if is_lap3:
                    if len(out_rows[-1]) >= 2:
                        timer_float += -out_rows[-1][0] - out_rows[-1][1]

                out_rows[-1].append(timer_float)
                if len(out_rows[-1]) > 3:
                    print("ERROR: more than 3 laps")
                    print(out_rows[-1])

    out_rows = [
        row + [float("nan")] * (3 - len(row))
        for i, row in enumerate(out_rows)
        if len(row) > 0
    ]
    out_rows = [
        [v if type(v) == str or 37 < v < 45 else float("nan") for v in row]
        for row in out_rows
    ]
    print(out_rows[:3])
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv("output/TA_laps.csv", index=False, header=["lap1", "lap2", "lap3"])


if __name__ == "__main__":
    main(parse_args())
