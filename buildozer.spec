[app]
# COMET ZIP - original Kivy Android platformer
# Build from this directory with: buildozer android debug
title = Comet Zip
package.name = cometzip
package.domain = org.cometzip
source.dir = game
source.include_exts = py,png,jpg,jpeg,wav,ogg,json,atlas,ttf
version = 1.0.0
requirements = python3,kivy
orientation = landscape
fullscreen = 1

# Android touch / packaging settings
android.api = 33
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.presplash_color = #07132A
android.allow_backup = False
android.numeric_version = 10000
android.entrypoint = org.kivy.android.PythonActivity
android.add_src = %(source.dir)s

# Keep build/release output outside the source tree
build_dir = .buildozer
bin_dir = bin

[buildozer]
log_level = 2
warn_on_root = 1
