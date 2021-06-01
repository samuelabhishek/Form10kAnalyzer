from Form10k import Form10kAnalyzer, Form10kExtractor, clean_text
import streamlit as st
import pandas as pd


def main():
    # Streamlit App

    st.title("Market Intelligence")
     
    st.header("Analyze Risk Factors and other Key textual information from Form-10k data!")
    
    section = st.sidebar.selectbox("Section", ['Risk Factors', 'undefined'], index = 0, help = 'select the section that you want to extract from he 10k report')

    st.subheader(section)

    myform = Form10kExtractor(download_path = r"documentRepo", company = "Apple Inc.", section = section ,is_ticker = False)
    myformanalysis = Form10kAnalyzer(myform)

    subsection_sentiment_df = pd.DataFrame(zip(myform.subsections_, myformanalysis.subsections_sentiment_polarity_, myformanalysis.subsections_sentiment_subjectivity_), 
    columns = ['Risk Factor', 'Sentiment - Polarity', 'Sentimeny - Subjectivity'])

    section_entities_df = get_entites_df(myformanalysis)    

    st.dataframe(subsection_sentiment_df)

    st.subheader("Entities found in section")

    st.dataframe(section_entities_df)

def get_entites_df(myformanalysis):
    entities_label_df = pd.DataFrame(zip(myformanalysis.entities_text_,myformanalysis.entities_label_), columns=['Entity','Label'])
    entities_label_count_df = pd.DataFrame(entities_label_df.value_counts(), columns=['# of Occurances']).reset_index()
    return entities_label_count_df




if __name__ == '__main__':
    
    main()
    print("Program successfull!")