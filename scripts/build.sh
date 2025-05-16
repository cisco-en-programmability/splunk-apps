#!/bin/bash

SCRIPT_BASE="$(cd "$( dirname "$0")" && pwd )"
ROOT=${SCRIPT_BASE}/..

# shellcheck source=/dev/null
source "$SCRIPT_BASE/log4bash.sh"
# shellcheck source=/dev/null
source "$SCRIPT_BASE/common.sh"
if [[ -z "$DEBUG" ]]; then
  log_set_debug "DEBUG"
elif [[ -n "$DEBUG" ]]; then
  log_set_debug "DEV"
fi
log_debug "DEBUG ENABLED"

# Exit immediatly if any command exits with a non-zero status
set -e

## Print command usage
print_usage () {
    echo ""
    echo "Usage:"
    echo ""
    echo "build.sh -a <app or addon> [-o filename] [-l] [-v <version> [-r <release-channel>]]"
    echo ""
    echo "  -a What to build. Must be either 'app' or 'addon'."
    echo "  -o The filename of the output package"
    echo "  -l Build from local files, not from git-archive"
    echo "  -v Set the version before building"
    echo "  -r When setting the version, specify a release channel (see set-version.sh)"
    echo ""
}

APP='Splunk-TA-cisco-catalyst-center'

while getopts a:o:v:r:lh FLAG; do
  case $FLAG in
    a)
      WHICHAPP=$OPTARG
      if [ "$OPTARG" == "app" ]; then
        APP=Splunk-cisco-catalyst-center
      elif [ "$OPTARG" == "addon" ]; then
        APP=Splunk-TA-cisco-catalyst-center
      else
        log_error "Unknown argument: $OPTARG"
        exit 1
      fi
      ;;
    o)
      OUTPUT_FILE="$OPTARG"
      ;;
    v)
      SET_VERSION="$OPTARG"
      ;;
    r)
      CHANNEL="$OPTARG"
      ;;
    l)
      BUILD_LOCAL="true"
      ;;
    h)
      print_usage
      exit 0
      ;;
    :)
      echo "$0: Must supply an argument to -$OPTARG." >&2
      exit 1
      ;;
    \?) #unrecognized option - show help
      print_usage
      exit 1
      ;;
  esac
done

ROOT_APP="$(echo "$ROOT/$APP" | sed 's/\([/]\)\1*/\1/g')"

# Clean up previous builds
rm -rf "${ROOT}/_build/tmp" 2>/dev/null
mkdir -p "${ROOT}/_build/tmp"

# Get the current version from the app
if [ "$SET_VERSION" ]; then
    log_debug "Using specified version: $SET_VERSION"
    VERSION="$SET_VERSION"
else
    log_info "Using version from app.conf"
    VERSION=$(get_version "$ROOT_APP")
fi

if [ -z "$BUILD_LOCAL" ]; then
    log_debug "Building from git archive"
    BRANCH=$(get_branch)
    BUILD=$(get_build)

    log_info "Building ${APP} version ${VERSION} build ${BUILD} from branch ${BRANCH}"

    cd "${ROOT}/${APP}"
    # Use GIT to build a temp archive
    git archive --format=tar --prefix="${APP}/" HEAD ./ | gzip >"${ROOT}/_build/tmp/${APP}-${VERSION}-${BUILD}-temp.tgz"
    # Uncompress the App
    cd "${ROOT}/_build/tmp"
    rm -rf "${APP}" >/dev/null
    tar xzf "${APP}-${VERSION}-${BUILD}-temp.tgz"
    rm "${APP}-${VERSION}-${BUILD}-temp.tgz"
else
    log_debug "Building from local"
    BRANCH=$(get_branch)
    BUILD=local

    log_info "Building ${APP} version ${VERSION} build ${BUILD} from branch ${BRANCH}"

    # Just copy the files, don't use git. Safe during CI, but not anywhere else.
    cd "${ROOT}/_build/tmp"
    rm -rf "${APP}"
    cp -R "${ROOT_APP}" "${ROOT}/_build/tmp/"
fi

# Strip out stuff that SplunkBase doesn't like
# such as hidden files and Makefiles
find ${APP} -type f -name ".*" -exec rm {} \;
find ${APP} -type d -name ".*" -exec rm -rf {} \;
find ${APP} -type f -name "*.pyc" -exec rm {} \;
find ${APP} -type f -name ".DS_Store" -exec rm {} \;


if [[ -d "${APP}/bin" ]]; then
  find "${APP}/bin" -type f -name "*.py" -exec chmod +x {} 2> /dev/null \;
fi

rm -f "${APP}/Makefile"

if [ "$WHICHAPP" == "addon" ]; then
  rm -f "${APP}/README.md"
  rm -f "${APP}/LICENSE"
fi

rm -rf "${APP}/release"
rm -rf "${APP}/local"

# Set the version if requested
if [ "$SET_VERSION" ]; then
    log_debug "Running set-version.sh..."
    LOG_LEVEL=$LOG_LEVEL "$SCRIPT_BASE/set-version.sh" -a "$WHICHAPP" -d ./ "$SET_VERSION" "$CHANNEL"
fi

if [ -z "$OUTPUT_FILE" ]; then
    FILENAME=$(get_build_filename "$APP" "$VERSION" "$BRANCH" "$BUILD")
else
    FILENAME="$OUTPUT_FILE"
fi

if [ "$APP" == "Splunk-cisco-catalyst-center" ]; then
  log_debug "Merging local.meta and removing file"
  if [ -e "${APP}/metadata/local.meta" ]; then
    # cat "${APP}/metadata/default.meta" "${APP}/metadata/local.meta" > "${APP}/metadata/merged.meta"
    # mv "${APP}/metadata/merged.meta" "${APP}/metadata/default.meta"
    rm "${APP}/metadata/local.meta"
    # chmod 600 "${APP}/metadata/default.meta"
  fi
fi

# Re-compress to tar file and clean up
tar czf "${ROOT}/_build/${FILENAME}" "${APP}"

# Set variables for GitHub Actions to pick up in subsequent steps
if [ "$GITHUB_ACTIONS" == "true" ]; then
    log_debug "Setting GitHub Actions outputs"
    # echo ::set-output "name=path::_build/$FILENAME"
    # echo ::set-output "name=file::$FILENAME"
    echo "name=path::_build/$FILENAME" >> $GITHUB_OUTPUT
    echo "name=file::$FILENAME" >> $GITHUB_OUTPUT
fi

log_debug "path: _build/$FILENAME"
log_debug "file: $FILENAME"

# Cleanup
cd "${ROOT}"
rm -rf "${ROOT}/_build/tmp"

log_success "SplunkBase package is ready at _build/$FILENAME"