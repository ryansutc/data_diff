## Data Diff: Compare csv files with Python

Using Pandas package to compare two tables with simular schema but different data.

#### Example A:

A simple example comparing two tables with identical schema and unique ids when using the ```ID``` and ```CODE``` fields
as composite keys: 

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
csv_diff.py 'c:/data/table_a.csv' 'c:/data/table_b.csv' 
   'c:/data/diff_table.csv' 'idfield1' 'idfield2' --namea 'tableA'
   --nameb 'tableB' --dirty
```

**Results in the Data Diff Comparison:**

| ID | CODE | NAME | GROUP | VAL | *Compare* |
|---:|-----:|:-----:|:---:|:----:|:---:|
| 1 | A | FOO | HIGH | 5 | tableA == tableB |
| 2 | A | BAR | MED --> HIGH | 13 --> 15 | tableA <> tableB |
| 3 | B | SALSA | MED | 2 --> 8 | tableA --> ??? |


#### Example B:

A simple example of comparing **"dirty"** data, where the schema of the two tables does not
match and the index fields are not quite unique:

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
| 2 | A | CHO | LOW | 2 |
| 3 | B | SAL | MED | 8 |


to compare we run the script like this (note ```--dirty```):

```
csv_diff.py 'c:/data/table_a.csv' 'c:/data/table_b.csv' 
   'c:/data/diff_table.csv' 'idfield1' 'idfield2' --namea 'results'
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

*CNC means *Could not compare*. If there are more than one option for an index
and no exact match, the tool will not try to use any logic to pick one to compare. 

With the dirty option we can compare even when indexes are not unique. If there are field
names that only exist in one input table these fields are not part of the comparison and are
appended at the end after the ```Compare``` field.

To see details of the process, see [process diagram here](https://www.lucidchart.com/documents/view/a5c3bef5-3ff1-44ba-af41-04e9d7c63ce3/0).

