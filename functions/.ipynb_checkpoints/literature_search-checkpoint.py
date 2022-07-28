from Bio import Entrez
from pubchempy import get_compounds, Compound, get_synonyms

import os
import numpy as np
import pandas as pd

import time
import datetime
import itertools

class searchPubmed:
    """
    This class will perform a Pubmed search for checmical names with context words.
    
    You need to enter your email and ideally an API_KEY for EntrezPy to work. 

    More information here:
    
    https://www.ncbi.nlm.nih.gov/books/NBK25497/"""
    
    def __init__(self, email, drug_list, api_key=None):
        Entrez.email = email #"alexander.ernst@unibe.ch"
        Entrez.api_key = api_key #"05b06f8adeace65e91dca5a0fac7d6ba330a"
        self.Entrez = Entrez
        self.combinations = [""]
        self.drug_list = drug_list
        self.synonyms = [self.find_synonyms(compound_name) for compound_name in drug_list]

    def search_and_export(self, context_list, context_title, output_path=None, output_df=True):
        """Execute the search"""

        if context_list == []:
            table_name = "No_context"
        else:
            table_name = "_".join(context_list)

        df_search = self.search_all_compounds(context_list, self.drug_list, self.synonyms)
        df_compounds = pd.DataFrame(list(zip(self.drug_list, self.synonyms)),columns=["Compound","Synonyms"])
        df_out = df_compounds.merge(df_search, on = "Compound")
        df_out = df_out.rename(columns={"Count":(context_title,"Count"),"PID":(context_title,"PID")}) 


        if output_path:
            #if not os.path.exists("./Tables_exported"):
            #  os.mkdir("./Tables_exported")
            df_out.to_excel("{}/{}_results_{}.xlsx".format(output_path,datetime.date.today(),table_name))
             
        if output_df:
            return df_out
    
    def multiple_context_search(self, context_dictionary=None, output_path=None, output_df=True):
        """The dictionary of context words as shown in the publication.
            
            args
            
            context_dictionary: if you want to use your own context dictionary, enter it here
            
        """
        if not context_dictionary:
            none = []
            covid = ["Covid-19","COVID-19","SARS-CoV2","SARS-CoV-2","Covid 19"]
            heart = ["heart","vasculature","cardiovascular","cardiac","cardio","angiogenesis","Vasculogenesis"]
            embryo = ["embryo","pregnancy","embryonic development","embryogenesis"]
            context_dictionary = {"Covid-19":covid, "Cardiovascular":heart, "Development":embryo}
        
        
        for i,context in enumerate(context_dictionary.items()):
            if i == 0:
                collect_context_results = self.search_and_export(context[1], context[0])
            else:
                context_results = self.search_and_export(context[1], context[0]).drop("Synonyms", axis=1)
                collect_context_results = collect_context_results.merge(context_results, on = "Compound")
        
        
        if output_path:
            table_name = "_".join(list(context_dictionary.keys()))
            collect_context_results.to_excel("{}/{}_results_{}.xlsx".format(output_path, datetime.date.today(), table_name))
            
            with open("{}/{}_searchterms_{}.pkl".format(output_path, datetime.date.today(), table_name), 'wb') as f:
                pickle.dump(context_dictionary, f)
        
        if output_df:    
            return (collect_context_results,context_dictionary)        
    
    
        
    def make_search_term(self, compound, synonyms, terms):
        """Function to create search term with synonyms, including AND OR
             Scheme search term: ("compound name" [tag] AND "context term"[tag]) OR ("compound synonym 1" [tag] AND "context term"[tag])
        """
        
        # merge the search TRIVIAL_NAME with the synonyms to one list  
        synonyms_list=[compound] + synonyms
        # tags for example [text], [all fields],[tiab]
        tag='[all]'
        OR= ' OR '

        # if no search terms are included
        if terms != []:
            AND = [['("'+i+'"{} AND "'.format(tag)+j+'"{})'.format(tag) for j in terms ] for i in synonyms_list[:6]]
            search_terms = [OR.join(list(search)) for search in AND] 
            or_terms = OR.join(search_terms)
            # merge everything to one search term
        else:
            search_terms = synonyms_list[:6]
            OR= "{}{} OR {}".format('"',tag,'"')
            or_terms='"'+OR.join(search_terms)+'"'

        return or_terms

    def find_synonyms(self,compound_name):
        """ search in pubchempy for the compound"""
        try:
            compound_cid = get_compounds(compound_name, 'name')
            synonyms = compound_cid[0].synonyms

        # retrieve the synonyms
        except:
            synonyms = [""]

        compound = [compound_name]
        # merge the search term 
        synonyms_list = compound + synonyms

        return synonyms_list



    def search_all_compounds(self, combinations, list_names, synonym_list,PID=True,):
        """Make the search for all "Search terms" and collect results """  
        if PID:
            results = pd.DataFrame(columns=["Compound","Count","PID"])
        else:
            results = pd.DataFrame(columns=["Compound","Count"])

        #Loop for database search with searchterms
        for i,j in zip(list_names, synonym_list):
            p = self.make_search_term(i, j, combinations)
            handle = self.Entrez.esearch(db="pubmed", retmax=100000, term=p)
            record = self.Entrez.read(handle)
            handle.close()
            time.sleep(0.1)
            
            # with PID list
            if PID:
                results = results.append({"Compound":i, "Count": int(record["Count"]),"PID":record["IdList"]},ignore_index=True)
            # without PID list
            else:
                results = results.append({"Compound":i,"Count":int(record["Count"])},ignore_index=True)  
        
        return results

   
    
def find_intersection(df_, string_to_list = False):
    PID_columns = list(filter(lambda x: "PID" in x, list(df_.columns)))
    PID_combinations = [i for i in itertools.product(PID_columns,PID_columns) if i[0] != i[1]]
    
    if string_to_list:
        for cols in PID_columns:
            df_[cols]=[(i.replace("'","").replace("[","").replace("]","").split(", ")) if i != "[]" else [] for i in list(df_[cols]) ]
    
    for combi in PID_combinations:
        df_[combi]=[len(set(a).intersection(b)) if ((a != "[]") and (b != "[]")) else 0 for a,b in zip(df_[combi[0]],df_[combi[1]])]
    return check_duplicates(df_)

def check_duplicates(df_): 
    list1 = list(df_.columns)
    inew = []
    newcolumns = []
    
    for c,i in enumerate(list1):
        inew.append(i)

        if not (i[1],i[0]) in inew:
            newcolumns.append(df_.columns[c])
    
    df_ = df_[newcolumns]
    return df_