import datetime
import time

from dash import dcc, html
import pandas as pd


df = pd.read_csv('data/db_test.csv', index_col=None)
df['date'] = pd.to_datetime(df['date'])

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks():
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    result = {}
    for date in daterange_marks:
        result[unixTimeMillis(date)] = str(date.strftime('%Y'))
    return result

def filter_date(date_range):
    small, big = date_range
    graph_df = df[df['date'] <= unixToDatetime(big)] # type: ignore
    graph_df = graph_df[graph_df['date'] >= unixToDatetime(small)]
    return graph_df

daterange = pd.date_range(start=df['date'].min().date(),
                          end=df['date'].max().date() + datetime.timedelta(days=31),
                          freq='MS')

daterange_marks = pd.date_range(start=df['date'].min().date(),
                                end=df['date'].max().date(),
                                freq='AS')

def getTimeLimits():
    begin = unixTimeMillis(df['date'].min().date().replace(day=1))
    end = unixTimeMillis(df['date'].max().date() + datetime.timedelta(days=31))
    return begin, end

def getCategoryOpts():
    return df['category'].unique()

def getPointsOpts():
    return sorted(df['points'].unique())[1:]

def getDateRangeObject():
    begin, end = getTimeLimits()
    return html.Div(
        [
            html.Label('From 2008 to 2023', id='time-range-label'),
            dcc.RangeSlider(
                id='year_slider',
                min=begin,
                max=end,
                value=[begin, end],
                marks=getMarks()
            ),
        ],
        style={'margin-top': '20'}
    )

def getSongs():
    return df['name'].unique()

def filter_song(song_name):
    return df[df['name'] == song_name]
