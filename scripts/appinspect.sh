#!/usr/bin/env bash

# This script checks the App against the AppInspect API
# It is intended to be used in a CI/CD pipeline

# Env Vars Required:
# SPLUNK_USER
# SPLUNK_PASS

set -e

command -v jq >/dev/null 2>&1 || (echo >&2 "The program 'jq' is required, please install it on your system"; exit 1)

echo "Get curl version: $(curl --version)"

if [ -z "$SPLUNK_USER" ] || [ -z "$SPLUNK_PASS" ]; then
    echo "Required environment variables: SPLUNK_USER, SPLUNK_PASS"
    exit 1
fi

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

## Print command usage
print_usage () {
    echo ""
    echo "Usage:"
    echo ""
    echo "appinspect.sh -a <APP NAME> [-f <FILENAME>] [-j] [-r] [-c]"
    echo ""
    echo "  -a What to inspect. Must be either 'app' or 'addon'."
    echo "  -f File to submit for inspection"
    echo "  -j Output a JSON report with details of all checks"
    echo "  -r Create an HTML report file with details of all checks"
    echo "  -c Include cloud and future tags for Splunk Cloud vetting"
    echo ""
}

## Gets an authentication token (JWT)
get_token () {
    local response
    log_info "Authenticating to AppInspect API"
    if ! response=$(curl -Ss -X GET \
        -u "$SPLUNK_USER:$SPLUNK_PASS" \
        --url "https://api.splunk.com/2.0/rest/login/splunk" -k)
    then
        log_error "Error during token API call: $response"
        exit 2
    fi
    echo "$response" | jq -r '.data.token'
}

## Submits an app for validation
submit_for_validation () {
    local app_path=$1
    local token=$2
    local response
    log_info "Submitting app for validation"

    if $CLOUD_VETTING; then
        log_info "Including cloud and future tags in validation"
        response=$(curl -Ss -X POST \
            -H "Authorization: bearer ${token}" \
            -H "Cache-Control: no-cache" \
            -F "app_package=@\"${app_path}\"" \
            -F "included_tags=cloud" \
            -F "included_tags=future" \
            --url "https://appinspect.splunk.com/v1/app/validate" -k)
    else
        response=$(curl -Ss -X POST \
            -H "Authorization: bearer ${token}" \
            -H "Cache-Control: no-cache" \
            -F "app_package=@\"${app_path}\"" \
            --url "https://appinspect.splunk.com/v1/app/validate" -k)
    fi

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Error during submit API call: $response"
        exit 2
    fi
    echo "$response" | jq -r '.request_id'
}

## Check status of validation
check_status () {
    local request_id=$1
    local token=$2
    local response
    log_debug "Checking status"
    if ! response=$(curl -Ss -X GET \
        -H "Authorization: bearer ${token}" \
        --url "https://appinspect.splunk.com/v1/app/validate/status/${request_id}" -k)
    then
        log_error "Error during check status API call: $response"
        exit 2
    fi
    CHECKS=$(echo "$response" | jq '.info')
    ERRORS=$(echo "$response" | jq '.info.error')
    FAILURES=$(echo "$response" | jq '.info.failure')
    STATUS=$(echo "$response" | jq -r '.status')
}

## Get the final report
get_report () {
    local request_id=$1
    local token=$2
    local report_type=$3
    local response
    local contenttype
    contenttype=$([ "$report_type" == "HTML" ] && echo "text/html" || echo "application/json")
    log_info "Fetching report"
    if ! response=$(curl -Ss -X GET \
         -H "Authorization: bearer ${token}" \
         -H "Cache-Control: no-cache" \
         -H "Content-Type: ${contenttype}" \
         --url "https://appinspect.splunk.com/v1/app/report/${request_id}" -k)
    then
        log_error "Error during get report API call: $response"
        exit 2
    fi
    if [ "$report_type" == "HTML" ]; then
        echo "$response"
    else
        echo "$response" | jq '.reports'
    fi
}

APP='Splunk-TA-cisco-catalyst-center'
CLOUD_VETTING=false

while getopts a:f:jrc FLAG; do
    case $FLAG in
        a)
        if [ "$OPTARG" == "app" ]; then
            APP=Splunk-cisco-catalyst-center
        elif [ "$OPTARG" == "addon" ]; then
            APP=Splunk-TA-cisco-catalyst-center
        else
            log_error "Unknown argument: $OPTARG"
            exit 1
        fi
        ;;
        f)
        FILENAME="$OPTARG"
        ;;
        j)
        JSON_REPORT=true
        ;;
        r)
        HTML_REPORT=true
        ;;
        c)
        CLOUD_VETTING=true
        ;;
        h)
        print_usage
        exit 0
        ;;
        \?)
        print_usage
        exit 1
        ;;
    esac
done

# Get the current version from the app
BRANCH=$(get_branch)
BUILD=$(get_build)

log_debug "AppInspect ${APP} build ${BUILD} for SplunkBase"

TOKEN=$(get_token)
log_debug "File1 $FILENAME"
if [ -z "$FILENAME" ]; then
    VERSION=$(get_version "$ROOT/$APP")
    log_debug "ROOT $ROOT"
    log_debug "APP $APP"
    log_debug "VERSION $VERSION"
    log_debug "BRANCH $BRANCH"
    log_debug "BUILD $BUILD"
    FILENAME="${ROOT}/_build/$(get_build_filename "$APP" "$VERSION" "$BRANCH" "$BUILD")"
fi 
log_debug "File $FILENAME"
log_debug "File to be submitted: $FILENAME"
if [ ! -f "$FILENAME" ]; then
  log_error "App package not found: $FILENAME"
  exit 1
fi


REQUEST_ID=$(submit_for_validation "$FILENAME" "$TOKEN")
log_debug "RequestID $REQUEST_ID"
if [ "$REQUEST_ID" == "null" ]; then
    log_error "Request for validation failed"
    exit 2
fi

STATUS="PROCESSING"
while [ "$STATUS" == "PROCESSING" ] || [ "$STATUS" == "PREPARING" ] || [ "$STATUS" == "PENDING" ]; do
    # sets STATUS, ERRORS, and CHECKS
    check_status "$REQUEST_ID" "$TOKEN"
    log_debug "STATUS $STATUS"
done

log_debug "END STATUS: $STATUS"
log_debug "ERRORS: $ERRORS"

# Print the report of requested, or the result counts if not
if [ "$JSON_REPORT" == "true" ]; then
    JSON_REPORT=$(get_report "$REQUEST_ID" "$TOKEN" "JSON")
    echo "$JSON_REPORT"
else
    log_info "Results:\n $CHECKS"
fi

if [ "$HTML_REPORT" == "true" ]; then
    REPORT_FILENAME="${ROOT}/_build/${APP}-${BUILD}.html"
    log_info "Saving html report to: $REPORT_FILENAME"
    HTML_REPORT=$(get_report "$REQUEST_ID" "$TOKEN" "HTML")
    mkdir -p "${ROOT}/_build"
    echo "$HTML_REPORT" > "$REPORT_FILENAME"
fi

# Check if there were any errors in the validation results
if [ "$STATUS" != "SUCCESS" ] || [ "$ERRORS" -ne 0 ] || [ "$FAILURES" -ne 0 ]; then
    log_error "Status: $STATUS - Error count: $ERRORS - Failure count: $FAILURES"
    exit 3
fi

log_success "Completed"
exit 0
