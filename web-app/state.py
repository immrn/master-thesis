import streamlit as st

_SHADOW = "shadow_"
_STATE = "state_"

def get_state(state: str) -> any:
    if state in st.session_state:
        return st.session_state[state]
    else:
        return None


def init_state(state: str, value: any):
    if state not in st.session_state:
        st.session_state[state] = value


def set_state(state: str, value: any):
    st.session_state[state] = value


def state(fun: callable, **kwargs):
    """
    Call a streamlit input widget function and keep its state permanently.
    :param fun: streamlit input widget function (like st.radio)
    :param kwargs: kwargs are passed as args to the function stated in fun
    :return: value that the widget returns
    """

    if "key" not in kwargs:
        raise KeyError("You must state a key as argument, like state(..., key='my_key').")

    def manage_state_index_based(index_key: str, fun: callable, **kwargs):
        key = kwargs["key"]
        if key not in st.session_state:
            st.session_state[_SHADOW + key] = st.session_state.get(
                key=_STATE + key,
                default=kwargs["options"][kwargs[index_key]],
            )
        kwargs[index_key] = kwargs["options"].index(st.session_state[_SHADOW + key])
        st.session_state[_STATE + key] = fun(**kwargs)
        return st.session_state[_STATE + key]

    def manage_state_value_based(value_key: str, fun: callable, **kwargs):
        key = kwargs["key"]
        if key not in st.session_state:
            st.session_state[_SHADOW + key] = st.session_state.get(
                key=_STATE + key,
                default=kwargs[value_key],
            )
        kwargs[value_key] = st.session_state[_SHADOW + key]
        st.session_state[_STATE + key] = fun(**kwargs)
        return st.session_state[_STATE + key]

    if "value" in kwargs and "index" not in kwargs:
        return manage_state_value_based(value_key="value", fun=fun, **kwargs)
    elif "index" in kwargs and "value" not in kwargs:
        return manage_state_index_based(index_key="index", fun=fun, **kwargs)
    elif "default_index" in kwargs:
        return manage_state_index_based(index_key="default_index", fun=fun, **kwargs)
    else:
        raise NotImplementedError(f"Either one of the arguments 'index' or 'value' can and must be stated. It seems like you "
             f"stated both or none of them. In case {fun} is a new streamlit input widget, it is possible "
             f"that you need to enhance this library.")