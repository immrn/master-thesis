import pandas as pd

rename = [str(i) for i in range(10,36)]

setup = pd.read_csv("setup_ueq.csv")
# Rename columns
for idx, i in enumerate(rename):
    setup = setup.rename(columns={f"UEQ[SQ0{i}]": str(idx+1)})

usage_trad = pd.read_csv("usage_trad_ueq.csv")
# Rename columns
for idx, i in enumerate(rename):
    usage_trad = usage_trad.rename(columns={f"UEQtrad[SQ0{i}]": str(idx+1)})
# Remove participant with id == 9 because they didn't use blue totp properly
usage_trad = usage_trad[~(usage_trad["id"] == 9)]

usage_bt = pd.read_csv("usage_bt_ueq.csv")
# Rename columns
for idx, i in enumerate(rename):
    usage_bt = usage_bt.rename(columns={f"UEQbt[SQ0{i}]": str(idx+1)})
# Remove participant with id == 9 because they didn't use blue totp properly
usage_bt = usage_bt[~(usage_bt["id"] == 9)]

dfs = [setup, usage_trad, usage_bt]
for i in range(len(dfs)):
    print(dfs[i])
    # Replace the limesurvey string with values
    dfs[i] = dfs[i].replace("AO01", 1)
    dfs[i] = dfs[i].replace("AO02", 2)
    dfs[i] = dfs[i].replace("AO03", 3)
    dfs[i] = dfs[i].replace("AO04", 4)
    dfs[i] = dfs[i].replace("AO05", 5)
    dfs[i] = dfs[i].replace("AO06", 6)
    dfs[i] = dfs[i].replace("AO07", 7)
    print(dfs[i])

    # Invertion not necesarry, the excel file of ueq does it already

dfs[0].to_csv("../transformed/setup_ueq.csv", index=False)
dfs[1].to_csv("../transformed/usage_trad_ueq.csv", index=False)
dfs[2].to_csv("../transformed/usage_bt_ueq.csv", index=False)