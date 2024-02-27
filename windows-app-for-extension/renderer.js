const ServiceUUID = "2e076308-26cb-4a9c-a79a-e3ec22b3f852";
const RxCharacteristicUUID = "2e076308-26cb-4a9c-a79a-e3ec22b3f853";
const TxCharacteristicUUID = "2e076308-26cb-4a9c-a79a-e3ec22b3f854";
let RxCharacteristic = null;
let TxCharacteristic = null;
let BLEDevice = null;

async function scanBLE() {
  let options = {
    filters: [
      { services: [ServiceUUID] }
    ]
  };
  console.log("bt scan filters:");
  console.log(options);

  let device;
  try {
    // requestDevice() will return when the user choose a device in the browser extension:
    device = await navigator.bluetooth.requestDevice(options);
  } catch (error) {
    if (error.message == "User cancelled the requestDevice() chooser.") {
      console.log("Probably bt adapter is turned off");
      window.api.send("btAdapterIsDisabled", null);
      return;
    } else {
      console.error(error);
      return;
    }
  }
  BLEDevice = device;
  console.log(device);

  device.addEventListener('gattserverdisconnected', onGattServerDisconnected);
  try {
    let server = await device.gatt.connect();
    let service = await server.getPrimaryService(ServiceUUID);
    RxCharacteristic = await service.getCharacteristic(RxCharacteristicUUID);
    await RxCharacteristic.startNotifications();
    RxCharacteristic.addEventListener('characteristicvaluechanged', onRxCharacteristicValueChanged);
    TxCharacteristic = await service.getCharacteristic(TxCharacteristicUUID);
    console.log("connection startup complete")
    // inform main.js about successfull connection:
    window.api.send("bleDeviceConnectedEvent", null);
  }
  catch(error) {
    if (error.message == "Connection failed for unknown reason.") {
      resetBleStuff();
      console.error(error);
    } else {
      console.error(error);
    }
  }
};

function onRxCharacteristicValueChanged(event) {
  const value = new TextDecoder().decode(event.target.value);
  // value is already a dictionary {"key": "message identifier", ...}
  console.log('Rx Characteristic changed to:');
  console.log(value);
  window.api.send("rxCharacteristicChangedEvent", value);
}

async function disconnectBLE() {
  console.log("RX characteristic: " + RxCharacteristic);
  console.log("BLEDevice: " + BLEDevice);
  if (BLEDevice) {
    // gatt.disconnect fires the gattserverdisconnected event.
    BLEDevice.gatt.disconnect();
  }
}

function onGattServerDisconnected(event) {
  const device = event.target;
  console.log(`disconnected from ${device.name}`);
  resetBleStuff();
}

function resetBleStuff() {
  if (RxCharacteristic) {
    RxCharacteristic.removeEventListener('characteristicvaluechanged', onRxCharacteristicValueChanged);
    RxCharacteristic = null;
  }
  if (BLEDevice) { BLEDevice = null; }
  window.api.send("bleDeviceDisconnectedEvent", null);
}

window.api.receive("ble_send", async (ble_msg) => {
  ble_send(ble_msg);
});

async function ble_send(ble_msg) {
  // ble_msg is a dict {"key": "msg id", ...}
  ble_msg = JSON.stringify(ble_msg);
  console.log("Sending on tx characteristic: " + ble_msg);

  if (!BLEDevice || !TxCharacteristic) {
    console.log("Couldn't send message: no object in BLEDevice or txCharacteristic.")
    resetBleStuff();
    return;
  }

  TxCharacteristic.writeValue(new TextEncoder().encode(ble_msg)).then(() => {
    console.log("still connected")
  }).catch((error) => {
    if (error.message == "GATT Service no longer exists.") {
      console.log("not connected anymore")
      resetBleStuff();
    } else {
      console.error(error);
    }
  })
}

async function isBleSupported() {
  let isBleAvaiable;
  try {
    isBleAvaiable = await navigator.bluetooth.getAvailability();
  } catch (error) {
    console.log(error);
    return false;
  }

  if (isBleAvaiable) {
    console.log("bt is supported")
    return true;
  } else {
    console.error("bt is not supported");
    return false;
  }
}
