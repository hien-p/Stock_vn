import streamlit as st
from vnstock import *
import numpy as np
import pandas as pd 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import requests
from io import BytesIO 




def table_aggrid(df,text):
    # Using Aggrid for custom table
    if df.empty:
        pass
    else:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()
        
        available_themes = ["streamlit","alpine", "material","balham"]
        with st.expander("TABLE"):
        #st.write("check out this demo [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)".upper())
        #st.write("[Documentation](https://pablocfonseca-streamlit-aggrid-examples-example-jyosi3.streamlitapp.com)".upper())
            selected_theme = st.selectbox(text, available_themes)
            response = AgGrid(
                df,
                editable=True,
                gridOptions=gridOptions,
                data_return_mode="filtered_and_sorted", 
                update_mode="no_update",
                fit_columns_on_grid_load=True,
                theme=str(selected_theme)
            )

def financial_ratio_s(symbol_ls, industry_comparison, frequency, start_year): 
    """
    This function returns the balance sheet of a stock symbol by a Quarterly or Yearly range.
    """
    global timeline
    if frequency == 'Yearly':
        timeline = str(start_year) + '_5'
    elif frequency == 'Quarterly':
        timeline = str(start_year) + '_4'

    for i in range(len(symbol_ls)):
        if i == 0:
            company_join = '&CompareToCompanies={}'.format(symbol_ls[i])
            url = 'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={}&CompareToIndustry={}{}&Frequency={}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom=2020'.format(symbol_ls[i], industry_comparison, '', frequency, timeline)
        elif i > 0:
            company_join = '&'.join([company_join, 'CompareToCompanies={}'.format(symbol_ls[i])])
            url = 'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={}&CompareToIndustry={}{}&Frequency={}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom={start_year}_5'.format(symbol_ls[i], industry_comparison, company_join, frequency, timeline,start_year=start_year)
    print(url)
    headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'DNT': '1',
            'sec-ch-ua-mobile': '?0',
            'X-Fiin-Key': 'KEY',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Fiin-User-ID': 'ID',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64conent; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'X-Fiin-Seed': 'SEED',
            'sec-ch-ua-platform': 'Windows',
            'Origin': 'https://iboard.ssi.com.vn',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://iboard.ssi.com.vn/',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
            }
    r = requests.get(url, headers=headers)
    df = pd.read_excel(BytesIO(r.content), skiprows=7, header=0,index_col=0).fillna(0)
    return df.T , str(url)



st.header("Company Overviews")
with st.expander("How it works"):
    st.markdown("You can watch more detaisl about company")


#st.write(st.session_state["multiselect"])
if "Baocao" not in st.session_state:
    st.session_state.Baocao = False
name = st.sidebar.selectbox("TICKER",st.session_state["multiselect"])
options = st.sidebar.selectbox('TYPE REPORT',['Financial_report','Income Statement','Cashflow'])

data = ['BalanceSheet','IncomeStatement','cashflow']
list_baocao = dict(zip(['Financial_report','Income Statement','Cashflow'],data))
if str(options) in list_baocao or st.session_state.Baocao:
    st.session_state.Baocao = True
    if options == 'Financial_report':
        st.info("Bảng cân đối kế toán theo quý hoặc năm")
    elif options == 'Income Statement':
        st.info("Bảng kết quả kinh doanh")
    else:
            st.info("báo cáo dòng tiền (cashflow)")
    
option = st.sidebar.selectbox('REPORT RANGE',('Yearly','Quarterly'))


try:
    df = financial_report(symbol=str(name), report_type=list_baocao.get(options), frequency=option)
except: 
    df = pd.DataFrame()
    st.info("Sorry to inform you that this ticker have some problem with your options {0}".format(list_baocao.get(options)).upper())
table_aggrid(df, "Theme for table 1".upper())


st.info("Tỷ lệ dòng tiền".upper())
try:
    df = financial_flow(symbol=str(name), report_type=(list_baocao.get(options)).lower(), report_range=option.lower())
    df = df[df.columns[df.isnull().mean() < 0.5]]
except: 
    df = pd.DataFrame()
    st.info("Sorry to inform you that this ticker have some problem with your options {0}".format(list_baocao.get(options)).upper())

table_aggrid(df, "Theme for table financial flow".upper())



    
## Đánh giá chung
st.info("Đánh giá chung".upper())


try:
    df = general_rating(str(name))
except: 
    df = pd.DataFrame()
    st.info("Sorry to inform you that this ticker have some problem with your options {0}".format(list_baocao.get(options)).upper())
license_key = "For_Trialing_ag-Grid_Only-Not_For_Real_Development_Or_Production_Projects-Valid_Until-18_March_2021_[v2]_MTYxNjAyNTYwMDAwMA==948d8f51e73a17b9d78e03e12b9bf934"
with st.expander("TABLE"):
    AgGrid(df, key='grid1', enable_enterprise_modules=True, license_key=license_key)
    
    
# https://stackoverflow.com/questions/71193085/creating-nested-columns-in-python-dataframe 
# financial_health_rating 
# try:
#     df = financial_health_rating(str(name))
# except: 
#     df = pd.DataFrame()
#     st.info("Sorry to inform you that this ticker have some problem with your options {0}".format(list_baocao.get(options)).upper())
# license_key = "For_Trialing_ag-Grid_Only-Not_For_Real_Development_Or_Production_Projects-Valid_Until-18_March_2021_[v2]_MTYxNjAyNTYwMDAwMA==948d8f51e73a17b9d78e03e12b9bf934"
# with st.expander("TABLE"):
#     AgGrid(df, key='grid1', enable_enterprise_modules=True, license_key=license_key)

    
    


st.markdown("---")
st.info("Các chỉ số tài chính".upper())
with st.expander("TABLE + DOWNLOAD DATA"):
    year_options = st.selectbox(
    'Choose years you want',
    ('2013', '2014', '2015','2016','2017','2018','2019','2020','2021')) 
    st.write()
    st.write(option)
    st.write(year_options)
    
    df,  url = financial_ratio_s(symbol_ls=st.session_state["multiselect"], industry_comparison='true', frequency= 'Yearly', start_year=year_options)
    # Financial Ratio function
    st.write(df)
        
    #     try:
    #     df, url_link = financial_ratio(symbol_ls=st.session_state["multiselect"], industry_comparison='true', frequency= option, start_year=year_options)
    #     except: 
    #         df = pd.DataFrame()
    #         st.info("Sorry to inform you that this ticker have some problem with your options")
    #     if year_options:
    #     st.write(df)
    #     else:
    #         pass
    #     st.download_button(
    #     label="Download data",
    #     data=url_link)

