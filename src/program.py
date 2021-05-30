from Form10k import Form10kAnalyzer, Form10kExtractor, clean_text


def main():

    myform = Form10kExtractor(download_path = r"documentRepo", company = "Apple Inc.", section = 'Risk Factors' ,is_ticker= False)
    myformanalysis = Form10kAnalyzer(myform)
    print("Code run complete!")
    
    
if __name__ == '__main__':
    
    main()