def main():

    import streamlit as st
    import pandas as pd
    import form10k
    import plotly.express as px
    import datetime as dt
    import os
    import joblib


    # Get Ticker Data


    Tickerdf = pd.read_csv("./src/files/secwiki_tickers.csv")
    Tickers = Tickerdf.loc[:,'Ticker']
    Names = Tickerdf.loc[:,'Name']


    # Design Streamlit App

    st.set_page_config(page_title= 'Market Intelligence', layout= 'wide')    

    mybar = st.progress(0)

    st.title("Market Intelligence")
     
    st.text("Analyze Risk Factors and other Key textual information from Form-10k data!")

    company = st.sidebar.selectbox("Company", list(Names), index=2007, help = 'select the company who\'s 10k report you want to extract')
    
    section = st.sidebar.selectbox("Section", ["Business", "Risk Factors", "Unresolved Staff Comments", "Properties", "Legal Proceedings" ,"Management’s Discussion and Analysis of Financial Condition and Results of Operations", "Quantitative and Qualitative Disclosures About Market Risk" , "Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
    "Controls and Procedures", "Form 10-K Summary"], index = 0, help = 'select the section that you want to extract from he 10k report')

    st.header(company)

    st.subheader(section)

    mybar.progress(10)


    # Perform 10-K Analysis

    ticker = Tickerdf.loc[Tickerdf['Name']== company, 'Ticker'].values[0]



    myform = form10k.Form10kExtractor(download_path = r"documentRepo", company = company, section = section ,is_ticker = False)

    mybar.progress(30)

    myformanalysis = form10k.Form10kAnalyzer(myform)

    mybar.progress(75)


    # Get Stock Data

    stock_df = form10k.get_stock_data(date = myform.date_doc_, source = 'yahoo', ticker = myform.ticker)

    fig = px.line(stock_df, x = stock_df.index, y = 'Adj Close')

    fig.add_vline(x=dt.datetime.strptime(myform.date_doc_, r'%m/%d/%y').timestamp() * 1000, line_width = 3, line_color = 'black', annotation_text = 'Report release date')

    mybar.progress(85)

    # Design Stramlit App


    st.image(myformanalysis.get_section_wordcloud(myform),  width=1250)

    st.subheader('Impact of the report on stock price')  

    st.plotly_chart(fig, use_container_width= True)

    st.subheader('Sentiment Analysis')  

    st.dataframe(myformanalysis.subsection_sentiment_df, width= 1250)

    st.subheader("Named Entities extracted")

    st.dataframe(myformanalysis.section_entities_df, width = 1250)

    mybar.progress(100)

    mybar.empty()

if __name__ == '__main__':
    
    main()
    print("Program successfull!")