# environment variables and tools
if [[ -f "$HOME/.bash/env.sh" ]]; then
    source "$HOME/.bash/env.sh"
fi

# Only interactive TTY1 logins start a desktop. niri-session itself starts a
# noninteractive login shell, so the interactive guard prevents recursion.
if [[ $- == *i* && -z "${WAYLAND_DISPLAY:-}" && -z "${DISPLAY:-}" && ${XDG_VTNR:-0} == 1 ]]; then
    if command -v niri-session &>/dev/null; then
        unset WLR_RENDERER SWAYSOCK
        exec niri-session
    elif command -v sway &>/dev/null; then
        # Vulkan is required for Sway's ICC color management.
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
