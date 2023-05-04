import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import random

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
            id="interval-component", interval=5 * 1000, n_intervals=0  # in milliseconds
        ),
    ]
)


def get_avg_rate(line):
    import numpy as np
    return np.median([int(r) for r in line.split(",")[5:]])


# コールバック関数
@app.callback(
    Output("my-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph(n_intervals):
    # update_tracesを使用してマーカーカラーを変更
    with open("out.csv", "r", encoding="utf8") as f:
        lines = f.readlines()[1:]  # [-40:]
        my_rates = [int(line.split(",")[4]) for line in lines]
        other_rates = [get_avg_rate(line) for line in lines]
        x = [i for i in range(len(my_rates))]

        starts = [0]
        for i in range(len(lines) - 1):
            ts1 = lines[i].split(",")[0]
            ts2 = lines[i + 1].split(",")[0]
            if ts1.split("@")[0] != ts2.split("@")[0]:
                starts.append(i + 1)

    updated_trace = go.Scatter(
        x=x, y=my_rates, mode="lines+markers", name="自分のレート", yaxis="y1"
    )
    updated_trace_median = go.Scatter(
        x=x, y=other_rates, mode="lines+markers", name="部屋のレート中央値", yaxis="y2"
    )

    # グラフに反映させる
    fig = go.Figure(data=[updated_trace, updated_trace_median])
    fig.update_layout(
        title=dict(
            text="<b>レート推移",
            font=dict(size=26, color="black"),
            x=0.5,
            y=0.77,
            xanchor="center",
        ),
        legend=dict(xanchor="left", yanchor="bottom", x=0.02, y=0.85, orientation="h"),
        yaxis1=dict(
            tickformat="%d",
            dtick=500,
            showgrid=True,
            linecolor="red",
        ),
        yaxis2=dict(side="right", showgrid=False, overlaying="y", tickformat="%d", linecolor="green"),
        font=dict(size=18, color="black"),
    )
    fig.update_layout(plot_bgcolor="white")
    # fig.update_layout(
    #     shapes=[
    #         dict(
    #             type="line",
    #             x0=x,
    #             x1=x,
    #             y0=0,
    #             y1=1,
    #             yref="paper",
    #             line=dict(color="green", width=1),
    #         ) for x in starts
    #     ]
    # )
    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor="black",
        color="black",
        showgrid=False,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor="black",
        color="black",
        gridcolor="lightgray",
        gridwidth=1,
    )

    return fig


# アプリケーションを実行
if __name__ == "__main__":
    app.run_server(debug=True)
