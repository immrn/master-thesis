import pandas as pd

setup = pd.read_csv("setup_sus_11.csv")
setup = setup.rename(columns={"SUS11[SQ001]": "11"})
usage_trad = pd.read_csv("usage_trad_sus_11.csv")
usage_trad = usage_trad.rename(columns={"SUS11trad[SQ001]": "11"})
usage_bt = pd.read_csv("usage_bt_sus_11.csv")
usage_bt = usage_bt.rename(columns={"SUS11bt[SQ001]": "11"})

dfs = [setup, usage_trad, usage_bt]

for i in range(len(dfs)):
    # Replace the limesurvey string with values
    dfs[i] = dfs[i].replace("AO01", 25)
    dfs[i] = dfs[i].replace("AO02", 30)
    dfs[i] = dfs[i].replace("AO03", 38)
    dfs[i] = dfs[i].replace("AO04", 52)
    dfs[i] = dfs[i].replace("AO05", 73)
    dfs[i] = dfs[i].replace("AO06", 85)
    dfs[i] = dfs[i].replace("AO07", 100)
    print(dfs[i])


dfs[0].to_csv("../transformed/setup_sus_11.csv", index=False)
dfs[1].to_csv("../transformed/usage_trad_sus_11.csv", index=False)
dfs[2].to_csv("../transformed/usage_bt_sus_11.csv", index=False)