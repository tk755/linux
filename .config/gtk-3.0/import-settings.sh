#!/usr/bin/env bash
# https://github.com/swaywm/sway/wiki/GTK-3-settings-on-Wayland

# gtk-3 config path
config="${HOME}/.config/gtk-3.0/settings.ini"
if [[ ! -f "${config}" ]]; then return 1; fi

# extract gtk-3 settings
gtk_theme="$(sed -n 's/^gtk-theme-name=//p' "${config}")"
icon_theme="$(sed -n 's/^gtk-icon-theme-name=//p' "${config}")"
font_name="$(sed -n 's/^gtk-font-name=//p' "${config}")"
cursor_theme="$(sed -n 's/^gtk-cursor-theme-name=//p' "${config}")"

# set gtk-3 settings
gnome_schema='org.gnome.desktop.interface'
if [[ -n "${gtk_theme}" ]]; then gsettings set "${gnome_schema}" gtk-theme "${gtk_theme}"; fi
if [[ -n "${icon_theme}" ]]; then gsettings set "${gnome_schema}" icon-theme "${icon_theme}"; fi
if [[ -n "${font_name}" ]]; then gsettings set "${gnome_schema}" font-name "${font_name}"; fi
if [[ -n "${cursor_theme}" ]]; then gsettings set "${gnome_schema}" cursor-theme "${cursor_theme}"; fi
gsettings set "${gnome_schema}" color-scheme 'prefer-dark'
