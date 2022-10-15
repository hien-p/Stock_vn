from ast import main
from datetime import datetime,timedelta
import streamlit as st
import pandas as pd
import numpy as np
from vnstock import *
import altair as alt
import plotly.graph_objects as go
import urllib.request




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
    button = st.button("Enter")
    if button or st.session_state.submitted:
            st.session_state.submitted = True
            # https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
            # https://plotly.com/python/candlestick-charts/
            #print(len(str(button))
            print(len(name))
            try:
                if button == True and len(name) == 0:
                    st.warning('Bạn chưa nhập tên cổ phiếu')
                    return 
                df = ticker_overview(name)
                if 'status' in df.columns:   
                    raise ValueError('A very specific bad thing happened.')
            except: 
                st.markdown(f'<h1 style="color:#ff334b;font-size:24px;">{"Name Error!!!"}</h1>', unsafe_allow_html=True)
                st.info('Kiểm tra xem bạn đã nhập đúng tên cổ phiếu chưa ')
                return

        
            #Sidebar options
            ticker = st.sidebar.selectbox('Options Phan tich',['Tu van Dau tu','Company Overview','Market','About me'])
            
            if ticker == 'About me':
                return about() 
            elif ticker == 'Company Overview':

                if "Baocao" not in st.session_state:
                    st.session_state.Baocao = False
                
                options = st.sidebar.selectbox('Type Report',['Financial_report','Income Statement','cashflow'])
                st.write(options)
                data = ['BalanceSheet','IncomeStatement','cashflow']
                list_baocao = dict(zip(['Financial_report','Income Statement','cashflow'],data))
                if str(options) in list_baocao or st.session_state.Baocao:
                    st.session_state.Baocao = True
                    if options == 'Financial_report':
                        st.info("Bảng cân đối kế toán theo quý hoặc năm")
                    elif options == 'Income Statement':
                        st.info("Bảng kết quả kinh doanh")
                    else:
                            st.info("báo cáo dòng tiền (cashflow)")
                    option = st.selectbox('Report range: ',('Yearly','Quarterly'))
                    
                    df = financial_report(symbol=str(name), report_type=list_baocao.get(options), frequency=option)
                    st.write(df)
            
            

            elif ticker == 'Market':
                days_to_plot = st.sidebar.slider(
                'Days to Plot', 
                min_value = 1,
                max_value = 365,
                value = 120,)
                d = datetime.today() - timedelta(days=days_to_plot+1)
                date_time = d.strftime("%m/%d/%Y, %H:%M:%S")
                #st.header('Bang Gia tu {} -> {}'.format(str(d).strftime("%m/%d/%Y")),str((datetime.now()).strftime("%m/%Y")))
                st.header("Bảng giá từ {} -> {}".format((datetime.today() - timedelta(days=days_to_plot)).strftime("%d/%m/%Y"), str((datetime.now()).strftime("%d/%m/%Y"))))
                df = stock_historical_data(name, d.strftime("%Y-%m-%d"), (datetime.now()).strftime("%Y-%m-%d"))
                st.write(df)
                # 
                max_close = df.xs(key='Close',axis=1).max()
                max_close = df.loc[df['Close'] == max_close,'TradingDate'].item()
                text_close = "Ngày có giá trị cổ phiếu đóng cửa lớn nhất là: {}".format(max_close.strftime("%d-%m-%Y"))
                st.info(text_close)

                #st.write()
                # fig = go.Figure(data=[go.Candlestick(x=df['TradingDate'],
                #             open=df['Open'],
                #             high=df['High'],
                #             low=df['Low'],
                #             close=df['Close'],
                # increasing_line_color= 'green', decreasing_line_color= 'red'           
                # )])

                # fig.update_layout(
                # margin=dict(l=20, r=20, t=20, b=20),
                # paper_bgcolor="LightSteelBlue",
                # )   
                

                #fig.update_layout(xaxis_rangeslider_visible=False)
                #st.plotly_chart(fig)
                
                
                
                # st.line_chart(df[['Close']])
            else:

                df = industry_analysis(str(name))
                #st.write(df)
                colms = st.columns((1, 2, 2, 1, 1))
                # overview of rating for companies at the same industry with the desired stock symbol
                fields = ["No", 'ten cong ty', 'ID', 'verified', "action"]

                # for col, field_name in zip(colms, fields):
                #     # header
                #     col.write(field_name)

                # for x, email in enumerate(user_table['email']):
                #     col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
                #     col1.write(x)  # index
                #     col2.write(user_table['email'][x])  # email
                #     col3.write(user_table['uid'][x])  # unique ID
                #     col4.write(user_table['verified'][x])   # email status
                #     disable_status = user_table['disabled'][x]  # flexible type of button
                #     button_type = "Unblock" if disable_status else "Block"
                #     button_phold = col5.empty()  # create a placeholder
                #     do_action = button_phold.button(button_type, key=x)
                #     if do_action:
                #         pass # do some action with row's data
                #         button_phold.empty()  #  remove button
                st.info("DEVELOPING")
                st.text("Watch more company overview and Market")
        
        
        
                

if __name__ == "__main__":
    st.title('Tư vấn chứng khoán')
    name = st.text_input("Which Ticker you want?","VIB")
    main(name)

   