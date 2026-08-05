#!/system/bin/sh

LOG=/data/local/tmp/stage102-direct-connect.log
TMP="${LOG}.tmp"

PATH="/system/bin:/system/xbin:/vendor/bin:/apex/com.android.runtime/bin:$PATH"
export PATH

mkdir -p /data/local/tmp

{
    echo "=== Stage102 old-kernel direct-connect compatibility ==="
    date 2>/dev/null || true

    echo
    echo "--- identity and kernel ---"
    id
    uname -a

    echo
    echo "--- service properties ---"
    getprop init.svc.netd
    getprop init.svc.waydroid_netd_direct_connect

    echo
    echo "--- rules before ---"
    ip -4 rule show 2>&1 || true
    ip -6 rule show 2>&1 || true

    echo
    echo "--- add IPv4 direct-connect rule ---"

    if ip -4 rule show 2>/dev/null |
       grep -q '^23000:'
    then
        echo "IPv4 priority-23000 rule already exists."
        IPV4_RC=0
    else
        ip -4 rule add \
            priority 23000 \
            fwmark 0x0/0xffff \
            uidrange 0-0 \
            lookup main

        IPV4_RC=$?
    fi

    echo "ipv4_rule_rc=$IPV4_RC"

    echo
    echo "--- add IPv6 direct-connect rule ---"

    if ip -6 rule show 2>/dev/null |
       grep -q '^23000:'
    then
        echo "IPv6 priority-23000 rule already exists."
        IPV6_RC=0
    else
        ip -6 rule add \
            priority 23000 \
            fwmark 0x0/0xffff \
            uidrange 0-0 \
            lookup main

        IPV6_RC=$?
    fi

    echo "ipv6_rule_rc=$IPV6_RC"

    echo
    echo "--- rules after ---"
    ip -4 rule show 2>&1 || true
    ip -6 rule show 2>&1 || true

    echo
    echo "=== Stage102 rule installation complete ==="
} > "$TMP" 2>&1

mv "$TMP" "$LOG"
chmod 0644 "$LOG" 2>/dev/null || true

exit 0
