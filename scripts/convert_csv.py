import pandas as pd


df = pd.read_csv("section2-221-Spring26.csv")
df_new = pd.DataFrame()
df_new["email"] = df["Email"]
df_new["condition"] = (df.index % 3) + 1
#.drop(columns=["Email", "OrgDefinedId","Last Name","First Name","End-of-Line Indicator"])

df_new.to_csv("section2_cleaned.csv")
