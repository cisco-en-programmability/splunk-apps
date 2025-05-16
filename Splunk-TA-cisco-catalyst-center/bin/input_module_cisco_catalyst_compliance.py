
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
    response["DeviceName"] = device_item.get("hostname") or "N/A"
    response["IpAddress"] = (
        device_item.get("managementIpAddress") or device_item.get("ipAddress") or ""
    )
    response["DeviceFamily"] = device_item.get("family") or ""
    response["Reachability"] = device_item.get("reachabilityStatus") or ""
    response["ReachabilityFailureReason"] = (
        device_item.get("reachabilityFailureReason") or ""
    )
    # Section to set the value of Manageability and ManageErrors
    response["ManageErrors"] = ""
    if device_item.get("managementState") == "Managed":
        response["Manageability"] = "Managed"
        if (
            device_item.get("collectionStatus")
            and device_item["collectionStatus"] != "Managed"
        ):
            response["Manageability"] = "Managed (With Errors)"
            response["ManageErrors"] = device_item["collectionStatus"]
    elif device_item.get("managementState") in ["Unmanaged", "Never Managed"]:
        response["Manageability"] = "Unmanaged"
    else:
        response["Manageability"] = "Managed (With Errors)"
    response["MACAddress"] = (
        device_item.get("macAddress") or device_item.get("apEthernetMacAddress") or ""
    )
    response["DeviceRole"] = device_item.get("role") or "UNKNOWN"
    response["ImageVersion"] = device_item.get("softwareVersion") or ""
    response["Uptime"] = device_item.get("upTime") or ""
    if device_item.get("uptimeSeconds") is not None:
        response["UptimeSeconds"] = device_item.get("uptimeSeconds")
    else:
        response["UptimeSeconds"] = 0
    response["LastUpdated"] = device_item.get("lastUpdated") or ""
    if device_item.get("lastUpdateTime") is not None:
        response["LastUpdateTime"] = device_item.get("lastUpdateTime")
    else:
        response["LastUpdateTime"] = 0
    response["SerialNumber"] = device_item.get("serialNumber") or ""
    response["DeviceSeries"] = device_item.get("series") or ""
    response["Platform"] = device_item.get("platformId") or ""
    response["SupportType"] = device_item.get("deviceSupportLevel") or ""
    response["AssociatedWLCIP"] = device_item.get("associatedWlcIp") or ""
    response["Site"] = site_info.get("siteNameHierarchy") or "N/A"
    return response


def get_simplified_compliance_detail(compliance_item):
    """
    This function will simplify the compliance data for Splunk searches
    :param compliance_item: compliance data
    :return: new compliance response
    """
    response = {}
    response["ComplianceDeviceID"] = (
        compliance_item.get("deviceUuid") or compliance_item.get("deviceId") or ""
    )
    response["ComplianceComplianceType"] = compliance_item.get("complianceType") or ""
    response["ComplianceStatus"] = compliance_item.get("status") or ""
    response["ComplianceState"] = compliance_item.get("state") or ""
    response["ComplianceLastSyncTime"] = compliance_item.get("lastSyncTime") or 0
    response["ComplianceLastUpdateTime"] = compliance_item.get("lastUpdateTime") or 0
    return response


def get_simplified_compliance_status(compliance_item):
    """
    This function will simplify the compliance data for Splunk searches
    :param compliance_item: compliance data
    :return: new compliance response
    """
    response = {}
    response["ComplianceDeviceID"] = (
        compliance_item.get("deviceUuid") or compliance_item.get("deviceId") or ""
    )
    response["ComplianceStatus"] = compliance_item.get("complianceStatus") or ""
    response["ComplianceLastUpdateTime"] = compliance_item.get("lastUpdateTime") or 0
    return response


def simplified_complaince_status_page(
    helper, catalyst, compliance_page_response, devices_retrieved
):
    """
    This function will retrieve the compliance status and devices data as necessary
    :param catalyst: Cisco Catalyst SDK api
    :return: compliance status response
    """
    simplified_complaince_response = []
    for compliance in compliance_page_response:
        simplified_complaince = dict(get_simplified_compliance_status(compliance))
        device_key = simplified_complaince["ComplianceDeviceID"]
        # Manage device info ...
        device_info = {}
        site_info = {}
        # ... if already present, reuse
        if devices_retrieved.get(device_key):
            device_info = dict(devices_retrieved[device_key])
            site_info = dict(devices_retrieved[device_key + "_site"])
        else:  # ... if not retrieve and save it
            helper.log_debug(
                "Getting the device data from the compliance device id {0}".format(
                    device_key
                )
            )
            device_info = catalyst.devices.get_device_by_id(id=device_key)
            site_info = catalyst.devices.get_site_assigned_network_device(id=device_key)
            devices_retrieved[device_key] = device_info
            devices_retrieved[device_key + "_site"] = site_info
        if isinstance(device_info, dict) and device_info.get("response"):
            simplified_complaince.update(
                get_important_device_values(device_info["response"], site_info["response"])
            )
            helper.log_debug(
                "Saved the device data from the compliance device id {0}".format(
                    device_key
                )
            )
        simplified_complaince_response.append(simplified_complaince)
    return simplified_complaince_response


def simplified_complaince_detail_page(
    helper, catalyst, compliance_page_response, devices_retrieved
):
    """
    This function will retrieve the compliance details and devices data as necessary
    :param catalyst: Cisco Catalyst SDK api
    :return: compliance details response
    """
    simplified_complaince_response = []
    for compliance in compliance_page_response:
        simplified_complaince = dict(get_simplified_compliance_detail(compliance))
        device_key = simplified_complaince["ComplianceDeviceID"]
        # Manage device info ...
        device_info = {}
        site_info = {}
        # ... if already present, reuse
        if devices_retrieved.get(device_key):
            device_info = dict(devices_retrieved[device_key])
            site_info = dict(devices_retrieved[device_key + "_site"])
        else: # ... if not retrieve and save it
            helper.log_debug(
                "Getting the device data from the compliance device id {0}".format(
                    device_key
                )
            )
            device_info = catalyst.devices.get_device_by_id(id=device_key)
            site_info = catalyst.devices.get_site_assigned_network_device(id=device_key)
            devices_retrieved[device_key] = device_info
            devices_retrieved[device_key + "_site"] = site_info
        if isinstance(device_info, dict) and device_info.get("response"):
            simplified_complaince.update(
                get_important_device_values(device_info["response"], site_info["response"])
            )
            helper.log_debug(
                "Saved the device data from the compliance device id {0}".format(
                    device_key
                )
            )
        simplified_complaince_response.append(simplified_complaince)
    return simplified_complaince_response


def get_compliance_and_device_details(helper, catalyst):
    """
    This function will retrieve the compliance details and devices as necessary
    :param catalyst: Cisco Catalyst SDK api
    :return: compliance details response
    """
    compliances_details_response = []
    compliances_response = []
    devices_retrieved = {}
    limit = 20
    offset = 1
    do_request_next = True
    while do_request_next:
        try:
            compliances_page_response = catalyst.compliance.get_compliance_status(
                limit=str(limit), offset=str(offset)
            )
            if compliances_page_response and compliances_page_response.response:
                compliances_response.extend(
                    simplified_complaince_status_page(
                        helper,
                        catalyst,
                        compliances_page_response.response,
                        devices_retrieved,
                    )
                )
                if len(compliances_page_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit

    # Set again for new requests
    do_request_next = True
    limit = 20
    offset = 1
    while do_request_next:
        try:
            compliances_page_details_response = catalyst.compliance.get_compliance_detail(
                limit=str(limit), offset=str(offset)
            )
            if compliances_page_details_response and compliances_page_details_response.response:
                compliances_details_response.extend(
                    simplified_complaince_detail_page(
                        helper,
                        catalyst,
                        compliances_page_details_response.response,
                        devices_retrieved,
                    )
                )
                if len(compliances_page_details_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return [compliances_details_response, compliances_response]


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
    current_version = "v2.3.7.6"
    session_key = helper.context_meta['session_key']
    current_verify = utils.get_sslconfig(session_key, helper)
    current_debug = False

    catalyst = api.CatalystCenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_catalyst_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug,
        helper=helper,
    )

    r_json = []

    # get the compliance devices count
    compliance_device_count = {
        "ComplianceDetail": "False",
        "ComplianceCount": "True",
        "cisco_catalyst_host": opt_cisco_catalyst_center_host
    }
    try:
        all_status = catalyst.compliance.get_compliance_status_count()
        if all_status and all_status.response:
            compliance_device_count["ComplianceDeviceCount"] = all_status.response
        compliant_status = catalyst.compliance.get_compliance_status_count(compliance_status="COMPLIANT")
        if compliant_status and compliant_status.response:
            compliance_device_count["CompliantDeviceCount"] = compliant_status.response
    except Exception as e:
        import traceback
        helper.log_error(traceback.format_exc())
        helper.log_error('Error getting COMPLIANT count. ' + str(e))
        pass
    r_json.append(compliance_device_count)

    # get the compliance details and devices data as necessary
    [overall_compliance_details, overall_compliance] = get_compliance_and_device_details(helper, catalyst)

    for item in overall_compliance_details:
        item["ComplianceDetail"] = "True"
        item["ComplianceCount"] = "False"
        r_json.append(item)

    for item in overall_compliance:
        item["ComplianceDetail"] = "False"
        item["ComplianceCount"] = "False"
        r_json.append(item)

    for index, item in enumerate(r_json):
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
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
