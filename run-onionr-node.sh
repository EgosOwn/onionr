#!/bin/sh
set -x
ORIG_ONIONR_RUN_DIR=`pwd`
export ORIG_ONIONR_RUN_DIR
cd "$(dirname "$0")"

if [[ -n "$ONIONR_DOCKER" ]]; then
	[[ -f "/privkey" ]] && privkey_opt="--private-key /privkey"
	[[ -n "$ONIONR_ONBOARDING" ]] || ONIONR_ONBOARDING=0
	[[ -n "$ONIONR_OPEN_UI" ]] || ONIONR_OPEN_UI=0
	[[ -n "$ONIONR_RANDOM_LOCALHOST_IP" ]] || ONIONR_RANDOM_LOCALHOST_IP=0
	[[ -n "$ONIONR_BIND_ADDRESS" ]] || ONIONR_BIND_ADDRESS=0.0.0.0
	[[ -n "$ONIONR_PORT" ]] || ONIONR_PORT=8080
fi

[[ -n "$ONIONR_PRIVATE_KEY_FILE" ]] && privkey_opt="--private-key $ONIONR_PRIVATE_KEY_FILE"
[[ -n "$ONIONR_USE_BOOTSTRAP_FILE" ]] && bootstrap_opt="--use-bootstrap-file $ONIONR_USE_BOOTSTRAP_FILE"
[[ -n "$ONIONR_SHOW_STATS" ]] && show_stats_opt="--show-stats $ONIONR_SHOW_STATS"
[[ -n "$ONIONR_ONBOARDING" ]] && onboarding_opt="--onboarding $ONIONR_ONBOARDING"
[[ -n "$ONIONR_SECURITY_LEVEL" ]] && security_level_opt="--security-level $ONIONR_SECURITY_LEVEL"
[[ -n "$ONIONR_OPEN_UI" ]] && open_ui_opt="--open-ui $ONIONR_OPEN_UI"
[[ -n "$ONIONR_RANDOM_LOCALHOST_IP" ]] && random_localhost_ip_opt="--random-localhost-ip $ONIONR_RANDOM_LOCALHOST_IP"
[[ -n "$ONIONR_USE_TOR" ]] && use_tor_opt="--use-tor $ONIONR_USE_TOR"
[[ -n "$ONIONR_ANIMATED_BACKGROUND" ]] && animated_background_opt="--animated-background $ONIONR_ANIMATED_BACKGROUND"
[[ -n "$ONIONR_KEEP_LOG" ]] && keep_log_opt="--keep-log-on-exit $ONIONR_KEEP_LOG"
[[ -n "$ONIONR_USE_UPLOAD_MIXING" ]] && use_upload_mixing_opt="--use-upload-mixing $ONIONR_USE_UPLOAD_MIXING"
[[ -n "$ONIONR_DEV_MODE" ]] && dev_mode_opt="--dev-mode $ONIONR_DEV_MODE"
[[ -n "$ONIONR_DISABLE_PLUGIN_LIST" ]] && disable_plugin_list_opt=" --disable-plugin-list $ONIONR_DISABLE_PLUGIN_LIST"
[[ -n "$ONIONR_STORE_PLAINTEXT" ]] && store_plaintext_opt="--store-plaintext $ONIONR_STORE_PLAINTEXT"
[[ -n "$ONIONR_BIND_ADDRESS" ]] && bind_address_opt="--bind-address $ONIONR_BIND_ADDRESS"
[[ -n "$ONIONR_PORT" ]] && port_opt="--port $ONIONR_PORT"


python3 run-onionr-node.py \
	$privkey_opt \
	$bootstrap_opt \
	$show_stats_opt \
	$onboarding_opt \
	$security_level_opt \
	$open_ui_opt \
	$random_localhost_ip_opt \
	$use_tor_opt \
	$animated_background_opt \
	$keep_log_opt \
	$use_upload_mixing_opt \
	$dev_mode_opt \
	$disable_plugin_list_opt \
	$store_plaintext_opt \
	$bind_address_opt \
	$port_opt \
	"$@"
