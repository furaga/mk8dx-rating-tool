"""
最下位のレースのshorts動画を自動生成したい
"""

import argparse
from pathlib import Path

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--mode", type=str, default="list")
    parser.add_argument("--race_info_path", type=Path, default="out.csv")
    parser.add_argument("--imshow", action="store_true")
    parser.add_argument(
        "--template_ymmp", type=Path, default="data/template_最下位葬儀会場.ymmp"
    )
    parser.add_argument("--video_path", type=Path, default=None)
    parser.add_argument("--start_time", type=str, default="0:00:00")
    parser.add_argument("--end_time", type=str, default="0:00:30")
    parser.add_argument("--out_ymmp_path", type=Path, default=None)
    args = parser.parse_args()
    return args


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


def generate_ymmp(tempalte_ymmp, video_path, start_time_str, end_time_str, output_path):
    from datetime import datetime

    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")

    video_length = int((end_time - start_time).total_seconds() * 60)

    with open(tempalte_ymmp, "r", encoding="utf8") as f:
        template = f.read()

    output = template
    video_path_escaped = str(video_path).replace("\\", "\\\\")
    output = output.replace("{{VIDEO_PATH}}", f'"{video_path_escaped}"')
    output = output.replace("{{VIDEO_OFFSET_TIME}}", f'"{start_time_str}"')
    output = output.replace("{{VIDEO_LENGTH}}", str(video_length))
    output = output.replace("{{SOUND_LENGTH}}", str(video_length + 30))
    output = output.replace("{{FINAL_TEXT_OFFSET}}", str(video_length + 30 - 360))

    with open(output_path, "w", encoding="utf8") as f:
        f.write(output)

    print(
        f"Save last race video. Video time: {end_time - start_time} | {str(output_path)}."
    )


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
        collect_last_place_races(df)
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
