## Data Diff: Compare csv files with Python

Using Pandas package to compare two tables with simular schema but different data.

#### Example A:

A simple example comparing two tables with identical schema and unique ids when using the ```ID``` and ```CODE``` fields
as composite keys 

**table A:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:|
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | MED | 13 |
3 | B| SALSA| MED| 2 |
4 | B | RODIN | LOW | 10 |

**table B:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:| 
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | HIGH | 15 |
3 | B| SALSA| MED| 8 |
4 | B | RODIN | LOW | 10 |
5 | B | DONGO | LOW | 5 | 

to compare we run the script like this:

```
csv_diff.py 'c:/data/table_a.csv' 'c:/data/table_b.csv' 
   'c:/data/diff_table.csv' 'idfield1' 'idfield2' --namea 'tableA'
   --nameb 'tableB'
```

**Results in the Data Diff Comparison:**

| ID | CODE | NAME | GROUP | VAL | *Version* | **has_change**
|---:|-----:|:-----:|:---:|:----:|:---:|:----:|
| 1  | A    | FOO   | HIGH| 5 | tableA > tableB | N |
| 2| A| BAR | MED --> HIGH | 13 --> 15 | tableA > tableB | **Y**
3 | B| SALSA| MED| 2 --> 8 | tableA > tableB | **Y** |
4 | B | RODIN | LOW | 10 | tableA > tableB | N |
5 | B | DONGO | LOW | 5 | tableB | N/A |

#### Example B:

A simple example of comparing "dirty" data, where the schema of the two tables does not match 
and the index fields are not quite unique:

**table A:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:|
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | MED | 13 |
3 | B| SALSA| MED| 2 |
4 | B | RODIN | LOW | 10 |

**table B:**

| ID | CODE | NAME | GROUP | VAL | 
|---:|-----:|:-----:|:---:|:----:| 
| 1  | A    | FOO   | HIGH| 5 | 
| 2| A| BAR | HIGH | 15 |
3 | B| SALSA| MED| 8 |
4 | B | RODIN | LOW | 10 |
5 | B | DONGO | LOW | 5 | 

to compare we run the script like this:

```
csv_diff.py 'c:/data/table_a.csv' 'c:/data/table_b.csv' 
   'c:/data/diff_table.csv' 'idfield1' 'idfield2' --namea 'results'
   --nameb 'solution'
```

**Results in the Data Diff Comparison:**

| ID | CODE | NAME | GROUP | VAL | *Version* | **has_change**
|---:|-----:|:-----:|:---:|:----:|:---:|:----:|
| 1  | A    | FOO   | HIGH| 5 | tableA > tableB | N |
| 2| A| BAR | MED --> HIGH | 13 --> 15 | tableA > tableB | **Y**
3 | B| SALSA| MED| 2 --> 8 | tableA > tableB | **Y** |
4 | B | RODIN | LOW | 10 | tableA > tableB | N |
5 | B | DONGO | LOW | 5 | tableB | N/A |
