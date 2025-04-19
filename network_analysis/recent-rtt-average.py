from datetime import timedelta
from io import StringIO

import pandas as pd

import pandas as pd


def calculate_recent_average(csv_string):
    # CSVデータを読み込む
    df = pd.read_csv(StringIO(csv_string))

    # timestamp列をdatetime型に変換
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 最新のタイムスタンプを取得
    latest_time = df["timestamp"].max()

    # 30分前の時刻を計算
    time_threshold = latest_time - timedelta(minutes=30)

    # 直近30分のデータを抽出
    recent_data = df[df["timestamp"] > time_threshold]

    # packet_lossが0より大きい場合、max_rttを1000に設定
    recent_data.loc[recent_data["packet_loss"] > 0, "max_rtt"] = 1000

    # 平均を計算
    average_rtt = recent_data["max_rtt"].mean()

    print(f"Latest timestamp: {latest_time}")
    print(f"30 minutes before: {time_threshold}")
    print(f"Number of measurements in last 30 minutes: {len(recent_data)}")
    print(f"Average max RTT in last 30 minutes: {average_rtt:.2f} ms")


# CSVデータを文字列として用意
with open("ping_results.csv", "r") as file:
    csv_data = file.read()


# 関数を実行
calculate_recent_average(csv_data)
