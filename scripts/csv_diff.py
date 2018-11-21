import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import os
import sys
import inspect
import pandas as pd
import xarray
import argparse
import csv
import hashlib

global compare_cols

def report_diff(x):
    if x.name[1] in compare_cols:
        return x[0] if x[0] == x[1] else '{} --> {}'.format(*x)
    else:
        return x[1] if x.isnull()[0] else x[0]
################

def has_change(row):
    print type(row)
    print row
    if "-->" in row.to_string():
        return "Y"
    else:
        return "N"
###############

def calc_hash(row):
    vals = [str(val) for index, val in row.iteritems() if index in compare_cols]
    return hashlib.sha1(", ".join(vals)).hexdigest()


###############
def create_comparison(df_1, df_2, name1= "Table A", name2 = "Table B"):
    ''''
    Merge two tables, matching records based on the
    index and comparing the differences

    :return dataframe
    '''

    # Add a results field
    df_1['version'] = name1
    df_2['version'] = name2

    # Make a big table of all data:
    full_set = pd.concat([df_1, df_2], sort=False)

    # get a list of duplicate/ matching indexes from combined table:
    dup_indexes = full_set[full_set.index.duplicated()].index

    if dup_indexes.shape[0] > 0:
        # strip orig tables to duplicate/matching records only
        df_1 = df_1.loc[dup_indexes]
        df_2 = df_2.loc[dup_indexes]

        # combine table in 3 dimensional panel [todo: update]
        diff_panel = pd.Panel(dict(name2=df_2, name1=df_1))

        # merge 3d panel into diff table:
        diff_output = diff_panel.apply(report_diff, axis=0)
        diff_output["version"] = "%s > %s" % (name1, name2)
        diff_output["has_change"] = diff_output.apply(has_change, axis=1)

        # strip duplicates from big table so that only unique orphans left:
        full_set = full_set.loc[~full_set.index.isin(dup_indexes)]
        full_set['has_change'] = "N/A"

        # add orphans to output table:
        comparison = pd.concat([diff_output, full_set])
    else:
        full_set['has_change'] = "N/A"
        comparison = full_set

    return comparison


def reorder_columns(input_df):
    """
    reorder compare_cols in input_df to match order in global "compare_cols"
    variable.

    :param input_df: input dataframe to be rearranged
    :return: input_df reordered

    :remarks: uses global variable compare_cols
    """

    bastard_fields = list(set(input_df.columns.values).difference(compare_cols))

    newlist = list(compare_cols)
    newlist.extend(bastard_fields)

    return input_df[newlist]


##################
if __name__ == '__main__':

    '''
    # Command line now: we expect an argument:
    parser = argparse.ArgumentParser(prog="Data Diff",
                                     description="Compare two csv files for changes",
                                     epilog="Example: csv_diff.py 'c:/data/table_a.csv' 'c:/data/table_b.csv'" +
                                            " 'c:/data/diff_table.csv' 'idfield1' 'idfield2' -a 'results' " +
                                            " -b 'solution'")
    parser.add_argument("tablea",
                        help="<Required> the full path to table A, your first csv file.")
    parser.add_argument("tableb",
                        help="<Required> the full path to table B, your next csv file.")
    parser.add_argument("output",
                        help="<Required> the output path to your diff csv file.")
    parser.add_argument("index", nargs='+',  # at least 1 field
                        help="<Required> the field(s) that make up the row ID and define the diff comparison. " +
                        "List each field separated by a space (\"field1\" \"field2\" etc.). Case Sensitive!)")
    parser.add_argument("-a", "--namea",
                        help="a custom name for your first csv file: tableA (default='tableA ' & filename of csv)")
    parser.add_argument("-b", "--nameb",
                        help="a custom name for your second csv file: tableB (default='tableB ' & filename of csv)")
    parser.add_argument("-d", "--dirty", action="store_true",
                        help="attempt comparison of input tables even if schema are not identical and " +
                             "index is not unique.")
    args = parser.parse_args()

    tbl_a = args.tablea
    tbl_b = args.tableb
    output = args.output
    index_fields = args.index  # list of fields
    if args.namea:
        tableAname = args.namea
    else:
        tableAname = "tableA " + os.path.split(tbl_a)[1]
    if args.nameb:
        tableBname = args.nameb
    else:
        tableBname = "tableB " + os.path.split(tbl_b)[1]
    if args.dirty:
        dirty = True
    else:
        dirty = False
    '''
    tbl_a = r"C:\Users\RSutcliffe\Desktop\github\data_diff\data\tableAdirty.csv" #args.results
    tbl_b = r"C:\Users\RSutcliffe\Desktop\github\data_diff\data\tableBdirty.csv" #args.solution
    tableAname = "tableA"
    tableBname = "tableB"
    index_fields = ["ID", "CODE"]
    output = r"C:\Users\RSutcliffe\Desktop\github\data_diff\data\result.csv" #args.output
    dirty = True


    # Make sure files exist
    try:
        if not os.path.exists(os.path.split(output)[0]):
            msg = "output is not a valid directory: " + output
            raise OSError(msg)

        # import tables as pandas dataframes:
        df_a = pd.read_csv(tbl_a) #, index_col=index_fields)
        df_b = pd.read_csv(tbl_b) #, index_col=index_fields)
    except IOError as e:
        msg = "Error loading data: " + e.message
        print msg
        raise IOError(msg)

    global compare_cols
    if dirty:
        compare_cols = [col for col in df_a.columns.values if col in
                   list(set(df_a.columns.values).intersection(set(df_b.columns.values)))]
        df_a = reorder_columns(df_a)
        df_b = reorder_columns(df_b)
    else:
        # Ensure that two tables have matching schema:
        compare_cols = df_a.columns.tolist()
        df_b = reorder_columns(df_b)
        if not df_a.dtypes.equals(df_b.dtypes):
            msg = "table A and B do not have matching schemas. Columns must be in same order."
            print msg
            exit(1)

    # Remove completely duplicate rows: matching keys and values

    orig_len_a = df_a.shape[0]
    orig_len_b = df_b.shape[0]
    df_a = df_a[~df_a.duplicated(keep='first')]
    df_b = df_b[~df_b.duplicated(keep='first')]

    if orig_len_a != df_a.shape[0]:
        msg = "warning: table a removed %s duplicate rows" % (orig_len_a - df_a.shape[0])
        print msg
    if orig_len_b != df_b.shape[0]:
        msg = "warning: removed %s duplicate rows" % orig_len_b - df_b.shape[1]
        print msg


    if dirty:
        # lets try to find EXACT matches first. Since this will allow
        # us to at least join some of the duplicates.

        # create a hash ID from all combine_cols
        df_a["hash"] = df_a.apply(calc_hash, axis=1)
        df_b["hash"] = df_b.apply(calc_hash, axis=1)

        # find hash values present in both tables (ie matching rows)
        matches = df_a.loc[df_b["hash"].isin(df_a["hash"])]["hash"]

        # extract it from the original tables

    # add index to dataframes, throw error if index fields not found:
    try:
        df_a.set_index(keys=index_fields, inplace=True)
        df_b.set_index(keys=index_fields, inplace=True)
    except KeyError as e:
        print "One or more index fields do not exist: %s" % e.message
        raise SystemExit(1)

    # Check for a non-unique primary key/indexes. If they exist we extract all
    # instances of the duplicates
    df_a_hasdups = False
    df_b_hasdups = False
    if df_a.index.has_duplicates:
        if not dirty:
            print "Error: table A does not have a unique index. quitting..."
            raise SystemExit(1)
        msg = tbl_a + " does not have a unique index. extracting dups..."
        print msg
        df_a_dups = df_a[df_a.index.duplicated(keep=False)]
        df_a_dups.reset_index(inplace=True)
        df_a_hasdups = True
        df_a_dups['version'] = tableAname
        df_a = df_a[~df_a.index.duplicated(keep=False)]

    if df_b.index.has_duplicates:
        if not dirty:
            print "Error: table B does not have a unique index. quitting..."
            raise SystemExit(1)
        msg = tbl_b + " does not have a unique index. extracting dups..."
        print msg
        df_b_dups = df_b[df_b.index.duplicated(keep=False)]
        df_b_dups.reset_index(inplace=True)
        df_b_hasdups = True
        df_b_dups['version'] = tableBname
        df_b = df_b[~df_b.index.duplicated(keep=False)]



    # Create results table for unique records first:
    comparison_tbl = create_comparison(df_a, df_b, tableAname, tableBname)
    # drop the index. we don't need anymore:
    comparison_tbl.reset_index(inplace=True)

    # compare all the duplicate index records b/w two tables (orphans)
    if df_a_hasdups or df_b_hasdups:
        # if we have dups in BOTH a and b:
        if df_a_hasdups and df_b_hasdups:
            # need to compare the duplicate records by adding ALL fields to index
            # because we know at least that way it will be unique:
            df_a_dups.set_index(compare_cols, inplace=True)
            df_b_dups.set_index(compare_cols, inplace=True)

            comparison_dups = create_comparison(df_a_dups, df_b_dups, tableAname, tableBname)
            comparison_dups.reset_index(inplace=True)
            final_output = pd.concat([comparison_tbl, comparison_dups], sort=False)

        else:
            dups_final = df_a_dups if df_a_hasdups else df_b_dups
            final_output = pd.concat([comparison_tbl, dups_final], sort=False)
    else:
        final_output = comparison_tbl
    final_output = final_output.set_index(index_fields).sort_index()
    final_output.to_csv(output)
    print "done"

