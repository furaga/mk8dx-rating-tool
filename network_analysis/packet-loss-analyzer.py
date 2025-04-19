#!/usr/bin/env python3
import sys

import matplotlib.pyplot as plt
import pandas as pd


def analyze_packet_loss(csv_file):
    """
    Analyze packet loss by day of week and hour from ping data CSV

    Args:
        csv_file (str): Path to the CSV file
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Convert timestamps to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract hour and day of week from timestamp
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek  # 0=Monday, 6=Sunday

    # English day names
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Average packet loss by day of week
    day_stats = (
        df.groupby("day_of_week")
        .agg({"packet_loss": "mean", "timestamp": "count"})
        .rename(columns={"timestamp": "count"})
    )

    day_stats.index = [day_names[i] for i in day_stats.index]

    print("Average packet loss by day of week:")
    print(day_stats[["packet_loss", "count"]])

    # Average packet loss by hour
    hourly_stats = (
        df.groupby("hour")
        .agg({"packet_loss": "mean", "timestamp": "count"})
        .rename(columns={"timestamp": "count"})
    )

    print("\nAverage packet loss by hour:")
    print(hourly_stats[["packet_loss", "count"]])

    # Average packet loss by day and hour combination
    day_hour_stats = (
        df.groupby(["day_of_week", "hour"])
        .agg({"packet_loss": "mean", "timestamp": "count"})
        .rename(columns={"timestamp": "count"})
    )

    # Convert to a more readable pivot table
    day_hour_pivot = pd.pivot_table(
        df,
        values="packet_loss",
        index="day_of_week",
        columns="hour",
        aggfunc="mean",
        fill_value=0,
    )

    # Convert index to day names
    day_hour_pivot.index = [day_names[i] for i in day_hour_pivot.index]

    print("\nAverage packet loss by day and hour:")
    print(day_hour_pivot)

    # Overall statistics
    # sum of packet_sent
    total_tests = df["packets_sent"].sum()
    total_failures = df["packet_loss"].sum()
    failure_rate = (total_failures / total_tests) * 100

    print(f"\nTotal tests: {total_tests}")
    print(f"Tests with packet loss: {total_failures}")
    print(f"Percentage of tests with packet loss: {failure_rate:.2f}%")

    if total_failures > 0:
        avg_loss_when_failing = df[df["packet_loss"] > 0]["packet_loss"].mean()
        print(f"Average packet loss when failure occurs: {avg_loss_when_failing:.2f}%")

    # Create heatmap
    plt.figure(figsize=(14, 8))

    # Fill missing data with zeros
    complete_pivot = day_hour_pivot.copy()
    for h in range(24):
        if h not in complete_pivot.columns:
            complete_pivot[h] = 0
    complete_pivot = complete_pivot.reindex(columns=sorted(complete_pivot.columns))

    # Draw heatmap
    plt.imshow(complete_pivot, cmap="YlOrRd", aspect="auto")
    plt.colorbar(label="Packet Loss (%)")
    plt.title("Packet Loss by Day and Hour")
    plt.xlabel("Hour")
    plt.ylabel("Day of Week")

    # Set X-axis labels
    plt.xticks(range(len(complete_pivot.columns)), complete_pivot.columns)
    # Set Y-axis labels
    plt.yticks(range(len(complete_pivot.index)), complete_pivot.index)

    plt.tight_layout()
    plt.savefig("packet_loss_heatmap.png")
    print("\nHeatmap saved as 'packet_loss_heatmap.png'")

    # Bar chart of packet loss by hour
    plt.figure(figsize=(12, 6))
    hourly_stats["packet_loss"].plot(kind="bar", color="salmon")
    plt.title("Average Packet Loss by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average Packet Loss (%)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("packet_loss_by_hour.png")
    print("Hourly chart saved as 'packet_loss_by_hour.png'")

    # Bar chart of packet loss by day of week
    plt.figure(figsize=(10, 6))
    day_stats["packet_loss"].plot(kind="bar", color="skyblue")
    plt.title("Average Packet Loss by Day of Week")
    plt.xlabel("Day of Week")
    plt.ylabel("Average Packet Loss (%)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("packet_loss_by_day.png")
    print("Daily chart saved as 'packet_loss_by_day.png'")

    # Show details for times with packet loss
    high_loss_times = df[df["packet_loss"] > 0].copy()
    if not high_loss_times.empty:
        print("\nTime periods with packet loss:")

        # Add day name
        high_loss_times["day_name"] = high_loss_times["day_of_week"].apply(
            lambda x: day_names[x]
        )

        for _, row in list(high_loss_times.iterrows())[-5:]:
            print(
                f"  {row['timestamp']} ({row['day_name']}) - Loss: {row['packet_loss']}% - Packets: {row['packets_received']}/{row['packets_sent']}"
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "paste.txt"  # Default filename

    try:
        analyze_packet_loss(csv_file)
    except Exception as e:
        print(f"Error: {e}")
