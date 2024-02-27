import logging
import os
import streamlit as st
import datetime as dt
from logging.handlers import RotatingFileHandler
from typing import Optional
from streamlit_javascript import st_javascript
import config


# For a later README:
#   import usage_tracking as track
#   track.init(...)
#   track.resize_window()
#   st.selectbox(...,key="my_sb",on_change=track.select,kwargs={"key": "my_sb"})
# Tracking functions:
#   Callbacks, use them as callback only:
#       - click (every st input widget with on_click)
#       - select (every st input widget with on_change)
#       - switch_page (when your app has multiple pages/views)
#   Usual functions:
#       - login (call after a successful login)
#       - resize_window (call it in every run)
#       - info, warning, error (call it st.info, st.warning, st.error)
# Reading the csv file:
#   _SEP_ is the csv seperator
# After reading the csv file:
#   - every "///" stands for a _SEP_ (this _SEP_ was within a value and not ment to be a real csv _SEP_)


# FORMAT: "timestamp,user,action,key,value,remark"

_track_logger_ = None
_key_for_username_ = None
_SEP_ = ";"  # seperator for csv file
_SAVE_FILE_PATH_ = config.PATH_TO_USAGE_TRACKING_FILE

class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _setup_(
    modul_name: str,
    console_output: bool,
    stdout_level=logging.DEBUG,
    file_level=logging.DEBUG,
    file_path: Optional[str] = "volume/log_file.txt",
    file_size: Optional[int] = 10 * 1024 * 1024,
):
    """!
    @param modul_name: a name, use predefined strings like log_setup.MODUL_BACKEND
    @param stdout_level: minimum logging level for the std output
    @param file_level: minimum logging level for the log file
    @param file_path: path (incl. filename) where the log file should be stored, must be in volume/
    @param file_size: size of the log file in bytes
    @return: a logger object
    """
    logger = logging.getLogger(modul_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # In case we restart the app but didn't delete the old usage_tracking.csv:
    if not logger.hasHandlers():
        timestamp = str(dt.datetime.now().isoformat(timespec='seconds')).replace(":", "-")
        # try except because if a user is active and the app is being restarted, the user will encounter
        # a FileNotFoundError after the website did reload. It is unclear why this happens, but this does fix it.
        try:
            if os.path.exists(_SAVE_FILE_PATH_):
                os.rename(_SAVE_FILE_PATH_, _SAVE_FILE_PATH_.split('.')[0] + "_until_" + timestamp + ".csv")
            if os.path.exists(_SAVE_FILE_PATH_ + ".1"):
                os.rename(_SAVE_FILE_PATH_ + ".1", _SAVE_FILE_PATH_.split('.')[0] + "_until_" + timestamp + "_1.csv")
        except FileNotFoundError:
            st.rerun()

    count_handlers = 3 if console_output else 2
    if logger.hasHandlers():
        if os.path.exists(_SAVE_FILE_PATH_) and len(logger.handlers) == count_handlers:
            return logger
        else:  # In this case some dev removed the usage_tracking.csv while the app was running
            logger.handlers.clear()

    format_str = "%(message)s"

    # Console output:
    if console_output:
        stdout_formatter = CustomFormatter(format_str)
        handler = logging.StreamHandler()
        handler.setLevel(stdout_level)
        handler.setFormatter(stdout_formatter)
        logger.addHandler(handler)

    # format stuff: https://docs.python.org/3/library/logging.html#logrecord-attributes

    # File output:
    file_formatter = logging.Formatter(format_str)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=file_path,
        mode="a",
        maxBytes=file_size,
        backupCount=1,  # do not change!
        encoding=None,
        delay=False,
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(file_level)

    logger.addHandler(file_handler)

    return logger


def init(st_key_for_username: str):
    global _track_logger_
    _track_logger_ = _setup_(
        modul_name="web-app",
        console_output=True,
        file_path=_SAVE_FILE_PATH_,
        file_size=25 * 1024 * 1024
    )
    global _key_for_username_
    _key_for_username_ = st_key_for_username


def _track_(action: str, key: str = None, remark: str = None, user_needed: bool = True):
    if user_needed:
        if _key_for_username_ not in st.session_state:
            raise NotImplementedError('You must declare st.session_state["user"]')
        if key and key not in st.session_state:
            raise NotImplementedError(f'You must declare st.session_state["{key}"]')

        user = st.session_state[_key_for_username_]
        value = st.session_state[key] if key else ""
    else:
        user = "-"
        value = ""

    # we don't want to save "None", we want to save an empty string:
    remark = "" if not remark else remark
    key = "" if not key else key

    # Because we store it as csv, we need to replace appearing _SEP_:
    user = str(user).replace(_SEP_, "///")
    action = str(action).replace(_SEP_, "///")
    key = str(key).replace(_SEP_, "///")
    value = str(value).replace(_SEP_, "///")
    remark = str(remark).replace(_SEP_, "///")

    # Format of message must match __FORMAT__ (constant at top of this file):
    entities = [dt.datetime.now(), user, action, key, value, remark]
    message = _SEP_.join([str(e) for e in entities])

    _track_logger_.info(message)


def custom_action(action: str, remark: str = None):
    """
    Track what happended. Consider using the click() and change() methods when needing a callback.
    A timestamp, the user (set st.session_state["user"]) and other information will be added automatically.
    :param action: what happened
    """
    return _track_(action=action, remark=remark)

# Functions used as callbacks at on_change param of streamlit input widgets:
class cb:
    def click(key: str, remark: str = None):
        """
        Use this func as callback only. Track when a user clicked an input widget. The widget is identified by its key.
        :param key: the name of the key of this widget
        :param remark: a short annotation
        """
        return _track_(action="clicked", key=key, remark=remark)


    def select(key: str, remark: str = None):
        """
        Use this func as callback only. Track when a user changed the value of an input widget.
        The widget is identified by its key.
        :param key: the name of the key of this widget
        :param remark: a short annotation
        """
        return _track_(action="selected", key=key, remark=remark)


    def switch_page(key: str, remark: str = None):
        """
        Use this func as callback only. Track when a user changed the value of an input widget that opens a page/view.
        The widget is identified by its key.
        :param key: the name of the key of this widget
        :param remark: a short annotation
        """
        return _track_(action="switched_page", key=key, remark=remark)
    
    def edit_text(key: str, remark: str = None):
        """
        Use this func as callback only. Track when a user changed the value of an text_input widget.
        The widget is identified by its key.
        :param key: the name of the key of this widget
        :param remark: a short annotation
        """
        return _track_(action="edited_text", key=key, remark=remark)


def enter_valid_credentials(remark: str = None):
    """
    After a user logged in, call this once.
    :param remark: a short annotation
    """
    return _track_(action="entered_valid_credentials", remark=remark)


def enter_invalid_totp(remark: str = None):
    """
    After a user entered a invaild TOTP, call this once.
    :param remark: a short annotation
    """
    return _track_(action="entered_invalid_totp", remark=remark)


def logout():
    return _track_(action="logout")


def enter_valid_totp():
    return _track_(action="entered_valid_totp")


def finish_totp_setup():
    return _track_(action="finished_totp_setup")


def failed_totp_setup():
    return _track_(action="failed_totp_setup")


def resize_window(key: str, remark: str = None):
    """
    This function observes if the user resized their browser window. This function ensures that your stated key will
    be initialized. Call this function at each streamlit run.
    :param key: unique key for st.session_state
    :param remark: a short annotation
    """
    sizes = st_javascript(
        """[
        window.outerWidth, window.outerHeight,
        window.innerWidth, window.innerHeight,
        document.documentElement.clientWidth, document.documentElement.clientHeight,
        document.body.clientWidth, document.body.clientHeight
        ];"""
    )
    # TODO: the values of each size does not change, when resizing the broswer window and rerunning the script. It is
    #  necessary to refresh the website, then the values change. So at the moment we can't detect a real resize action.

    def did_size_change():
        for idx, val in enumerate(sizes):
            if st.session_state[key][idx] != sizes[idx]:
                return True
        return False

    if key not in st.session_state or type(st.session_state[key]) != list:
        st.session_state[key] = sizes
        if type(sizes) == list:
            return _track_(action="resized_window", key=key, remark=remark)
        return
    elif did_size_change():
        # Check for type != dict, because it is initialized as int.
        st.session_state[key] = sizes
        return _track_(action="resized_window", key=key, remark=remark)


def info(remark: str):
    """
    Call this after st.info().
    :param remark: this should be the message the user is reading
    """
    _track_(action="faced_st.info()", remark=remark)


def warning(remark: str):
    """
    Call this after st.warning().
    :param remark: this should be the message the user is reading
    """
    _track_(action="faced_st.warning()", remark=remark)


def error(remark: str):
    """
    Call this after st.error().
    :param remark: this should be the message the user is reading
    """
    _track_(action="faced_st.error()", remark=remark)
