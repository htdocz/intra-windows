#!/bin/bash

# ==============================================================================
# IntraWindows - Linux CLI & headless Proxy Manager
# ==============================================================================

# CONFIGURATION
SOCKS_PORT="10808"
HTTP_PORT="10809"
DNS_PORT="" # Leave blank to disable local DNS proxy. Set to 53 to intercept system DNS (requires root).
DOH_URL="https://cloudflare-dns.com/dns-query"
BOOTSTRAP_IPS="1.1.1.1,1.0.0.1"

# PID File Path
PID_FILE="/var/run/intrawindows.pid"
if [ "$EUID" -ne 0 ]; then
    PID_FILE="$HOME/.intrawindows.pid"
fi

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bin"
BIN_PATH="$BIN_DIR/intra-linuxdpi"

is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

start() {
    if is_running; then
        echo "IntraWindows is already running (PID: $(cat "$PID_FILE"))."
        return 0
    fi

    echo "Starting IntraWindows..."
    if [ ! -f "$BIN_PATH" ]; then
        echo "Error: Binary not found at $BIN_PATH"
        exit 1
    fi
    chmod +x "$BIN_PATH"

    DNS_ARG=""
    if [ -n "$DNS_PORT" ]; then
        DNS_ARG="-dns 127.0.0.1:$DNS_PORT"
    fi

    nohup "$BIN_PATH"         -addr "127.0.0.1:$SOCKS_PORT"         -http "127.0.0.1:$HTTP_PORT"         $DNS_ARG         -doh "$DOH_URL"         -bootstrap "$BOOTSTRAP_IPS" > /dev/null 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"
    sleep 0.5

    if is_running; then
        echo "IntraWindows started successfully (PID: $PID)."
        echo "SOCKS5 Proxy: 127.0.0.1:$SOCKS_PORT"
        echo "HTTP Proxy: 127.0.0.1:$HTTP_PORT"
    else
        echo "Error: Failed to start IntraWindows. Check port conflicts."
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if ! is_running; then
        echo "IntraWindows is not running."
        return 0
    fi

    PID=$(cat "$PID_FILE")
    echo "Stopping IntraWindows (PID: $PID)..."
    kill "$PID"
    rm -f "$PID_FILE"
    echo "Stopped."
}

status() {
    if is_running; then
        echo "Status: Running (PID: $(cat "$PID_FILE"))"
        echo "SOCKS5 Proxy: 127.0.0.1:$SOCKS_PORT"
        echo "HTTP Proxy: 127.0.0.1:$HTTP_PORT"
    else
        echo "Status: Stopped"
    fi
}

install_service() {
    if [ "$EUID" -ne 0 ]; then
        echo "Error: Please run 'install' command with sudo privileges."
        exit 1
    fi

    echo "Installing systemd service..."
    SCRIPT_PATH=$(readlink -f "$0")
    SERVICE_FILE="/etc/systemd/system/intrawindows.service"

    cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=IntraWindows Secure Shield Proxy Service
After=network.target

[Service]
Type=forking
ExecStart=$SCRIPT_PATH start
ExecStop=$SCRIPT_PATH stop
PIDFile=$PID_FILE
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable intrawindows
    echo "IntraWindows systemd service installed & enabled successfully."
    echo "Usage commands:"
    echo "  sudo systemctl start intrawindows"
    echo "  sudo systemctl stop intrawindows"
    echo "  sudo systemctl status intrawindows"
}

uninstall_service() {
    if [ "$EUID" -ne 0 ]; then
        echo "Error: Please run 'uninstall' command with sudo privileges."
        exit 1
    fi

    echo "Uninstalling systemd service..."
    systemctl stop intrawindows 2>/dev/null
    systemctl disable intrawindows 2>/dev/null
    rm -f /etc/systemd/system/intrawindows.service
    systemctl daemon-reload
    echo "IntraWindows service removed."
}

enable_gnome_proxy() {
    if command -v gsettings >/dev/null; then
        echo "Configuring Gnome system proxy settings..."
        gsettings set org.gnome.system.proxy mode 'manual'
        gsettings set org.gnome.system.proxy.socks host '127.0.0.1'
        gsettings set org.gnome.system.proxy.socks port "$SOCKS_PORT"
        gsettings set org.gnome.system.proxy.http host '127.0.0.1'
        gsettings set org.gnome.system.proxy.http port "$HTTP_PORT"
        gsettings set org.gnome.system.proxy.https host '127.0.0.1'
        gsettings set org.gnome.system.proxy.https port "$HTTP_PORT"
        echo "Gnome GUI system proxy enabled."
    else
        echo "Gnome environment (gsettings) not found. No GUI proxy configured."
    fi
}

disable_gnome_proxy() {
    if command -v gsettings >/dev/null; then
        echo "Disabling Gnome system proxy..."
        gsettings set org.gnome.system.proxy mode 'none'
        echo "Gnome GUI system proxy disabled."
    fi
}

print_env() {
    echo "export http_proxy="http://127.0.0.1:$HTTP_PORT""
    echo "export https_proxy="http://127.0.0.1:$HTTP_PORT""
    echo "export all_proxy="socks5://127.0.0.1:$SOCKS_PORT""
    echo "echo 'IntraWindows CLI proxy environment variables enabled.'"
}

print_unenv() {
    echo "unset http_proxy"
    echo "unset https_proxy"
    echo "unset all_proxy"
    echo "echo 'IntraWindows CLI proxy environment variables disabled.'"
}

usage() {
    echo "Usage: $0 {start|stop|restart|status|install|uninstall|enable-gui|disable-gui|env|unenv}"
    echo ""
    echo "Commands:"
    echo "  start       : Start the proxy background process"
    echo "  stop        : Stop the proxy background process"
    echo "  restart     : Restart the proxy"
    echo "  status      : Show status of the proxy"
    echo "  install     : Install systemd service for boot startup (requires sudo)"
    echo "  uninstall   : Uninstall the systemd service (requires sudo)"
    echo "  enable-gui  : Enable system proxy for Gnome DE"
    echo "  disable-gui : Disable system proxy for Gnome DE"
    echo "  env         : Print commands to set CLI proxy environment variables"
    echo "  unenv       : Print commands to unset CLI proxy environment variables"
    echo ""
    echo "Trick for SSH / CLI sessions:"
    echo "  eval \$($0 env)   # to proxy current shell session"
    echo "  eval \$($0 unenv) # to remove proxy from current session"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 0.5
        start
        ;;
    status)
        status
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    enable-gui)
        enable_gnome_proxy
        ;;
    disable-gui)
        disable_gnome_proxy
        ;;
    env)
        print_env
        ;;
    unenv)
        print_unenv
        ;;
    *)
        usage
        exit 1
        ;;
esac
