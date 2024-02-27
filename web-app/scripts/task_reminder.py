# Run this script at 20:00:00 UTC every day
# It reminds users who haven't made a transaction today

import pandas as pd
import datetime as dt

import task_util
from user_management import Users
import config


today_date = pd.Timestamp.utcnow().date()
user_ids = Users.df().index.tolist()
bcc = []

for user_id in user_ids:
    # Get registration date of the user:
    user = Users.get_user_by("id", user_id)
    registration_date = user[Users.Col.reg_timestamp_utc].date()

    if registration_date + dt.timedelta(days=config.LENGHT_OF_STUDY_PHASE_2_IN_DAYS) < today_date:
        continue  # user finished 2. phase of the study

    # Get last transaction (ta) date:
    df = Users.df_transaction(user_id)
    df = df.sort_index(ascending=True)
    if not df.empty:
        last_ta_date = df.index[-1].date()
    else:
        last_ta_date = None

    if today_date > registration_date and (not last_ta_date or last_ta_date < today_date):
        # user missed it to do a transaction until now for today -> remind them:
        bcc += [user[Users.Col.email]]


task_util.send_task_email(
    path_to_html="./scripts/task_reminder_email.html",
    bcc_list=bcc,
    subject="Erinnerung an Ihre heutige Aufgabe",
    increment_counter=True
)
