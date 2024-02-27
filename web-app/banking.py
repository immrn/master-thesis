import streamlit as st
import time
import datetime as dt
import platform
from millify import millify
import pandas as pd

import util
import state
import config
import usage_tracking as track
import user_management as um
from constants import SessionStateKey


Key = SessionStateKey.Banking

TRANSACTION_SUCCESS = "transaction_success"
BALANCE_OVERDRAW = 10000

_RECIPIENT_HELP = "Geben Sie eine beliebige IBAN an.  \nDas ist keine echte Online-Zahlung."
_REFERENCE_HELP = "Geben Sie eine beliebige Nachricht an.  \nDas ist keine echte Online-Zahlung."
_VALUE_HELP = "Geben Sie einen beliebigen Betrag an.  \nDas ist keine echte Online-Zahlung."


def get_balance(user_id):
    user = um.Users.get_user_by(um.Users.Col.id, user_id)
    return float(user[um.Users.Col.balance])


def balance_to_str(balance):
    return ("%.2f" % round(balance, 2)).replace(".",",") + " €"


def transaction_view():
    state.init_state("focus_id", 0)

    def text_input_changed(key: str):
        track.cb.edit_text(key)
        match key:
            case Key.recipient:
                st.session_state.focus_id = 1
            case Key.value:
                st.session_state.focus_id = 2
            case Key.message:
                pass

    cols = st.columns([2,1])
    cols[0].title("Geld senden", anchor=False)
    cols[1].write(f'<br><div style="text-align: right; color: {config.COLOR_GREY_TEXT};"> <i> Das ist keine echte Zahlung. </i></div>', unsafe_allow_html=True)
    
    recipient = st.text_input(
        label="Emfpänger",
        key=Key.recipient,
        on_change=text_input_changed,
        kwargs={"key": Key.recipient},
        placeholder="Name oder Email",
        help=_RECIPIENT_HELP
    )

    value = st.text_input(
        label="Betrag in €",
        key=Key.value,
        placeholder="0,00",
        on_change=text_input_changed,
        kwargs={"key": Key.value},
        help=_VALUE_HELP,
    )
    if "," in value:
        value = value.replace(",",".")

    message = st.text_input(
        label="Nachricht",
        key=Key.message,
        on_change=text_input_changed,
        kwargs={"key": Key.message},
        placeholder="Schreibe eine Nachricht",
        help=_REFERENCE_HELP
    )
    
    # Jump from one text input to the next one:
    util.set_focus_id()

    col = st.columns([1,2,1])
    confirm = col[1].button(
        label="Senden",
        key=Key.confirm,
        type="secondary",
        use_container_width=True,
        on_click=track.cb.click,
        kwargs={"key": Key.confirm},
        disabled=True if state.get_state("did_rerun_after_transaction") else False
    )    
    
    if confirm or state.get_state("did_rerun_after_transaction"):
        if "did_rerun_after_transaction" not in st.session_state:
            st.session_state["did_rerun_after_transaction"] = False
        
        # Hande invalid inputs:
        balance = get_balance(st.session_state[SessionStateKey.Common.user_id])
        exit_app = False
        try:
            value = float(value)
        except:
            st.warning("Ungültiger Betrag. Geben Sie eine Zahl für den Betrag ein.")
            exit_app = True
        if recipient == "":
            st.warning("Geben Sie einen Empfänger an.")
            exit_app = True
        if value == 0:
            st.warning("Geben Sie einen Betrag an.")
            exit_app = True
        if isinstance(value, float | int) and value > balance + BALANCE_OVERDRAW:
            st.warning(f"Wählen Sie einen geringeren Betrag. Sie können Ihr Konto nicht mit mehr als {BALANCE_OVERDRAW} € überziehen.")
            exit_app = True
        if exit_app:
            exit(0)
        
        util.center_spinner()
        with st.spinner(""):
            if not st.session_state["did_rerun_after_transaction"]:
                um.Users.do_transaction(
                    user_id=st.session_state[SessionStateKey.Common.user_id],
                    recipient=recipient,
                    value=value,
                    message=message
                )
                st.session_state["did_rerun_after_transaction"] = True
                st.rerun()
            else:
                del st.session_state["did_rerun_after_transaction"]
                time.sleep(2)
        
        st.session_state.focus_id = 0
        st.session_state[Key.state] = TRANSACTION_SUCCESS
        st.rerun()


def transaction_success_view():
    st.title("Geld senden", anchor=False)
    st.write("")
    st.success("✅ Ihre simulierte Zahlung wurde bestätigt.")
    st.write("")

    new_payment = st.columns(3)[1].button(
        label="Neue Zahlung",
        key=Key.new_payment,
        use_container_width=True
    )
    if new_payment:
        st.session_state[Key.state] = None
        st.rerun()

    # Show users progress in user study:
    today_date = pd.Timestamp.utcnow().date()
    user = um.Users.get_user_by("id", st.session_state[SessionStateKey.Common.user_id])
    registration_date = user[um.Users.Col.reg_timestamp_utc].date()

    days_remaining = registration_date + dt.timedelta(days=config.LENGHT_OF_STUDY_PHASE_2_IN_DAYS) - today_date
    days_remaining = days_remaining.days
    if days_remaining <= 0:
        # user finished
        progress_text = f"Sie haben die 2. Phase der Studie abgeschlossen. Bitte nehmen Sie Ihren Abschlusstermin war."
    else:
        progress_text = f"Bitte melden Sie sich morgen wieder an."

    with open("html/info_box_from_user_study.html") as file:
        html = file.read()
        html = html.replace("{progress_text}", progress_text)
    st.markdown(html, True)


def overview():
    # Balance:
    st.title("Bilanz", False)
    user_id = st.session_state[SessionStateKey.Common.user_id]
    balance = get_balance(user_id)
    color = config.COLOR_PRIMARY if balance >= 0 else config.COLOR_OUTGOING_MONEY
    balance_str = balance_to_str(balance)

    st.markdown(f'<div style="color: {color}; font-size: 50px;">{balance_str}</div>', True)
    st.write("")

    # History:
    df = um.Users.get_transactions(user_id)
    st.title("Verlauf", False)
    if df.empty:
        st.markdown(f'<br><div style="text-align: center; color: {config.COLOR_GREY_TEXT};"> <i> Keine kürzlichen Aktivitäten </i></div>', True)
    else:
        for idx, row in df.iterrows():
            transaction_log_box(
                timestamp=idx,
                recipient=row["recipient"],
                value=row["value"],
                message=row["message"]
            )


def transaction_log_box(timestamp: dt.datetime, recipient: str, value: float, message: str):
        msg_len = 35
        message = message if len(message) < msg_len else message[0:msg_len] + "..."
        if message == "nan":
            message = ""
        else:
            message = "\"" + message + "\""

        if value < 10000:
            value = ("%.2f" % round(value, 2)).replace(".",",") + " €"
        else:
            value = millify(value) + " €"

        match platform.system():
            case "Windows":
                s = "#"
            case "Darwin" | "Linux":
                s = "-"
            case _:
                s = ""

        with open("html/transaction_log_box.html") as file:
            html = file.read()
        
        html = html.replace("{primary_color}", config.COLOR_PRIMARY)
        html = html.replace("{recipient}", recipient)
        html = html.replace("{message}", message)
        html = html.replace("{grey_color}", config.COLOR_GREY_TEXT)
        html = html.replace("{date}", timestamp.strftime(f"%{s}d.%{s}m.%y"))
        html = html.replace("{time}", timestamp.strftime(f"%{s}H:%M"))
        html = html.replace("{value}", value)
        st.markdown(html, True)


def logout_button():
    st.write("")
    logout = st.button(
        label="Abmelden",
        key=Key.logout,
        use_container_width=True
    )

    if logout:
        track.logout()
        for _state in st.session_state:
            del st.session_state[_state]
        st.rerun()
