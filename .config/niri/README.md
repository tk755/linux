# niri

Niri 26.04, with the agreed positional keymap adapted from Sway. The configuration
does not include niri's stock keybindings. Ctrl replaces the old secondary Shift
modifier. TTY1 login starts niri through `niri-session`, with Sway still installed
as a fallback.

## Layout and navigation

A workspace contains a horizontal strip of columns. A column contains one or
more windows stacked vertically, all visible; tabs are unused. New windows
normally create new half-width columns. Firefox creates a full-width column,
which still leaves the bar and gaps visible. Super+F is actual fullscreen.
Firefox picture-in-picture and the existing Waybar popup terminals float.

Workspaces form a vertical list on each monitor. Indices 1–9 refer to their current
positions; reordering or removing workspaces changes those indices. A bottom empty
workspace is always available. Super+V selects it, and Super+Ctrl+V sends a window
there without following it. No fixed or persistent workspaces are declared.

Super+K/L focuses down/up within a column, then moves to the next workspace at the
edge. Super+Ctrl+K/L moves windows down/up within the column, then to the adjacent
workspace at its edges, following the moved window.
Super+Ctrl+J/semicolon moves the whole column horizontally.

Super+comma/period moves the focused window through the left/right side of its
column: an isolated window joins the neighboring column; a grouped window leaves
into a new column on that side. Super+Ctrl+comma/period reorders whole workspaces
up/down. Super+Ctrl+M/slash moves a whole workspace to the left/right monitor.

Native touchpad gestures: three fingers horizontally scroll columns; three fingers
vertically switch workspaces; four fingers vertically open/close overview. Bare
Super and an overview keybinding are intentionally unassigned. Native gesture
finger counts are not configurable in this version. Short, non-bouncing animations
retain movement/fullscreen feedback. Keyboard repeat stays at 600 ms delay, 25 Hz.

## Workspace names

Super+Return opens a fuzzel prompt with the current name prefilled. Enter applies
the name; Escape or an empty submission cancels. Duplicate names are rejected.
The prompt targets the original workspace by its stable ID even if it moves.

Niri normally preserves named workspaces when empty. `workspaces.py watch` removes
the name when the workspace is empty and no longer visible on its monitor; niri
then cleans it up. This lets you name an empty workspace before launching apps.
An empty workspace still visible on another monitor keeps its name. Disconnected
outputs and floating windows are accounted for. Names are temporary session labels,
not a saved window/session restoration mechanism. No unname shortcut is assigned.

Waybar shows the current workspace's name, or its index when unnamed. Niri's
overview does not draw workspace-name labels directly on every thumbnail; the
bar remains the name display. The niri Waybar files include the shared Waybar
configuration/style and override only the workspace module.

## Positional keymap

Each row follows the 3×10 letter block of the Planck layout. Other physical key
positions are not inferred from the Sway configuration. `—` is unassigned.

Super:

```text
Q:WS1    W:WS2    E:WS3    R:—       T:—        | Y:Spotify  U:width½  I:height½ O:height1 P:width1
A:WS4    S:WS5    D:WS6    F:fullscr G:terminal | H:Firefox  J:focus←  K:focus↓  L:focus↑  ;:focus→
Z:WS7    X:WS8    C:WS9    V:emptyWS B:files    | N:VSCode   M:screen← ,:group←  .:group→  /:screen→
```

Super+Ctrl:

```text
Q:send1  W:send2  E:send3  R:—       T:—        | Y:—        U:width−5 I:height−5 O:height+5 P:width+5
A:send4  S:send5  D:send6  F:—       G:Claude   | H:private  J:column← K:window↓ L:window↑ ;:column→
Z:send7  X:send8  C:send9  V:sendNew B:—        | N:newCode  M:WSscr←  ,:WS↑     .:WS↓     /:WSscr→
```

Send moves only the focused window without following it. Super+U/I/O/P snaps to
half width, half height, full height, and full width respectively. Ctrl+U/I/O/P
adjusts those dimensions by −5%, −5%, +5%, and +5% of the working area. Width is
column-wide for tiled windows; full width is distinct from Super+F fullscreen.

| Key | Super | Super+Ctrl |
| --- | --- | --- |
| Return | Name/rename workspace | Unassigned |
| Space | Focus floating/tiling layer | Toggle floating |
| Tab | Previous workspace | Unassigned |
| Apostrophe | Close window | Unassigned |
| Escape | fuzzel app launcher | Unassigned |
| Backspace | Reload config | swaylock |

Brightness, playback, seeking and volume keys retain their original commands.
Only Play, Pause and Stop work while locked. Print bindings await the next round;
the original Sway screenshot bindings remain in the Sway config.

## Migration differences and deferred work

- Sway's parent/child tree navigation, split direction and tabbed-layout commands
  are removed. Niri's columns replace arbitrary nested split trees.
- The gaps toggle is removed; gaps stay at 8 logical pixels.
- Resizing uses niri's percentage changes, rather than Sway's tiled-versus-floating
  `px or ppt` behavior. No compatibility helper emulates Sway's tree semantics.
- Default session startup uses niri's systemd integration. Wallpaper selection and
  GTK theme settings are retained. X11 applications use xwayland-satellite on demand.
- The BOE display ICC profile cannot be applied by niri. Sway's renderer/color
  management setting is kept only in the fallback startup path.
- Print bindings, bare-Super overview and hibernation remain deferred. Hibernation
  needs disk-backed swap/resume setup; the machine currently uses only zram swap.
- Native niri does not restore all application windows and their layout after
  shutdown. Hibernation is the future system-level approach we agreed to investigate.

## Validation and fallback

Run `niri validate` after editing. Niri also reloads saved configuration automatically.
The migration was checked with the installed compositor and an isolated nested
session, including grouping/extraction, naming, moving windows without following,
and removal of empty names after switching workspaces.

On the next TTY1 login, `~/.bash_profile` starts `niri-session`. The current
session is not automatically closed by this change. Sway remains available from
an unused TTY with:

```sh
WLR_RENDERER=vulkan XDG_CURRENT_DESKTOP=sway sway
```

## Session integration

- `~/.bash_profile` prefers `niri-session` on an interactive TTY1 login, with Sway
  as a fallback when niri is not installed. The interactive guard prevents recursion
  through niri-session's own noninteractive login shell.
- `~/.bin/bootstrap` excludes `.config/niri` in headless installations.
- `~/.hosts/suzuki/install` includes niri, xwayland-satellite and the GNOME portal
  in the desktop package list; Sway is retained for fallback use.

References: [niri configuration](https://niri-wm.github.io/niri/Configuration:-Introduction.html),
[named workspaces](https://niri-wm.github.io/niri/Configuration:-Named-Workspaces.html),
[animations](https://niri-wm.github.io/niri/Configuration:-Animations.html),
[session integration](https://niri-wm.github.io/niri/Getting-Started.html).
