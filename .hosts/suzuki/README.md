# suzuki

Arch Linux on a Framework Laptop 13.

## Specifications

### Hardware

- **Model** — Framework Laptop 13 (manufactured Oct 2025)
- **CPU** — AMD Ryzen 5 7640U
- **GPU** — Radeon 760M (RDNA 3)
- **RAM** — 64GB DDR5-5600
- **Storage** — 2TB WD Black SN850X (reformatted to 4K native)
- **Display** — 13.5" 2880x1920 120Hz (BOE0CB4, custom ICC profile)
- **Wireless** — MT7922 (Wi-Fi + Bluetooth)

### System

- **OS** — Arch Linux
- **Filesystem** — btrfs, subvolumes: `@` `@home` `@snapshots` `@var_log` `@var_cache`
- **Encryption** — LUKS2 via sd-encrypt (TPM2 auto-unlock)
- **Bootloader** — systemd-boot
- **Swap** — zram ram/2 (no swap partition)
- **Desktop** — sway (Wayland)
- **Network** — NetworkManager + iwd backend (MT7922 5GHz stability)
- **Power** — power-profiles-daemon (not tlp, discouraged for Ryzen 7040)
- **Snapshots** — snapper + snap-pac (pacman hooks, no timeline)

## Installation

### 1. Install (automatic)

> Runs unattended after a single password prompt; reboots when finished.

Boot the Arch ISO. Then run:

```bash
iwctl station wlan0 connect "YourNetworkName"
pacman -Sy git
git clone https://github.com/tk755/linux
linux/.hosts/suzuki/install
```

### 2. Post-install (interactive)

> Handles remaining setup that requires user interaction.

After first boot, log in as user tk. Then run:

```bash
nmcli device wifi connect "YourNetworkName" --ask
suzuki post-install
```

### 3. Next steps (manual)

> Requires a browser and credentials.

- Sign into Firefox + Bitwarden
- Sign into VS Code Settings Sync
- Sign into Google

## Modifying the installer

Always comment non-trivial operations with an [Arch Wiki](https://wiki.archlinux.org) link (include the section anchor).

### Functions

Each function is self-contained: it installs its own packages, writes its own config files, and enables its own services. To disable a feature, comment out its call in `main()`.

- `configure_*` — base system, always runs
- `setup_*` — toggleable features
- `install_base` — boot-critical packages (via pacstrap)
- `install_tools` — dev tools and CLI utilities
- `install_desktop` — graphical desktop environment and GUI apps
- `aur_install` — helper for AUR packages, usable from any function

### Config files

**Heredocs** for declarative config (key-value settings, ini files). These are short and readable inline.

**System files** for anything with executable logic (scripts, systemd units, udev rules) and binary artifacts (e.g. ICC profiles). These live in the `root/` directory, mirroring their target path on the filesystem. Each system file is referenced by exactly one function, which copies it to the target filesystem with `install -Dm<mode>`.

```
suzuki/root/    → machine-specific (e.g. MT7922 wifi fixes, ICC profile)
all/root/       → shared across hosts (e.g. OLKB Planck udev rule)
```

## Maintenance

Verified August 2026. Expected behavior, not faults:

- **The fan ramps hard on trivial load, then drops.** The EC drives it from sensors placed away from the APU with a narrow off/max window, so it behaves close to binary. Framework calls this by design ([tracking thread](https://community.frame.work/t/tracking-amd-fw13-fan-speed-jumps-up-high-drops-quickly-back-to-low-off/39875)).
- **Brief CPU spikes to ~90 C.** Tjmax is ~95 C. [Precision Boost 2](https://www.amd.com/en/resources/support-articles/faqs/CPU-PB2.html) boosts until it hits a power or thermal limit. Sustained 95 C *with* clock throttling would be the fault.
- **Clocks drop under sustained load.** Power limits (PPT, then STAPM) settle sustained load at ~28 W. Power budget, not thermal throttling.
- **The `powersave` governor is correct.** Under `amd-pstate-epp` it is the normal governor and EPP does the tuning; forcing `performance` worsens fan noise.

Wear counters are monotonic and device-reported, so they compare directly across years:

| Counter | Aug 2026 | Check |
|---|---|---|
| NVMe wear | 1% used, 100% spare | `sudo nvme smart-log /dev/nvme0n1` |
| Battery cycles | 9 | `cat /sys/class/power_supply/BAT1/cycle_count` |
| Battery health | 100% | `charge_full` vs `charge_full_design` |
