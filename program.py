import src.Form10k


def main():

    myform = Form10kExtractor(download_path = r"\documentRepo", company = "Microsoft", section = 'Risk Factors' ,is_ticker= False)
    myformanalysis = Form10kAnalyzer(myform)
    print(myformanalysis.entities)
    
    
if __name__ == '__main__':
    
    main()