from ast import main
from datetime import datetime
from turtle import onclick
import streamlit as st
import pandas as pd
import numpy as np
from vnstock import *
import altair as alt
import plotly.graph_objects as go





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

def get_file_content_as_string(url: str):
    data = urllib.request.urlopen(url).read()
    return data.decode("utf-8")

def about():
    content = get_file_content_as_string(
        "https://raw.githubusercontent.com/hien-p/Stock_vn/main/README.md"
    )
    st.markdown(content)

def callback():
    st.session_state.button_clicked = True


if "submitted" not in st.session_state:
    st.session_state.submitted = False

def main(name):
    if st.button("Enter") or st.session_state.submitted:
            st.session_state.submitted = True
            # https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
            # https://plotly.com/python/candlestick-charts/
            df = stock_historical_data(name, "2022-01-01", (datetime.now()).strftime("%Y-%m-%d"))
            
            #Sidebar options
            ticker = st.sidebar.selectbox('Options Phan tich',['Tu van Dau tu','Company Overview','Market','About me'])
            # with st.form(key ='Form1'):
            #     with st.sidebar:
            #         user_word = st.sidebar.text_input("Enter a keyword", "habs")    
            #         select_language = st.sidebar.radio('Tweet language', ('All', 'English', 'French'))
            #         include_retweets = st.sidebar.checkbox('Include retweets in data')
            #         num_of_tweets = st.sidebar.number_input('Maximum number of tweets', 100)
            #         submitted1 = st.form_submit_button(label = 'Search Twitter 🔎')
            
            if ticker == 'About me':
                return about() 
            elif ticker == 'Company Overview':
                # symbol: name 
                #  report_range 
                option = st.selectbox('Report range: ',('Yearly','Quarterly'))
                st.write(option)
                df = financial_report(symbol=str(name), report_type='BalanceSheet', frequency=option)
                st.write(df)
            elif ticker == 'Market':
                # days_to_plot = st.sidebar.slider(
                # 'Days to Plot', 
                # min_value = 1,
                # max_value = 300,
                # value = 120,)

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
                
                
                st.line_chart(df[['Close']])
            else:
                st.header("Is developing")
                

if __name__ == "__main__":
    st.title('APP Tu van Chung Khoan')
    name = st.text_input("Which Ticker you want?","VIB")
    main(name)

   