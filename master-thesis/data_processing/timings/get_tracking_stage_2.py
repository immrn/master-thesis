import pandas as pd
import numpy as np
import datetime as dt

# pd.options.display.max_rows = 999
pd.options.display.max_columns = None

df = pd.read_csv("./cleaned_data/usage_tracking_stage_1.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# df["id"] = df["id"].replace('-', np.nan)
# df["id"] = df["id"].fillna(method='bfill')

df = df.sort_values(by=['id', 'timestamp'])
df['time_diff'] = df.groupby('id')['timestamp'].diff()
df['group'] = ((df['time_diff'] > pd.Timedelta(hours=1)) | (df['time_diff'].isnull())).cumsum()
df = df.drop(['time_diff'], axis=1)

counter_df = df.groupby('id')['group'].nunique().reset_index(name='group_count')

# Some participants made more logins after the study was finished, delete the additional logins:
users = pd.read_csv("./raw_data/user_info.csv")
users = users.set_index("id")
users = users[["reg_timestamp_utc"]]
users["reg_timestamp_utc"] = pd.to_datetime(users["reg_timestamp_utc"])
users["date"] = users["reg_timestamp_utc"].dt.date
df["date"] = df["timestamp"].dt.date
for id in users.index:
    if counter_df.loc[counter_df["id"] == id, "group_count"].iloc[0] > 6:
        cutoff_date = users.at[id, "date"] + dt.timedelta(days=6)
        df = df[(df['id'] != id) | (df['date'] <= cutoff_date)]

print(df.groupby('id')['group'].nunique().reset_index(name='group_count'))

df.to_csv("./cleaned_data/usage_tracking_stage_2.csv", index=False)
print(f"created usage tracking stage 2 at ./cleaned_data/usage_tracking_stage_2.csv")