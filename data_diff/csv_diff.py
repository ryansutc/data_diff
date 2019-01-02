#!/usr/bin/env python
from warnings import filterwarnings, simplefilter
filterwarnings("ignore", message="numpy.dtype size changed")
filterwarnings("ignore", message="numpy.ufunc size changed")
simplefilter(action='ignore', category=FutureWarning)

from os import path
import pandas as pd
import argparse
import hashlib

global compare_cols

def __report_diff(x):
    if x.name[1] in compare_cols:
        return x[0] if x[0] == x[1] else '{} <> {}'.format(*x)
    else:
        return x[1] if x.isnull()[0] else x[0]
################

def __has_change(row, tableAname, tableBname):

    if "<>" in row.to_string():
        return "%s <> %s" % (tableAname, tableBname)
    else:
        return "%s == %s" % (tableAname, tableBname)
###############

def __calc_hash(row):
    """
    calculate a hash field based on the compare fields

    :param row: input row being analyzed
    :rtype: object
    """
    vals = [str(val) for index, val in row.iteritems() if index in compare_cols]
    return hashlib.sha1(", ".join(vals).encode('utf-8')).hexdigest()


###############
def create_comparison(df_1, df_2, name1, name2):
    ''''
    Merge two tables, matching records based on the
    index and comparing the differences

    :return dataframe
    '''

    # Add a results field
    df_1['compare'] = name1 + "--> ???"
    df_2['compare'] = name2 + "--> ???"

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
        diff_output = diff_panel.apply(__report_diff, axis=0)

        #update compare field:
        diff_output["compare"] = diff_output.apply(__has_change, axis=1, args=(name1, name2))
        # strip duplicates from big table so that only unique orphans left:
        full_set = full_set.loc[~full_set.index.isin(dup_indexes)]

        # add orphans to output table:
        comparison = pd.concat([diff_output, full_set])
    else:
        comparison = full_set

    return comparison

def __reorder_columns(input_df):
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

def __fix_order_columns(comparison_tblcols):
    """

    :return: reordered list of column names for comparison_tbl
    this puts the bastard_fields at the end after the compare field
    """
    cols = compare_cols + ['compare']
    bastard_fields = set(comparison_tblcols).difference(set(cols))

    cols += list(bastard_fields)
    return cols
########

def data_diff(tbl_a, tbl_b, index_fields, tableAname="Table A", tableBname="Table B", output=None, dirty=False):
    """
    Function that takes two tables and compares them based on some index fields and returns the result
    as a pandas dataframe object as well as optionally outputing a difference/comparison table in csv
    form

    :param tbl_a: first input table (.csv)
    :param tbl_b: second input table (.csv)
    :param tableAname: name of table
    :param tableBname:
    :param index_fields: list of index fields
    :param output: filepath for output csv (optional)
    :param dirty: whether to try to deal with dirty data and indexes that aren't unique
    :return: returns a pandas dataframe object of the output table
    """

    # Make sure files exist
    try:
        if output:
            if not path.exists(path.split(output)[0]):
                msg = "output is not a valid directory: " + output
                raise OSError(msg)

        # import tables as pandas dataframes:
        df_a = pd.read_csv(tbl_a) #, index_col=index_fields)
        df_b = pd.read_csv(tbl_b) #, index_col=index_fields)
    except IOError as e:
        msg = "Error loading data: " + e.message
        print(msg)
        raise IOError(msg)

    # add index to dataframes, throw error if index field(s) not found:
    try:
        df_a.set_index(keys=index_fields, inplace=True)
        df_b.set_index(keys=index_fields, inplace=True)
    except KeyError as e:
        print("One or more index fields do not exist: %s") % e.message
        raise SystemExit(1)

    # Make sure Indexes are unique (if not dirty)
    if not dirty:
        if df_a.index.has_duplicates:
            print("Error: table A does not have a unique index. quitting...")
            raise SystemExit(1)
        if df_b.index.has_duplicates:
            print("Error: table B does not have a unique index. quitting...")
            raise SystemExit(1)

    # indexes good, lets drop them for now..
    df_a.reset_index(inplace=True)
    df_b.reset_index(inplace=True)

    print("processing...")
    # Determine what columns each input table has in common ("comparable fields"):
    global compare_cols
    compare_cols = [col for col in df_a.columns.values if col in
               list(set(df_a.columns.values).intersection(set(df_b.columns.values)))]
    df_a = __reorder_columns(df_a)
    df_b = __reorder_columns(df_b)

    if not df_a.dtypes.equals(df_b.dtypes):
        msg = "table A and B do not have exactly matching fields. Only comparing common fields.."
        print(msg)

    df_a.reset_index(inplace=True)
    df_b.reset_index(inplace=True)
    # create a hash ID value for all comparable fields and use it as index
    df_a["hash"] = df_a.apply(__calc_hash, axis=1)
    df_b["hash"] = df_b.apply(__calc_hash, axis=1)
    df_a.set_index(keys="hash", inplace=True)
    df_b.set_index(keys="hash", inplace=True)

    # Check for duplicate hashes. If they exist, remove them & warn user.
    if df_a.index.has_duplicates:
        orig_len_a = df_a.shape[0]
        df_a = df_a[~df_a.duplicated(keep='first')]
        msg = "warning: removed %s duplicate rows from %s" % (orig_len_a - df_a.shape[0], tableAname)
        print(msg)
    if df_b.index.has_duplicates:
        orig_len_b = df_b.shape[0]
        df_b = df_b[~df_b.duplicated(keep='first')]
        msg = "warning: removed %s duplicate rows from %s" % (orig_len_b - df_b.shape[0], tableBname)
        print(msg)

    # find hash values present in both tables (ie matching rows)
    matches = df_a.index[df_a.index.isin(df_b.index)]
    # make copies of these matches & run compare on them (comparison_tbl):
    df_a_matches = df_a[df_a.index.isin(matches)].copy(deep=True)
    df_a = df_a[~df_a.index.isin(matches)]
    df_b_matches = df_b[df_b.index.isin(matches)].copy(deep=True)
    df_b = df_b[~df_b.index.isin(matches)]

    # run comparison
    comparison_tbl = create_comparison(df_a_matches, df_b_matches, tableAname, tableBname)
    del df_a_matches, df_b_matches
    comparison_tbl.reset_index(inplace=True)
    comparison_tbl.set_index(keys=index_fields, inplace=True)

    df_a.reset_index(inplace=True)
    df_b.reset_index(inplace=True)
    df_a.set_index(keys=index_fields, inplace=True)
    df_b.set_index(keys=index_fields, inplace=True)

    # Check for a non-unique primary key/indexes. If they exist we extract all
    # instances of them. These are the CNCs or Uncomparables.
    if dirty:
        # strip uncomparables (dup ids within table) to new dataframes:
        df_a_dups = df_a[df_a.index.duplicated(keep=False)]
        df_a = df_a[~df_a.index.duplicated(keep=False)]
        df_b_dups = df_b[df_b.index.duplicated(keep=False)]
        df_b = df_b[~df_b.index.duplicated(keep=False)]

        # Lets also pull matching index from table a where
        # table_b had dups and vice versa b/c these are also
        # uncomparables:
        df_a_dups = df_a_dups.append(df_a[df_a.index.isin(df_b_dups.index)])
        df_a = df_a[~df_a.index.isin(df_b_dups.index)]
        df_b_dups = df_b_dups.append(df_b[df_b.index.isin(df_a_dups.index)])
        df_b = df_b[~df_b.index.isin(df_a_dups.index)]

        if df_a_dups.shape[0] > 0:

            df_a_dups['compare'] = tableAname + "--> [CNC]"
            # append these uncomparables to the output comparison dataframe:
            comparison_tbl = comparison_tbl.append(df_a_dups)

        if df_b_dups.shape[0] > 0:
            df_b_dups['compare'] = tableBname + "--> [CNC]"
            # append these uncomparables to the output comparison dataframe:
            comparison_tbl = comparison_tbl.append(df_b_dups)

    # Now lets look at all matching records. (Same Index exists in both tables,
    # but not necessarily identical data...)
    comparison_tbl = comparison_tbl.append(create_comparison(df_a, df_b, tableAname, tableBname))
    comparison_tbl.drop(["hash", "index"], inplace=True, axis=1)
    comparison_tbl.reset_index(inplace=True)
    comparison_tbl = comparison_tbl[__fix_order_columns(comparison_tbl.columns)]
    comparison_tbl.sort_values(by=index_fields, inplace=True)

    if output:
        comparison_tbl.to_csv(output)
    else:
        print(comparison_tbl)
    print("done.")
    return comparison_tbl

###################################
def main():

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
    parser.add_argument("-o", "--output", required=True,
                        help="<Required> the output path for your diff csv file.")
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

    tbl_a = args.tablea.replace("'","").replace('"','')
    tbl_b = args.tableb.replace("'","").replace('"','')
    output = str(args.output).replace("'","").replace('"','')
    index_fields = ['{0}'.format(s).replace("'","") for s in args.index]  # list of fields

    if args.namea:
        tableAname = args.namea.replace("'","'").replace('"','')
    else:
        tableAname = "tblA " + path.split(tbl_a)[1]
    if args.nameb:
        tableBname = args.nameb.replace("'","'").replace('"','')
    else:
        tableBname = "tblB " + path.split(tbl_b)[1]
    if args.dirty:
        dirty = True
    else:
        dirty = False

    data_diff(tbl_a, tbl_b, index_fields, tableAname, tableBname, output, dirty)


if __name__ == '__main__':
    main()



