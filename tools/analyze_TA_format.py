import argparse
from pathlib import Path

import cv2
import numpy as np


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


fontsize = 32


def plot(xs, ys, n_lap, label, borders, ideal_times):
    import matplotlib.pyplot as plt

    inds = [i for i, y in enumerate(ys) if not np.isnan(y)]
    print(f"LAP{n_lap}: {len(inds)} ({100 * len(inds) / len(xs)} %)")
    if n_lap < 3:
        inds = [i for i, y in enumerate(ys) if 37.8 < y < 42]

    # set canvas size
    plt.figure(figsize=(20, 10))
    plt.rcParams["font.size"] = fontsize
    plt.xlabel("Practice Time [hours]")
    plt.ylabel("Time [sec]")

    xs = np.take(xs, inds)
    ys = np.take(ys, inds)
    plt.plot(xs, ys, label=label)

    # for border in borders:
    #     y0 = min(ys)
    #     y1 = max(ys)
    #     plt.plot(
    #         [border, border],
    #         [y0, y1],
    #         color="gray",
    #         linestyle="dashed",
    #         linewidth=0.5,
    #     )

    # moving average
    ksize = 30
    move_avg = np.convolve(ys, np.ones(ksize), mode="valid") / ksize
    plt.plot(xs[-len(move_avg) :], move_avg, label=label + " MA (k=30)")
    plt.legend()

    # save as png
    plt.savefig(f"output/LAP{n_lap}_RAW.png")

    # moving minimum
    move_min = np.minimum.accumulate(ys)
    plt.plot(xs, move_min, label=label + " Best")

    # save as png
    plt.legend()
    plt.savefig(f"output/LAP{n_lap}.png")

    if n_lap == 3:
        plt.plot(xs, np.take(ideal_times, inds), label="Ideal Time")
        # save as png
        plt.legend()
        plt.savefig(f"output/LAP{n_lap}_IDEAL.png")

    # 更新時期
    miny = 1e10
    for x, y in zip(xs, ys):
        if y < miny:
            print(f"{x} {y}")
            miny = y


def main(args):
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

    n_lap = 0
    out_rows = []
    video_time_offset = 0
    borders = []
    borders.append(video_time_offset)
    for vi, vid in enumerate(video_ids):
        csv_path = list(args.out_dir.glob(f"*{vid}.csv"))[0]
        laps_path = f"output/{csv_path.name}"

        import pandas as pd

        df = pd.read_csv(laps_path)

        for row in df.values:
            video_time, _, timer = row

            import datetime

            video_time_dt = datetime.datetime.strptime(
                video_time, "%H:%M:%S.%f"
            ) - datetime.datetime.strptime("0:0:0.0", "%H:%M:%S.%f")
            video_time_sec = video_time_offset + video_time_dt.total_seconds() / 3600

            # parse and convert timer to sec

            dt = datetime.datetime.strptime(timer, "%M:%S.%f")
            second = dt.minute * 60 + dt.second + dt.microsecond / 1000000

            is_start = second == 0
            # 一周目39.3以上しか取れてないのでそれより小さい値はおかしい
            is_not_lap1 = second < 39.3
            is_finish = second > 60

            if is_start:
                n_lap = 0
            elif is_finish:
                n_lap = 3
            else:
                n_lap = len(out_rows[-1]) if len(out_rows) > 0 else 0
                if n_lap >= 3:
                    out_rows.append([])
                    n_lap = 1
                if n_lap == 1 and is_not_lap1:
                    n_lap = 2

            if n_lap == 0:
                out_rows.append([])

            while len(out_rows[-1]) < n_lap:
                out_rows[-1].append((float("nan"), float("nan")))

            out_rows[-1].append((video_time_sec, second))

            assert (
                len(out_rows[-1]) <= 4
            ), f"ERROR: more than 4 elements: {out_rows[-1]}"

            if n_lap == 3:
                out_rows.append([])

        video_time_offset += video_time_dt.total_seconds() / 3600
        borders.append(video_time_offset)

    def find_valid(vs):
        for v in vs:
            if v != float("nan"):
                return v
        return float("nan")

    out_rows = [
        [find_valid([v[0] for v in row])] + [v[1] for v in row] for row in out_rows
    ]

    # out_rows = [
    #     row for row in out_rows if len(row) < 3 or max(row[2 : min(4, len(row))]) < 42
    # ]

    print(out_rows[:3])
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(
        "output/TA_laps.csv",
        index=False,
        header=["Practice Time", "Start", "LAP1", "LAP2", "FINISH"],
    )

    # video_time_offset to HH:MM:SS
    print(video_time_offset)

    print("TOTAL:", len(out_rows))

    min_times = []

    for n_lap in range(1, 4):
        if n_lap == 3:
            vs = [
                row[4] - row[2] - row[3]
                if len(row) > 4 and not np.any(np.isnan(row[2:5]))
                else np.inf
                for row in out_rows
            ]
        else:
            vs = [
                row[n_lap + 1] if len(row) > n_lap + 1 else float("nan")
                for row in out_rows
            ]
        vs = [v if not np.isnan(v) and 37.8 < v < 42 else np.inf for v in vs]
        mins = np.minimum.accumulate(vs)
        #        print(mins)
        min_times.append(mins)

    print(min_times[0][-1], min_times[1][-1], min_times[2][-1])

    ideal_times = [ts[0] + 2 * min(ts[1:]) for ts in zip(*min_times)]

    print(ideal_times[-1])

    for n_lap in range(1, 4):
        xs = [row[0] for row in out_rows]
        ys = [
            row[n_lap + 1] if len(row) > n_lap + 1 else float("nan") for row in out_rows
        ]
        plot(xs, ys, n_lap, f"LAP{n_lap}", borders, ideal_times)


if __name__ == "__main__":
    main(parse_args())
