# Blue TOTP Service

## Setup
- install [Node.js](https://nodejs.org/en/download)
- probably you need to **reboot your PC** before the following steps work
- check installtion with `node -v` and `npm -v`
- in this dir run: `npm install --save-dev electron`

## Develop / Debug
- run app: `npm start`

## Build Executeables
Install electron-builder:
- `npm i --save-dev electron-builder`
Build installer:
- `npm run build`
- you can find the install executable in dir `dist`

## Informative Stuff
- [how to install a nsis plugin](https://stackoverflow.com/questions/54398357/use-inetc-plugin-for-nsis-with-electron-builder)
- [electron first app tutorial](https://www.electronjs.org/docs/latest/tutorial/tutorial-first-app)
- [electron distribute and package your app](https://www.electronjs.org/docs/latest/tutorial/quick-start#package-and-distribute-your-application)
- [electron build](https://www.electron.build)
- [native Messaging](https://developer.chrome.com/docs/extensions/mv3/nativeMessaging/)