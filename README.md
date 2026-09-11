# Machines

This repository defines the unified Linux environment across my machines.

## Bootstrap

`~/.bin/bootstrap` installs and updates this repository on a machine idempotently. It clones this repository as a [bare repository](https://www.atlassian.com/git/tutorials/dotfiles) with [sparse checkout](https://git-scm.com/docs/git-sparse-checkout), backing up conflicting files before checkout and restoring them afterward. Stale files from previous installations are removed; local changes are kept unless `--force` is passed.

### New machine

Run the `bootstrap` script directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/tk755/machines/main/.bin/bootstrap | bash
```

### Existing machine

Use the `bootstrap` command to apply the latest changes:

```bash
bootstrap   # see --help for more options
```

## Version control

The `m` alias is provided to interact with the bare repository:

```bash
alias m='git --git-dir=$HOME/.machines.git --work-tree=$HOME'
```

Use it like a `git` command:

```bash
m add ~/.bashrc
m commit -m 'update bashrc'
m push
```

## Conventions

Files are organized by scope:
- `~/.bin/` — user scripts (on `$PATH`)
- `~/.config/**` — application scripts and config files
- `~/.hosts/**` — host scripts and system files

### Host commands

Use the hostname as a command to run scripts in `~/.hosts/<hostname>/`:

```bash
suzuki                # list available commands
suzuki upgrade        # run ~/.hosts/suzuki/upgrade
```
