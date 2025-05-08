#!/usr/bin/env bash

get_version () {
  # local APP_PATH="$(echo $1 | sed 's/\([/]\)\1*/\1/g')"
  # # Get the current version from the app
  # grep -o '^version = [0-9A-Za-z.-]*' "${APP_PATH}/default/app.conf" | awk '{print $3}'
  local APP_PATH="$(echo "$1" | sed 's/\([/]\)\1*/\1/g')"

  # Primero intenta obtener el version dentro de la sección [id]
  local id_version
  id_version=$(awk '
    /^\[id\]/ { in_id=1; next }
    /^\[/     { in_id=0 }
    in_id && /^version[[:space:]]*=/ {
      gsub(/ /, "", $0);
      split($0, a, "=");
      print a[2];
      exit;
    }
  ' "${APP_PATH}/default/app.conf")

  if [[ -n "$id_version" ]]; then
    echo "$id_version"
  else
    # Fallback: tomar el primer "version =" en todo el archivo
    grep -m1 -o '^version[[:space:]]*=[[:space:]]*[0-9A-Za-z._-]*' "${APP_PATH}/default/app.conf" | awk -F '=' '{gsub(/ /, "", $2); print $2}'
  fi
}

get_splunk_supported () {
  local APP_PATH="$(echo $1 | sed 's/\([/]\)\1*/\1/g')"
  # Get the current version of splunk supported from the app
  grep -o '^splunk_supported = [0-9A-Za-z.,-]*' "${APP_PATH}/default/app.conf" | awk '{print $3}'
}

get_cim_supported () {
  local APP_PATH="$(echo $1 | sed 's/\([/]\)\1*/\1/g')"
  # Get the current version of splunk supported from the app
  grep -o '^cim_supported = [0-9A-Za-z.,-]*' "${APP_PATH}/default/app.conf" | awk '{print $3}'
}

get_branch () {
  if [ "$TRAVIS" == "true" ]; then
    BRANCH=${TRAVIS_BRANCH}
  elif [ "$GITHUB_ACTIONS" == "true" ]; then
    BRANCH=${GITHUB_REF#refs/}
    BRANCH=${BRANCH#heads/}
    BRANCH=${BRANCH#heads/}
    BRANCH=${BRANCH%/merge}
  else
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
  fi
  BRANCH=${BRANCH//\//_}
  echo "$BRANCH"
}

get_build () {
  if [ "$TRAVIS" == "true" ]; then
    BUILD=${TRAVIS_BUILD_NUMBER}
  elif [ "$GITHUB_ACTIONS" == "true" ]; then
    BUILD=${GITHUB_RUN_ID}
  else
    BUILD="local"
  fi
  echo "$BUILD"
}

get_build_filename () {
    local app=$1
    local version=$2
    local branch=$3
    local build=$4
    if [ "$branch" == "master" ]; then
        echo "${app}-${version}.spl"
    else
        echo "${app}-${version}-${branch}-${build}.spl"
    fi
}