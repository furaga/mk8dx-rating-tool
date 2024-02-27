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
        "IJTO0NvjLGMfeature=share",
        "sdUAxBQoQyQfeature=share",
        "xL4iRGg0PCofeature=share",
        "LaQwSTrJlxAfeature=share",
        "K-m20UB1BTIfeature=share",
        "C0UNZGT6LFcfeature=share",
        "6yg_29fm1cYfeature=share",
        "jir9MdwUGf8feature=share",
        "gVSuVCh-FV0feature=share",
        "Sm_pHXNrHzsfeature=share",
        "zH5L_tRmXnUfeature=share",
        "wE2lersICoE",
        "_w5LUqIQI7w",
        "JpHaGi8Sma4",
        "ZkZd3RoHoqM",
        "t0sh0duNUG4",
        "JtzFkut4n4I",
        "LA3s-vVYnPc",
        "OrNyVYKgYJw",
    ]

    for vi, vid in enumerate(video_ids):
        print(vid)
        csv_path = list(args.out_dir.glob(f"*{vid}.csv"))[0]
        video_path = list(args.video_dir.glob(f"*{vid}.mp4"))[0]

        if Path(f"output/{csv_path.name}").exists():
            continue

        with open(f"output/{csv_path.name}", "w") as f:
            pass

        print("=========================================")
        print(f"[{vi + 1}/{len(video_ids)}] {str(video_path)}")
        print("=========================================")

        cap = cv2.VideoCapture(str(video_path))

        import pandas as pd

        df = pd.read_csv(csv_path)

        prev_hit = -10000
        for i in range(len(df.values) - 2):
            row = df.values[i]
            tokens = row[0].split(":")
            ts = (
                int(tokens[0]) * 3600 * 1000
                + int(tokens[1]) * 60 * 1000
                + int(tokens[2].split(".")[0]) * 1000
                + int(tokens[2].split(".")[1])
            )

            if df.values[i][2] == df.values[i + 1][2] == df.values[i + 2][2]:
                # print(f"[{i}] {row}")
                if i - prev_hit > 20:
                    with open(f"output/{csv_path.name}", "a") as f:
                        f.write(",".join([str(v) for v in row]))
                        f.write("\n")
                        f.flush()
                    cap.set(cv2.CAP_PROP_POS_MSEC, ts)
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow("frame", frame)
                        if ord("q") == cv2.waitKey(1):
                            exit()
                prev_hit = i


if __name__ == "__main__":
    main(parse_args())
