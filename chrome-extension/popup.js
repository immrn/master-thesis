const KEY_URL_USERNAME_DICT = "url_username_dict";
const POPUP_STATE_MACHINE = {
    "onboarding": loadOnboarding,
    "home": loadHome,
    "devices": loadDevices,
    "setupWasEnabledBefore": loadSetupWasEnabledBefore,
    "setupOnWebservice": loadSetupOnWebservice,
    "setupOnWebserviceAgain": loadSetupOnWebserviceAgain,
    "setupEnterUsername": loadSetupEnterUsername,
    "setupCreateProfile": loadSetupCreateProfile,
    "setupFinished": loadSetupFinished,
    "error": loadError
}
var errorState = null;
let bleDeviceList = null;
let tmpDeviceName = null; // this is just to temporarly safe the deviceName while waiting for the background app to acknowledge the successful ble connection

function log(msg) {
    if (typeof msg === "string") {
      console.log("[POPUP]: " + msg);
    } else {
      console.log(msg);
    }
  }

function connectCall() {
    tmpDeviceName = this.innerHTML;
    this.style.backgroundColor = "var(--prim-color)";
    this.style.scale = "1.05";
    document.getElementById("statusText").innerHTML = chrome.i18n.getMessage("devices_connectingTo") + " " + tmpDeviceName + " ...";
    let lis = document.getElementById("device_ul").getElementsByTagName("li");
    log("lis:");
    log(lis);
    for(i = 0; i < lis.length; i++) { 
        lis[i].onclick = null;
    }
    chrome.runtime.sendMessage({"key": "connect_with_ble_device", "id": this.dataset.id});
}

async function fetchHtml(url, showHomeButton=false) {
    // Title and eventually home button:
    if (showHomeButton) {
        const head = await fetch("title_with_home_btn.html");
        document.getElementById("head").innerHTML = await head.text();
        document.getElementById("homeButton").addEventListener("click", function () {
            // When user was in setup process, they ended it by pressing the home button. Therefore we must reset the domainBySetup and usernameBySetup key:
            chrome.storage.session.set({"domainBySetup": null});
            chrome.storage.session.set({"usernameBySetup": null});
            loadHome();
        });
    } else {
        const head = await fetch("title.html");
        document.getElementById("head").innerHTML = await head.text();
    }
    // Content:
    const response = await fetch(url);
    document.getElementById("content").innerHTML = await response.text();
    // If there are text variables, call their function to fill them:
    async function _getDeviceName() {
        return await getStorageSession("deviceName");
    }
    async function _getDomain() {
        // Determine if user already started setup process:
        let domain = await getStorageSession("domainBySetup");
        if (!domain) {
            return await byPopupGetDomain();
        } else {
            return domain;
        }
    }
    let variables = { "domainVar": _getDomain, "deviceNameVar": _getDeviceName }
    for (const [varName, varFun] of Object.entries(variables)) {
        let occurences = document.getElementsByClassName(varName);
        let value = await varFun();
        for (let i = 0; i < occurences.length; i++) {
            occurences[i].innerHTML = value;
        }
    }

    // Translate texts to support different languages:
    function translateElements() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const messageKey = element.getAttribute('data-i18n');
            const translatedMessage = chrome.i18n.getMessage(messageKey);
            if (element.placeholder != null) {
                element.placeholder = translatedMessage
            }
            else if (element.tagName === 'TITLE') {
                document.title = translatedMessage;
            } else {
                element.innerHTML = translatedMessage;
            }
        });
    }
    translateElements();
}

async function loadOnboarding(showCheckbox=true) {
    setPopupState("onboarding");
    await fetchHtml("onboarding.html");
    // Download button:
    document.getElementById("downloadButton").addEventListener("click", function() {
        window.open("https://totp-study.informatik.tu-freiberg.de/?page=download_only_service", "_blank");
    });
    // QR code:
    document.getElementById("qrCode").innerHTML = "";
    // TODO IMPORTANT: value must be the link of real Blue TOTP app instead!
    let value = "https://play.google.com/store/apps/details?id=org.liberty.android.freeotpplus&hl=de&gl=US";
    new QRCode(
        document.getElementById("qrCode"),
        {   text: value,
            width: 140,
	        height: 140 }
    );
    // Checkbox:
    if (!showCheckbox) {
        chrome.storage.local.get(["skip_onboarding"]).then( (res) => {
            document.getElementById("skipOnboardingCheckbox").checked = res["skip_onboarding"];
        });
        document.getElementById("skipOnboardingCheckboxDiv").style.display = "none";
    }
    // Continue button:
    document.getElementById("continueButton").addEventListener("click", function() {
        if (document.getElementById("skipOnboardingCheckbox").checked) {
            chrome.storage.local.set({"skip_onboarding": true});
        }
        loadHome();
    });
}

async function loadError(showHomeButton=false) {
    setPopupState("error");
    await fetchHtml("error.html", showHomeButton);

    switch(errorState) {
        case null:
            console.error("no error state set... loading home screen");
            loadHome();
            break;
        case "waitForBackgroundApp":
            document.getElementById("waitForBackgroundAppErrorMsg").style.display = "initial";
            break;
        case "unknown":
            document.getElementById("unkownErrorMsg").style.display = "initial";
            break;
        case "btNotSupported":
            document.getElementById("btNotSupported").style.display = "initial";
            break;
        case "btAdapterIsDisabled":
            document.getElementById("btAdapterIsDisabled").style.display = "initial";
            break;
    }

    // Enable onboarding link at bottom:
    document.getElementById("linkOnboarding").addEventListener("click", 
    function() {
        errorState = null;
        loadOnboarding(false);
    })
}

async function loadHome() {
    setPopupState("home");
    await fetchHtml("home.html");
    chrome.storage.session.set({"isSetupComplete": false});

    chrome.runtime.sendMessage({"key": "check_ble_support"});

    let deviceName = await getStorageSession("deviceName");
    log("device Name: " + deviceName);

    // Determine whether to show disconnected card XOR connected card + setup card:
    if (deviceName) { // => show connected card + setup card
        checkBleDeviceConnection(); // When device isn't connected anymore, this will cause a "bleDeviceDisconnectedEvent" message from background.js -> the following code will be obsolete in this case.

        document.getElementById("disconnectedCard").style.display = "none";

        // Add functionality for connected card:
        document.getElementById("disconnectDeviceButton").addEventListener("click", function () {
            disconnectBle();
        });
        
        // Decide if setup card must be showed (dont show it on "domains" like "newtab", or "extensions", which are no domains):
        let domain = await byPopupGetDomain();
        log("domain in loadhome: " + domain);
        log(". in domain: " + domain.includes("."));
        if (domain.includes(".")) { // if it has a dot, it will probably be a real domain
            // Add functionality for setup card:
            let setupButton = document.getElementById("setupButton");
            if (domain.length > 20) {
                setupButton.textContent = chrome.i18n.getMessage("home_setupFor") + "\r\n" + domain;
            } else {
                setupButton.textContent = chrome.i18n.getMessage("home_setupFor") + " " + domain;;
            }
            setupButton.addEventListener("click", function () {
                byPopupGetDomain().then( (domain) => {
                    chrome.storage.session.set( {"domainBySetup": domain} );
                    loadSetupWasEnabledBefore();
                })
            });
        } else { // not a real domain, hide setup card:
            document.getElementById("setupCard").style.display = "none";
            document.getElementById("setupHintCard").style.display = "flex";
        }
    }
    else { // => show disconnected card:
        document.getElementById("connectedCard").style.display = "none";
        document.getElementById("setupCard").style.display = "none";
        document.getElementById("searchDeviceButton").addEventListener("click", () => {
            disconnectBle(); // disconnect from an eventually existing ble connection
            loadDevices();
        });
    }

    // Enable onboarding link at bottom:
    document.getElementById("linkOnboarding").addEventListener("click", 
    function() {
        loadOnboarding(false);
    })
}

async function loadDevices() {
    setPopupState("devices");
    await fetchHtml("devices.html", true);
    scanForBleDevices();
    // When user presses home button, stop ble scanning
    document.getElementById("homeButton").addEventListener("click", () => {
        chrome.runtime.sendMessage({"key": "stop_scan_ble"});
    });
}

async function loadSetupWasEnabledBefore() {
    setPopupState("setupWasEnabledBefore");
    await fetchHtml("setup_was_enabled_before.html", true);
    // add event listeners:
    document.getElementById("yesButton").addEventListener("click", loadSetupOnWebserviceAgain);
    document.getElementById("noButton").addEventListener("click", loadSetupOnWebservice);
}

async function loadSetupOnWebservice() {
    chrome.storage.session.set({"wasSetupOnWebserviceAgain": false});
    setPopupState("setupOnWebservice");
    await fetchHtml("setup_on_webservice.html", true);
    // add event listeners:
    document.getElementById("backButton").addEventListener("click", loadSetupWasEnabledBefore);
    document.getElementById("continueButton").addEventListener("click", loadSetupEnterUsername);
}

async function loadSetupOnWebserviceAgain() {
    chrome.storage.session.set({"wasSetupOnWebserviceAgain": true});
    setPopupState("setupOnWebserviceAgain");
    await fetchHtml("setup_on_webservice_again.html", true);
    // add event listeners:
    document.getElementById("backButton").addEventListener("click", loadSetupWasEnabledBefore);
    document.getElementById("continueButton").addEventListener("click", loadSetupEnterUsername);
}

async function loadSetupEnterUsername() {
    setPopupState("setupEnterUsername");
    await fetchHtml("setup_enter_username.html", true);

    // --- Autofill username if possible ---
    // Check if the stored domain for the username is the same as in the current active tab: otherwise the user is on a new domain, where they didn't enter a username or no username input was recognized by foreground.js
    let UrlUsernameDict = await getStorageSession(KEY_URL_USERNAME_DICT);
    let domain = await getStorageSession("domainBySetup");
    if (UrlUsernameDict && domain in UrlUsernameDict) {
        document.getElementById("usernameInput").value = UrlUsernameDict[domain];
    }

    // add event listeners:
    if (await getStorageSession("wasSetupOnWebserviceAgain")) {
        document.getElementById("backButton").addEventListener("click", loadSetupOnWebserviceAgain);
    } else {
        document.getElementById("backButton").addEventListener("click", loadSetupOnWebservice);
    }
    document.getElementById("continueButton").addEventListener("click", function() {
        let inputElement = document.getElementById("usernameInput");
        let enteredUsername = inputElement.value;
        if (enteredUsername == "") {
            inputElement.focus();
            inputElement.style.outline = "1px solid var(--attention-color)";
            inputElement.style.border = "1px solid var(--attention-color)";
            inputElement.addEventListener("keypress", function(){
                inputElement.style.border = "1px solid var(--sec-color)";
                inputElement.style.outline = "1px solid var(--sec-color)";
            })
        } else {
            chrome.storage.session.set( {"usernameBySetup": enteredUsername} );
            loadSetupCreateProfile();
        }
    });
}

async function loadSetupCreateProfile() {
    setPopupState("setupCreateProfile");
    await fetchHtml("setup_create_profile.html", true);
    if (await getStorageSession("isSetupComplete")) {
        chrome.runtime.sendMessage({"key": "dont_await_qr_scan"});
        chrome.storage.session.set({"isSetupComplete": false});
        loadSetupFinished();
        return;
    }
    // Extension informs smartphone, that it is ready for the qr scan:
    chrome.runtime.sendMessage({"key": "await_qr_scan"});
    // add event listeners:
    document.getElementById("backButton").addEventListener("click", async () => {
        chrome.runtime.sendMessage({"key": "dont_await_qr_scan"});
        POPUP_STATE_MACHINE["setupEnterUsername"]();
    });
    document.getElementById("homeButton").addEventListener("click",
    () => {
        chrome.runtime.sendMessage({"key": "dont_await_qr_scan"});
    })
    // No continue button: Smartphone sends a message to extension when the profile was created. After that the extension will show the setupFinished screen.
}

async function loadSetupFinished() {
    setPopupState("setupFinished");
    await fetchHtml("setup_finished.html", true);
    // add event listeners:
    document.getElementById("continueButton").addEventListener("click", loadHome);
}

chrome.runtime.onMessage.addListener( (msg, sender, sendResponse) => {
    switch(msg.key) {
        case "bleDeviceDisconnectedEvent":
            log("received bleDeviceDisconnectedEvent");
            getPopupState().then( (state) => {
                if (!["onboarding", "setupFinished", "error"].includes(state)) {
                    loadHome();
                    // TODO IMPORTANT but load a version of home screen that includes a message that states, that we lost the connection to the smartphone
                }
            })
            break;
        case "bleDeviceConnectedEvent":
            log("received bleDeviceConnectedEvent");
            chrome.storage.session.set( {"deviceName": tmpDeviceName});
            tmpDeviceName = null;
            loadHome();
            break;
        case "background_app_disconnected_event":
            log("received background_app_disconnected_event");
            getPopupState().then( (state) => {
                if (state != "onboarding") {
                    chrome.storage.session.set( {"deviceName": null});
                    errorState = "waitForBackgroundApp";
                    loadError();
                }
            })
            break;
        case "background_app_connected_event":
            log("received " + msg.key);
            errorState = null;
            loadHome();
            break;
        case "setup_complete":
            log("received " + msg.key);
            getPopupState().then((state) => {
                if (state == "setupCreateProfile") {
                    loadSetupFinished();
                } else {
                    console.error("Received " + msg.key + "\nBut was not in the typical popup state to receive this msg.");
                }
            });
            break;
        case "btAdapterIsDisabled":
            log("received " + msg.key);
            errorState = "btAdapterIsDisabled";
            loadError(true);
            break;
        case "btNotSupported":
            log("received " + msg.key);
            errorState = "btNotSupported";
            loadError();
            break;
    }
});

// chrome.storage.local.set({"skip_onboarding": false});
document.addEventListener('DOMContentLoaded', function() {
    chrome.storage.local.get(["skip_onboarding"]).then( (res) => {
        res = res["skip_onboarding"];
        log("skip onb = " + res);
        if (!res) {
            loadOnboarding();
        } else { // When we should skip onboarding:
            getPopupState().then( (state) => {
                if (!state) { // No state set
                    loadHome();
                } else {
                    POPUP_STATE_MACHINE[state]();
                }
            })
        }
    })
}, false);

// Utility

async function buildFallbackQrCode(username, domain) {
    document.getElementById("qrCode").innerHTML = "";
    let value = "bluetotp://totp2?host=" + domain + "&username=" + username;
    new QRCode(
        document.getElementById("qrCode"),
        {   text: value,
            width: 190,
	        height: 190 }
    );
}

async function getStorageSession(key) {
    let res = await chrome.storage.session.get([key]);
    res = res[key];
    if (!res) { res = null; }
    return res;
}

async function setPopupState(state) {
    chrome.storage.session.set( {"popupState": state} )
}

async function getPopupState() {
    return await getStorageSession("popupState");
}

async function byPopupGetDomain() {
    let tabs = await chrome.tabs.query({active: true, currentWindow: true});
    let url = tabs[0].url;
    let domain = new URL(url).hostname.replace("www.", "");
    log("byPopupGetDomain => " + domain);
    return domain;
}

function scanForBleDevices() {
    chrome.runtime.onMessage.addListener( function (msg, sender, sendResponse) {
        getPopupState().then( (state) => {
            if (state != "devices") { return }
            switch(msg.key) {
                case "ble_device_list":
                    log("received ble device list");
                    let ul = document.getElementById("device_ul");
                    ul.innerHTML = "";
                    bleDeviceList = msg["ble_device_list"];
                    bleDeviceList.forEach((device) => {
                        let li = document.createElement("li");
                        li.appendChild(document.createTextNode(device.deviceName));
                        li.dataset.id = device.deviceId;
                        li.onclick = connectCall;
                        ul.appendChild(li);
                    });
                    break;
            }
        });
    });
    chrome.runtime.sendMessage({"key": "scan_ble"});
}

function disconnectBle() {
    chrome.runtime.sendMessage({"key": "disconnect_ble"});
}

function checkBleDeviceConnection() {
    chrome.runtime.sendMessage({"key": "check_ble_device_connection"})
}