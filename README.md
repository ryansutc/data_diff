<h1 align="center">
<img src="https://raw.githubusercontent.com/ryansutc/data_diff/master/doc/blob/data_diff.png" alt="doc-diff" width="20%" height="20%">
    <br>
        data-diff
    <br>
  <h4 align="center">Data Diff: Compare files with Python</h4>
</h1>

<p align="center">
  <a href="https://github.com/ryansutc/data_diff/blob/master/LICENSE">
    <img src="https://img.shields.io/npm/l/express.svg?maxAge=2592000&style=flat-square"
         alt="License">
  </a>
</p>

## Summary
Using Pandas package to compare two tables with simular schema but different data.

### Example 1:

A simple example comparing two tables with unique ids when using 
the ```ID``` and ```CODE``` fields as composite keys: 

**table A:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:|
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | MED | 13 |
| 3 | B| SALSA| MED| 2 |


**table B:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:| 
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | HIGH | 15 |

to compare we run the script like this:

```
csv_diff.py 'c:/data/tableA.csv' 'c:/data/tableB.csv' 
   --output 'c:/data/diff_table.csv' 'ID' 'CODE' --namea 'tableA'
   --nameb 'tableB'
```

**Results in the Data Diff Comparison:**

| ID | CODE | NAME | GROUP | VAL | *Compare* |
|---:|-----:|:-----:|:---:|:----:|:---:|
| 1 | A | FOO | HIGH | 5 | tableA == tableB |
| 2 | A | BAR | MED --> HIGH | 13 --> 15 | tableA <> tableB |
| 3 | B | SALSA | MED | 2 --> 8 | tableA --> ??? |

*The first record was an exact match, the second had some changes, and
the third could only be found in table A.*
### Example 2:

A simple example of comparing **"dirty"** data, where the index fields are not quite unique:

**table A:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:|
| 1 | A | FOO | HIGH| 5 | 
| 1 | A | FOO | MED | 13 |
| 3 | B | SAL | MED | 2 |
| 3 | B | SAL | LOW | 10 |

**table B:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:| 
| 1 | A | FOO | HIGH| 5 | 
| 3 | B | SAL | MED | 8 |


to compare we run the script like this (note ```--dirty```):

```
csv_diff.py 'c:/data/tableAdirty.csv' 'c:/data/tableBdirty.csv' 
   --output 'c:/data/diff_table.csv' 'idfield1' 'idfield2' --namea 'results'
   --nameb 'solution' --dirty
```

**Results in the Data Diff Comparison:**

| ID | CODE | NAME | GROUP | VAL | *Compare* | 
|---:|-----:|:-----:|:---:|:----:|:---:|
| 1 | A | FOO | HIGH| 5 | tableA == tableB | 
| 1 | A | FOO | MED | 13 | tableA --> ??? |
| 3 | B | SAL | MED | 2 | tableA --> [CNC] | 
| 3 | B | SAL | LOW | 10 | tableA --> [CNC] |
| 3 | B | SAL | MED | 8 | tableB --> [CNC] | 

*The first record matches, the second was only found in table A, the
rest could not be compared.*

*CNC means *Could not compare*. If there are more than one option for an index
and no exact match, the tool will not try to use any logic to pick one to compare. 

If there are field names that only exist in one input table these 
fields are not part of the comparison and are
appended at the end after the ```Compare``` field.

To see details of the process, see [process diagram here](https://www.lucidchart.com/documents/view/a5c3bef5-3ff1-44ba-af41-04e9d7c63ce3/0).

~
Note to self..
To build: ```pyinstaller csv_diff.py -F --onedir```
