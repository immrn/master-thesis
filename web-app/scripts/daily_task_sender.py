# Run this script at 00:00:00 UTC every day

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

    if registration_date + dt.timedelta(days=config.LENGHT_OF_STUDY_PHASE_2_IN_DAYS) >= today_date:
        # user is still doing 2. phase of the study
        bcc += [user[Users.Col.email]]

task_util.send_task_email(
    path_to_html="./scripts/daily_task_email.html",
    bcc_list=bcc,
    subject="Ihre heutige Aufgabe",
    increment_counter=False
)