
# encoding = utf-8

import datetime
import json
import os
import sys
import time

import cisco_dnac_api as api

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''


def get_important_device_values(device_item):
    """
    This function will simplify the device information for Splunk searches
    :param device_item: device information
    :return: simplified device response
    """
    response = {}
    response["DeviceID"] = device_item.get("id") or ""
    response["DeviceName"] = device_item.get("hostname") or "N/A"
    response["DeviceIpAddress"] = (
        device_item.get("managementIpAddress") or device_item.get("ipAddress") or ""
    )
    response["DeviceFamily"] = device_item.get("family") or ""
    response["DeviceMACAddress"] = (
        device_item.get("macAddress") or device_item.get("apEthernetMacAddress") or ""
    )
    response["DeviceRole"] = device_item.get("role") or "UNKNOWN"
    response["DeviceImageVersion"] = device_item.get("softwareVersion") or ""
    response["DeviceUptime"] = device_item.get("upTime") or ""
    if device_item.get("uptimeSeconds") is not None:
        response["DeviceUptimeSeconds"] = device_item.get("uptimeSeconds")
    else:
        response["DeviceUptimeSeconds"] = 0
    response["DeviceLastUpdated"] = device_item.get("lastUpdated") or ""
    if device_item.get("lastUpdateTime") is not None:
        response["DeviceLastUpdateTime"] = device_item.get("lastUpdateTime")
    else:
        response["DeviceLastUpdateTime"] = 0
    response["DeviceSerialNumber"] = device_item.get("serialNumber") or ""
    response["DeviceSeries"] = device_item.get("series") or ""
    response["DevicePlatform"] = device_item.get("platformId") or ""
    response["DeviceSupportType"] = device_item.get("deviceSupportLevel") or ""
    return response


def simplify_issue(issue_responses):
    """
    This function will simplify the site data for Splunk searches
    :param issue_resp: Cisco DNAC SDK api
    :return: new site response
    """
    simplified_issue = {}
    if len(issue_responses) > 0 and isinstance(issue_responses[0], dict):
        issue_resp = issue_responses[0]
        simplified_issue["IssueID"] = issue_resp.get("issueId")
        simplified_issue["IssueSpecificCategory"] = issue_resp.get("issueCategory")
        simplified_issue["IssueSpecificSource"] = issue_resp.get("issueSource")
        simplified_issue["IssueSpecificName"] = issue_resp.get("issueName")
        simplified_issue["IssueSpecificDescription"] = issue_resp.get(
            "issueDescription"
        )
        simplified_issue["IssueSpecificEntity"] = issue_resp.get("issueEntity")
        simplified_issue["IssueSpecificEntityValue"] = issue_resp.get(
            "issueEntityValue"
        )
        simplified_issue["IssueSpecificSeverity"] = issue_resp.get("issueSeverity")
        simplified_issue["IssueSpecificPriority"] = issue_resp.get("issuePriority")
        simplified_issue["IssueSpecificSummary"] = issue_resp.get("issueSummary")
        simplified_issue["IssueSpecificTimestamp"] = issue_resp.get("issueTimestamp")
        return simplified_issue
    else:
        return {}


def simplify_site(site_resp):
    """
    This function will simplify the site data for Splunk searches
    :param site_resp: Cisco DNAC SDK api
    :return: new site response
    """
    simplified_site = {}
    if site_resp:
        simplified_site["SiteName"] = site_resp.get("name")
        simplified_site["SiteNameHierarchy"] = site_resp.get("siteNameHierarchy")
        simplified_site["SiteType"] = "area"
        if site_resp.get("additionalInfo"):
            if len(site_resp["additionalInfo"]) > 0:
                for additional_info in site_resp["additionalInfo"]:
                    if isinstance(additional_info, dict) and additional_info.get(
                        "attributes"
                    ):
                        if isinstance(
                            additional_info["attributes"], dict
                        ) and additional_info["attributes"].get("type"):
                            simplified_site["SiteType"] = additional_info[
                                "attributes"
                            ].get("type")
        return simplified_site
    else:
        return {}


def clean_dict_of_empty_strings(**kwargs):
    dict_ = {**kwargs}
    dict_new = {}
    for key, value in dict_.items():
        if isinstance(value, str) and value != "":
            dict_new[key] = value
    return dict_new


def get_issues(helper, dnac, **kwargs):
    """
    This function will retrieve the issue details and devices&site data as necessary
    :param dnac: Cisco DNAC SDK api
    :param **kwargs: key arguments
    :return: simplified issues and device&site response
    """
    responses = []
    issues_response = dnac.issues.issues(**clean_dict_of_empty_strings(**kwargs))
    issue_info = {}
    site_info = {}
    device_info = {}
    wait_seconds_for_issue_details_requests = 15
    if issues_response and issues_response.response:
        last_index = len(issues_response.response) - 1
        for index, issue_item in enumerate(issues_response.response):
            response = {}
            issue_id = issue_item.get("issueId") or ""
            site_id = issue_item.get("siteId") or ""
            device_id = issue_item.get("deviceId") or ""
            # site_id represents a siteId hierarchy, the last value is the correct siteId
            # Python allows to call last string array without issues here
            site_id = site_id.split("/")[-1]
            if issue_id:
                helper.log_debug(
                    "Getting the issue details from the issue id {0}".format(issue_id)
                )
                if issue_info.get(issue_id):
                    response.update(issue_info[issue_id])
                    helper.log_debug(
                        "Saved the issue details from the issue id {0} to final response. Cache".format(
                            issue_id
                        )
                    )
                else:
                    tmp_issue = {}
                    try:
                        tmp_issue = dnac.issues.get_issue_enrichment_details(
                            headers=dict(entity_type="issue_id", entity_value=issue_id)
                        )
                        if index != last_index:
                            time.sleep(wait_seconds_for_issue_details_requests)
                    except Exception as e:
                        tmp_issue = {}
                        import traceback
                        helper.log_error(traceback.format_exc())
                        helper.log_error('Error getting issues. ' + str(e))

                    if (
                        tmp_issue
                        and isinstance(tmp_issue.get("issueDetails"), dict)
                        and isinstance(tmp_issue["issueDetails"].get("issue"), list)
                    ):
                        issue_info[issue_id] = simplify_issue(
                            tmp_issue["issueDetails"]["issue"]
                        )
                        helper.log_debug(
                            "Saved the issue details from the issue id {0}".format(
                                issue_id
                            )
                        )
                    else:
                        issue_info[issue_id] = {}

                    issue_info[issue_id].update(
                        {
                            "IssueName": issue_item.get("name") or "",
                            "IssueDeviceRole": issue_item.get("deviceRole") or "",
                            "IssueAiDriven": issue_item.get("aiDriven") or "",
                            "IssueClientMac": issue_item.get("clientMac") or "",
                            "IssueCount": issue_item.get("issue_occurence_count") or "",
                            "IssueStatus": issue_item.get("status") or "",
                            "IssuePriority": issue_item.get("priority") or "",
                            "IssueCategory": issue_item.get("category") or "",
                        }
                    )
                    response.update(issue_info[issue_id])
                    helper.log_debug(
                        "Saved the issue details from the issue id {0} to final response.".format(
                            issue_id
                        )
                    )
            if site_id:
                helper.log_debug(
                    "Getting the site data from the site id {0}".format(site_id)
                )
                if site_info.get(site_id):
                    response.update(site_info[site_id])
                    helper.log_debug(
                        "Saved the site data from the site id {0} to final response. Cache".format(
                            site_id
                        )
                    )
                else:
                    tmp_site = {}
                    try:
                        tmp_site = dnac.sites.get_site(site_id=site_id)
                    except Exception as e:
                        tmp_site = {}
                        import traceback
                        helper.log_error(traceback.format_exc())
                        helper.log_error('Error getting site. ' + str(e))

                    if tmp_site and tmp_site.response:
                        site_info[site_id] = simplify_site(tmp_site["response"])
                        response.update(site_info[site_id])
                        helper.log_debug(
                            "Saved the site data from the site id {0} to final response.".format(
                                site_id
                            )
                        )
            if device_id:
                helper.log_debug(
                    "Getting the device data from the device id {0}".format(device_id)
                )
                if device_info.get(device_id):
                    response.update(device_info[device_id])
                    helper.log_debug(
                        "Saved the device data from the device id {0} to final response. Cache".format(
                            device_id
                        )
                    )
                else:
                    tmp_device = {}
                    try:
                        tmp_device = dnac.devices.get_device_by_id(id=device_id)
                    except Exception as e:
                        tmp_device = {}
                        import traceback
                        helper.log_error(traceback.format_exc())
                        helper.log_error('Error getting device. ' + str(e))

                    if tmp_device and tmp_device.response:
                        device_info[device_id] = get_important_device_values(
                            tmp_device["response"]
                        )
                        response.update(device_info[device_id])
                        helper.log_debug(
                            "Saved the device data from the device id {0} to final response.".format(
                                device_id
                            )
                        )
            responses.append(response)
            helper.log_debug("Saved the issue data with all details to responses.")
    return responses


def is_different(helper, state, item):
    if not isinstance(state, dict):
        helper.log_debug("is_different. The state is not a dictionary.")
        return True
    if not isinstance(item, dict):
        helper.log_debug("is_different. The item is not a dictionary.")
        return True
    keys = set(state.keys())
    keys = keys.union(set(item.keys()))
    properties = list(keys)
    for property_ in properties:
        if state.get(property_) != item.get(property_):
            helper.log_debug(
                "is_different. The state and item have different values for property '{0}', values are {1} and {2}.".format(
                    property_,
                    state.get(property_),
                    item.get(property_),
                )
            )
            return True
    return False


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    cisco_dna_center_host = definition.parameters.get("cisco_dna_center_host", None)
    cisco_dna_center_account = definition.parameters.get(
        "cisco_dna_center_account", None
    )
    # review: check cisco_dna_center_host
    if not isinstance(cisco_dna_center_host, str):
        raise TypeError("URL must be string")
    if not cisco_dna_center_host.startswith("https"):
        raise ValueError("URL must be HTTPS")
    pass


def collect_events(helper, ew):
    opt_cisco_dna_center_host = helper.get_arg("cisco_dna_center_host")
    opt_cisco_dna_center_account = helper.get_arg("cisco_dna_center_account")

    account_username = opt_cisco_dna_center_account.get("username", None)
    account_password = opt_cisco_dna_center_account.get("password", None)
    account_name = opt_cisco_dna_center_account.get("name", None)
    current_version = "2.2.3.3"
    current_verify = False
    current_debug = False

    dnac = api.DNACenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_dna_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug,
        helper=helper,
    )

    r_json = []

    # get the issue details and devices&site data as necessary
    overall_issues = []
    overall_issues_active = []
    overall_issues_ignored = []
    overall_issues_resolved = []
    try:
        overall_issues_active = get_issues(helper, dnac, issue_status="ACTIVE")
    except Exception as e:
        import traceback
        helper.log_error(traceback.format_exc())
        helper.log_error('Get exception when getting issues of type ACTIVE. ' + str(e))
        overall_issues_active = []
    try:
        overall_issues_ignored = get_issues(helper, dnac, issue_status="IGNORED")
    except Exception as e:
        import traceback
        helper.log_error(traceback.format_exc())
        helper.log_error('Get exception when getting issues of type IGNORED. ' + str(e))
        overall_issues_ignored = []
    try:
        overall_issues_resolved = get_issues(helper, dnac, issue_status="RESOLVED")
    except Exception as e:
        import traceback
        helper.log_error(traceback.format_exc())
        helper.log_error('Get exception when getting issues of type RESOLVED. ' + str(e))
        overall_issues_resolved = []

    overall_issues = (
        overall_issues_active + overall_issues_ignored + overall_issues_resolved
    )
    for item in overall_issues:
        key = "{0}_{1}".format(opt_cisco_dna_center_host, item.get("IssueID"))
        item["cisco_dnac_host"] = opt_cisco_dna_center_host
        state = helper.get_check_point(key)
        if state is None:
            helper.save_check_point(key, item)
            r_json.append(item)
        elif is_different(helper, state, item):
            helper.save_check_point(key, item)
            r_json.append(item)
        # helper.delete_check_point(key)

    # To create a splunk event
    event = helper.new_event(
        json.dumps(r_json),
        time=None,
        host=None,
        index=None,
        source=None,
        sourcetype=None,
        done=True,
        unbroken=True,
    )
    ew.write_event(event)
