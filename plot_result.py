import random

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# データを作成
x = [1, 2, 3, 4]


def generate_y():
    return [random.randint(10, 20) for _ in range(len(x))]


# グラフを作成
initial_trace = go.Scatter(
    x=x, y=generate_y(), mode="markers", marker=dict(color="red")
)

# Dashアプリケーションの作成
app = dash.Dash(__name__)

# アプリケーションのレイアウト
app.layout = html.Div(
    [
        dcc.Graph(id="my-graph", figure=go.Figure(data=[initial_trace])),
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,
            n_intervals=0,  # in milliseconds
        ),
    ]
)


def get_avg_rate(line):
    import numpy as np

    rates = [int(r) for r in line.split(",")[5:]]
    return np.median([r for r in rates if r > 0])


# コールバック関数
@app.callback(
    Output("my-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph(n_intervals):
    show_num = 25

    # update_tracesを使用してマーカーカラーを変更
    with open("out.csv", "r", encoding="utf8") as f:
        lines = f.readlines()[1:][-show_num:]
        my_rates = [int(line.split(",")[4]) for line in lines]
        x = [i for i in range(len(my_rates))]

        starts = []
        for i in range(len(lines) - 1):
            ts1 = lines[i].split(",")[0]
            ts2 = lines[i + 1].split(",")[0]
            if ts1.split("@")[0] != ts2.split("@")[0]:
                starts.append(i + 1)

    updated_trace = go.Scatter(
        x=x,
        y=my_rates,
        mode="lines+markers",
        name="自分のレート",
        yaxis="y1",
        line=dict(color="#11ff11", width=2),
        marker=dict(size=4),
    )

    # グラフに反映させる
    fig = go.Figure(data=[updated_trace])  # , updated_trace_median])

    # 基本レイアウト
    fig.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(size=18, color="white"),
    )

    # タイトル
    fig.update_layout(
        title=dict(
            text="<i>Versus Rate",
            font=dict(size=24, color="white"),
            x=0.5,
            y=0.82,
            xanchor="center",
        )
    )
    fig.update_layout(
        shapes=[
            # 縦の区切り線
            *[
                dict(
                    type="line",
                    x0=x,
                    x1=x,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(
                        color="#cccccc",
                        width=1,
                    ),
                )
                for x in starts
            ],
            # 水平の参照線
            dict(
                type="line",
                x0=0,
                x1=len(my_rates) - 1,
                y0=77777,
                y1=77777,
                line=dict(
                    color="#ff0000",
                    width=1,
                ),
            ),
        ]
    )
    fig.update_xaxes(
        showline=True,
        linewidth=3,
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    # レート値からrangeを計算
    min_rate = min(my_rates)
    max_rate = max(my_rates)
    rate_center = (min_rate + max_rate) / 2  # 中心値
    range_min = min(min_rate - 10, rate_center - 200)  # 中心から±100
    range_max = max(max_rate + 10, rate_center + 200)
    fig.update_yaxes(
        showline=True,
        linewidth=3,
        linecolor="white",
        dtick=100,
        tickformat="%d",
        color="white",
        showgrid=True,
        gridcolor="#cccccc",
        gridwidth=1,
        range=[range_min, range_max],
    )

    return fig


# アプリケーションを実行
if __name__ == "__main__":
    app.run_server(debug=True)
    app.run_server(debug=True)
