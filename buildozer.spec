[app]
title = Sabahoglu Apartmani
package.name = sabahogluapartmani
package.domain = org.apartman
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,flet,pillow
orientation = portrait
fullscreen = 0

# Android için kritik izinler (Galeriye kayıt yapabilmek için)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.min_api = 21
android.ndk = 25b
android.sdk = 30
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
android.accept_sdk_license = True
