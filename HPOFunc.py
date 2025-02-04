import pandas as pd
import re
from pyhpo.ontology import Ontology
import numpy as np
import itertools
import math

ontology=Ontology()

NullList=["none", "none documented", "nil", "(borderline)", "no concerns"]

def check_and_set_nan(strg: str, NullList: list = ["none", "none documented", "nil", "(borderline)", "no concerns"])->str:
    """
    Some of the HPO responses are different variations of people saying "no"
    This function is designed to catch those so that I don't faff about with
    non-responses that don't need to be processed.

    A pre-defined "NullList" is used to check if the string is in there and 
    then that element is removed.
    NullList=["none", "none documented", "nil", "(borderline)", "no concerns"]

    Then a string is checked to see if it contains values from the NullList.
    Returns a string which has all the null list items removed. 
    If the original input is NaN, returns an empty string
    """
    if pd.isna(strg):
        strg = ""
    if strg.lower() in [s.lower() for s in NullList]:
        strg = ""
    return strg

def drop_leading_hp(strg: str)->str:
    """
    Takes in a string, ideally a HPO term, and removes the leading HP or hp from it
    """
    return strg[2:] if strg.startswith('HP') else strg


def HPOSorter(strg: str) -> tuple[list[str], list[str]]:
    """
    Takes a string from a single cell from the HPOData dataframe
    Checks if it's null
    Then separates it into two separate lists, one list of non_numeric values and one list of numeric values
    The non_numeric values are then cleaned up to remove any leading "HP:" or "hp:" and then returned
    Returns two lists, one of numeric values and one of non_numeric values
    """

    strg=check_and_set_nan(strg, NullList)

    if pd.isna(strg): 
        non_numeric_values=[]
        numeric_values=[]
    else:
        numeric_values = re.findall(r'\d{2,}', strg)
        # I want free text to have a leading capital preserved, but I want to remove any leading HP: or hp:
        # different entries have upper or lower case combinations of HP, so I'm going to remove all of them

        strg = re.sub(r'HP:', '', strg)
        strg = re.sub(r'hp:', '', strg)
        strg = re.sub(r'hP:', '', strg)
        strg = re.sub(r'Hp:', '', strg)
        strg = re.sub(r'HP', '', strg)
        strg = re.sub(r'hp', '', strg)
        strg = re.sub(r'hP', '', strg)
        strg = re.sub(r'Hp', '', strg)

        strg = re.sub(r':', '', strg)


        strg = re.sub(r'\d{2,}', '', strg)

        # Once that's been handled, split one thing into the entire list
        non_numeric_values=re.split(r',|  ', strg)
        non_numeric_values=[value for value in non_numeric_values if re.search('[a-zA-Z]', value)]
        non_numeric_values=[r.lstrip() for r in non_numeric_values]
        non_numeric_values=[drop_leading_hp(r) for r in non_numeric_values]
    
    return numeric_values, non_numeric_values

def get_hpo_or_error(strg: str, Process_Type: str="Non_numeric")->str:
    """
    Takes a string "strg" and tries to get the HPO object from the ontology
    If it fails, proceeds differently depending on the Process_Type

    If Process_Type is "None", errors result in an empty string
    If Process_Type is "Non_numeric", it tries a few different ways of cleaning up the string


    it tries a few different ways of cleaning up the string
    Designed to work with non_numeric values
    If it still fails, it returns an error message, which can then be added to a list of problems
    """

    # Maybe I want process type and error type

    # Process type is numerical or letters
    # If numerical, try it, then check if there's any "HPs"
    # If there are HPs but no colons, add colons
    # If t
    if Process_Type == "None":
        try:
            out = ontology.get_hpo_object(strg)
            return out
        except RuntimeError:
                out = ""
                return out
    elif Process_Type == "Non_numeric":
        # Remove trailing whitespace
        strg = strg.rstrip()
        # Remove leading and trailing non-word characters
        strg = re.sub(r'^\W+|\W+$', '', strg)
        if len(strg) > 1:
            strg = strg[0].upper() + strg[1:].lower()
        else:
            strg = strg.upper()
        try:
            # Attempt to get the HPO object
            out = ontology.get_hpo_object(strg)
            return out
        except RuntimeError:
            # Return an error message if both attempts fail
            out = f"Error: {strg}"
        return out
    elif Process_Type == "Numeric":
        try:
            out = ontology.get_hpo_object(strg)
            return out
        except RuntimeError:
            try:
                hpstrg = "HP:"+strg
                out = ontology.get_hpo_object(hpstrg)
                return out
            except RuntimeError:
                out = f"Error: HP:{strg}"
        return out
    else:
        print("Process_Type must be one of 'None', 'Non_numeric', or 'Numeric'")
        return None


#print(get_hpo_or_error("arachnodactyly"))             
    
def list_to_csv(lst: list)->str:
    """
    Final output is going to be a single cell with semicolon separated HPO terms in a standardised format
    This function just lets me turn a list into a singl string (because one HPO code has a comma in it, rip)
    """
    return '; '.join(map(str, lst)) 
    
def HPOOutPutter(numeric_values: list[str], non_numeric_values: list[str])->tuple[list[str], list[str], str]:
    """
    Takes the two lists from HPOSorter and then runs them through the get_hpo_or_error function
    Numeric values are pretty easy to check
    Non_numeric still require a bit of fiddling
    Also it's quite important to output the errors in a nice way so that they can be manually checked
    This is useful for me to develop this code so that it hits as many common expressions as possible
    But also tells me what I missed.
    It's also just handy because there are some specific entries that are so weird that it's way too much faff
    to just make a general rule for them. Instead easier to flag and give to my PI who can manually check
    """
    ProblemList = []
    if not numeric_values:  # If the list is empty
        numeric_terms = []
        # No contribution to ProblemList
    else:
        #numeric_terms = ["HP:" + str(r) for r in numeric_values]
        numeric_terms = [str(get_hpo_or_error(r, Process_Type="Numeric")) for r in numeric_values]
        ProblemList.extend([value for value in numeric_terms if isinstance(value, str) and value.startswith('Error:')])
        numeric_terms = [value for value in numeric_terms if not (isinstance(value, str) and value.startswith('Error:'))]
    if not non_numeric_values:  # If the list is empty
        non_numeric_terms = []
        # No contribution to ProblemList
    else: 
        non_numeric_terms = [str(get_hpo_or_error(r, Process_Type="Non_numeric")) for r in non_numeric_values]
        ProblemList.extend([value for value in non_numeric_terms if isinstance(value, str) and value.startswith('Error:')])
        non_numeric_terms = [value for value in non_numeric_terms if not (isinstance(value, str) and value.startswith('Error:'))]

    Problems = list_to_csv(ProblemList)
    
    return numeric_terms, non_numeric_terms, Problems # Note that outputs include the Problem cases so that they can be manually checked

def HPOSquisher(terms1, terms2):
    """
    Takes the list of HPO terms from the numeric and non_numeric lists and does the union of them to give a list of all possible mentions
    Sometimes people write stuff in both numeric and non_numeric form, and sometimes just in one or the other
    """
    if len(terms1)+len(terms2) == 0:
        BigTerms=[]
    else:
        BigTerms=sorted(list(set(terms1) | set(terms2)))
        # Making it alphabetical makes testing easier
    TermList=list_to_csv(BigTerms)

    return TermList

def process_column(entry: str)  -> tuple[str, str]:
    """
    Takes the cell entry, runs it through the HPOSorter, HPOOutPutter and HPOSquisher functions
    Returns the terms in a single cell, and any problems that go encountered
    """

    numeric_values, non_numeric_values = HPOSorter(entry)
    terms1, terms2, Problems = HPOOutPutter(numeric_values, non_numeric_values)
    TermList = HPOSquisher(terms1, terms2)
    
    return TermList, Problems

def HPOScorer(doctor_responses, parent_responses):
    """
    Takes a list of HPO terms from the doctor and parent
    returns the quantity and quality scores for both
    as well as the codes where the quality score is non-zero
    """
    
    if pd.notna(doctor_responses):
        doctor_hpo = doctor_responses.split(";")
        doctor_hpo = [hpo.split(" | ")[0] for hpo in doctor_hpo]
        doctor_hpo = [doc.replace(" ", "") for doc in doctor_hpo]
        doc_quant = len(doctor_hpo)
    else:
        doc_quant = 0

    if pd.notna(parent_responses):
        parent_hpo = parent_responses.split(";")
        parent_hpo = [hpo.split(" | ")[0] for hpo in parent_hpo]
        parent_hpo = [par.replace(" ", "") for par in parent_hpo]
        par_quant = len(parent_hpo)
    else:
        par_quant = 0

    doc_qual = 0
    par_qual = 0

    doc_codes = []
    par_codes = []

    if pd.notna(doctor_responses) and pd.notna(parent_responses):
        for doc, par in itertools.product(doctor_hpo, parent_hpo):
            #print(doc, par)
            # Assuming ontology.path returns a list or tuple where the 3rd and 4th elements are needed
            try: 
                path_result = ontology.path(doc, par)
            except: 
                continue
            a, b = path_result[2], path_result[3]  # Corrected indexing
            if a == 0:
                doc_qual += 0  # This line could be omitted as it has no effect
                par_qual += b
                if b != 0:
                    par_codes.append(par)
            elif b == 0:
                doc_qual += a
                par_qual += 0  # This line could also be omitted
                if a != 0:
                    doc_codes.append(doc)
    
    return int(doc_quant), int(par_quant), int(doc_qual), int(par_qual), doc_codes, par_codes



def Turn_Lists_Of_HPOs_Into_Just_Codes(HPOString):
    """
    Takes a string of HPO terms and returns a list of just the codes
    """
    if isinstance(HPOString, str):
        HPOList = HPOString.split(", ")
        if len(HPOList) == 0:
            return HPOString
        NewList = []
        for HPO in HPOList:
            HPO = HPO.split(" | ")[0]
            NewList.append(HPO)
        return NewList
    else:
        return HPOString