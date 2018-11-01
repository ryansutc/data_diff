'''
 A simple test to show how two csv files with identical schema
 can be compared to find differences using the python pandas library:
 https://pandas.pydata.org/.

 this sample roughly based on "Using Pandas to create an Excel Diff"
 by Chris Moffitt (http://pbpython.com/excel-diff-pandas.html)

'''

# let's ignore some unimportant numpy version conflict messages
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import pandas as pd
import numpy as np

def report_diff(x):
    return x[0] if x[0] == x[1] else '{} --> {}'.format(*x)

def has_change(row):
    print type(row)
    print row
    if "-->" in row.to_string():
        return "Y"
    else:
        return "N"

###########################
    
results = pd.read_csv("../data/resultstable.csv",
                      index_col=['STREET','STR_KEY','GSA_KEY', 'CO_CODE', 'ESN', 'OEB'])
solution = pd.read_csv("../data/solutiontable.csv",
                       index_col=['STREET','STR_KEY','GSA_KEY', 'CO_CODE', 'ESN', 'OEB'])

results['version'] = "results"
solution['version'] = "solution"

# Make a big table of all data:
full_set = pd.concat([results, solution])

# get a list of the duplicated records when the two tables are combined
# we are assuming here that our composite key fields are unique:
dup_indexes = full_set[full_set.index.duplicated()].index

# now filter original tables to only include duplicate records:
results = results.loc[dup_indexes]
solution = solution.loc[dup_indexes]

# create a 3d panel containing the results & solution:
diff_panel = pd.Panel(dict(solution=solution,results=results))

# extract a diff table based on the panel:
diff_output = diff_panel.apply(report_diff, axis=0)
diff_output["version"] = "results > solution"

# update output with a "has_change" field:
diff_output["has_change"] = diff_output.apply(has_change, axis=1)

print diff_output

# now lets add the mismatched fields that were only in one of the tables (solution/results):
# we are filtering the full_set data frame to only include these orphans:
full_set = full_set.loc[~full_set.index.isin(dup_indexes)]

# create a "has_change" field for these orphan records
full_set['has_change'] = "N/A"
print full_set

# create a new table with both the compared results and the orphans:
final_output = pd.concat([diff_output, full_set])

# print the final results:
print final_output

# export results to csv file:
final_output.to_csv("../data/comparisontable.csv")

