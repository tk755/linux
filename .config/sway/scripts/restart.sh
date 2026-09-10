#!/usr/bin/env bash

# set wallpaper
wallpaper_dir="$HOME/.wallpapers"
if [[ -f "$wallpaper_dir/$HOSTNAME" ]]; then
    swaymsg "output * bg '$wallpaper_dir/$HOSTNAME' fill"
elif [[ -f "$wallpaper_dir/default" ]]; then
    swaymsg "output * bg '$wallpaper_dir/default' fill"
fi

# import gtk3 settings
source "${HOME}/.config/gtk-3.0/import-settings.sh"