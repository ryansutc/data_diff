import pandas as pd

tbl_a = r"C:\Users\RSutcliffe\Desktop\github\data_diff\data\tableA.csv"  # args.results
tbl_b = r"C:\Users\RSutcliffe\Desktop\github\data_diff\data\tableA.csv"  # args.results
index_fields = ["ID", "IDPt2"]
df_a = pd.read_csv(tbl_a, index_col=index_fields)
df_b = pd.read_csv(tbl_b, index_col=index_fields)

#print df_a
if df_a.dtypes.equals(df_b.dtypes):
    print "Match!!1"


'''
schema_a = pd.DataFrame.from_dict(data=dict(df_a.dtypes),
                                  orient="index",
                                  columns=["NumpyType"])
print schema_a
'''