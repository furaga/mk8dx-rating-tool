import argparse
import time
from pathlib import Path

import cv2

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


def main(args):
    all_video_paths = list(args.video_dir.glob("*.mp4"))

    start_time = time.time()
    for vi, video_path in enumerate(all_video_paths):
        print("=========================================")
        print(f"[{vi + 1}/{len(all_video_paths)}] {str(video_path)}")
        print("=========================================")

        out_path = args.out_dir / f"{video_path.stem}.csv"
        if out_path.exists():
            continue
        with open(out_path, "w", encoding="utf8") as f:
            f.write("VIDEO_TIME_MS,LAP,TIMER\n")
        cap = cv2.VideoCapture(str(video_path))

        ts = 0
        delta_time = 333  # 3FPSくらい

        while True:
            ts += delta_time
            cap.set(cv2.CAP_PROP_POS_MSEC, ts)
            ret, frame = cap.read()
            if not ret:
                break

            ret_lap, n_lap = RaceAnalyzer.detect_lap(frame, 3)
            if not ret_lap:
                n_lap = -1

            ret_timer, timer_str = RaceAnalyzer.detect_timer(frame)
            if not ret_timer:
                timer_str = ""

            with open(out_path, "a", encoding="utf8") as f:
                # ミリ秒をhh:mm:ss.msに変換
                import datetime

                t = datetime.datetime(1, 1, 1) + datetime.timedelta(milliseconds=ts)
                video_time_str = t.strftime("%H:%M:%S.%f")[:-3]

                text = f"{video_time_str},{n_lap},{timer_str}\n"
                f.write(text)
                if (ts // delta_time) % 500 == 0:
                    print(
                        vi,
                        video_path.stem,
                        "|",
                        text.strip(),
                        "|",
                        f"Elapsed Time: {time.time() - start_time:.1f} sec",
                    )

            if args.imshow:
                cv2.imwrite("out.png", frame)
                cv2.imshow("frame", frame)
                if cv2.waitKey(0) == ord("q"):
                    break


if __name__ == "__main__":
    main(parse_args())
    main(parse_args())
