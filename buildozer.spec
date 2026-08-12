[app]
title = Megatron Mobile
package.name = megatron
package.domain = org.fatihmakes
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml,wav
version = 1.0

# Dependencies
requirements = python3,kivy,google-generativeai,pyjnius

# Orientation
orientation = portrait

# Android Permissions
android.permissions = RECORD_AUDIO,READ_CONTACTS,CALL_PHONE,SEND_SMS,INTERNET,VIBRATE

# Android API level
android.api = 33
android.minapi = 21

# Splash screen and icon (can customize later)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
