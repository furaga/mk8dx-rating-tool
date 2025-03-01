#!/usr/bin/env python3
"""
Windows用のシンプルなping監視スクリプト
定期的にpingを実行し、結果をCSVファイルに保存します
"""

import csv
import datetime
import os
import subprocess
import time
from typing import Any, Dict, List


def run_ping(host: str, count: int) -> Dict[str, Any]:
    """
    pingコマンドを実行し、結果を解析します

    Args:
        host: ping対象のホスト
        count: 送信するpingパケットの数

    Returns:
        ping統計情報を含む辞書
    """
    timestamp = datetime.datetime.now()

    # Windowsのpingコマンドを構築
    cmd = f"ping -4 -n {count} {host}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 結果初期化
        ping_data = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "host": host,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_rtt": None,
            "avg_rtt": None,
            "max_rtt": None,
            "success": False,
            "error": None,
        }

        if result.returncode == 0:
            ping_data["success"] = True
            output = result.stdout

            # 個別のRTT値を収集
            rtts = []

            for line in output.splitlines():
                # "からの応答: ..." の行からRTTを抽出
                if "からの応答:" in line and "時間" in line:
                    try:
                        time_part = line.split("時間 =")[1].split("ms")[0]
                        time_value = float(time_part)
                        rtts.append(time_value)
                    except Exception:
                        pass

                # パケット統計を取得
                if "パケット数:" in line:
                    try:
                        # "パケット数: 送信 = 4、受信 = 4、損失 = 0 (0% の損失)"の形式をパース
                        sent_part = line.split("送信 = ")[1].split("、")[0]
                        ping_data["packets_sent"] = int(sent_part)

                        received_part = line.split("受信 = ")[1].split("、")[0]
                        ping_data["packets_received"] = int(received_part)

                        # 損失率を取得
                        loss_part = line.split("(")[1].split("%")[0]
                        ping_data["packet_loss"] = float(loss_part)
                    except Exception:
                        pass

                # RTT統計情報を要約行から取得
                if "最小 =" in line:
                    try:
                        # "最小 = 10ms、最大 = 11ms、平均 = 10ms"の形式をパース
                        min_part = line.split("最小 = ")[1].split("ms")[0]
                        ping_data["min_rtt"] = float(min_part)

                        max_part = line.split("最大 = ")[1].split("ms")[0]
                        ping_data["max_rtt"] = float(max_part)

                        avg_part = line.split("平均 = ")[1].split("ms")[0]
                        ping_data["avg_rtt"] = float(avg_part)
                    except Exception:
                        pass

            # 個別のRTTから統計を計算（要約行から取得できなかった場合）
            if rtts and (ping_data["min_rtt"] is None or ping_data["avg_rtt"] is None):
                ping_data["min_rtt"] = min(rtts)
                ping_data["max_rtt"] = max(rtts)
                ping_data["avg_rtt"] = sum(rtts) / len(rtts)

        else:
            ping_data["error"] = "pingコマンドの実行に失敗しました"

        return ping_data

    except Exception as e:
        return {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "host": host,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_rtt": None,
            "avg_rtt": None,
            "max_rtt": None,
            "success": False,
            "error": str(e),
        }


def save_results(results: List[Dict[str, Any]], filename: str) -> None:
    """
    結果をCSVファイルに保存します

    Args:
        results: ping結果の辞書リスト
        filename: 出力ファイルパス
    """
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as csvfile:
        fieldnames = [
            "timestamp",
            "host",
            "success",
            "packets_sent",
            "packets_received",
            "packet_loss",
            "min_rtt",
            "avg_rtt",
            "max_rtt",
            "error",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for result in results:
            writer.writerow(result)

        csvfile.flush()


def print_result_summary(result: Dict[str, Any]) -> None:
    """ping結果のサマリーをコンソールに表示します"""
    print(f"\n--- Ping結果 {result['timestamp']} ---")
    print(f"ホスト: {result['host']}")

    if result["success"]:
        print("状態: 成功")
        print(
            f"パケット: 送信={result['packets_sent']}, 受信={result['packets_received']}, "
            f"損失={result['packet_loss']:.1f}%"
        )

        if result["min_rtt"] is not None:
            print(
                f"応答時間 (ms): 最小={result['min_rtt']:.2f}, 平均={result['avg_rtt']:.2f}, "
                f"最大={result['max_rtt']:.2f}"
            )
    else:
        print("状態: 失敗")
        print(f"エラー: {result['error']}")

    print("-" * 50)


def main():
    """メイン関数"""
    # デフォルト設定
    host = "8.8.8.8"  # Googleのパブリックドメインネームサーバー
    interval = 60  # 秒
    count = 4  # pingの回数
    output_file = "ping_results.csv"

    # カスタム設定（必要に応じて変更）
    print("Ping監視設定")
    custom_host = input(f"監視するホスト [{host}]: ").strip()
    if custom_host:
        host = custom_host

    try:
        custom_interval = input(f"実行間隔（秒）[{interval}]: ").strip()
        if custom_interval:
            interval = int(custom_interval)
    except ValueError:
        print(f"無効な値です。デフォルト値の{interval}秒を使用します。")

    try:
        custom_count = input(f"Pingの回数 [{count}]: ").strip()
        if custom_count:
            count = int(custom_count)
    except ValueError:
        print(f"無効な値です。デフォルト値の{count}回を使用します。")

    custom_output = input(f"出力ファイル名 [{output_file}]: ").strip()
    if custom_output:
        output_file = custom_output

    try:
        custom_duration = input("実行時間（分）[無期限の場合は0]: ").strip()
        if custom_duration:
            duration = int(custom_duration)
        else:
            duration = 0
    except ValueError:
        print("無効な値です。無期限で実行します。")
        duration = 0

    print(f"\n{host}に対してPing監視を開始します")
    print(f"間隔: {interval}秒")
    print(f"Ping回数/サイクル: {count}")
    print(f"結果は {output_file} に保存されます")

    if duration > 0:
        print(f"合計実行時間: {duration}分")
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)
    else:
        print("無期限で実行します（終了するには Ctrl+C を押してください）")
        end_time = None

    results = []
    cycles = 0

    try:
        previous_time = time.time()
        while True:
            cycles += 1
            print(
                f"\nサイクル {cycles} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Ping実行
            result = run_ping(host, count)
            results.append(result)

            # 結果表示
            print_result_summary(result)

            # 定期的に結果を保存（5サイクルごと、またはエラー発生時）
            if cycles % 5 == 0 or not result["success"]:
                save_results(results, output_file)
                results = []  # 保存後にリストをクリア
                print(f"結果を {output_file} に保存しました")

            # 指定した実行時間に達したかチェック
            if end_time and datetime.datetime.now() >= end_time:
                print(f"\n指定した実行時間 {duration}分 に達しました。終了します。")
                break

            # 次の間隔まで待機
            sleep_time = interval - (time.time() - previous_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            previous_time = time.time()

    except KeyboardInterrupt:
        print("\nユーザーによって監視を停止しました。")

    finally:
        # 残りの結果を保存
        if results:
            save_results(results, output_file)
            print(f"最終結果を {output_file} に保存しました")


if __name__ == "__main__":
    main()
