#!/bin/bash

# The image runs as a non-root user, so the mounted Docker socket is only
# reachable if that user belongs to the group owning it on the host. That group
# is resolved at runtime because its id is a property of the host, not the image.

socket=/var/run/docker.sock

if [ -S "$socket" ] && [ ! -w "$socket" ]; then
    user=$(id -un 2>/dev/null) || user=$(id -u)
    gid=$(stat -c '%g' "$socket" 2>/dev/null)
    group=$(getent group "$gid" 2>/dev/null | cut -d: -f1)

    if [ -z "$group" ] && sudo -n groupadd -g "$gid" docker-host >/dev/null 2>&1; then
        group=docker-host
    fi

    # sg runs the command with $group as the primary group, so files created in a
    # mounted folder are group-owned by it rather than by the user's own group.
    if [ -n "$group" ] && sudo -n usermod -aG "$group" "$user" >/dev/null 2>&1; then
        exec sg "$group" -c "$(printf '%q ' "$@")"
    fi

    # Warn rather than exit: the image is a general-purpose toolchain and most of
    # it needs no daemon. This grants nothing beyond the passwordless sudo the
    # image already gives this user, and must be revisited if that sudo is removed.
    echo "iotedgedev: cannot access $socket as $user; rerun with --group-add $gid" >&2
fi

exec "$@"