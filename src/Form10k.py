print("Importing Dependancies")

import pandas as pd
import numpy as np
import spacy
import sec_edgar_downloader
import bs4
from spacy import matcher
from bs4 import BeautifulSoup
import re
from spacy.matcher import PhraseMatcher
from spacytextblob.spacytextblob import SpacyTextBlob
from collections import Counter
import os
import streamlit as st

print("Completed Imports")


class Form10kExtractor:

    
    def __init__ (self, download_path, company, section, is_ticker = None):
        self.is_ticker = is_ticker if is_ticker is not None else False
        self.company = company if self.is_ticker is False else self.get_company()
        self.ticker = company if self.is_ticker is True else self.get_ticker()
        self.download_path = download_path
        self.section = section
        self.nlp = spacy.load("en_core_web_lg")
        self.nlp.add_pipe('spacytextblob')
        print("Extracting Report")
        try:
            self.get_report()
        except:
            print("Error getting report")
        print("Extracting Section")
        try:
            self.get_section()
            print("sections extracted!")
        except:
            print("Error getting section")
        try:
            self.get_subsections()
            print("subsections extracted!")
        except:
            print("error getting subsections")


    
    def get_ticker(self):
        Tickerdf = pd.read_csv("./src/files/secwiki_tickers.csv")
        Tickers = Tickerdf.loc[:,'Ticker']
        Names = Tickerdf.loc[:,'Name']
        TickerDict = {}
        for ticker, name in list(zip(Tickers, Names)):
            TickerDict[name] = ticker
        ticker = TickerDict[self.company]
        return ticker

    
    
    def get_company(self):
        Tickerdf = pd.read_csv("./src/files/secwiki_tickers.csv")
        Tickers = Tickerdf.loc[:,'Ticker']
        Names = Tickerdf.loc[:,'Name']
        TickerDict = {}
        for ticker, name in list(zip(Tickers, Names)):
            TickerDict[ticker] = name
        name = TickerDict[self.ticker]
        return name


    
    def get_report(self):
        dl = sec_edgar_downloader.Downloader(self.download_path)
        dl.get("10-K", self.ticker, amount=1)
        ReportNumber = os.listdir(f"./{self.download_path}/sec-edgar-filings/{self.ticker}/10-K")

        f = open(f"./{self.download_path}/sec-edgar-filings/{self.ticker}/10-K/{ReportNumber[0]}/filing-details.html", 'r', encoding = 'utf-8')
        HtmlDoc = f.read()
        SoupDoc = BeautifulSoup(HtmlDoc, 'html.parser')
        TextDoc = str(SoupDoc.get_text())
        self.soup_doc_ = SoupDoc
        self.html_doc_ = HtmlDoc
        self.text_doc_ = TextDoc


    
    def get_section(self):

        ## Working on the Table of Contents to pick up the IDs of the section to be extracted

        StartLink = self.soup_doc_.find_all('a', string = re.compile(self.section))[0]['href']
        StartSectionID = StartLink[StartLink.rfind('/')+2:]
        Thresh = 0
        for link in self.soup_doc_.find_all('a'):
            if link['href'] != StartLink and Thresh == 0:
                continue
            if link['href'] == StartLink:
                Thresh = 1
            if link['href'] != StartLink and Thresh == 1:
                EndLink = link['href']
                break
        EndSectionID = EndLink[EndLink.rfind('/')+2:]

        ## Navigating to required section in the report using the IDs obtained. 
        ## Aquiring anchor points for extraction

        StartSectionTag = str(self.soup_doc_.find(id=StartSectionID))
        EndSectionTag = str(self.soup_doc_.find(id=EndSectionID))
        StartSectionIndex = re.search(str(StartSectionTag), str(self.html_doc_)).end()
        EndSectionIndex = re.search(str(EndSectionTag), str(self.html_doc_)).start()

        ## Exctracting Section

        self.html_section_ = self.html_doc_[StartSectionIndex:EndSectionIndex]
        self.soup_section_ = BeautifulSoup(self.html_section_, 'html.parser')
        self.text_section_ = str(self.soup_section_.get_text())


    
    def get_subsections(self):

        try:
            self.get_subsection_headers()
            self.get_bold_subsections()
            
        except:
            print("Unable to indentify individual headers. Extracting each paragraph as a subsection instead")
            self.get_div_subsections()

            
        # Going back to the extracted text to pick up sebsections for each header


    
    def get_subsection_headers(self):

        # A reliable way to get the risk headings but some of the section text is missing

        ListSubSections_ForHeaders = [i.get_text() for i in self.soup_section_.find_all('p', style = re.compile(r"font-weight:bold"))]
        if ListSubSections_ForHeaders is None: raise ValueError("SubSection headings aren't distinctly formatted")
        ListSubSection_ForHeaders_SpacyDocs = list(self.nlp.pipe(ListSubSections_ForHeaders))
        self.subsection_headers_ = [list(doc.sents)[0] for doc in ListSubSection_ForHeaders_SpacyDocs]


    
    def get_bold_subsections(self):

        Section_SpacyDoc = self.nlp(self.text_section_)
        matcher = PhraseMatcher(self.nlp.vocab)
        HeaderPatterns = [self.nlp.make_doc(text.text) for text in self.subsection_headers_]
        matcher.add("10KSection", HeaderPatterns)
        matches = matcher(Section_SpacyDoc)
        a, b, prevEnd = matches[0]
        self.subsection_contents_ = []
        self.subsection_count_ = len(matches)
        for _, start, end in matches[1:]:
            if (start - prevEnd) > 5:
                self.subsection_contents_.append(Section_SpacyDoc[prevEnd:start])
            else:
                self.subsection_contents_.append(Section_SpacyDoc[0:0])
            prevEnd = end
        self.subsection_contents_.append(Section_SpacyDoc[prevEnd:])

        self.subsections_ = list(zip(self.subsection_headers_, self.subsection_contents_))


    
    def get_div_subsections(self):
        self.subsection_contents_ = [div.get_text() for div in self.soup_section_.find_all('div') if len(div.get_text()) > 50]
        self.subsection_headers_ = ['N/A' for i in self.subsection_contents_]
        self.subsections_ = list(zip(self.subsection_headers_, self.subsection_contents_))


class Form10kAnalyzer:

    
    def __init__(self, form):
        try:
            self.get_entities(form)
            print("Entities extracted!")
        except:
            print("Error getting entities")
        try:
            self.get_sentiment(form)
            print("Sentiment extracted")
        except:
            print("Error getting sentiment")

    
    def get_entities(self, form):
        self.Section_SpacyDoc = form.nlp(form.text_section_)
        self.entities_text_ = [ent.text for ent in self.Section_SpacyDoc.ents]
        self.entities_label_ = [ent.label_ for ent in self.Section_SpacyDoc.ents]

    
    
    def get_sentiment(self, form):
        self.subsections_sentiment_polarity_ = [form.nlp(str(subsection))._.polarity for subsection in form.subsection_contents_]
        self.subsections_sentiment_subjectivity_ = [form.nlp(str(subsection))._.subjectivity for subsection in form.subsection_contents_]



def clean_text(text):
    text = str(text)
    text = (" ").join(text.split()).replace(u"\u2022", "")
    return(text)