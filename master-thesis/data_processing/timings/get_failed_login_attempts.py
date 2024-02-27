import pandas as pd

pd.options.display.max_rows = 999
pd.options.display.max_columns = None

login_fails_str = ""

df = pd.read_csv("./cleaned_data/usage_tracking_stage_2.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Remove participant 9, because they didn't login in using Bluetooth:
df = df[~(df["id"] == 9)]

# Delete all "entered_valid_credentials" per group if they are not followed by a "entered_valid_totp" within that group:
df.sort_values(by=['group', 'timestamp'], ascending=[True, False], inplace=True)
for group in df["group"].unique():
    for index, row in df[df["group"] == group].iterrows():
        if row["action"] == "entered_valid_credentials":
            df.drop(index, inplace=True)
        else:
            break
df.sort_values(["group","timestamp"], inplace=True)

# Sum of all failed login attemps due no or wrong totp input:
success_count = df[df["action"] == "entered_valid_totp"]["action"].count()
fails = df[df["action"] == "entered_valid_credentials"]["action"].count() - success_count
login_fails_str += f"Sum of all failed login attemps due no or wrong totp input:\n{fails}\n\n"

# Count of sessions where the login failed at least one time
login_fails_str += "Count of sessions where the login failed at least one time (due no or wrong totp input):\n"
# 1. Calculate the difference between the sum of 'entered_valid_credentials' and 'entered_valid_totp' for each group
grouped_df = df.groupby('group').apply(lambda x: x[x['action'] == 'entered_valid_credentials'].shape[0] - x[x['action'] == 'entered_valid_totp'].shape[0])
# 2. Count the groups with a sum greater than 0
login_fails_str += str((grouped_df > 0).sum()) + "\n"

with open("results/login_fails.txt", "w") as file:
    file.write(login_fails_str)
    print("- Saved failed login data in results/login_fails.txt")