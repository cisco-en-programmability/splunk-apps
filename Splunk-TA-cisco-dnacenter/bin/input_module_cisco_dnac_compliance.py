
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
    This function will simplify the device data for Splunk searches
    :param device_item: device data
    :return: new device response
    """
    response = {}
    response['DeviceName'] = device_item.get('hostname') or 'NA'
    response['IpAddress'] = device_item.get('managementIpAddress') or device_item.get('ipAddress') or ''
    response['DeviceFamily'] = device_item.get('family') or ''
    response['Reachability'] = device_item.get('reachabilityStatus') or ''
    response['ReachabilityFailureReason'] = device_item.get('reachabilityFailureReason') or ''
    # Section to set the value of Manageability and ManageErrors
    response['ManageErrors'] = ''
    if device_item.get('managementState') == "Managed":
        response['Manageability'] = "Managed"
        if device_item.get('collectionStatus') and device_item['collectionStatus'] != "Managed":
            response['Manageability'] = "Managed (With Errors)"
            response['ManageErrors'] = device_item['collectionStatus']
    elif device_item.get('managementState') in ["Unmanaged", "Never Managed"]:
        response['Manageability'] = "Unmanaged"
    else:
        response['Manageability'] = "Managed (With Errors)"
    response['MACAddress'] = device_item.get('macAddress') or device_item.get('apEthernetMacAddress') or ''
    response['DeviceRole'] = device_item.get('role') or 'UNKNOWN'
    response['ImageVersion'] = device_item.get('softwareVersion') or ''
    response['Uptime'] = device_item.get('upTime') or ''
    if device_item.get('uptimeSeconds') is not None:
        response['UptimeSeconds'] = device_item.get('uptimeSeconds')
    else:
        response['UptimeSeconds'] = 0
    response['LastUpdated'] = device_item.get('lastUpdated') or ''
    if device_item.get('lastUpdateTime') is not None:
        response['LastUpdateTime'] = device_item.get('lastUpdateTime')
    else:
        response['LastUpdateTime'] = 0
    response['SerialNumber'] = device_item.get('serialNumber') or ''
    response['DeviceSeries'] = device_item.get('series') or ''
    response['Platform'] = device_item.get('platformId') or ''
    response['SupportType'] = device_item.get('deviceSupportLevel') or ''
    response['AssociatedWLCIP'] = device_item.get('associatedWlcIp') or ''
    return response

def get_simplified_compliance(compliance_item):
    """
    This function will simplify the compliance data for Splunk searches
    :param compliance_item: compliance data
    :return: new compliance response
    """
    response = {}
    response['ComplianceDeviceID'] = compliance_item.get('deviceUuid') or compliance_item.get('deviceId') or ''
    response['ComplianceComplianceType'] = compliance_item.get('complianceType') or ''
    response['ComplianceStatus'] = compliance_item.get('status') or ''
    response['ComplianceState'] = compliance_item.get('state') or ''
    response['ComplianceLastSyncTime'] = compliance_item.get('lastSyncTime') or 0
    response['ComplianceLastUpdateTime'] = compliance_item.get('lastUpdateTime') or 0
    return response

def simplified_complaince_page(dnac, compliance_page_response, devices_retrieved):
    """
    This function will retrieve the compliance details and devices data as necessary
    :param dnac: Cisco DNAC SDK api
    :return: compliance details response
    """
    simplified_complaince_response = []
    for compliance in compliance_page_response:
        simplified_complaince = dict(get_simplified_compliance(compliance))
        device_key = simplified_complaince['ComplianceDeviceID']
        # Manage device info ...
        device_info = {}
        # ... if already present, reuse
        if devices_retrieved.get(device_key):
            device_info = dict(devices_retrieved[device_key])
        else:  # ... if not retrieve and save it
            device_info = dnac.devices.get_device_by_id(id=device_key)
            devices_retrieved[device_key] = device_info
        if isinstance(device_info, dict) and device_info.get('response'):
            simplified_complaince.update(get_important_device_values(device_info['response']))
        simplified_complaince_response.append(simplified_complaince)
    return simplified_complaince_response

def get_compliance_and_device_details(dnac):
    """
    This function will retrieve the compliance details and devices as necessary
    :param dnac: Cisco DNAC SDK api
    :return: compliance details response
    """
    limit = 20
    offset = 1
    compliances_response = []
    do_request_next = True
    devices_retrieved = {}
    while do_request_next:
        try:
            compliance_page_response = dnac.compliance.get_compliance_detail(limit=str(limit), offset=str(offset))
            if compliance_page_response and compliance_page_response.response:
                compliances_response.extend(simplified_complaince_page(dnac, compliance_page_response.response, devices_retrieved))
                if len(compliance_page_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return compliances_response

def is_different(state, item):
    if not isinstance(state, dict):
        return True
    if not isinstance(item, dict):
        return True
    keys = set(state.keys())
    keys = keys.union(set(item.keys()))
    properties = list(keys)
    for property_ in properties:
        # if property_ in ['UptimeSeconds', 'ComplianceLastSyncTime', 'ComplianceLastUpdateTime']:
        #     continue
        if state.get(property_) != item.get(property_):
            return True
    return False

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    cisco_dna_center_host = definition.parameters.get('cisco_dna_center_host', None)
    cisco_dna_center_account = definition.parameters.get('cisco_dna_center_account', None)
    pass

def collect_events(helper, ew):
    opt_cisco_dna_center_host = helper.get_arg('cisco_dna_center_host')
    opt_cisco_dna_center_account = helper.get_arg('cisco_dna_center_account')

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
        debug=current_debug)

    r_json = []
    # get the compliance details and devices data as necessary
    overall_compliance_details = get_compliance_and_device_details(dnac)

    for item in overall_compliance_details:
        key = "{0}_{1}_{2}_{3}".format(opt_cisco_dna_center_host, item.get('ComplianceDeviceID') or "NA", item.get('ComplianceComplianceType') or "NA", item.get('IpAddress') or "NA")
        state = helper.get_check_point(key)
        item["cisco_dnac_host"] = opt_cisco_dna_center_host
        if state is None:
            helper.save_check_point(key, item)
            r_json.append(item)
        elif is_different(state, item):
            helper.save_check_point(key, item)
            r_json.append(item)
        # helper.delete_check_point(key)

    # To create a splunk event
    event = helper.new_event(json.dumps(r_json), time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    ew.write_event(event)
