# import plotly.graph_objects as go

# import time

# with open("out.csv", "r", encoding="sjis") as f:
#     lines = f.readlines()
#     my_rates = [int(line.split(",")[3]) for line in lines[1:]]
#     x =  [i for i in range(len(my_rates))]

# fig = go.Figure()
# fig.add_trace(go.Scatter(x=x, y=my_rates, mode='lines+markers', name='Line 1'))
# fig.update_layout(title='Interactive Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
# fig.show()

# while True:
#     with open("out.csv", "r", encoding="sjis") as f:
#         lines = f.readlines()
#         my_rates = [int(line.split(",")[4]) * 1.01 for line in lines[1:]]
#         x =  [i for i in range(len(my_rates))]

#     fig.update_traces(go.Scatter(x=x, y=my_rates, mode='lines+markers', name='Line 1'))
#     fig.update_layout(title='Interactive Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
#     print("update")
#     time.sleep(5)


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# データを作成
x = [1, 2, 3, 4]
y = [10, 15, 13, 17]

# グラフを作成
initial_trace = go.Scatter(x=x, y=y, mode="markers", marker=dict(color="red"))

# Dashアプリケーションの作成
app = dash.Dash(__name__)

# アプリケーションのレイアウト
app.layout = html.Div(
    [
        html.Button("Update Graph", id="update-button"),
        dcc.Graph(id="my-graph", figure=go.Figure(data=[initial_trace])),
    ]
)


# コールバック関数
@app.callback(
    Output("my-graph", "figure"),
    Input("update-button", "n_clicks"),
)
def update_graph(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    with open("out.csv", "r", encoding="sjis") as f:
        lines = f.readlines()
        my_rates = [int(line.split(",")[4]) * 1.01 for line in lines[1:]]
        x =  [i for i in range(len(my_rates))]

    updated_trace = go.Scatter(x=x, y=my_rates, mode='lines+markers', name='Line 1')

    # グラフに反映させる
    return go.Figure(data=[updated_trace])


# アプリケーションを実行
if __name__ == "__main__":
    app.run_server(debug=True)
