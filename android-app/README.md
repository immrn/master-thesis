# FreeOTP Plus
- immrn (BlueTOTP) here: this is the readme and repo of the freeOTP plus app. I enhanced the app with bluetooth functionality to communicate with my extension. Look at [this commit](https://github.com/immrn/FreeOTPPlusBlueTOTP/commit/0b2aaf3fe265e4095d31c6f4210a0620421f87e8) of my real repo. This is the commit where I added FreeOTPplus. Use that commit to diff to the latest commit there to see my part of contribution. End of my message!

FreeOTP Plus forked the same functionality of FreeOTP provided by RedHat with the following enhancement:
* Export settings to Google Drive or other document providers
* Import settings from Google Drive or other document providers
* Lots of stability improvement
* Support Android 6.0 permissions.
* Enhanced UI with material design with dark theme support
* Search bar to search token
* Provide more token details for better interoperatibility with other apps
* Utilize modern camera hardware to scan QR code faster
* Option to require Biometric / PIN authentication to launch the app
* Heuristic based offline icon for tokens of 250+ websites.
* More settings to customize the app functionality

Most part of the code is re-written with modern Jetpack libraries and Kotlin language.

<a href="https://f-droid.org/packages/org.liberty.android.freeotpplus/" target="_blank">
<img src="https://f-droid.org/badge/get-it-on.png" alt="Get it on F-Droid" height="80"/></a>
<a href="https://play.google.com/store/apps/details?id=org.liberty.android.freeotpplus" target="_blank">
<img src="https://play.google.com/intl/en_us/badges/images/generic/en-play-badge.png" alt="Get it on Google Play" height="80"/></a>

# Build Dependencies
* Android SDK
* Android Studio 4.0+

# Translate

[Crowdin](https://crowdin.com/project/freeotpplus) can be used for translation if you are uncomfortable working with strings.xml files.  
If your language is not listed, please open an issue so we can add it.  
If you don't like to use Crowdin feel free to submit a pull with the updated/added locales.

Link: https://crowdin.com/project/freeotpplus
