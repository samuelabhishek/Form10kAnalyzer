from Form10k import Form10kAnalyzer, Form10kExtractor, clean_text
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy


def main():


    # Get Data


    Tickerdf = pd.read_csv("./src/files/secwiki_tickers.csv")
    Tickers = Tickerdf.loc[:,'Ticker']
    Names = Tickerdf.loc[:,'Name']


    # Streamlit App


    st.title("Market Intelligence")
     
    st.text("Analyze Risk Factors and other Key textual information from Form-10k data!")

    company = st.sidebar.selectbox("Company", list(Names), index=2007, help = 'select the company who\'s 10k report you want to extract')
    
    section = st.sidebar.selectbox("Section", ['Risk Factors'], index = 0, help = 'select the section that you want to extract from he 10k report')

    st.header(company)

    st.subheader(section)


    # Do Analysis


    myform = Form10kExtractor(download_path = r"documentRepo", company = company, section = section ,is_ticker = False)
    myformanalysis = Form10kAnalyzer(myform)

    headerstext = [clean_text(header.text) if type(header) is spacy.tokens.span.Span else clean_text(header) for header in myform.subsection_headers_]
    contentstext = [clean_text(content.text) if type(content) is spacy.tokens.span.Span else clean_text(content) for content in myform.subsection_contents_]
    subsection_sentiment_df = pd.DataFrame(zip(headerstext, contentstext, myformanalysis.subsections_sentiment_polarity_, myformanalysis.subsections_sentiment_subjectivity_), 
    columns = ['Risk Factor - Header', 'Risk Factor - Detailed', 'Sentiment - Polarity', 'Sentimeny - Subjectivity'])

    section_entities_df = get_entites_df(myformanalysis)


    # Stramlit App


    st.image(get_section_wordcloud(myform, myformanalysis))

    st.dataframe(subsection_sentiment_df)

    st.subheader("Entities found in section")

    st.dataframe(section_entities_df)


def get_entites_df(myformanalysis):
    entities_label_df = pd.DataFrame(zip(myformanalysis.entities_text_,myformanalysis.entities_label_), columns=['Entity','Label'])
    entities_label_count_df = pd.DataFrame(entities_label_df.value_counts(), columns=['# of Occurances']).reset_index()
    return entities_label_count_df

def get_section_wordcloud(myform, myformanalysis):
    wordcloud = WordCloud(width = 1200, height = 600, max_font_size=70, prefer_horizontal = 1, stopwords = myformanalysis.entities_text_ + list(myform.nlp.Defaults.stop_words)).generate_from_text(myform.text_section_)
    return wordcloud.to_image()
    




if __name__ == '__main__':
    
    main()
    print("Program successfull!")