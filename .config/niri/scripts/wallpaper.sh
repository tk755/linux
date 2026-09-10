#!/usr/bin/env bash

wallpaper_dir="$HOME/.wallpapers"
if [[ -f "$wallpaper_dir/$HOSTNAME" ]]; then
    exec swaybg -i "$wallpaper_dir/$HOSTNAME" -m fill
elif [[ -f "$wallpaper_dir/default" ]]; then
    exec swaybg -i "$wallpaper_dir/default" -m fill
fi
