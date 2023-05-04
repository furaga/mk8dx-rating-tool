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


# コールバック関数
@app.callback(
    Output("my-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph(n_intervals):
    # update_tracesを使用してマーカーカラーを変更
    with open("out.csv", "r", encoding="sjis") as f:
        lines = f.readlines()[1:]
        my_rates = [int(line.split(",")[4]) for line in lines]
        start_days = [0]
        for i in range(len(lines) - 1):
            if lines[i + 1].split(",")[0].split('@')[0] != lines[i].split(",")[0].split('@')[0]:
                start_days.append(i + 1)
        x = [i for i in range(len(my_rates))]

    updated_trace = go.Scatter(x=x, y=my_rates, mode="lines+markers", name="Line 1")

    # グラフに反映させる
    fig = go.Figure(data=[updated_trace])

    # x=10の赤色の縦線を追加
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                x0=x,
                x1=x,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="red"),
            ) for x in start_days
        ]
    )

    return fig

# アプリケーションを実行
if __name__ == "__main__":
    app.run_server(debug=True)
