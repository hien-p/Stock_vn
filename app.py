from datetime import datetime
from tkinter.filedialog import Open
from tokenize import Name
import streamlit as st
import pandas as pd
import numpy as np
from vnstock import *
import altair as alt
import plotly.graph_objects as go

st.title('APP Tu van Chung Khoan')

def get_candlestick_chart(df: pd.DataFrame):

    layout = go.Layout(
        title = 'TSLA Stock Price',
        xaxis = {'title': 'Date'},
        yaxis = {'title': 'Price'},
    ) 
    
    fig = go.Figure(
        layout=layout,
        data=[
            go.Candlestick(
                x = df['Date'],
                open = df['Open'], 
                high = df['High'],
                low = df['Low'],
                close = df['Close'],
                name = 'Candlestick chart'
            ),
        ]
    )
    
    fig.update_xaxes(rangebreaks = [{'bounds': ['sat', 'mon']}])
    
    return fig


def get_candlestick_plot(
        df: pd.DataFrame,
        ma1: int,
        ma2: int,
        ticker: str
):
    '''
    Create the candlestick chart with two moving avgs + a plot of the volume
    Parameters
    ----------
    df : pd.DataFrame
        The price dataframe
    ma1 : int
        The length of the first moving average (days)
    ma2 : int
        The length of the second moving average (days)
    ticker : str
        The ticker we are plotting (for the title).
    '''
    
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.1,
        subplot_titles = (f'{ticker} Stock Price', 'Volume Chart'),
        row_width = [0.3, 0.7]
    )
    
    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'], 
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            name = 'Candlestick chart'
        ),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Line(x = df['Date'], y = df[f'{ma1}_ma'], name = f'{ma1} SMA'),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Line(x = df['Date'], y = df[f'{ma2}_ma'], name = f'{ma2} SMA'),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Bar(x = df['Date'], y = df['Volume'], name = 'Volume'),
        row = 2,
        col = 1,
    )
    
    fig['layout']['xaxis2']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'Volume'
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    return fig


# text = st.text_input("Comments:", placeholder="Some long comment to edit")
# st.button("Submit", on_click=handler_func)
    
name = st.text_input("Which Ticker you want?","VIB")


# button1 = st.button('Check 1')

# if st.session_state.get('button') != True:

#     st.session_state['button'] = button1

# if st.session_state['button'] == True:

#     st.write("button1 is True")

#     if st.button('Check 2'):

#         st.write("Hello, it's working")

#         st.session_state['button'] = True

#         st.checkbox('Reload')

if st.button("Enter"):
     print("name ", name)
     st.write(name)
     # https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
     # https://plotly.com/python/candlestick-charts/
     df = stock_historical_data(name, "2022-01-01", (datetime.now()).strftime("%Y-%m-%d"))
     
     #Sidebar options
     ticker = st.sidebar.selectbox(
     'cac Options Phan tich', 
     options = ['Tu van Dau tu', 'Bai Bao lien Quan', 'Market']
     )
    
     days_to_plot = st.sidebar.slider(
     'Days to Plot', 
     min_value = 1,
     max_value = 300,
     value = 120,)

     fig = go.Figure(data=[go.Candlestick(x=df['TradingDate'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
     increasing_line_color= 'green', decreasing_line_color= 'red'           
     )])

     fig.update_layout(
     margin=dict(l=20, r=20, t=20, b=20),
     paper_bgcolor="LightSteelBlue",
     )   
     # if st.sidebar.button('Include Rangeslider'):
     fig.update_layout(xaxis_rangeslider_visible=False)
     st.plotly_chart(fig)
     st.header('Bang Gia tu 1/2022 -> {}'.format(str((datetime.now()).strftime("%m/%Y"))))
     st.write(df)
     
     
     #st.line_chart(df[['Close']])

     

#      ma1 = st.sidebar.number_input(
#      'Moving Average #1 Length',
#      value = 10,
#      min_value = 1,
#      max_value = 120,
#      step = 1,    
#      )
#      ma2 = st.sidebar.number_input(
#     'Moving Average #2 Length',
#      value = 20,
#      min_value = 1,
#      max_value = 120,
#      step = 1,    
#      )
#      ticker = name
#      st.plotly_chart(
#      get_candlestick_plot(df, ma1, ma2, ticker),
#      use_container_width = True,
#      )