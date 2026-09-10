# source environment variables and tools
if [[ -f "$HOME/.bash/env.sh" ]]; then
    source "$HOME/.bash/env.sh"
fi

# start desktop session from interactive TTY1 login
if [[ $- == *i* && -z "${WAYLAND_DISPLAY:-}" && -z "${DISPLAY:-}" && ${XDG_VTNR:-0} == 1 ]]; then
    if command -v niri-session &>/dev/null; then
        exec niri-session
    elif command -v sway &>/dev/null; then
        # vulkan required for icc color management on sway
        export WLR_RENDERER=vulkan
        export XDG_CURRENT_DESKTOP=sway
        exec sway
    elif command -v startx &>/dev/null; then
        exec startx
    fi
fi

# set up interactive shell session
if [[ -f "$HOME/.bashrc" ]]; then
    source "$HOME/.bashrc"
fi
