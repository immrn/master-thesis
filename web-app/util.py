import streamlit as st
import streamlit.components.v1 as components

import config

def header():
    st.header(config.WEBSERVICE_ICON + " " + config.WEBSERVICE_NAME, False)


def center_spinner():
    st.markdown("""
        <style>
        div.stSpinner > div {
            text-align:center;
            align-items: center;
            justify-content: center;
        }
        </style>""", unsafe_allow_html=True
    )


def set_focus_id():
    # this javascript code snippet changes the focus according to the value in st.sessions_state.focus_id
    components.html(
        f"""
        <div>some hidden container</div>
        <p>{st.session_state.focus_id}</p>
        <script>
            var input = window.parent.document.querySelectorAll("input[type=text],input[type=password]");
            // for (var i = 0; i < input.length; ++i) {{
            //     input[i].focus();
            // }}
            if ({st.session_state.focus_id} >= 0) {{
                input[{st.session_state.focus_id}].focus();
            }}
        </script>
        """,
        height=0,
    )
