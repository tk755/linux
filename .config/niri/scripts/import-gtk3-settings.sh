#!/usr/bin/env bash
# Import GTK 3 settings for applications that use the settings portal.

config="$HOME/.config/gtk-3.0/settings.ini"
[[ -f "$config" ]] || exit 0

import_setting() {
    local value
    value=$(sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//p" "$config")
    if [[ -n "$value" ]]; then
        gsettings set org.gnome.desktop.interface "$2" "$value"
    fi
}

import_setting gtk-theme-name gtk-theme
import_setting gtk-icon-theme-name icon-theme
import_setting gtk-font-name font-name
import_setting gtk-cursor-theme-name cursor-theme

if grep -Eiq '^[[:space:]]*gtk-application-prefer-dark-theme[[:space:]]*=[[:space:]]*(1|true|yes|on)[[:space:]]*$' "$config"; then
    gsettings set org.gnome.desktop.interface color-scheme prefer-dark
fi
