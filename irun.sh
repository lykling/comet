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
#set -x
readonly SCRIPT_DIR=$(
  cd $(dirname $0)
  pwd
)

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
run() {
  local cmd=$1
  shift
  ${cmd} "$@"
  local ret=$?
  [[ "$ret" != "0" ]] &&
    err "command error $ret: ${cmd} $@, exiting" &&
    return $ret
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
err() {
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
info() {
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") $@" >&1
}

join_by() {
  local IFS="$1"
  shift
  echo "$*"
}

_ii_usage() {
  echo "Usage:
    $0 <func> [...args]
Examples:
    "
}

_ii_create_dir_index_html() {
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
        --noreport \
        --dirsfirst \
        --charset utf-8 \
        --ignore-case \
        --timefmt '%d-%b-%Y %H:%M' \
        -I index.html \
        -T Files \
        -s \
        -h \
        --du \
        -D \
        -F \
        -C \
        | sed -e '/<hr>/,+6d' > \${target}/index.html \
        " {} \;
}

_ii_edeps() {
  local pkg=$1
  # qdepends -CQqqF'%{CAT}/%{PN}:%{SLOT}' "^${pkg}" | tr '\n' ' '
  qdepends -CQqqF'%{CAT}/%{PN}:%{SLOT}' "^${pkg}"
}

_ii_replace_apollo_cc_library() {
  files=("$@")
  current_pkg=""
  for x in $(cat "${files[@]}" | tr -d '",' | sort); do
    pkg=${x%:*}
    slot=${x#*:}
    if [[ "${slot}" =~ .*proto ]]; then
      echo "skip proto target ${x}"
      continue
    fi
    if buildozer "print srcs" ${x} |& grep -c "\.so" 2>&1 > /dev/null; then
      echo "skip shared library target ${x}"
      continue
    fi
    if [[ "${pkg}" != "${current_pkg}" ]]; then
      current_pkg="${pkg}"
      buildozer "new_load //tools:apollo_package.bzl apollo_cc_library" "${pkg}:__pkg__"
      echo "add new load of apollo_cc_library for ${pkg}"
    fi
    buildozer "set kind apollo_cc_library" "${x}"
    echo "process ${x} done"
  done
}

_ii_find_apollo_package_paths() {
  for x in $(find cyber modules -name cyberfile.xml); do
    echo $(dirname $x)
  done
}

_ii_get_external_dep_targets() {
  package_path=$1
  for target in $(buildozer "print label" ${package_path}/...:%cc_library); do
    for dep in $(buildozer "print deps" ${target} 2> /dev/null | grep -oP '(?<=[\[ "])//.*?(?=[ "\]])'); do
      if [[ "${dep}" =~ ^//${package_path}[/:] ]]; then
        :
      else
        echo ${dep}
      fi
    done
  done | sort | uniq | grep -v third_party | grep -v -E 'proto$'
}

_ii_fix_so_lib_to_apollo_cc_library() {
  target=$1
  if [[ "${target}" =~ .*:.* ]]; then
    pkg=${target%:*}
    slot=${target#*:}
  else
    pkg=${target}
    slot="${target##*/}"
  fi
  buildozer "new_load //tools:apollo_package.bzl apollo_cc_library" "${pkg}:__pkg__"
  # bin_rule=$(buildozer "print srcs" ${target} | tr -d '[]:')
  bin_rule=$(buildozer "print srcs" ${target} | tr -d '[]:')

  buildozer "new apollo_cc_library ${slot}_tmp before ${slot}" "${pkg}:__pkg__"
  buildozer "copy hdrs ${slot}" "${pkg}:${slot}_tmp"
  buildozer "set srcs $(buildozer "print srcs" ${pkg}:${bin_rule} | tr -d '[]' | tr ' ' '\n' | grep -o -E '.*.cc')" "${pkg}:${slot}_tmp"

  bin_deps=$(buildozer "print deps" ${pkg}:${bin_rule} | tr -d '[]' | grep -v missing)
  lib_deps=$(buildozer "print deps" ${pkg}:${slot} | tr -d '[]' | grep -v missing)
  buildozer "set deps ${bin_deps} ${lib_deps}" "${pkg}:${slot}_tmp"

  buildozer "delete" "${pkg}:${slot}"
  buildozer "delete" "${pkg}:${bin_rule}"

  buildozer "set name ${slot}" "${pkg}:${slot}_tmp"

  echo "fix ${target} done"
}

main() {
  if [[ (-L "$0") && ("$(type -t _ii_$(basename $0))" == "function") ]]; then
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
