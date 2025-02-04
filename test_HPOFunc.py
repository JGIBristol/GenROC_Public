import pandas as pd
import re
import numpy as np
import itertools
import math
from pyhpo.ontology import Ontology
import HPOFunc

NullList=["none", "none documented", "nil", "(borderline)", "no concerns"]

def test_check_and_set_nan():
    
    for item in NullList:
        output = HPOFunc.check_and_set_nan(item, NullList)
        expect = ""
        assert output == expect, "Expected: " + expect + " Got: " + output
    
    test2 = "Something else"
    output2 = HPOFunc.check_and_set_nan(test2, NullList)
    expect2 = "Something else"
  
    assert output2 == expect2, "Expected: " + expect2 + " Got: " + output2

print("Testing check_and_set_nan")
test_check_and_set_nan()

def test_drop_leading_hp():
    test1 = "HP:0000001"
    test2 = "0000001"
    test3 = "HP0000001"

    output1 = HPOFunc.drop_leading_hp(test1)
    output2 = HPOFunc.drop_leading_hp(test2)
    output3 = HPOFunc.drop_leading_hp(test3)

    expect1 = ":0000001"
    expect2 = "0000001"
    expect3 = "0000001"

    assert output1 == expect1, "Expected: " + expect1 + " Got: " + output1
    assert output2 == expect2, "Expected: " + expect2 + " Got: " + output2
    assert output3 == expect3, "Expected: " + expect3 + " Got: " + output3

print("Testing drop_leading_hp")
test_drop_leading_hp()

def test_HPOSorter():
    test1 = "None"
    test2 = "Allergy"
    test3 = "HP:0012393"
    test4 = "Allergy, HP:0500093"
    test5 = "HP:0500093 Food allergy Nystagmus HP:0000639"
    test6 = "Weird edge case"

    output1 = HPOFunc.HPOSorter(test1)
    output2 = HPOFunc.HPOSorter(test2)
    output3 = HPOFunc.HPOSorter(test3)
    output4 = HPOFunc.HPOSorter(test4)
    output5 = HPOFunc.HPOSorter(test5)
    output6 = HPOFunc.HPOSorter(test6)

    # Outputs look like numeric (no HP) values and non numeric values
    # should be strings inside lists, as a tuple
    expect1 = ([], [])
    expect2 = ([], ["Allergy"])
    expect3 = (['0012393'], [])
    expect4 = (["0500093"], ['Allergy'])
    expect5 = (["0500093", "0000639"], ['Food allergy Nystagmus '])
    expect6 = ([], ['Weird edge case'])

    assert output1 == expect1, "Expected: " + str(expect1) + " Got: " + str(output1)
    assert output2 == expect2, "Expected: " + str(expect2) + " Got: " + str(output2)
    assert output3 == expect3, "Expected: " + str(expect3) + " Got: " + str(output3)
    assert output4 == expect4, "Expected: " + str(expect4) + " Got: " + str(output4)
    assert output5 == expect5, "Expected: " + str(expect5) + " Got: " + str(output5)
    assert output6 == expect6, "Expected: " + str(expect6) + " Got: " + str(output6)

print("Testing HPOSorter")
test_HPOSorter()

print("Loading Ontology")
ontology=Ontology()

def test_get_hpo_or_error():
    # Need to redo these tests
    # Want a standard HPO code or two
    # Want viable outputs for Process_Type = "None", "Non_numeric" and "Numeric"
    # Also want a test case for if I put the wrong process type in
    # Then I want to try lots of different HPO codes, not going to call from the ontology for the expected
    
    # Running stuff without errors
    test_case_easy1 = "HP:0001166"
    test_case_easy2 = "Arachnodactyly"
    expected_easy = "HP:0001166 | Arachnodactyly"
    
    output_easy1 = HPOFunc.get_hpo_or_error(test_case_easy1, "Numeric")
    output_easy1a = HPOFunc.get_hpo_or_error(test_case_easy1, "None")
    output_easy2 = HPOFunc.get_hpo_or_error(test_case_easy2, "Non_numeric")
    output_easy2a = HPOFunc.get_hpo_or_error(test_case_easy2, "None")

    assert str(output_easy1) == expected_easy, "Expected:" + expected_easy + "Got: " + output_easy1
    assert str(output_easy1a) == expected_easy, "Expected:" + expected_easy + "Got: " + output_easy1a
    assert str(output_easy2) == expected_easy, "Expected:" + expected_easy + "Got: " + output_easy2
    assert str(output_easy2a) == expected_easy, "Expected:" + expected_easy + "Got: " + output_easy2a

    # Next to just check if I give it a nonsense process type it won't return something
    nonsense_test = HPOFunc.get_hpo_or_error(test_case_easy1, "supercalifragilisticexpelidocious")
    assert nonsense_test is None, "Expected: None Got: " + str(nonsense_test)

    # Now to test how it handles errors
    test_none = "Not a HPO code"
    output_none = HPOFunc.get_hpo_or_error(test_none, "None")
    assert output_none == "", "Expected: '' Got: " + output_none
    
    test_none_num = "123456789"
    output_numeric = HPOFunc.get_hpo_or_error(test_none_num, "Numeric")
    assert output_numeric == f"Error: HP:{test_none_num}", "Expected: '' Got: " + output_numeric
    
    test_lower = "arachnodactyly"
    output_lower = HPOFunc.get_hpo_or_error(test_lower, "Non_numeric")
    assert str(output_lower) == expected_easy, "Expected:" + expected_easy + "Got: " + str(output_lower)
    
    # arguably non-numeric could be tested more thoroughly but happy with this for now 
    
print("Testing get_hpo_or_error")
test_get_hpo_or_error()


def test_list_to_csv():
    test1 = ["HP:0000001", "HP:0000002", "HP:0000003"]
    output1 = HPOFunc.list_to_csv(test1)
    expect1 = "HP:0000001; HP:0000002; HP:0000003"
    assert output1 == expect1, "Expected: " + expect1 + " Got: " + output1

print("Testing list_to_csv")
test_list_to_csv()

def test_HPOOutPutter():
    # Need quite a few test cases here
    # Test case 1: No numeric values, no non-numeric values
    num_test1 = []
    non_num_test1 = []
    output1a, output1b, prob1 = HPOFunc.HPOOutPutter(num_test1, non_num_test1)
    assert output1a == [], "Expected: '[]' Got: " + output1a
    assert output1b == [], "Expected:" + '[]' + "Got: " + output1b
    assert prob1 == "", "Expected:" +  "" + "Got: " + str(prob2)
   
    # Test case 2a: No numeric values, some non-numeric values
    num_test2 = ["0000077", "0000890"]
    non_num_test2 = []
    output2a, output2b, prob2 = HPOFunc.HPOOutPutter(num_test2, non_num_test2)
    expected2 = ["HP:0000077 | Abnormality of the kidney", "HP:0000890 | Long clavicles"]
    assert output2a == expected2, "Expected: " + str(expected2) + " Got: " + str(output2a)
    assert output2b == [], "Expected:" + '[]' + "Got: " + str(output2b)
    assert prob2 == "", "Expected:" +  "" + "Got: " + str(prob2)

    #Test 2b: No numeric values, some non-numeric values, some error non-numeric errors
    num_test2 = ["0000077", "0000890"]
    non_num_test2 = ["Pizza"]
    output2a, output2b, prob2 = HPOFunc.HPOOutPutter(num_test2, non_num_test2)
    expected2 = ["HP:0000077 | Abnormality of the kidney", "HP:0000890 | Long clavicles"]
    assert output2a == expected2, "Expected: " + str(expected2) + " Got: " + str(output2a)
    assert output2b == [], "Expected:" + '[]' + "Got: " + str(output2b)
    assert prob2 == "Error: Pizza", "Expected:" +  "" + "Got: " + str(prob2)

    # Test case 3a: Some numeric values, no non-numeric values
    num_test3 = []
    non_num_test3 = ["Long clavicles", "Abnormality of the kidney"]
    output3a, output3b, prob3 = HPOFunc.HPOOutPutter(num_test3, non_num_test3)
    expected3 = ["HP:0000890 | Long clavicles", "HP:0000077 | Abnormality of the kidney"]
    assert output3a == [], "Expected: '[]' Got: " + str(output3a)
    assert output3b == expected3, "Expected:" + str(expected3) + "Got: " + str(output3b)
    assert prob3 == "", "Expected:" +  "" + "Got: " + str(prob3)

    # Test case 3b: Some numeric values, some non-numeric values, some error numeric errors
    num_test3 = ["1218476100"]
    non_num_test3 = ["Long clavicles", "Abnormality of the kidney"]
    output3a, output3b, prob3 = HPOFunc.HPOOutPutter(num_test3, non_num_test3)
    expected3 = ["HP:0000890 | Long clavicles", "HP:0000077 | Abnormality of the kidney"]

    assert output3a == [], "Expected: '[]' Got: " + str(output3a)
    assert output3b == expected3, "Expected:" + str(expected3) + "Got: " + str(output3b)
    assert prob3 == "Error: HP:1218476100", "Expected:" +  "" + "Got: " + str(prob3)

    # Test case 4: Some numeric values, some non-numeric values
    num_test4 = ["0002401", "0000717"]
    non_num_test4 = ["Stroke-like episode", "Increased vertebral height"]

    expected_num4 = ["HP:0002401 | Stroke-like episode", "HP:0000717 | Autism"]
    expected_non_num4 = ["HP:0002401 | Stroke-like episode", "HP:0004570 | Increased vertebral height"]

    output4a, output4b, prob4 = HPOFunc.HPOOutPutter(num_test4, non_num_test4)
    assert output4a == expected_num4, "Expected: " + str(expected_num4) + " Got: " + str(output4a)
    assert output4b == expected_non_num4, "Expected:" + str(expected_non_num4) + "Got: " + str(output4b)
    assert prob4 == "", "Expected:" +  "" + "Got: " + str(prob4)

    # Test case 5: Some numeric values, some non-numeric values, some errors
    num_test5 = ["0002401", "0000717", "123456"]
    non_num_test5 = ["Stroke-like episode", "Increased vertebral height", "Pizza"]

    expected_num5 = ["HP:0002401 | Stroke-like episode", "HP:0000717 | Autism"]
    expected_non_num5 = ["HP:0002401 | Stroke-like episode", "HP:0004570 | Increased vertebral height"]
    expected_prob5 = "Error: HP:123456; Error: Pizza"

    output5a, output5b, prob5 = HPOFunc.HPOOutPutter(num_test5, non_num_test5)
    assert output5a == expected_num5, "Expected: " + str(expected_num5) + " Got: " + str(output5a)
    assert output5b == expected_non_num5, "Expected:" + str(expected_non_num5) + "Got: " + str(output5b)
    assert prob5 == expected_prob5, "Expected:" +  expected_prob5 + "Got: " + str(expected_prob5)
    
print("Testing HPOOutPutter")
test_HPOOutPutter()

def test_HPOSquisher():
    # Fairly routine? This function isn't designed to deal with errors, just to squash things together

    # Test case 1: No numeric values, no non-numeric values
    num_test1 = []
    non_num_test1 = []
    output1 = HPOFunc.HPOSquisher(num_test1, non_num_test1)
    expect1 = ""
    assert output1 == expect1, "Expected: " + expect1 + " Got: " + output1

    # Test case 2: No numeric values, some non-numeric values
    num_test2 = []
    non_num_test2 = ["HP:0012170 | Nail-biting", "HP:0007302 | Bipolar affective disorder"]
    output2 = HPOFunc.HPOSquisher(num_test2, non_num_test2)
    expect2 = "HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting"
    assert str(output2) == expect2, "Expected: " + expect2 + " Got: " + str(output2)

    # Test case 3: Some numeric values, no non-numeric values
    num_test3 = ["HP:0007302 | Bipolar affective disorder", "HP:0012170 | Nail-biting"]
    non_num_test3 = []
    output3 = HPOFunc.HPOSquisher(num_test3, non_num_test3)
    expect3 = "HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting"
    assert str(output3) == expect3, "Expected: " + str(expect3) + " Got: " + str(output3)

    # Test case 4: Some numeric values, some non-numeric values, make sure there's intercepts
    num_test4 = ["HP:0007302 | Bipolar affective disorder", "HP:0012170 | Nail-biting"]
    non_num_test4 = ["HP:0002401 | Stroke-like episode", "HP:0007302 | Bipolar affective disorder"]
    output4 = HPOFunc.HPOSquisher(num_test4, non_num_test4)
    expect4 = "HP:0002401 | Stroke-like episode; HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting"
    assert str(output4) == expect4, "Expected: " + str(expect4) + " Got: " + str(output4)

print("Testing HPOSquisher")
test_HPOSquisher()

def test_process_column():
    # So I want to test this on cell entries but then I want to test it on a whole column of a df

    # Test case 1: Single cell entry, no numeric values, no non-numeric values
    test1 = pd.NA
    termlist1, problems1 = HPOFunc.process_column(test1)
    expect1 = ("", "")
    assert termlist1 == expect1[0], "Expected: " + str(expect1[0]) + " Got: " + str(termlist1)
    assert problems1 == expect1[1], "Expected: " + str(expect1[1]) + " Got: " + str(problems1)    

    # Test case 2: Single cell entry, no numeric values, some non-numeric values
    test2 = "Nail-biting, Bipolar affective disorder"
    termlist2, problems2 = HPOFunc.process_column(test2)
    expect2 = ("HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting", "")
    assert termlist2 == expect2[0], "Expected: " + str(expect2[0]) + " Got: " + str(termlist2)
    assert problems2 == expect2[1], "Expected: " + str(expect2[1]) + " Got: " + str(problems2)

    # Test case 3: Single cell entry, some numeric values, no non-numeric values
    test3 = "HP:0007302, HP:0012170"
    termlist3, problems3 = HPOFunc.process_column(test3)
    expect3 = ("HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting", "")
    assert termlist3 == expect3[0], "Expected: " + str(expect3[0]) + " Got: " + str(termlist3)
    assert problems3 == expect3[1], "Expected: " + str(expect3[1]) + " Got: " + str(problems3)

    # Test case 4: Single cell entry, some numeric values, some non-numeric values
    test4 = "HP:0007302, Nail-biting"
    termlist4, problems4 = HPOFunc.process_column(test4)
    expect4 = ("HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting", "")
    assert termlist4 == expect4[0], "Expected: " + str(expect4[0]) + " Got: " + str(termlist4)
    assert problems4 == expect4[1], "Expected: " + str(expect4[1]) + " Got: " + str(problems4)

    # Test case 5: Single cell entry, some numeric values, some non-numeric values, some errors
    test5 = "HP:0007302 | Bipolar affective disorder, Nail-biting, Pizza"
    termlist5, problems5 = HPOFunc.process_column(test5)
    expect5 = ("HP:0007302 | Bipolar affective disorder; HP:0012170 | Nail-biting", "Error: Pizza")
    assert termlist5 == expect5[0], "Expected: " + str(expect5[0]) + " Got: " + str(termlist5)
    assert problems5 == expect5[1], "Expected: " + str(expect5[1]) + " Got: " + str(problems5)

    # Test case 6: Whole column of a dataframe and populate it with entries from previous tests
    df = pd.DataFrame({"Test": [test1, test2, test3, test4, test5],
                       "Expected": [expect1[0], expect2[0], expect3[0], expect4[0], expect5[0]],
                       "Problems": [expect1[1], expect2[1], expect3[1], expect4[1], expect5[1]],
                        })
    df["Output"], df["Output_Problems"] = zip(*df["Test"].map(HPOFunc.process_column))

    assert df["Output"].equals(df["Expected"]), "Expected: " + str(df["Expected"]) + " Got: " + str(df["Output"])

print("Testing process_column")
test_process_column()

# Should probably write some tests for the scoring functions but uh, in the mean time, good job me

print("All your tests have passed! You are a super star!")