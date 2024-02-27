import streamlit as st
import config

query_params = st.experimental_get_query_params()
called_download_page = False
if "page" in query_params.keys():
    if query_params["page"][0].startswith("download"):
        called_download_page = True
        st.set_page_config(page_title="Blue TOTP", page_icon="")
if not called_download_page:
    st.set_page_config(page_title=config.WEBSERVICE_NAME, page_icon=config.WEBSERVICE_ICON)

import banking
import user_management as um
import util
import usage_tracking as track
from constants import SessionStateKey
import mist_views
from state import get_state, init_state

Key = SessionStateKey.Common

# This must be the first code lines:
track.init(st_key_for_username=Key.user_id)
um.checkFiles()
st.markdown(config.STREAMLIT_STYLE, unsafe_allow_html=True)

if called_download_page:
    pass
elif Key.state not in st.session_state and len(query_params.keys()) == 0 \
    or Key.state in st.session_state and st.session_state[Key.state] == um.TOTP:
    um.login_header()
else:
    cols = st.columns([9,2])
    with cols[0]:
        util.header()
    with cols[1]:
        if len(query_params.keys()) == 0 and Key.state in st.session_state and st.session_state[Key.state] not in [um.TOTP, um.SETUP_TOTP, um.FINISH_TOTP_SETUP]:
            banking.logout_button()

# Login:
if not get_state(Key.state):
    # User is not logged in:
    if "page" in query_params.keys():
        match query_params["page"][0]:
            case um.REGISTRATION:
                um.registration_view()
            case um.RESET_PW:
                um.initiate_reset_pw_view()
            case "about":
                mist_views.about()
            case "contact":
                mist_views.contact()
            case "download_app":
                mist_views.download_app_prototype()
            case "download_pc":
                mist_views.download_pc_prototype()
            case _:
                mist_views.not_found_404()
    elif "register" in query_params.keys():
        um.finish_registration_view(reg_uuid=query_params["register"][0])
    elif "reset_pw" in query_params.keys():
        um.reset_pw_view(reset_pw_uuid=query_params["reset_pw"][0])
    um.login_view()
match st.session_state[Key.state]:
    case um.TOTP:
        um.totp_view()
    case um.SETUP_TOTP:
        um.setup_totp_view()
    case um.REGISTRATION_MAIL_SENT:
        um.registration_mail_sent_view()
    case um.RESET_PW_MAIL_SENT:
        um.reset_pw_mail_sent_view(user_id=st.session_state[Key.user_id])
    case um.FINISH_RESET_PW:
        um.finish_reset_pw_view()
    case um.FINISH_TOTP_SETUP:
        um.finish_totp_setup_view()

# After login was successfull:
Key = SessionStateKey.Banking
init_state(Key.state, None)
overview_tab, transaction_tab = st.tabs(["Übersicht", "Geld senden"])
with overview_tab:
    banking.overview()
with transaction_tab:
    if st.session_state[Key.state] == banking.TRANSACTION_SUCCESS:
        banking.transaction_success_view()
    else:
        banking.transaction_view()

# This must be the end of main file:
if not called_download_page:
    st.markdown(config.CUSTOM_FOOTER, unsafe_allow_html=True)