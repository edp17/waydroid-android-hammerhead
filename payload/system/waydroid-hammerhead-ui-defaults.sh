#!/system/bin/sh

MARKER=/data/local/tmp/.waydroid-hammerhead-ui-defaults-v1
LOG=/data/local/tmp/waydroid-hammerhead-ui-defaults.log
TMP="${LOG}.tmp"

PATH="/system/bin:/system/xbin:/vendor/bin:/apex/com.android.runtime/bin:$PATH"
export PATH

mkdir -p /data/local/tmp

if [ -f "$MARKER" ]; then
    exit 0
fi

FAILED=0

{
    echo "=== Hammerhead Android UI defaults ==="
    date 2>/dev/null || true

    run_cmd()
    {
        echo
        echo "+ $*"
        "$@"
        RC=$?
        echo "rc=$RC"
        if [ "$RC" -ne 0 ]; then
            FAILED=1
        fi
    }

    run_cmd settings --user 0 put global window_animation_scale 0.0
    run_cmd settings --user 0 put global transition_animation_scale 0.0
    run_cmd settings --user 0 put global animator_duration_scale 0.0
    run_cmd settings --user 0 put system font_scale 0.85
    run_cmd wm density 336

    echo
    echo "--- readback ---"

    WINDOW="$(settings --user 0 get global window_animation_scale 2>&1)"
    TRANSITION="$(settings --user 0 get global transition_animation_scale 2>&1)"
    ANIMATOR="$(settings --user 0 get global animator_duration_scale 2>&1)"
    FONT="$(settings --user 0 get system font_scale 2>&1)"
    DENSITY="$(settings --user 0 get secure display_density_forced 2>&1)"

    echo "window_animation_scale=$WINDOW"
    echo "transition_animation_scale=$TRANSITION"
    echo "animator_duration_scale=$ANIMATOR"
    echo "font_scale=$FONT"
    echo "display_density_forced=$DENSITY"

    [ "$WINDOW" = "0.0" ] || FAILED=1
    [ "$TRANSITION" = "0.0" ] || FAILED=1
    [ "$ANIMATOR" = "0.0" ] || FAILED=1
    [ "$FONT" = "0.85" ] || FAILED=1
    [ "$DENSITY" = "336" ] || FAILED=1

    echo
    if [ "$FAILED" -eq 0 ]; then
        : > "$MARKER"
        chmod 0644 "$MARKER" 2>/dev/null || true
        echo "result=success"
    else
        echo "result=failed"
    fi
} > "$TMP" 2>&1

mv "$TMP" "$LOG"
chmod 0644 "$LOG" 2>/dev/null || true

if [ "$FAILED" -eq 0 ]; then
    exit 0
fi

exit 1
