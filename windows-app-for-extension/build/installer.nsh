 !macro customInstall
   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "BlueTOTP" "C:\Program Files\Blue TOTP Service\Blue TOTP Service.exe"
 !macroend

 !macro customUnInstall
   DeleteRegValue HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "BlueTOTP"
   SetShellVarContext current
   RMDir /r "$APPDATA\Blue TOTP Service"
 !macroend