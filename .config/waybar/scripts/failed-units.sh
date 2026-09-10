#!/usr/bin/env bash
# Read-only diagnostics for the Waybar systemd-failed-units indicator.
# The launcher uses Ghostty's --wait-after-command to keep this report open.
set -uo pipefail

export SYSTEMD_COLORS=1
export SYSTEMD_PAGER=cat

printf 'Failed unit report — %s\n' "$(date --iso-8601=seconds)"

for scope in system user; do
    printf '\n━━ %s units ━━\n' "$scope"
    scope_args=()
    if [[ "$scope" == user ]]; then
        scope_args=(--user)
    fi

    if ! units=$(SYSTEMD_COLORS=0 systemctl "${scope_args[@]}" --failed --all --plain --no-legend --no-pager list-units); then
        printf 'Could not query the %s service manager.\n' "$scope"
        continue
    fi
    if [[ -z "$units" ]]; then
        printf 'No failed units.\n'
        continue
    fi

    printf '%s\n' "$units"
    while read -r unit _; do
        [[ -n "$unit" ]] || continue
        printf '\n━━ %s: status ━━\n' "$unit"
        # Failed/inactive units intentionally return nonzero from status.
        systemctl "${scope_args[@]}" --no-pager --full status -- "$unit" || true
        printf '\n━━ %s: latest 60 journal entries this boot ━━\n' "$unit"
        journalctl "${scope_args[@]}" --boot --unit="$unit" --lines=60 --no-pager || true
    done <<< "$units"
done

printf '\nReport complete. No services were restarted or reset.\n'
