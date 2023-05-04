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
        lines = f.readlines()[1:][-40:]
        my_rates = [int(line.split(",")[4]) for line in lines]
        x = [i for i in range(len(my_rates))]

    updated_trace = go.Scatter(x=x, y=my_rates, mode="lines+markers", name="Line 1")

    # グラフに反映させる
    fig = go.Figure(data=[updated_trace])
    fig.update_layout(
        title=dict(
            text="<b>レート推移",
            font=dict(size=26, color="black"),
            x=0.5,
            y=0.77,
            xanchor="center",
        ),
        legend=dict(xanchor="left", yanchor="bottom", x=0.02, y=0.85, orientation="h"),
        yaxis=dict(
            tickformat="%d",
            dtick=100,
            showgrid=True,
            linecolor="red",
        ),
        font=dict(size=18, color="black"),
    )
    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor="black",
        color="black",
        showgrid=False,
    )
    fig.update_yaxes(
        showline=True, linewidth=2, linecolor="black", color="black",
        gridcolor="lightgray",
        gridwidth=2,
    )

    return fig


# アプリケーションを実行
if __name__ == "__main__":
    app.run_server(debug=True)
