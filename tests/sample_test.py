from data_diff import csv_diff
import pandas as pd


def test_sample():
    # Compare tool result output to expected answer for simple data:
    df_output = csv_diff.data_diff("./data/tableA.csv",
                                   "./data/tableB.csv",
                                   ["ID", "CODE"],
                                   "tableA",
                                   "tableB")

    df_output.set_index(keys=["ID","CODE"], inplace=True)
    answer = pd.read_csv("./data/diff_table.csv")
    answer.set_index(keys=["ID", "CODE"], inplace=True)
    print(answer)
    pd.testing.assert_frame_equal(df_output, answer, check_index_type=False, check_dtype=False, check_like=True,
                                  check_names=False)


def test_sample_dirty():
    # Compare tool result output to expected answer for dirty data:
    df_output = csv_diff.data_diff("./data/tableAdirty.csv",
                                   "./data/tableBdirty.csv",
                                   ["ID", "CODE"],
                                   "tableA",
                                   "tableB",
                                   dirty=True)
    df_output.reset_index(drop=True,inplace=True)
    answer = pd.read_csv("./data/diff_table_dirty.csv")
    print(answer)

    for fld in answer.columns.values:
        if map(str, list(df_output[fld].values)) != map(str, list(answer[fld].values)):
            raise ValueError("Mismatch in values in " + fld)
