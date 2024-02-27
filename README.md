# master-thesis
Master thesis about more usable and phishing resistent time-based one-time passwords.
It's written in german only.

If you build the software components by yourself, always change into the respective dir before running any commands.

## 1. Explanation
Besides my master thesis and the related tex stuff, you can see four software components.

The web app is just an extra for my finished study. But you can use it if the server is not shut down.
- https://totp-study.informatik.tu-freiberg.de/

The Android app ist a TOTP app which makes use of bluetooth to send the totp to the extension (the connection is not secure, don't use this for real accounts!)

The Chrome Extension reads your username and the domain you are visiting, so the android app can identify the TOTP secret to send you the TOTP after you accepted a notification. The TOTP will be enteren autmatically by the extension into the browser.

## 2. Install Blue TOTP (Win10/11 and Android 10 or higher)
For lazy people which have the needed devices and which have luck by reaching the host (maybe it will be shut down).

On your Window 10/11 device with the Chrome Browser installed:
- download everything from here and follow the instructions https://totp-study.informatik.tu-freiberg.de/?page=download_pc
- ignore the onboarding in the extension

On your Android device:
- download https://totp-study.informatik.tu-freiberg.de/?page=download_app
- ignore the onboarding in the app

If you want, register at the webservice of the study:
- Don't reuse your passwords! Use a dummy password, it's just a fictional web service.
- https://totp-study.informatik.tu-freiberg.de/?page=registration


## 3. Data
In `ma/data_processing/` you can find a `README.md` for how to process all the raw data and render plots, create csv files and more.
This is the data I acquired by some users who participated in my study. The data is anonymised.

## 4. Web App
In `web-app/` you can find the web service made with streamlit. Check out the `README.md` there as well. This is the thing which you can see at https://totp-study.informatik.tu-freiberg.de/ (hopefully).

## 5. Android App
In `android-app/` you can find the android app. Just download android studio, start it and open the directory `android-app/`.
It's only tested until Android 13.

## 6. Chrome Extension
This is straightforward. Follow the easy instructions in the `chrome-extension/README.md`.

## 7. Windows Background App to Enhance the Extension
Look at `windows-app-for-extension/README.md`. 