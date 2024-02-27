const KEY_URL_USERNAME_DICT = "url_username_dict";
let TOTP_INPUT_ELEM = null;

function log(msg) {
    if (typeof msg === "string") {
      console.log("[FOREGROUND]: " + msg);
    } else {
      console.log(msg);
    }
  }

// TODO ADDITIONAL we can use storage.local to remember website <-> username pairs

function dynDict(key, val) {
    // Helper function to build a dict dynamically.
    d = {};
    d[key] = val;
    return d;
}

function getDomain() {
    let url = document.location.href;
    let domain = new URL(url).hostname.replace("www.", "");
    return domain;
}

async function getStorageSession(key) {
    let res = await chrome.storage.session.get([key]);
    res = res[key];
    if (!res) { res = null; }
    return res;
}

function setUsernameChangeEvent(html_elem) {
    html_elem.addEventListener("change", () => {
        // When user entered their username:
        let username = html_elem.value;
        log("username: " + username);
        let domain = getDomain();
        log("domain: " + domain);
        // The username is stored to its domain where it was entered by the user. These pairs are stored in a dictionary, so we need to update it:
        getStorageSession(KEY_URL_USERNAME_DICT).then( (url_username_dict) => {
            if (!url_username_dict) { // dictionary wasn't created yet.
                url_username_dict = {};
            }
            url_username_dict[domain] = username;
            chrome.storage.session.set(dynDict(KEY_URL_USERNAME_DICT, url_username_dict));
        })
    }, false);
    // For websites that don't redirect to a new url while changing from username/password site to totp site:
    document.body.addEventListener('DOMNodeInserted', totpNodeInsertedCallback);
};

function fillTotp(html_elem) {
    getStorageSession(KEY_URL_USERNAME_DICT).then((url_username_dict) => {
        if (!url_username_dict) {
            // Extension wasn't able to detect the username
            // TODO
        } else {
            let domain = getDomain();
            let username = url_username_dict[domain];
            TOTP_INPUT_ELEM = html_elem;

            chrome.runtime.sendMessage({"key": "found_totp_element", "domain": domain, "username": username});
            chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
                if (msg.key == "response_totp_await_user_confirm") {
                    showHintOnTotpInputElement();
                }
            });
        }
    });    
};

function selectUsernameInputElement(html_obj) {
    elem = null;
    selectors = [
        // TODO ADDITIONAL add more selectors, not all websites set the autocomplete attribute:
        "[autocomplete=username]"
    ]
    for (let i = 0; i < selectors.length; i++) {
        if (i == selectors.length) break;
        elem = html_obj.querySelector(selectors[i]);
        if (elem) {
            return elem;
        }
    }
    return elem;
};

function selectTotpElement(html_obj) {
    // Checks if html_obj is an totp input element.
    // Returns the totp input element if it found one, otherwise null.
    elem = null
    selectors = [
        "[autocomplete=one-time-code]",
        "[name=totp]", "[name=otp]", "[name=app_otp]",
        "[id=otp]", "[id=totp]", "[id=app_totp]"]
    for (let i = 0; i < selectors.length; i++) {
        if (i == selectors.length) break;
        elem = html_obj.querySelector(selectors[i]);
        if (elem) return elem;
    }
    return elem;
};

function usernameNodeInsertedCallback(event) {
    user_elem = selectUsernameInputElement(event.target);
    if (user_elem) {
        setUsernameChangeEvent(user_elem);
    }
};

function totpNodeInsertedCallback(event) {
    let totp_elem = selectTotpElement(event.target);
    if (!totp_elem) {
        // TODO ext should check if already stored the field permanently and use this
        // TODO add context menu entry, so user can right click on the totp html element and chose "remember this token field"
    }
    else {
        fillTotp(totp_elem);
    }
};

function showHintOnTotpInputElement() {
    console.log("now adding hint");

    let node = document.createElement("div");
    let rectTotp = TOTP_INPUT_ELEM.getBoundingClientRect();

    // fetch notification hint html/css:
    fetch(chrome.runtime.getURL("notification_hint.html")).then((ret) => {
        ret.text().then((text) => {
            node.innerHTML = text;
            // Position element:
            node.style.position = "absolute";
            document.body.appendChild(node);           
            node.style.left = (rectTotp.right - (0.25 * rectTotp.width)).toString() + "px";
            node.style.top = (rectTotp.top - node.getBoundingClientRect().height - 10).toString() + "px";
            
            let opacity = 0;
            function animate(rm_with_animation = false) {
                if (opacity == 0) {
                    node.style.opacity = 0;
                    opacity += 0.01;
                    setTimeout(animate, 800);
                }
                else if (opacity < 1) {
                    opacity += 0.02;
                    setTimeout(function(){animate()},50);
                    node.style.opacity = opacity;
                }
            }
            animate();

            // Check when user entered the totp, so we will remove the hint.
            // On most websites this is obsolete, but on websites, which do not change
            // their path after login, the will remain.
            TOTP_INPUT_ELEM.addEventListener("change", () => {
                document.body.removeChild(node);
            });
        });
    });
}

// Code runs from here!

// Messaging with background script:
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    log(msg);
    switch(msg.key) {
        case "insert_totp":
            // Received the totp, so fill it in:
            log("totp: " + msg.totp);
            TOTP_INPUT_ELEM.setAttribute("value", msg.totp);
            TOTP_INPUT_ELEM.dispatchEvent(new Event("change", { bubbles: true }));
            TOTP_INPUT_ELEM.focus();
            TOTP_INPUT_ELEM.dispatchEvent(new Event("blur", { bubbles: true }));
            break;
    }
});

// Search for the username and totp input elements on the website:
getStorageSession(KEY_URL_USERNAME_DICT).then( (url_username_dict) => {
    log("url_username_dict: " + url_username_dict)
    let storedUsername = null;
    if (url_username_dict) {
        storedUsername = url_username_dict[getDomain()];
    }
    log("storedUsername: " + storedUsername);
    usernameInputElement = selectUsernameInputElement(document.body);
    log("usernameInputElement: " + usernameInputElement);
    if (usernameInputElement) {
        setUsernameChangeEvent(usernameInputElement);
    } else if (!storedUsername) {
        // Some websites (like websites made with streamlit) build there html DOM after reporting they are fully loaded, so we need to wait for the website to be really loaded fully:
        document.body.addEventListener('DOMNodeInserted', usernameNodeInsertedCallback);
        // TODO ADDITIONAL maybe we could listen to input elements only     
    } else {
        log("totp elem")
        let totp_element = selectTotpElement(document.body);
        if (!totp_element) {
            document.body.addEventListener('DOMNodeInserted', totpNodeInsertedCallback);
            // TODO ADDITIONAL maybe we could listen to input elements only
        } else {
            fillTotp(totp_element);
        }
    }
});
