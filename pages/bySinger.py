import dash
from dash import dcc, html, callback, Input, Output
import pandas as pd
import plotly.express as px

from pages.utils import (getDateRangeObject,
                    unixToDatetime,
                    getSingers,
                    filter_date,
                    filter_singer)

dash.register_page(__name__, path='/singer')

layout = html.Div([
    html.H4("Singer's songs statistsics"),
    dcc.Dropdown(
        id='dropdown-singer',
        value='Céline Dion',
        options=[{'label': i, 'value': i} for i in getSingers()]
    ),
    getDateRangeObject(),
    dcc.Graph(id="categories-graph-singer"),
    html.H4("Singer occurence in time"),
    dcc.Graph(id="timeline-graph-singer")
])

@callback(
    Output('categories-graph-singer', 'figure'),
    Input('dropdown-singer', 'value'),
    Input('year_slider', 'value'))
def update_figure(song_name, date_range):
    graph_df = filter_date(date_range)
    graph_df = graph_df[graph_df['singer'] == song_name]
    graph_df = graph_df.astype({'points':'string'})
    graph_df["category"] = graph_df.category + " " + graph_df.points
    graph_df["category"] = graph_df["category"].str.replace(" -1","")
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)['date'].count()
    fig = px.histogram(
        data_frame=graph_df,
        x="name",
        y="date",
        color="category"
    )
    fig.update_layout(height=500, xaxis={'categoryorder':'total descending'})
    return fig

@callback(
    Output('timeline-graph-singer', 'figure'),
    Input('dropdown-singer', 'value'))
def update_timeline(song_name):
    graph_df = filter_singer(song_name)
    graph_df.insert(5, "nb", 1)
    # fix view VS copy
    graph_df = graph_df.astype({'points':'string'})
    graph_df["category"] =  graph_df.points + " " + graph_df.category
    graph_df["category"] = graph_df["category"].str.replace("-1 ","")
    fig = px.scatter(graph_df,
                    x=graph_df["date"],
                    y=graph_df["category"],
                    color=graph_df["name"],
                    symbol=graph_df["name"],
                    hover_data={"date": "|%B %d, %Y",
                                "nb":False, 
                                "points":False,
                                "category": True})
    # fig.update_traces(width=0.2)
    fig.update_layout(height=500,
                      yaxis={'categoryorder':'array',
                             'categoryarray':['10 Points',
                                              '20 Points',
                                              '30 Points',
                                              '40 Points',
                                              '50 Points',
                                              'Même chanson']})
    return fig
