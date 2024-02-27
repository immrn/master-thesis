chrome.storage.session.setAccessLevel({ accessLevel: 'TRUSTED_AND_UNTRUSTED_CONTEXTS' });
const WS_PORT = "3030";
let webSocket = null;
let foregroundTabId = null;
let popupId = null;

function log(msg) {
  if (typeof msg === "string") {
    console.log("[BACKGROUND]: " + msg);
  } else {
    console.log(msg);
  }
}

async function getStorageSession(key) {
  let res = await chrome.storage.session.get([key]);
  res = res[key];
  if (!res) { res = null; }
  return res;
}

ws_connect();

function ws_connect() {
  webSocket = new WebSocket('ws://localhost:' + WS_PORT);

  webSocket.onopen = (event) => {
    log('websocket open');
    webSocket.send(JSON.stringify({"ctl": "Hello from Websocket"}));
    // Tell popup that background app connected:
    chrome.runtime.sendMessage(
      popupId,
      {"key": "background_app_connected_event"}
    );
    // keepAlive();
  };

  webSocket.onmessage = (event) => {
    let msg = event.data;
    log(`[WSS]: ${msg}`);
    if (msg.startsWith('{"ctl":')) {
      return;
    }
    try {
      msg = JSON.parse(msg);
      switch (msg.key) {
        case "response_totp_await_user_confirm":
          log("received totp response, that user needs to confirm the totp request");
          chrome.tabs.sendMessage(
            foregroundTabId,
            {"key": "response_totp_await_user_confirm"}
          );
          break;
        case "response_totp":
          log("received totp: " + msg.totp);
          if (msg.totp != "null") {
            chrome.tabs.sendMessage(
              foregroundTabId,
              {"key": "insert_totp", "totp": msg.totp}
            );
          }
          break;
        case "ble_device_list":
          log("received ble device list: " + msg.ble_device_list);
          chrome.runtime.sendMessage(
            popupId,
            {"key": msg.key, "ble_device_list": msg.ble_device_list}
          );
          break;
        case "bleDeviceDisconnectedEvent":
          log("received info, that ble device did disconnect");
          chrome.storage.session.set({"isSetupComplete": false});
          chrome.storage.session.set( {"deviceName": null});
          chrome.runtime.sendMessage(
            popupId,
            {"key": msg.key}
          );
          break;
        case "bleDeviceConnectedEvent":
          log("received info, that ble device connected succesfull");
          chrome.runtime.sendMessage(
            popupId,
            {"key": msg.key}
          );
          break;
        case "request_setup_domain_and_username":
          // it asks for the domain that the user chose for the setup
          log("received request for setup domain and username");
          getStorageSession("domainBySetup").then( (domain) => {
            getStorageSession("usernameBySetup").then( (username) => {
              webSocket.send(JSON.stringify({
                "key": "ble_send",
                "ble_msg": {
                  "key": "response_setup_domain_username",
                  "domain": domain,
                  "username": username
                }
              }));
            });
          });
          break;
        case "request_domain_and_username":
          // it asks for the current domain (active window, active tab).
          getDomain( (domain) => {
            getStorageSession("url_username_dict").then( (dict) => {
              let username = null;
              if (domain in dict) {
                username = dict[domain];
              }
              webSocket.send(JSON.stringify({
                "key": "ble_send",
                "ble_msg": {
                  "key": "response_domain_username",
                  "domain": domain,
                  "username": username
                }
              }));
            });
          });
          break;
        case "setup_complete":
          log("received info, that setup is completed");
          chrome.storage.session.set({"isSetupComplete": true}).then(() => {
            chrome.runtime.sendMessage(
              popupId,
              {"key": msg.key}
            );
          });
          break;
        case "btAdapterIsDisabled":
          log("received info, that bt adapter is disabled");
          chrome.runtime.sendMessage(
            popupId,
            {"key": "btAdapterIsDisabled"}
          );
          break;
        case "btNotSupported":
          log("received info, that bt is not supported on this device");
          chrome.runtime.sendMessage(
            popupId,
            {"key": "btNotSupported"}
          );
          break;
      }
    } catch (error) {
      console.error(error);
    }
  };

  webSocket.onclose = (event) => {
    log('[WS]: Connection closed. Trying to reconnect in 2s...');
    webSocket = null;
    // Tell popup that background app disconnected:
    chrome.runtime.sendMessage(
      popupId,
      {"key": "background_app_disconnected_event"}
    );
    setTimeout(function() {
      ws_connect();
    }, 2000);

  };
}

function ws_disconnect() {
  if (webSocket == null) {
    return;
  }
  webSocket.close();
}

function ws_keepAlive() {
  const keepAliveIntervalId = setInterval(
    () => {
      if (webSocket) {
        webSocket.send('keepalive');
      } else {
        clearInterval(keepAliveIntervalId);
      }
    },
    // Set the interval to 20 seconds to prevent the service worker from becoming inactive.
    20 * 1000 
  );
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
    // && /^http/.test(tab.url)) {
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ["./foreground.js"]
      })
      .then(() => {
          log("injected foreground script");
      })
      .catch(err => log(err));
    }
});

chrome.storage.onChanged.addListener((changes, namespace) => {
  // observe storage changes:
  for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
    log(
      `Storage key "${key}" in namespace "${namespace}" changed.\n` +
      `Old value was "${oldValue}", new value is "${newValue}".`
    );
  }
});

// Messaging within the extension (popup, foreground):
chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) {
  let msg_to_send = null;
  switch(msg.key) {
    case "found_totp_element":
      foregroundTabId = parseInt(sender.tab.id);
      log("forwarding request totp to native app");
      msg_to_send = JSON.stringify({
        "key": "ble_send",
        "ble_msg": {
          "key": "request_totp",
          "domain": msg.domain,
          "username": msg.username
        }
      });
      webSocket.send(msg_to_send);
      break;
    case "scan_ble":
      popupId = sender.id;
      log("forwarding command to scan for BLE devices");
      msg_to_send = JSON.stringify({
        "key": "scan_ble"
      });
      webSocket.send(msg_to_send);
      break;
    case "disconnect_ble":
      log("forwarding command to disconnect BLE");
      popupId = sender.id;
      webSocket.send(JSON.stringify( {"key": "disconnect_ble"} ));
      break;
    case "connect_with_ble_device":
      log("forwarding command to connect with ble device " + msg.id);
      popupId = sender.id;
      webSocket.send(JSON.stringify({
        "key": "connect_with_ble_device",
        "id": msg.id
      }));
      break;
    case "stop_scan_ble":
      log("forwarding command to stop ble scanning");
      popupId = sender.id;
      webSocket.send(JSON.stringify(msg));
      break;
    case "check_ble_device_connection":
      log("forwarding command to check if ble device is still connected");
      popupId = sender.id;
      log("forwarding request totp to native app");
      msg_to_send = JSON.stringify({
        "key": "ble_send",
        "ble_msg": msg
      });
      webSocket.send(msg_to_send);
      break;
    case "await_qr_scan":
      log("forward: await qr scan");
      popupId = sender.id;
      msg_to_send = JSON.stringify({
        "key": "ble_send",
        "ble_msg": msg
      });
      webSocket.send(msg_to_send);
      break;
    case "dont_await_qr_scan":
      log("forward: dont_await_qr_scan");
      popupId = sender.id;
      msg_to_send = JSON.stringify({
        "key": "ble_send",
        "ble_msg": msg
      });
      webSocket.send(msg_to_send);
      break;
    case "check_ble_support":
      log("forward: check_ble_support");
      popupId = sender.id;
      msg_to_send = JSON.stringify({
        "key": "check_ble_support"
      });
      webSocket.send(msg_to_send);
      break;
  }
  return true;
});

async function getDomain() {
  let tabs = await chrome.tabs.query({active: true, currentWindow: true});
  let url = tabs[0].url;
  let domain = new URL(url).hostname.replace("www.", "");
  return domain;
}

// // Native Messaging:
// console.log("Connecting...");
// try {
//   var port = chrome.runtime.connectNative('bluetotp');
// }
// catch(err) {
//   console.log(err.message);
// }
// console.log(port)
// port.onMessage.addListener(function (msg) {
//   console.log('Received' + msg);
// });
// port.onDisconnect.addListener(function () {
//   console.log('Disconnected');
//   if (chrome.runtime.lastError) {
//     console.log(chrome.runtime.lastError.message);
//   }
// });

// setInterval(function() {
//     console.log("Sending: Hello from Extension");
//     try {
//       port.postMessage({text: 'Hello, from Extension'});
//     }
//     catch(err) {
//       console.log(err.message);
//     }
//     // chrome.runtime.sendNativeMessage(
//     //   'bluetotp',
//     //   {text: 'Hello from Extension'},
//     //   function (response) {
//     //     console.log('Received ' + response);
//     //   }
//     // );
// }, 2000)
