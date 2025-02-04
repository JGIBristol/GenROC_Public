# GenROC_Public

Public repo for GenROC Project working with Dr Karen Low

## HPO Code
All the Python files + notebooks for doing analysis on HPO (Human Phenotype Ontology) related things: https://hpo.jax.org/

### HPOFunc.py

A python module for various functions for processing HPO codes.

Main functions of note:

#### HPOSorter:

-  Takes a single cell from the HPOData dataframe
- Checks if it's null
- Then separates it into two separate lists, one list of non_numeric values and one list of numeric values
- The non_numeric values are then cleaned up to remove any leading "HP:" or "hp:" and then returned

#### HPOOutPutter:

- Takes the two lists from HPOSorter and then runs them through the get_hpo_or_error function
- Numeric values are pretty easy to check
- Non_numeric still require a bit of fiddling
- Also it's quite important to output the errors in a nice way so that they can be manually checked
- This is useful for me to develop this code so that it hits as many common expressions as possible
- But also tells me what I missed.
- It's also just handy because there are some specific entries that are so weird that it's way too much faff
to just make a general rule for them. Instead easier to flag and give to my PI who can manually check

#### HPOSquisher:

- Takes the list of HPO terms from the numeric and non_numeric lists and does the union of them to give a list of all possible mentions
- Sometimes people write stuff in both numeric and non_numeric form, and sometimes just in one or the other
process_column:
- Takes the cell entry, runs it through the HPOSorter, HPOOutPutter and HPOSquisher functions
- Returns the terms in a single cell, and any problems that go encountered

#### HPOScorer:

- Takes a list of HPO terms from the doctor and parent
- returns the quantity and detail scores for both
- as well as the codes where the detail score is non-zero

## test_HPOFunc.py

- A python file that loads in HPOFunc.py as a module
- A suite of test functions that assert if the functions in HPOFunc.py give the expected outputs
