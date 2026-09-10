#!/usr/bin/env bash
set -euo pipefail

main() {
    # import gtk3 settings
    source "${HOME}/.config/gtk-3.0/import-settings.sh" ||
        printf 'GTK settings import failed\n' >&2

    # set wallpaper
    local wallpaper_dir="${HOME}/.wallpapers"
    if [[ -f "${wallpaper_dir}/${HOSTNAME}" ]]; then
        exec swaybg -i "${wallpaper_dir}/${HOSTNAME}" -m fill
    elif [[ -f "${wallpaper_dir}/default" ]]; then
        exec swaybg -i "${wallpaper_dir}/default" -m fill
    fi
}

main "$@"
