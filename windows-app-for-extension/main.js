const { app, BrowserWindow, ipcMain, nativeImage, Tray, Menu} = require("electron");
const path = require("path");
const fs = require('fs');
const WebSocket = require("ws");

const WSSPORT = 3030;
const CONFIG_KEY_INITIAL_AFTER_INSTALL = "initial_after_install"

let mainWindow;
let BLEDevicesWindow;
let BLEDevicesList=[];
let webSocket;
let wss; //web socket server
let tray = null // system tray (e.g.: in windows this is the menu including the small icons of apps (mostly apps that run in the background))
var isAppQuitting = false;

let callbackForBluetoothEvent = null;
const dataPath = app.getPath('userData');
const filePath = path.join(dataPath, 'config.json');
console.log("path to config: " + filePath);

// ------------------- Functions ------------------------

function writeConfig(key, value){
  let config = getParsedConfig();
  config[key] = value;
  fs.writeFileSync(filePath, JSON.stringify(config));
}

function readConfig(key) {
 let config = getParsedConfig();
 return config[key]
}

function getParsedConfig(){
  const dict = {}
  try {
   return JSON.parse(fs.readFileSync(filePath));
 } catch(error) {
   return dict;
 }
}

function createTray () {
  const icon = path.join(__dirname, '/icon.ico')
  const trayicon = nativeImage.createFromPath(icon)
  tray = new Tray(trayicon.resize({ width: 16 }))
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Beenden',
      click: () => {
        console.log("quit app");
        app.quit() // actually quit the app.
      }
    },
  ])
  tray.on("click", () => {
    mainWindow.show(0);
  })
  tray.setToolTip('Blue TOTP Service')
  tray.setContextMenu(contextMenu)
}

function createWindow(isRestarted = false) {
  if (!tray) { // if tray hasn't been created already.
    createTray()
  }

  // Sometimes we need to restart renderer.js but then we don't want the window to be shown:
  let showWindow;
  if (isRestarted) {
    showWindow = false;
  } else {
    showWindow = readConfig(CONFIG_KEY_INITIAL_AFTER_INSTALL) // true when app was run for the first time after install, false otherwise
  }

  mainWindow = new BrowserWindow({
    show: showWindow,
    width: 800,
    height: 600,
    icon: __dirname + "/icon.ico",
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  // mainWindow.removeMenu();

  mainWindow.on("close", async event => {
    if (!isAppQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  })

  mainWindow.webContents.on("select-bluetooth-device", (event, deviceList, callback) => {
    event.preventDefault(); // do not choose the first one

    if (deviceList && deviceList.length > 0) {  // find devices?
      deviceList.forEach((element) => {
        if (BLEDevicesList.length > 0) {  // BLEDevicesList not empty?
          if (
            BLEDevicesList.findIndex(     // element is not already in BLEDevicesList
              (object) => object.deviceId === element.deviceId
            ) === -1
          ) {
            BLEDevicesList.push(element);
            console.log(BLEDevicesList);
            webSocket.send(JSON.stringify({"key": "ble_device_list", "ble_device_list": BLEDevicesList}));
          }
        } else {
          BLEDevicesList.push(element);
          console.log(BLEDevicesList);
          webSocket.send(JSON.stringify({"key": "ble_device_list", "ble_device_list": BLEDevicesList}));
        }
      });
    }

    callbackForBluetoothEvent = callback; // to make it accessible outside
  });

  mainWindow.loadFile("index.html");
  // mainWindow.webContents.openDevTools();
  mainWindow.webContents.once("did-finish-load", function () {
    if (wss) { wss.close(); }
    initWebSocket();
  });
}

function initWebSocket() {
  wss = new WebSocket.WebSocketServer({ port: WSSPORT });

  wss.on("connection", (ws) => {
    webSocket = ws; 
    ws.on("message", (msg) => {
      console.log("[WS]: " + msg);
      if ("ctl" in msg) {
        return;
      }
      try {
        msg = JSON.parse(msg);

        switch (msg.key) {
          case "scan_ble":
            console.log("Received command to scan ble.");
            BLEDevicesList = [];
            mainWindow.close();
            createWindow(isRestarted=true);
            mainWindow.webContents.executeJavaScript(`scanBLE().catch(error => console.error(error));`, true);
            break;
          case "disconnect_ble":
            console.log("Received command to disconnect ble.");
            mainWindow.webContents.executeJavaScript(`disconnectBLE().catch(error => console.error(error));`);
            break;
          case "connect_with_ble_device":
            console.log("Received command to connect to ble device " + msg.id);
            console.log(BLEDevicesList.find((item) => item.deviceId === msg.id));
            let BLEDevicesChoosen = BLEDevicesList.find((item) => item.deviceId === msg.id);
            BLEDevicesList = [];  // clear for next scan
            if (!BLEDevicesChoosen) {
              callbackForBluetoothEvent(""); // stop BLE scan
            } else {
              callbackForBluetoothEvent(BLEDevicesChoosen.deviceId);  // stop BLE scan
            }
            break;
          case "stop_scan_ble":
            // stop BLE scan is only possible when we call callbackForBluetoothEvent. But this is only defined when the scanning process found a device (https://github.com/electron/electron/issues/20331So). We will do a workaround by restarting the renderer here:
            mainWindow.close();
            BLEDevicesList = [];
            createWindow(isRestarted=true);
            break;
          case "ble_send":
            console.log("received command to send via ble:");
            console.log(msg.ble_msg);
            mainWindow.webContents.send("ble_send", msg.ble_msg);
            break;
          case "check_ble_support":
            // Check if Bluetooth is supported by the PC:
            console.log("received command to check_ble_support:");
            mainWindow.webContents.executeJavaScript(`isBleSupported().then((ret) => { return ret; });`, true).then((isBleSupported) => {
              if (!isBleSupported) {
                console.log("bt not supported");
                webSocket.send(JSON.stringify( {"key": "btNotSupported"}));
              } else {
                console.log("bt supported");
                // no need to inform the extension
              }
            });
            break;
        }
      } catch (error) {
        console.error(error);
      }
    });
  
    //send immediatly a feedback to the incoming connection
    ws.send(JSON.stringify({"ctl": "Hello from WebSocket server"}));
  });
}

// ------------------------- Running Code ---------------------------

// Track if we started app directly after installing it:
if ( !(CONFIG_KEY_INITIAL_AFTER_INSTALL in getParsedConfig()) ) {
  console.log("writing cfg to true")
  writeConfig(CONFIG_KEY_INITIAL_AFTER_INSTALL, true);
} else if (readConfig(CONFIG_KEY_INITIAL_AFTER_INSTALL)) {
  console.log("write cfg to false")
  writeConfig(CONFIG_KEY_INITIAL_AFTER_INSTALL, false);
}

// app related
app.whenReady().then(() => {
  createWindow();
  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("before-quit", () => {
  isAppQuitting = true;
});

app.on("window-all-closed", function () {
  if (process.platform == "darwin") {
    app.dock.hide() // for mac os
  }
});

// Communication with renderer.js:

// From BLEDevicesRenderer:
ipcMain.on("toMain", (event, args) => {
  console.log(args);
});
// From BLEDevicesRenderer:
ipcMain.on("BLEScanFinished", (event, args) => {
  console.log(args);
  console.log(BLEDevicesList.find((item) => item.deviceId === args));
  let BLEDevicesChoosen = BLEDevicesList.find((item) => item.deviceId === args);
  BLEDevicesList = [];  // clear for next scan
  if (!BLEDevicesChoosen) {
    callbackForBluetoothEvent(""); // stop BLE scan
  } else {
    callbackForBluetoothEvent(BLEDevicesChoosen.deviceId);  // stop BLE scan
  }
  
});
// From BLEDevicesRenderer:
ipcMain.on("getBLEDeviceList", (event, args) => {
  if (BLEDevicesWindow) {
    BLEDevicesWindow.webContents.send("BLEDeviceList", BLEDevicesList);
  }
});
// From renderer:
ipcMain.on("bleDeviceDisconnectedEvent", (event, args) => {
  console.log("main received bleDeviceDisconnectedEvent");
  webSocket.send(JSON.stringify( {"key": "bleDeviceDisconnectedEvent"} ));
});
ipcMain.on("bleDeviceConnectedEvent", (event, args) => {
  console.log("main received bleDeviceConnectedEvent");
  webSocket.send(JSON.stringify( {"key": "bleDeviceConnectedEvent"}));
});
ipcMain.on("rxCharacteristicChangedEvent", (event, args) => {
  console.log("main received rxCharacteristicChangedEvent");
  console.log(args);
  // Just forward the value, it is already a dictionary {"key": "msg id", ...}
  webSocket.send(args);
});
ipcMain.on("btAdapterIsDisabled", (event, args) => {
  console.log("main received btAdapterIsDisabled");
  webSocket.send(JSON.stringify( {"key": "btAdapterIsDisabled"}))
});
