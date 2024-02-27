import pandas as pd


rename = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]

setup = pd.read_csv("setup_sus.csv")
# Rename columns
for idx, i in enumerate(rename):
    setup = setup.rename(columns={f"SUS[SQ0{i}]": str(idx+1)})

usage_trad = pd.read_csv("usage_trad_sus.csv")
# Rename columns
for idx, i in enumerate(rename):
    usage_trad = usage_trad.rename(columns={f"SUStrad[SQ0{i}]": str(idx+1)})

usage_bt = pd.read_csv("usage_bt_sus.csv")
# Rename columns
for idx, i in enumerate(rename):
    usage_bt = usage_bt.rename(columns={f"SUSbt[SQ0{i}]": str(idx+1)})

dfs = [setup, usage_trad, usage_bt]
for i in range(len(dfs)):
    # Replace the limesurvey string with values
    dfs[i] = dfs[i].replace("AO01", 0)
    dfs[i] = dfs[i].replace("AO02", 1)
    dfs[i] = dfs[i].replace("AO03", 2)
    dfs[i] = dfs[i].replace("AO04", 3)
    dfs[i] = dfs[i].replace("AO05", 4)
    print(dfs[i])

    # Invert the speicic values of questions 2,4,6,8,10
    invert = ["2","4","6","8","10"]
    for j in invert:
        dfs[i][j] = 4 - dfs[i][j]
    print(dfs[i])
    print("\n")

dfs[0].to_csv("../transformed/setup_sus_with_inversions.csv", index=False)
dfs[1].to_csv("../transformed/usage_trad_sus_with_inversions.csv", index=False)
dfs[2].to_csv("../transformed/usage_bt_sus_with_inversions.csv", index=False)