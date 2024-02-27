# web-app

## Prerequisites
- install Python 3.11
- if using linux maybe you need to install python3.11-venv
- look at the `config.py` and you will find the variable `PATH_TO_EMAIL_PW_FILE`.
    - it should be a path: at the path create the file and dump a application password for the email you will be using at `SENDER_EMAIL_ADDRESS`
    - please create a new email account for it, you don't wanna give people access to your private email account accidently


## Local Development & Execution (using bash)
On Windows `./venv/bin` should be `./venv/Scripts`

```bash
python3.11 -m venv venv
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
streamlit run main.py
```

## Do these things on your remote machine where you host the web app:
- `$ export PRODUCTION="True"`
- Do this step ONLY IF YOU WANNA SEND DAILY mails `$ cron` to start the cron process (when you are using a docker container, otherwise add cron to your init daemon)
    - you can see the emails html files at `html/`
- copy the parent dir `web-app` to your remote machine (explanation below)
- copy the content of `web-app/scripts/crontab` into the editor opened by the command `crontab -e`
- `$ sh setup.sh`
- start or resume to a screen and run the web app (look below)

### screen (it's like running parallel terminals):
- `$ screen -S SESSION_NAME` create session
- `$ screen -ls` list sessions
- `$ screen -d ID` or `CTRL + A + D` detach from session
- `$ screen -r ID` resume to screen

### actually run the web app:
- `$ . ./venv/bin/activate`
- change the following port and address on your needs:
    - `$ streamlit run main.py --server.port=443 --server.address=0.0.0.0`

### Copy things using secure shell copy:
- copy files: `scp -P PORT PATH_SOURCE USER@DOMAIN:/PATH/TO/ANYTHING`


## Management
### Remove a user:
`$ python scripts/rm_user.py USER_ID` will remove the user from `user_info.csv` and `transactions/USER_ID.csv`