import pandas as pd
import datetime as dt

# load user data:
users = pd.read_csv("./raw_data/user_info.csv")
users = users.set_index("id")
users = users[["reg_timestamp_utc"]]
users["reg_timestamp_utc"] = pd.to_datetime(users["reg_timestamp_utc"])
users = users[users.index != 0]  # 0 is no real participant
users["date"] = users["reg_timestamp_utc"].dt.date

df = pd.read_csv("./raw_data/usage_tracking.csv", sep=";")
df = df.drop(["remark", "st_key", "value"], axis=1)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[df['id'] != "0"]  # 0 is no real participant
# keep only necessary actions:
df = df[~df['action'].isin(["loaded_login", "edited_text", "clicked", "logout", "finished_totp_setup"])]
df = df.drop_duplicates()  # logging produced sometimes duplicates

# add date column:
df["date"] = df["timestamp"].dt.date

for id in users.index:
    reg_date = users.at[id, "date"]
    # remove all logging data of the participant (id) at registration date:
    df = df[~((df["id"] == str(id)) & (df["date"] == reg_date))]

df = df.drop_duplicates()

df = df.drop(["date"], axis=1)

df.to_csv("./cleaned_data/usage_tracking_stage_1.csv", index=False)
print(f"created usage tracking stage 1 at ./cleaned_data/usage_tracking_stage_1.csv")