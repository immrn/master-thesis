class SessionStateKey:
    # The keys are used in streamlits session state and must be unique:

    # Global keys will be initialized at this EOF:
    class Common:
        _prefix = "common" + "-"
        user_id = _prefix + "user_id"
        state = _prefix + "state"

        # Used by login:
        ret_check_login = _prefix + "ret_check_login"
        changed_pw = _prefix + "changed_pw"
        changed_username_or_email = _prefix + "changed_username_or_email"

        # Used by TOTP Setup:
        curr_totp_uri_and_secret = _prefix + "curr_totp_uri_and_secret"

    class Banking:
        _prefix = "banking" + "-"
        recipient = _prefix + "recipient"
        message = _prefix + "message"
        value = _prefix + "value"
        confirm = _prefix + "confirm"
        cancel = _prefix + "cancel"
        state = _prefix + "state"
        new_payment = _prefix + "new_payment"
        logout = _prefix + "logout"
