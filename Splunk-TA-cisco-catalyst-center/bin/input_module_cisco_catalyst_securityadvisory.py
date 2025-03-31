
# encoding = utf-8

import datetime
import json
import os
import sys
import time
import utils
import re

import cisco_catalyst_api as api

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


def get_important_device_values(device_item, site_info):
    """
    This function will simplify the device data for Splunk searches
    :param device_item: device data
    :param site_info: site data
    :return: new device response
    """
    response = {}
    response["DeviceID"] = device_item.get("id") or ""
    response["DeviceName"] = device_item.get("hostname") or "N/A"
    response["DeviceIpAddress"] = (
        device_item.get("managementIpAddress") or device_item.get("ipAddress") or ""
    )
    response["DeviceFamily"] = device_item.get("family") or ""
    response["DeviceReachability"] = device_item.get("reachabilityStatus") or ""
    response["DeviceReachabilityFailureReason"] = (
        device_item.get("reachabilityFailureReason") or ""
    )
    # Section to set the value of Manageability and ManageErrors
    response["DeviceManageErrors"] = ""
    if device_item.get("managementState") == "Managed":
        response["DeviceManageability"] = "Managed"
        if (
            device_item.get("collectionStatus")
            and device_item["collectionStatus"] != "Managed"
        ):
            response["DeviceManageability"] = "Managed (With Errors)"
            response["DeviceManageErrors"] = device_item["collectionStatus"]
    elif device_item.get("managementState") in ["Unmanaged", "Never Managed"]:
        response["DeviceManageability"] = "Unmanaged"
    else:
        response["DeviceManageability"] = "Managed (With Errors)"
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
    response["DeviceAssociatedWLCIP"] = device_item.get("associatedWlcIp") or ""
    response["Site"] = site_info.get("siteNameHierarchy") or "N/A"
    return response


def get_advisories_summary(catalyst):
    """
    This function will retrieve the advisories summary
    :param catalyst: Cisco Catalyst SDK api
    :return: simplified advisories summary response
    """
    advisories_summary = catalyst.security_advisories.get_advisories_summary()
    responses = []
    if advisories_summary and advisories_summary.response:
        for category in advisories_summary.response:
            for subcategory in advisories_summary.response[category]:
                responses.append(
                    {
                        "Summary": "True",
                        "Category": category,
                        "SubCategory": subcategory,
                        "Amount": int(
                            advisories_summary.response[category][subcategory]
                        ),
                    }
                )
    return responses


def get_devices_per_advisory(catalyst):
    """
    This function will retrieve the advisories data and devices data as necessary
    :param catalyst: Cisco Catalyst SDK api
    :return: simplified advisories and devices response
    """
    advisories_list = catalyst.security_advisories.get_advisories_list()
    responses = []
    devices_retrieved = {}
    if advisories_list and advisories_list.response:
        for advisories_item in advisories_list.response:
            response = {}
            response["AdvisoryID"] = advisories_item.get("advisoryId") or ""
            response["AdvisoryDeviceCount"] = advisories_item.get("deviceCount") or 0
            # response['AdvisoryCves'] = advisories_item.get('cves') or []
            response["AdvisoryCvesStr"] = ", ".join(advisories_item.get("cves")) or ""
            response["AdvisoryPublicationUrl"] = (
                advisories_item.get("publicationUrl") or ""
            )
            response["AdvisorySir"] = advisories_item.get("sir") or ""
            response["AdvisoryDetectionType"] = (
                advisories_item.get("detectionType") or ""
            )
            response["AdvisoryDefaultDetectionType"] = (
                advisories_item.get("defaultDetectionType") or ""
            )
            if response["AdvisoryID"]:
                advisory_device = catalyst.security_advisories.get_devices_per_advisory(
                    response["AdvisoryID"]
                )
                if advisory_device and advisory_device.response:
                    for device_id in advisory_device.response:
                        # Manage device info ...
                        device_info = {}
                        site_info = {}
                        # ... if already present, reuse
                        if devices_retrieved.get(device_id):
                            device_info = dict(devices_retrieved[device_id])
                            site_info = dict(devices_retrieved.get(device_id + "_site", {}))
                        else:  # ... if not retrieve and save it
                            device_info = catalyst.devices.get_device_by_id(id=device_id)
                            site_info = catalyst.devices.get_site_assigned_network_device(id=device_id)
                            devices_retrieved[device_id] = device_info
                            devices_retrieved[device_id + "_site"] = site_info
                        if isinstance(device_info, dict) and device_info.get(
                            "response"
                        ):
                            response_device = dict(response)
                            response_device.update(
                                get_important_device_values(device_info["response"], site_info.get("response", {}))
                            )
                            response_device.update({"Summary": "False"})
                            responses.append(response_device)
            else:
                responses.append(response)
    return responses


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    cisco_catalyst_center_host = definition.parameters.get("cisco_catalyst_center_host", None)
    cisco_catalyst_center_account = definition.parameters.get(
        "cisco_catalyst_center_account", None
    )
    # review: check cisco_catalyst_center_host
    if not isinstance(cisco_catalyst_center_host, str):
        raise TypeError("URL must be string")
    regex = re.compile(
        r'^(https:\/\/)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$|^(?:\d{1,3}\.){3}\d{1,3}$'
    )
    if not regex.match(cisco_catalyst_center_host):
        raise ValueError("URL does not match the required pattern")
    pass


def collect_events(helper, ew):
    opt_cisco_catalyst_center_host = helper.get_arg("cisco_catalyst_center_host")
    if opt_cisco_catalyst_center_host:
        opt_cisco_catalyst_center_host = opt_cisco_catalyst_center_host.strip()
        if not opt_cisco_catalyst_center_host.startswith("https://"):
            opt_cisco_catalyst_center_host = "https://" + opt_cisco_catalyst_center_host
    opt_cisco_catalyst_center_account = helper.get_arg("cisco_catalyst_center_account")

    account_username = opt_cisco_catalyst_center_account.get("username", None)
    account_password = opt_cisco_catalyst_center_account.get("password", None)
    account_name = opt_cisco_catalyst_center_account.get("name", None)
    current_version = "2.2.3.3"
    session_key = helper.context_meta['session_key']
    current_verify = utils.get_sslconfig(session_key, helper)
    current_debug = False

    # use default input_interval
    input_interval = 900
    try:
        input_interval = int(helper.get_arg("interval"))
    except ValueError as e:
        input_interval = 900

    catalyst = api.CatalystCenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_catalyst_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug,
        helper=helper,
    )

    # get the security advisories details and devices data as necessary
    r_json = []
    security_advisories = []
    advisories_summary = []
    try:
        security_advisories = get_devices_per_advisory(catalyst)
    except Exception as e:
        import traceback

        stack = traceback.format_exc()
        helper.log_error(stack)


    for item in security_advisories:
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
        r_json.append(item)

    try:
        advisories_summary = get_advisories_summary(catalyst)
    except Exception as e:
        import traceback

        stack = traceback.format_exc()
        helper.log_error(stack)

    for item in advisories_summary:
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
        r_json.append(item)

    for index, item in enumerate(r_json):
        done_flag = (index == len(r_json) - 1)
        event = helper.new_event(
        json.dumps(item),
        time=None,
        host=None,
        index=None,
        source=None,
        sourcetype=None,
        done=done_flag,
        unbroken=False,
        )
        ew.write_event(event)
