#!/usr/bin/env bash

SCRIPTPATH="$(
    cd "$(dirname "$0")"
    pwd -P
)"

CURRENT_DIR=$SCRIPTPATH
ROOT_DIR="$(dirname $CURRENT_DIR)"
PROGNAME="$(basename $0)"

function help() {
  echo 1>&2 "Usage: ${PROGNAME} <command>"
  echo 1>&2 ""
  echo 1>&2 "Commands:"
  echo 1>&2 "  start        start the service"
  echo 1>&2 "  up			      pull and start infrastructure images"
  echo 1>&2 "  down			    stop all infrastructure images"
}

function setup_env() {
    # Should use semicolon ";" instead of new line (\r\n): Because it will get some problems if it runs "bin.sh" file on Linux, which generated on Window before
    set -a; export $(grep -v '^#' "$ROOT_DIR/builders/.base.env" | xargs -0) >/dev/null 2>&1; . $ROOT_DIR/builders/.base.env; set +a
}

function start() {
	setup_env
	python3 main.py
}

function up() {
	docker compose -f ./builders/docker-compose.yml up -d
}

function down() {
	docker compose -f ./builders/docker-compose.yml down
}


SUBCOMMAND="${1:-}"
case "${SUBCOMMAND}" in
  "" | "help" | "-h" | "--help" )
    help
    ;;

  "start" )
    shift
    start "$@"
    ;;

  "up" )
    shift
    up "$@"
    ;;

  "down" )
    shift
    down "$@"
    ;;

  *)
    help
    exit 1
    ;;
esac