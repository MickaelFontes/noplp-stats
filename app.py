from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from pages.utils import (getCategoryOpts,
                   getPointsOpts,
                   getDateRangeObject,
                   filter_date,
                   unixToDatetime)

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Popular songs of NOPLP'),
    dcc.Graph(id="graph"),
    getDateRangeObject(),
    html.H4('Most popular songs by category'),
    html.Div([dcc.Dropdown(
            options=getCategoryOpts(),
            value='Points',
            id='category-selector'
            )], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([dcc.Dropdown(
            options=getPointsOpts(),
            value=[50,40,30,20,10],
            id='points-selector',
            multi=True
            )], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    dcc.Graph(id="sorted-graph")
])

@app.callback(
    Output('graph', 'figure'),
    Input('year_slider', 'value')
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
    Input('year_slider', 'value'),
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

@app.callback(
    Output('time-range-label', 'children'),
    Input('year_slider', 'value'))
def _update_time_range_label(year_range):
    return (f'From {unixToDatetime(year_range[0]).date()} '
           f'to {unixToDatetime(year_range[1]).date()}')


if __name__ == "__main__":
    app.run_server(debug=True)
