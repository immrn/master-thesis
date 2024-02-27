import pandas as pd


# maybe I can reuse
def count_transaction_days():
    today_date = pd.Timestamp.utcnow().date()

    # Get registration date of the user:
    user_id = st.session_state[SessionStateKey.Common.user_id]
    user = um.Users.get_user_by("id", user_id)
    registration_date = user["reg_timestamp_utc"].date()

    # Count all transaction (ta) days:
    df = um.Users.df_transaction(user_id)
    ta_dates = pd.Series(df.index.map(pd.Timestamp.date).unique())
    # ta_dates[len(ta_dates)] = registration_date
    ta_dates = pd.to_datetime(ta_dates)
    min_date = registration_date # ta_dates.min()
    max_date = today_date # ta_dates.max()
    all_dates = pd.date_range(min_date, max_date, freq='D').tolist()
    ta_dates = ta_dates.tolist()
    non_ta_dates = [d for d in all_dates if d not in ta_dates]
    
    all_dates = [d.date() for d in all_dates]
    ta_dates = [d.date() for d in ta_dates]
    non_ta_dates = [d.date() for d in non_ta_dates]

    sorted(ta_dates)
    sorted(non_ta_dates)

    print(ta_dates)
    print(non_ta_dates)

    if ta_dates and ta_dates[-1] < dt.datetime.utcnow().date():
        print("u missed it")