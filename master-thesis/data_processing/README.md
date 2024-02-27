Just do the following steps if you want to reproduce the data. It's not fully automated and needs time because you have to delete some rows manually.

## Setup
- change dir into `data_processing`
```bash
python3.12 -m venv venv
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Timings
- change dir into `timings/` and run the scripts in the following order:
1. `$ python get_tracking_stage_1.py`
3. `$ python get_tracking_stage_2.py`
    - it also prints a dataframe into the console where the column `group_count` stands for the count of measurements that have been produced by each id (each individual participant)
4. `$ python get_failed_login_attempts.py`
5. `$ python get_login_times.py`
6. `$ python plot_timings.py`
7. `$ python plot_setup_timings.py`
- You can find the results in dir `timings/results/`

## Questionaires
- change dir into `questionaires/`
1. change dir into `limesurvey` and run:
    - `$ python sus_transform_values.py`
    - `$ python sus_11_transform_values.py`
    - `$ python ueq_transform_values.py`
    - then you will find new data in `questionaires/transformed/`
2. change dir into `questionaires/transformed` and run:
    - `$ python sus_make_results`
3. in `transformed/` you find the UEQs (3 csv-files with `ueq` in their names)
    - copy their values to their respective excel file in `results/`
    - each excel file has a data sheet, where you input the data
    - you can use the compare excel file to compare the usage of Blue TOTP (bt) and traditional TOTP apps (trad)
    - After putting in the data, the excel will do all the calculations for you. Look at the others sheets for the results.

## Interview
- change dir into `interviews/` and run:
1. `$ python describe_exit_meeting.py`
- their you will find the `exit_meeting_statistics.csv`