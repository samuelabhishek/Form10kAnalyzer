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
from collections import Counter

print("Completed Imports")


class Form10k:

    def __init__ (self, download_path, company, section, is_ticker = None):
        self.is_ticker = is_ticker if is_ticker is not None else False
        self.company = company
        self.ticker = company if self.is_ticker is True else self.get_ticker()
        self.download_path = download_path
        self.section = section
        print("Extracting Report")
        self.get_report()
        print("Extracting Section")
        self.get_section()
        print("Extracting Subsection Headers")
        self.get_subsection_headers()
        print("Extracting Subsections")
        self.get_subsections()


    def get_ticker(self):
        return "MSFT"

    def get_report(self):
        dl = sec_edgar_downloader.Downloader(self.download_path)
        dl.get("10-K", "MSFT", amount=1)

        f = open(f"{self.download_path}\\sec-edgar-filings\\{self.ticker}\\10-K\\0001564590-20-034944\\filing-details.html", 'r', encoding = 'utf-8')
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
        EndLink = [self.soup_doc_.find_all('a')[i+1]['href'] for i, link in enumerate(self.soup_doc_.find_all('a')) if link.string == self.section]
        EndSectionID = EndLink[0][EndLink[0].rfind('/')+2:]

        ## Navigating to required section in the report using the IDs obtained. 
        ## Aquiring anchor points for extraction

        StartSectionTag = str(self.soup_doc_.find(id=StartSectionID))
        EndSectionTag = str(self.soup_doc_.find(id=EndSectionID))
        StartSectionIndex = re.search(str(StartSectionTag), str(self.html_doc_)).end()
        EndSectionIndex = re.search(str(EndSectionTag), str(self.html_doc_)).start()

        ## Exctracting Section

        self.html_section_ = self.html_doc_[StartSectionIndex:EndSectionIndex]
        self.soup_section_ = BeautifulSoup(self.html_section_, 'html.parser')
        self.text_section_ = self.soup_section_.get_text()


    def get_subsection_headers(self):

        # A reliable way to get the risk headings but some of the section text is missing

        ListSubSections_ForHeaders = [i.get_text() for i in self.soup_section_.find_all('p', style = re.compile(r"font-weight:bold"))]
        self.nlp = spacy.load("en_core_web_lg")
        ListSubSection_ForHeaders_SpacyDocs = list(self.nlp.pipe(ListSubSections_ForHeaders))
        self.subsection_headers_ = [list(doc.sents)[0] for doc in ListSubSection_ForHeaders_SpacyDocs]


    def get_subsections(self):

        # Going back to the extracted text to pick up sebsections for each header

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

        self.subsections_ = list(zip(range(self.subsection_count_), self.subsection_headers_, self.subsection_contents_))


class Form10kAnalyzer:

    def __init__(self, form):
        self.get_entities(form)

    def get_entities(self, form):
        self.Section_SpacyDoc = form.nlp(form.text_section_)
        self.entities = self.Section_SpacyDoc.ents


def clean_text(text):
    text = str(text)
    text = (" ").join(text.split()).replace(u"\u2022", "")
    return(text)