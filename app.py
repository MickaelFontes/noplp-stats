import datetime

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)

df = pd.read_csv('data/db_test.csv', index_col=None)
df['date'] = pd.to_datetime(df['date'])

app.layout = html.Div([
    html.H4('Popular songs of NOPLP'),
    dcc.Graph(id="graph"),
    dcc.RangeSlider(
        id = 'datetime_RangeSlider',
        updatemode = 'mouseup', #don't let it update till mouse released
        min = 0,
        max = 200,
        value = [0,200],
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.H4('Most popular songs by category'),
    html.Div([dcc.Dropdown(
            df['category'].unique(),
            'Points',
            id='category-selector'
            )], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([dcc.Dropdown(
            sorted(df['points'].unique())[1:],
            [50,40,30,20,10],
            id='points-selector',
            multi=True
            )], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    dcc.Graph(id="sorted-graph")

])

@app.callback(
    Output('graph', 'figure'),
    Input('datetime_RangeSlider', 'value')
    )
def update_figure(date_range):
    graph_df = filter_date(date_range)
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)['date'].count()
    fig = px.histogram(
        data_frame=graph_df,
        x="name",
        y="date",
        color="category"
    )
    fig.update_layout(height=500, xaxis={'categoryorder':'total descending'})
    return fig

@app.callback(
    Output('sorted-graph', 'figure'),
    Input('datetime_RangeSlider', 'value'),
    Input('category-selector', 'value'),
    Input('points-selector', 'value')
    )
def update_figure2(date_range, category_value, points_selector):
    graph2_df = filter_date(date_range)
    graph2_df = graph2_df[graph2_df['category'] == category_value]
    if category_value == "Points":
        graph2_df = graph2_df[graph2_df['points'].isin(points_selector)]
        graph2_df = graph2_df.groupby(by=["name", "points"], as_index=False)['date'].count()
        fig2 = px.histogram(
            data_frame=graph2_df,
            x="name",
            y="date",
            color="points"
    )
    else:
        graph2_df = graph2_df.groupby(by=["name"], as_index=False)['date'].count()
        fig2 = px.histogram(
            data_frame=graph2_df,
            x="name",
            y="date"
        )
    fig2.update_layout(height=500, xaxis={'categoryorder':'total descending'})
    return fig2

def filter_date(date_range):
    now = datetime.datetime.now()
    small, big = date_range
    graph_df = df[now - df['date'] <= datetime.timedelta(days=30*big)] # type: ignore
    graph_df = graph_df[now - graph_df['date'] >= datetime.timedelta(days=30*small)]
    return graph_df


if __name__ == "__main__":
    app.run_server(debug=True)
