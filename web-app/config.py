import toml
from config_util import (getenv_bool, getenv_int, getenv_switch_str)

ST_CONFIG = toml.load(".streamlit/config.toml")

PRODUCTION = getenv_bool("PRODUCTION", False)

WEBSERVICE_NAME = "SimPay"
WEBSERVICE_ICON = "💸"

SENDER_EMAIL_ADDRESS = "user.study.totp.authentication@gmail.com"
SENDER_EMAIL_NAME = WEBSERVICE_NAME
SMTP_SERVER = "smtp.gmail.com"
URL_BASE = "http://localhost:8501/"
PATH_TO_USER_DB_CSV = "volume/user_info.csv"
PATH_TO_EMAIL_PW_FILE = "gmail_pw.txt"
PATH_TO_USAGE_TRACKING_FILE = "volume/usage_tracking.csv"
PATH_TO_TRANSACTIONS_DIR = "volume/transactions"
PATH_TO_DOWNLOAD = "volume/download"

COLOR_PRIMARY = ST_CONFIG["theme"]["primaryColor"]
COLOR_SECONDARY = ST_CONFIG["theme"]["textColor"]
COLOR_BACKGROUND = ST_CONFIG["theme"]["backgroundColor"]
COLOR_SECONDARY_BACKGROUND = ST_CONFIG["theme"]["secondaryBackgroundColor"]
COLOR_OUTGOING_MONEY = "#ff4545"
COLOR_GREY_TEXT = "#ABABAB"

LENGHT_OF_STUDY_PHASE_2_IN_DAYS = 6  # DO NOT CHANGE WHEN STUDY STARTED!!!

if PRODUCTION:
    URL_BASE = "https://totp-study.informatik.tu-freiberg.de/"
    PATH_TO_USER_DB_CSV = "/share/volume/user_info.csv"
    PATH_TO_EMAIL_PW_FILE = "/share/volume/gmail_pw.txt"
    PATH_TO_USAGE_TRACKING_FILE = "/share/volume/usage_tracking.csv"
    PATH_TO_TRANSACTIONS_DIR = "/share/volume/transactions"
    PATH_TO_DOWNLOAD = "/share/volume/download"

# -------------------- Streamlit stuff -------------------- #

# Should the user see the hamburger menu in the top right corner:
HIDE_TOP_RIGHT_HAMBURGER_MENU = PRODUCTION

STREAMLIT_STYLE=f"""
    <style>
        {"#" if HIDE_TOP_RIGHT_HAMBURGER_MENU else ""}MainMenu {{visibility: hidden;}}

        .reportview-container {{
            margin-top: -2em;
        }}
        .stDeployButton {{display:none;}}
        #stDecoration {{display:none;}}

        a:link , a:visited{{
            color: #2e9aff;
            background-color: transparent;
            text-decoration: underline;
        }}

        .main > .block-container {{
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 4rem;
            padding-right: 4rem;
        }}
        header {{visibility: hidden;}}

        a:hover,  a:active {{
            color: #42D0C9;
            background-color: transparent;
            text-decoration: underline;
        }}

        footer {{visibility: hidden;}}
    </style>
"""

CUSTOM_FOOTER =f"""
    <style>
        html {{
            min-height: 100%;
        }}
        /* ------- Footer ------- */
        .footer {{
            position: fixed;
            margin-top: 40px;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: transparent;
            color: #666666;
            text-align: center;
        }}
        .footer a:link {{
            color: #666666;
        }}
        .footer a:visited {{
            color: #666666;
        }}
        .footer a:hover {{
            color: #dddddd;
        }}
        .footer a:active {{
            color: #dddddd;
        }}
    </style>
    <div class="footer">
        <p>
            <a href="/" target="_self">Anmeldung</a> &#160 | &#160
            <a href="/?page=about" target="_blank">Über die Studie</a> &#160 | &#160 
            <a href="/?page=contact" target="_blank">Kontakt</a>
        </p>
    </div>
"""
