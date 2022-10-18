from ast import main
from datetime import date, datetime,timedelta
import streamlit as st
import pandas as pd
import numpy as np
from vnstock import *
import altair as alt
import plotly.graph_objects as go
import urllib.request
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import time

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

def rangePrice():
    pass

@st.cache
def expensive(a, b, name):
    time.sleep(2)
    df =  stock_intraday_data(symbol=str(name),page_num=0,page_size=10000)
    return df


def main(name):
    button = st.button("Enter")
    if button or st.session_state.submitted:
            st.session_state.submitted = True
            # https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
            # https://plotly.com/python/candlestick-charts/
            #print(len(str(button))
            #print(len(name))
            try:
                if button == True and len(name) == 0:
                    st.warning('Bạn chưa nhập tên cổ phiếu')
                    return 
                df = ticker_overview(name)
                
                # st.info(ticker)
                # st.info(company_name)
                # st.info(company_short_name)
                #st.write(df.iloc[0]['shortName'])
                if 'status' in df.columns:   
                    raise ValueError('A very specific bad thing happened.')
            except: 
                st.markdown(f'<h1 style="color:#ff334b;font-size:24px;">{"Name Error!!!"}</h1>', unsafe_allow_html=True)
                st.info('Kiểm tra xem bạn đã nhập đúng tên cổ phiếu chưa ')
                return

            
        
            #Sidebar options
            ticker = st.sidebar.selectbox('Options Phan tich',['Investment','Company Overview','Market','About me'])
            
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
                if "intra" not in st.session_state:
                    st.session_state.intra = False

                if st.sidebar.button("Intraday market") or st.session_state.intra:
                    st.session_state.intra = True
                    colms1, colms2 = st.columns(2)

                    with colms1:
                        a = 2
                        b = 3
                        with st.spinner("Loading. Please waiting"):
                            res = expensive(a, b, name)
                        res = res[['price','volume','cp','a','time']]
                        res = res.rename(columns={"cp": "+/-", "a": "Types of trade"})
                        st.write(res)
                    
                    text = """
                    ## Intraday Price
                    **price**:  giá  
                    
                    **volume**: khối lượng giao dich

                    **"+/-"**: Mức tăng giảm của Giá khớp trung bình so với giá tham chiếu trong ngày.

                    **types of trade**: "Diễn biến khớp lệnh realtime.
                        * Phân loại nhà đầu tư cho lệnh:
                        * CM: Cá mập (>1 tỷ/lệnh);
                        * SG:Sói già (200tr-1tỷ/lệnh) 
                        * CN: Cừu non (<200tr/lệnh). 
                        * Mua chủ động (hay Buy Up) là khi NĐT thực hiện mua thẳng cổ phiếu tại giá dư bán gần nhất để có thể khớp luôn. 
                        * Bán chủ động (hay Sell Down) là khi NĐT thực hiện bán thẳng cổ phiếu tại giá dư mua gần nhất để có thể khớp ngay.
                    """     

                   
                    #print(st.session_state.Description)
                    if "Description" not in st.session_state:
                        st.session_state.Description = False
                    if st.button("Description"):
                        with colms2:             
                            st.markdown(text)
                    else: 
                        with colms2:             
                            st.markdown("")
            
                if 'id' not in st.session_state.keys():
                    st.session_state['id']='1'
                if 'name' not in st.session_state.keys():
                    st.session_state['name'] = 'name'

                cols = st.columns(4)
                #cols[0].code(st.session_state['id'], language="markdown")
                #cols[1].code(st.session_state['name'], language="markdown")
                #if cols[2].button('Clear'):
                    # st.session_state['id']=''
                    # st.session_state['name']=''
                    # st.experimental_rerun()

                # if "insert" not in st.session_state:
                #         st.session_state.insert = False

                # if cols[3].button("Insert") or st.session_state.insert:
                #     st.session_state.insert = True
                #     text = st.text_input("Which Ticker you want?","s")
                #     #cols[0].code(, language="markdown")
                #     if st.button("enter"):
                #         st.session_state.insert = False
                #         #st.write(text)
                #         #st.session_state['id']= text
                #         #if 'id' not in st.session_state.keys():
                #         st.session_state['id']= text
                #         #st.experimental_rerun()
                     
                #     cols[0].code(st.session_state['id'], language="markdown")
               
                if st.sidebar.button("Watch price days before"):       
                    days_to_plot = st.sidebar.slider('Days to Plot', 
                    min_value = 1,
                    max_value = 365,
                    value = 120,)
                    d = datetime.today() - timedelta(days=days_to_plot+1)
                    date_time = d.strftime("%m/%d/%Y, %H:%M:%S")
                    
                    st.header("Bảng giá từ {} -> {}".format((datetime.today() - timedelta(days=days_to_plot)).strftime("%d/%m/%Y"), str((datetime.now()).strftime("%d/%m/%Y"))))
                    df = stock_historical_data(name, d.strftime("%Y-%m-%d"), (datetime.now()).strftime("%Y-%m-%d"))
                    st.write(df)
                    # 
                    max_close = df.xs(key='Close',axis=1).max()
                    max_close = df.loc[df['Close'] == max_close].drop_duplicates(subset=['Close'])['TradingDate'].item()
                    text_close = "Ngày có giá trị cổ phiếu đóng cửa lớn nhất là: {}".format(max_close.strftime("%d-%m-%Y"))
                    st.info(text_close)

                    # max open price
                    max_open = df.xs(key='Open',axis=1).max()
                    max_open = df.loc[df['Open'] == max_open].drop_duplicates(subset=['Open'])['TradingDate'].item()
                    text_close = "Ngày có giá trị cổ phiếu mở cửa lớn nhất là: {}".format(max_open.strftime("%d-%m-%Y"))
                    st.info(text_close)

                    try: 
                        max_high = df.xs(key='High',axis=1).max()
                        #st.write((df[df['High'] == max_high]).drop_duplicates().item())
                        max_high =  df.loc[df['High'] == max_high].drop_duplicates(subset=['High'])['TradingDate'].item()
                        text_close = "Ngày có giá trị cổ phiếu lớn nhất là: {}".format(max_high.strftime("%d-%m-%Y"))
                        st.info(text_close)
                    except Exception as e:
                        data = df.loc[df['High'] == max_high].drop_duplicates(subset=['High'])['TradingDate']
                        st.write(data)
                    #print(e)
                    
                    options = st.sidebar.multiselect(
                    'chọn giá trị cổ phiếu theo ngày',
                    ['Open','High', 'Low','Close'])  
                    #st.sidebar.write('You selected:', options)    
                    #st.write(type(options))    
                    if options:
                        min_max = st.sidebar.radio("Miền giá trị của giá ",('Max', 'Min','both'))
                        st.sidebar.write('You selected', min_max)
                        
                    # tỉ suất lợi nhuận 
                    # (giá đóng cửa hiện tại – giá đóng cửa ngày trước đó)/giá đóng cửa ngày trước đó 
                    value_banks = pd.DataFrame()
                    #for name in list_banks:
                    value_banks[name+' value_bank'] = df['Close'].pct_change()
                    value_banks['Day'] = df['TradingDate']
                    value_banks.dropna(inplace= True)
                # #
               

                # st.write(plt.figure(figsize=(15,5))) # Tùy chỉnh kích thước biểu đồ
                # st.write(sns.distplot(value_banks.loc['VIB Value_bank'],color='green',bins=100))
                
                #group_labels = value_banks.iloc[:, 1].values.tolist()
                #fig = ff.create_distplot(value_banks.iloc[:, 0].values.tolist(), group_labels, bin_size=100)
                # Add histogram data
                    x1 = np.random.randn(200) - 2
                    

                    # Group data together
                    hist_data = [x1]
                    #group_labels = ['Group 1', 'Group 2', 'Group 3']

                    # Create distplot with custom bin_size
                    fig = ff.create_distplot(
                            [value_banks.iloc[:, 0].values],[str(name)],bin_size=[.01])

                    # Plot!
                    # config = dict({'scrollZoom': True})
                    # fig.update(config=config)
                    #fig.update(layout_xaxis_rangeslider_visible=False)
                    fig.layout.xaxis.fixedrange = True
                    fig.layout.yaxis.fixedrange = True 
                    config = {
                    'displayModeBar': False,
                    'scrollZoom': True
                    }
                    st.plotly_chart(fig, use_container_width=True,config=config)

                    weekno = datetime.today().weekday()
                    
                    if st.sidebar.button("xem dữ liệu hôm nay"):
                        if weekno < 5: 
                            try: 
                                with st.spinner('Wait for it...'):
                                    intraday_data =  stock_intraday_data(symbol=str(name),page_num=0,page_size=10000)
                                    st.write(intraday_data[['price','volume','a','time']])
                                st.success('Done!')
                            except Exception as e:
                                st.warning("giá không được cập nhập ")
                        else:
                            st.info("Hôm nay là ngày cuối tuần nên không có dữ liệu gì cả ")
                
                
                    
               
                #config = dict({'scrollZoom':False})

                # fig.add_trace(
                #     go.Scatter(
                #         x=[1, 2, 3],
                #         y=[1, 3, 1]))
                # fig.layout.xaxis.fixedrange = True
                # fig.layout.yaxis.fixedrange = True        
                # st.plotly_chart(fig, use_container_width=True)#**{'config': config})
                # st.write(fig.update(config=config))

                #  # Create distplot with custom bin_size
                # fig = ff.create_distplot(
                #         hist_data, group_labels, bin_size=[.1])
                #st.plotly_chart(fig, use_container_width=True)
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
                
                #df = industry_analysis(str(name))
                #st.write(df)
                colms = st.columns((1, 2, 2, 1, 1))
                # overview of rating for companies at the same industry with the desired stock symbol
                #fields = ["No", 'ten cong ty', 'ID', 'verified', "action"]

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
                data_name_df = listing_companies()
                table = data_name_df[data_name_df['ticker'] == name].values.tolist()

                text = """
                ### **Ticker**: {} \n
                ### **Company name**: {}\n
                ### **company short name** :{}
                """.format(table[0][0],table[0][2],table[0][3])
                st.markdown(text)
                st.info("DEVELOPING")
                st.text("Watch more company overview and Market")
        
        
        


if __name__ == "__main__":
    #_max_width_()
    # https://blog.devgenius.io/how-to-build-a-multi-language-dashboard-with-streamlit-9bc087dd4243 
    st.set_page_config(layout='wide')
    st.title('Tư vấn chứng khoán')
    name = st.text_input("Which Ticker you want?","VIB")
    main(name)

   