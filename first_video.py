"""
最下位のレースのshorts動画を自動生成したい
"""

import argparse
import cv2
from pathlib import Path
from typing import NamedTuple, List
import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--mode", type=str, default="list")
    parser.add_argument("--race_info_path", type=Path, default="out.csv")
    parser.add_argument("--imshow", action="store_true")
    parser.add_argument(
        "--template_ymmp", type=Path, default="data/template_1位感謝供養.ymmp"
    )
    parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--start_time", type=str, default="0:00:00")
    parser.add_argument("--end_time", type=str, default="0:00:30")
    parser.add_argument("--out_ymmp_path", type=Path, default=None)
    args = parser.parse_args()
    return args


def collect_first_place_races(df):
    indexes = []
    for i, row in df.iterrows():
        #        print(row)
        med_rate = np.median(
            [row[f"rates_{i}"] for i in range(12) if 0 < row[f"rates_{i}"] <= 99999]
        )
        if row["place"] == 1 and med_rate > 20000:
            indexes.append(i)
            print(row["ts"], row["course"], row["place"], row["my_rate"], med_rate)
    return indexes


def generate_ymmp(tempalte_ymmp, video_path, start_time_str, end_time_str, output_path):
    cap = cv2.VideoCapture(str(video_path))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    from datetime import datetime

    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")

    video_length = int((end_time - start_time).total_seconds() * 60)
    print(end_time - start_time, "|", video_length, fps)

    with open(tempalte_ymmp, "r", encoding="utf8") as f:
        template = f.read()

    output = template
    video_path_escaped = str(video_path).replace("\\", "\\\\")
    output = output.replace("{{VIDEO_PATH}}", f'"{video_path_escaped}"')
    output = output.replace("{{VIDEO_OFFSET_TIME}}", f'"{start_time_str}"')
    output = output.replace("{{VIDEO_LENGTH}}", str(video_length))
    output = output.replace("{{SOUND_LENGTH}}", str(video_length + 150))
    output = output.replace("{{FRAME_LENGTH}}", str(video_length + 180))
    output = output.replace("{{TOTAL_LENGTH}}", str(video_length + 300))

    with open(output_path, "w", encoding="utf8") as f:
        f.write(output)


def main(args):
    #    cap = cv2.VideoCapture(str(args.video_path))

    if args.mode == "list":
        import pandas as pd

        df = pd.read_csv(
            args.race_info_path,
            encoding="utf8",
            engine="python",
            on_bad_lines="skip",
        )
        collect_first_place_races(df)
    else:
        args.out_ymmp_path.parent.mkdir(parents=True, exist_ok=True)
        generate_ymmp(
            args.template_ymmp,
            args.video_path,
            args.start_time,
            args.end_time,
            args.out_ymmp_path,
        )


if __name__ == "__main__":
    main(parse_args())
