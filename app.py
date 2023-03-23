from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

import datetime

app = Dash(__name__)


df = pd.read_csv('data/db_test.csv', index_col=0)
df['date'] = pd.to_datetime(df['date'])


app.layout = html.Div([
    html.H4('Popular songs of NOPLP'),
    dcc.Graph(id="graph"),
        dcc.RangeSlider(
            id = 'datetime_RangeSlider',
            updatemode = 'mouseup', #don't let it update till mouse released
            min = 0,
            max = 100,
            value = [0,100]
        )
])

@app.callback(
    Output('graph', 'figure'),
    Input('datetime_RangeSlider', 'value'))
def update_figure(value):
    now = datetime.datetime.now()
    small, big = value
    graph_df = df[now - df['date'] <= datetime.timedelta(days=30*big)]
    graph_df = graph_df[now - graph_df['date'] >= datetime.timedelta(days=30*small)]
    graph_df = graph_df.groupby(by=["name"], as_index=False)['date'].count()
    fig = px.bar(
        data_frame=graph_df,
        x="name",
        y="date"
    )
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
