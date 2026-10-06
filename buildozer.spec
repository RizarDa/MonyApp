[app]

title = Money Manager
package.name = moneyapp
package.domain = org.abolfazl

version = 1.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24

android.permissions = android.permission.POST_NOTIFICATIONS

[buildozer]

log_level = 2
warn_on_root = 0
