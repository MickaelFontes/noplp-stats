"""Statistics page for singer specific stats."""
import dash
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import filter_date, filter_singer, get_date_range_object, get_singers

dash.register_page(__name__, path="/singer")

layout = html.Div(
    [
        html.H4("Singer's songs statistsics"),
        dcc.Dropdown(
            id="dropdown-singer",
            value="Céline Dion",
            options=[{"label": i, "value": i} for i in get_singers()],
        ),
        get_date_range_object(),
        dcc.Graph(id="categories-graph-singer"),
        html.H4("Singer occurence in time"),
        dcc.Graph(id="timeline-graph-singer"),
    ]
)


@callback(
    Output("categories-graph-singer", "figure"),
    Input("dropdown-singer", "value"),
    Input("year_slider", "value"),
)
def update_figure(song_name, date_range):
    """Update the graph with the singer's songs stats.

    Args:
        song_name (str): Song title.
        date_range (int): date range in Unix format.

    Returns:
        figure: songs graph for selected singer.
    """
    graph_df = filter_date(date_range)
    graph_df = graph_df[graph_df["singer"] == song_name]
    graph_df = graph_df.astype({"points": "string"})
    graph_df["category"] = graph_df.category + " " + graph_df.points
    graph_df["category"] = graph_df["category"].str.replace(" -1", "")
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)["date"].count()
    fig = px.histogram(data_frame=graph_df, x="name", y="date", color="category")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    return fig


@callback(Output("timeline-graph-singer", "figure"), Input("dropdown-singer", "value"))
def update_timeline(singer_name):
    """Update the timeline graph of the singer

    Args:
        singer_name (str): Singer's name.

    Returns:
        fig: Graph with the songs occurences.
    """
    graph_df = filter_singer(singer_name)
    graph_df.insert(5, "nb", 1)
    # fix view VS copy
    graph_df = graph_df.astype({"points": "string"})
    graph_df["category"] = graph_df.points + " " + graph_df.category
    graph_df["category"] = graph_df["category"].str.replace("-1 ", "")
    fig = px.scatter(
        graph_df,
        x=graph_df["date"],
        y=graph_df["category"],
        color=graph_df["name"],
        symbol=graph_df["name"],
        hover_data={
            "date": "|%B %d, %Y",
            "nb": False,
            "points": False,
            "category": True,
        },
    )
    # fig.update_traces(width=0.2)
    fig.update_layout(
        height=500,
        yaxis={
            "categoryorder": "array",
            "categoryarray": [
                "10 Points",
                "20 Points",
                "30 Points",
                "40 Points",
                "50 Points",
                "Même chanson",
            ],
        },
    )
    return fig
