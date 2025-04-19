from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd


def analyze_network_data_combined(csv_string):
    # CSVデータを読み込む
    df = pd.read_csv(StringIO(csv_string))

    # timestamp列をdatetime型に変換
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 日付と時間を抽出
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    # packet_lossが0より大きい場合、max_rttを1000に設定
    df.loc[df["packet_loss"] > 0, "max_rtt"] = 1000

    # グラフの作成
    plt.figure(figsize=(12, 6))

    # 日付ごとに異なる色で描画
    for date in df["date"].unique():
        # その日のデータを抽出
        daily_data = df[df["date"] == date]

        # 時間ごとの平均を計算
        hourly_avg = daily_data.groupby("hour")["max_rtt"].mean().reset_index()

        # プロット（日付をラベルに使用）
        plt.plot(hourly_avg["hour"], hourly_avg["max_rtt"], marker="o", label=str(date))

    plt.title("Average Max RTT by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average Max RTT (ms)")
    plt.grid(True)

    # X軸の設定（0-23時）
    plt.xticks(range(0, 24))

    # Y軸の範囲を0-1000に設定
    plt.ylim(0, 1000)

    # 凡例を表示
    plt.legend()

    # グラフの余白を調整
    plt.tight_layout()

    # グラフを保存
    plt.savefig("network_rtt_analysis.png")
    plt.close()


def analyze_network_data_combined2(csv_string):
    # CSVデータを読み込む
    df = pd.read_csv(StringIO(csv_string))

    # timestamp列をdatetime型に変換
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 日付と時間を抽出
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["time_10min"] = df["hour"] + (df["timestamp"].dt.minute // 20) * (20 / 60)

    # packet_lossが0より大きい場合、max_rttを1000に設定
    df.loc[df["packet_loss"] > 0, "max_rtt"] = 1000

    # 日付のリストを取得し、ソート
    dates = sorted(df["date"].unique())
    latest_date = dates[-1]  # 最新の日付

    # グラフの作成
    plt.figure(figsize=(12, 6))

    # 日付ごとに描画
    for date in dates:
        # その日のデータを抽出
        daily_data = df[df["date"] == date]

        # 時間ごとの平均を計算
        hourly_avg = daily_data.groupby("time_10min")["max_rtt"].mean().reset_index()

        if date == latest_date:
            # 最新の日付は太い赤線で表示
            plt.plot(
                hourly_avg["time_10min"],
                hourly_avg["max_rtt"],
                color="red",
                linewidth=3,
                marker="o",
                markersize=8,
                label=f"{date} (Latest)",
            )
        else:
            # その他の日付は細い灰色の線で表示
            plt.plot(
                hourly_avg["time_10min"],
                hourly_avg["max_rtt"],
                color="gray",
                alpha=0.5,
                linewidth=1,
                marker="o",
                markersize=4,
                label=str(date),
            )

    plt.title("Average Max RTT by Hour\nLatest Date Highlighted in Red", pad=20)
    plt.xlabel("Hour")
    plt.ylabel("Average Max RTT (ms)")
    plt.grid(True)

    # X軸の設定（0-23時）
    plt.xticks(range(0, 24))

    # Y軸の範囲を0-1000に設定
    plt.ylim(0, 1000)

    # 凡例を表示（最新の日付が一番上に来るように逆順にソート）
    handles, labels = plt.gca().get_legend_handles_labels()
    handles = handles[::-1]
    labels = labels[::-1]
    plt.legend(handles, labels, title="Dates")

    # グラフの余白を調整
    plt.tight_layout()

    # グラフを保存
    plt.savefig("network_rtt_analysis_highlight.png")
    plt.close()


# CSVデータを文字列として用意
with open("ping_results.csv", "r") as file:
    csv_data = file.read()

# 関数を実行
analyze_network_data_combined(csv_data)
analyze_network_data_combined2(csv_data)
