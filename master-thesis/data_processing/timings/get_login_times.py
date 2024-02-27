import pandas as pd

pd.options.display.max_rows = 999

# Load data:
df = pd.read_csv("./cleaned_data/usage_tracking_stage_2.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df[df["action"].isin(["entered_valid_credentials", "entered_valid_totp"])]

df.sort_values(by=['group', 'timestamp'], inplace=True)

grouped = df.groupby('group')

# Define a function to filter rows for each group:
def filter_rows(group):
    mask = (group['action'] == 'entered_valid_credentials') & (group['action'].shift(-1) != 'entered_valid_totp')
    return group[~mask]

# Apply the function to each group and concatenate the results:
filtered_df = pd.concat([filter_rows(group) for _, group in grouped])

filtered_df.sort_values(by=["group", 'timestamp'], inplace=True)
filtered_df = filtered_df.groupby('group').head(2)

filtered_df['time_totp'] = filtered_df.groupby(['group'])['timestamp'].diff()

filtered_df = filtered_df[filtered_df["action"] == "entered_valid_totp"]
filtered_df = filtered_df.sort_values(by=["timestamp"])

filtered_df.to_csv("./cleaned_data/totp_times.csv", index=False)
print(f"saved auth times in ./cleaned_data/totp_times.csv")