import argparse
import random

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# データを作成 (クラス外に移動しても良い、または初期化で使うならクラス内でも)
x_template = [1, 2, 3, 4]  # Example, might not be needed anymore


def generate_y():
    return [random.randint(10, 20) for _ in range(len(x_template))]


def get_avg_rate(line):
    rates = [int(r) for r in line.split(",")[5:]]
    return np.median([r for r in rates if r > 0])


class RatePlotter:
    def __init__(self, file_path="out.csv", line_color="#11ff11", show_num=25):
        self.file_path = file_path
        self.line_color = line_color
        self.show_num = show_num
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        # 初期グラフ（空またはダミーデータ）
        # 起動時にファイルを読む必要がなければ、空のグラフで良い
        initial_figure = go.Figure()

        self.app.layout = html.Div(
            [
                dcc.Graph(id="my-graph", figure=initial_figure),
                dcc.Interval(
                    id="interval-component",
                    interval=5 * 1000,  # 5 seconds
                    n_intervals=0,
                ),
            ]
        )

    def _setup_callbacks(self):
        @self.app.callback(
            Output("my-graph", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_graph(n_intervals):
            # インスタンス変数からファイルパスと色、表示件数を取得
            file_path = self.file_path
            line_color = self.line_color
            show_num = self.show_num

            try:
                with open(file_path, "r", encoding="utf8") as f:
                    lines = f.readlines()[1:]  # ヘッダーを除外
                    if not lines:
                        print(f"Warning: No data found in {file_path} after header.")
                        return go.Figure()  # データがない場合は空のグラフ

                    # 表示件数分を取得、足りない場合は全て表示
                    lines = lines[-show_num:]

                    if not lines:
                        print(
                            f"Warning: No lines selected after slicing in {file_path}."
                        )
                        return go.Figure()

                    my_rates = [int(line.split(",")[4]) for line in lines]
                    x = list(range(len(my_rates)))

                    starts = []
                    for i in range(len(lines) - 1):
                        try:
                            ts1 = lines[i].split(",")[0]
                            ts2 = lines[i + 1].split(",")[0]
                            if ts1.split("@")[0] != ts2.split("@")[0]:
                                starts.append(i + 1)
                        except IndexError:
                            # 行の形式が正しくない場合の処理
                            print(
                                f"Warning: Skipping line {i+1} due to unexpected format."
                            )
                            continue  # 次の行へ

            except FileNotFoundError:
                print(f"Error: File not found at {file_path}")
                return go.Figure()
            except Exception as e:
                print(f"Error reading or processing file {file_path}: {e}")
                return go.Figure()

            if not my_rates:  # my_ratesが空の場合（すべての行がスキップされたなど）
                print("Warning: No valid rate data could be extracted.")
                return go.Figure()

            # グラフデータ作成
            updated_trace = go.Scatter(
                x=x,
                y=my_rates,
                mode="lines+markers",
                name="自分のレート",
                yaxis="y1",
                line=dict(color=line_color, width=2),  # インスタンス変数を使用
                marker=dict(size=4),
            )

            fig = go.Figure(data=[updated_trace])

            # 基本レイアウト
            fig.update_layout(
                paper_bgcolor="black",
                plot_bgcolor="black",
                font=dict(size=18, color="white"),
                title=dict(
                    text="<i>Versus Rate</i>",
                    font=dict(size=24, color="white"),
                    x=0.5,
                    y=0.95,  # Adjust title position slightly
                    xanchor="center",
                ),
                margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
            )

            # Shapes (区切り線と参照線)
            shapes = [
                dict(
                    type="line",
                    x0=s,
                    x1=s,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="#cccccc", width=1),
                )
                for s in starts
            ]
            # Add reference line only if x has data
            if x:
                shapes.append(
                    dict(
                        type="line",
                        x0=min(x) if x else 0,
                        x1=max(x) if x else 0,
                        y0=7777,
                        y1=7777,  # Example static value, maybe make dynamic?
                        line=dict(color="#ff0000", width=1),
                    )
                )
            fig.update_layout(shapes=shapes)

            # X軸設定
            fig.update_xaxes(
                showline=True,
                linewidth=2,  # Slightly thinner line
                linecolor="white",
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[-0.5, len(x) - 0.5]
                if x
                else [-0.5, 0.5],  # Ensure range covers markers
            )

            # Y軸設定 (レート値からrangeを計算)
            if my_rates:
                min_rate = min(my_rates)
                max_rate = max(my_rates)
                rate_diff = max_rate - min_rate
                padding = max(rate_diff * 0.1, 50)  # Add padding based on range, min 50
                range_min = min_rate - padding
                range_max = max_rate + padding
            else:  # Default range if no data
                range_min = 7000
                range_max = 9000

            fig.update_yaxes(
                showline=True,
                linewidth=2,
                linecolor="white",
                dtick=100,
                tickformat="%d",
                color="white",
                showgrid=True,
                gridcolor="#555555",  # Darker grid lines
                gridwidth=1,
                range=[range_min, range_max],
                zeroline=False,
            )

            return fig

    def run(self, debug=True, host="127.0.0.1", port=8050):
        self.app.run_server(debug=debug, host=host, port=port)


# グローバル変数としてファイルパスと色を定義 (削除)
# csv_file_path = "out.csv"
# line_color = "#11ff11"

# def get_avg_rate(line): ... (移動またはそのまま)

# def update_graph(n_intervals): ... (クラスメソッドに移動)

# アプリケーションを実行
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plotting tool for Versus Rate.")
    parser.add_argument(
        "--file",
        type=str,
        default="out.csv",
        help="Path to the input CSV file (default: out.csv)",
    )
    parser.add_argument(
        "--color",
        type=str,
        default="#11ff11",
        help="Line color for the plot (default: #11ff11)",
    )
    parser.add_argument(
        "--show_num",
        type=int,
        default=25,
        help="Number of recent data points to show (default: 25)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to run the server on (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to run the server on (default: 8050)",
    )

    args = parser.parse_args()

    # RatePlotterのインスタンスを作成し、引数を渡す
    plotter = RatePlotter(
        file_path=args.file, line_color=args.color, show_num=args.show_num
    )
    plotter.run(debug=True, host=args.host, port=args.port)  # runメソッドを呼び出す
