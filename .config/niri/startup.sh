#!/usr/bin/env bash
set -euo pipefail

# Keep GTK's portal settings in sync with the existing GTK 3 configuration.
python3 - <<'PY'
import configparser
from pathlib import Path
import subprocess

config = configparser.ConfigParser(interpolation=None)
config.read(Path.home() / '.config/gtk-3.0/settings.ini')
if config.has_section('Settings'):
    settings = config['Settings']
    for source, target in (
        ('gtk-theme-name', 'gtk-theme'),
        ('gtk-icon-theme-name', 'icon-theme'),
        ('gtk-font-name', 'font-name'),
        ('gtk-cursor-theme-name', 'cursor-theme'),
    ):
        if settings.get(source):
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface',
                            target, settings[source]], check=True)
    if settings.getboolean('gtk-application-prefer-dark-theme', fallback=False):
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface',
                        'color-scheme', 'prefer-dark'], check=True)
PY

wallpaper_dir="$HOME/.wallpapers"
if [[ -f "$wallpaper_dir/$HOSTNAME" ]]; then
    exec swaybg -i "$wallpaper_dir/$HOSTNAME" -m fill
elif [[ -f "$wallpaper_dir/default" ]]; then
    exec swaybg -i "$wallpaper_dir/default" -m fill
fi
