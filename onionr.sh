#!/bin/sh
ORIG_ONIONR_RUN_DIR=`pwd`
export ORIG_ONIONR_RUN_DIR
cd "$(dirname "$0")"

[[ -n "$USE_TOR" ]] || USE_TOR=1
[[ -n "$PORT" ]] || PORT=8080
[[ -n "$KEEP_LOG" ]] || KEEP_LOG=0
[[ -n "$STORE_PLAINTEXT" ]] || STORE_PLAINTEXT=1

PRIVKEY_OPT=""
[[ -f "privkey.key" ]] && PRIVKEY_OPT="--private-key privkey.key"

python run-onionr-node.py \
	--open-ui 0 \
	--onboarding 0 \
	--bind-address 0.0.0.0 \
	--port $PORT \
	--use-tor $USE_TOR \
	--keep-log-on-exit $KEEP_LOG \
	--store-plaintext $STORE_PLAINTEXT \
	$PRIVKEY_OPT \
	"$@"
