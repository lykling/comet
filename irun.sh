#!/bin/bash
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
# Author: Pride Leong<lykling.lyk@gmail.com>
# Date: Mon Jun  5 07:01:30 PM CST 2023
# Brief:
#   scripts entry, run functions
# Globals:
#   *
# Arguments:
#   *
# Returns:
#   EX_OK: success
#   EX_FAILED: failed

# Flags
#set -u
#set -e
readonly SCRIPT_DIR=$(cd $(dirname $0); pwd)

###############################################################################
# Breif:
#   Exit if procedure check failure
# Arguments:
#   $1: command to be run
#   $@: arguemts to be passed to command
# Returns:
#   0: run command succeed
#   ?: run command failed with exit code $?
###############################################################################
function run() {
    local cmd=$1
    shift
    ${cmd} "$@"
    local ret=$?
    [[ "$ret" != "0" ]] && \
        err "command error $ret: ${cmd} $@, exiting" && \
        exit $ret
    return 0
}

###############################################################################
# Brief:
#   Output arguments to stderr
# Arguments:
#   $@: message to be outputed
# Returns:
#   None
###############################################################################
function err() {
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") $@" >&2
}

###############################################################################
# Brief:
#   Output arguments to stdout
# Arguments:
#   $@: message to be outputed
# Returns:
#   None
###############################################################################
function info() {
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") $@" >&1
}

function join_by() {
    local IFS="$1"
    shift
    echo "$*"
}

function _ii_usage {
    echo "Usage:
    $0 <func> [...args]
Examples:
    "
}

function _ii_create_dir_index_html {
    local dir="$(readlink -f $1)"
    local out="${2:-$dir}"
    find "${dir}" -type d -exec bash -c "\
        dir=$dir; \
        out=$out; \
        source=\${0}; \
        target=\${0/\${dir}/\${out}}; \
        echo \${source} --\> \${target}; \
        mkdir -p \${target}; \
        tree \${source} \
        -H "." \
        -L 1 \
        --noreport \
        --dirsfirst \
        --charset utf-8 \
        --ignore-case \
        --timefmt '%d-%b-%Y %H:%M' \
        -I index.html \
        -T Files \
        -s \
        -D \
        -F \
        -C \
        | sed -e '/<hr>/,+6d' > \${target}/index.html \
        " {} \;
}

function _ii_edeps {
    local pkg=$1
    # qdepends -CQqqF'%{CAT}/%{PN}:%{SLOT}' "^${pkg}" | tr '\n' ' '
    qdepends -CQqqF'%{CAT}/%{PN}:%{SLOT}' "^${pkg}"
}

function main {
    if [[ ( -L "$0" ) && ( "$(type -t _ii_$(basename $0))" == "function" ) ]]; then
        # symlink alias, use filename as command
        cmd="$(basename $0)"
    else
        cmd=$1
        if [[ "$#" > 0 ]]; then
            shift
        fi
    fi
    if [[ "${cmd}" == "" ]]; then
        cmd="usage"
    fi
    run _ii_${cmd} "$@"
}

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Being sourced, do nothing
    :
else
    main "$@"
fi
