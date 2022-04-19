
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

def get_epoch_current_previous_times(interval_seconds):
    """
    This function will return the epoch time for the {timestamp} and a previous epoch time
    :return: epoch time (now) including msec, epoch time (previous) including msec
    """
    # REVIEW: It is recommended that this time matches the Splunk's data input interval
    now = datetime.datetime.now()
    rounded = now - datetime.timedelta(
        seconds=now.second % interval_seconds + interval_seconds if interval_seconds > 0 else now.second)
    now = now.replace(microsecond=0)
    rounded = rounded.replace(microsecond=0)
    return (int(now.timestamp() * 1000), int(rounded.timestamp() * 1000))


def simplify_device_health(device_health_response):
    """
    This function will simplify the device health data for Splunk searches
    :param device_item: device health data
    :return: new device health response
    """
    response = {}
    if device_health_response:
        response['DeviceName'] = device_health_response.get('name')
        response['DeviceModel'] = device_health_response.get('model')
        response['DeviceLocation'] = device_health_response.get('location')
        response['DeviceIpAddress'] = device_health_response.get('ipAddress')
        response['DeviceFamily'] = device_health_response.get('deviceFamily')
        response['DeviceType'] = device_health_response.get('deviceType')
        response['DeviceMACAddress'] = device_health_response.get('macAddress')
    return response

def simplify_devices_health(dnac, devices_health_responses):
    """
    This function will simplify the device health data and add the fabric site
    :param dnac: Cisco DNAC SDK api
    :param devices_health_responses: devices health response
    :return: new fabric devices response
    """
    fabric_devices_response = []
    for device_health in devices_health_responses:
        device = simplify_device_health(device_health)
        device_key = device['DeviceLocation']
        fabric_site = get_simplified_fabric_site(dnac, device_key)
        fabric_device_new = dict(device)
        if fabric_site:
            fabric_device_new.update({'HasFabric': 'True'})
        else:
            fabric_device_new.update({'HasFabric': 'False'})
        fabric_device_new.update(fabric_site)
        fabric_devices_response.append(fabric_device_new)
    return fabric_devices_response

def get_device_health(dnac, input_interval):
    """
    This function will retrieve the device health from a previous time to the time the function is called
    :param dnac: Cisco DNAC SDK api
    :return: device health response
    """
    (epoch_current_time, epoch_previous_time) = get_epoch_current_previous_times(input_interval)
    limit = 20
    offset = 1
    devices_responses = []
    do_request_next = True
    while do_request_next:
        try:
            health_response = dnac.devices.devices(start_time=epoch_previous_time, end_time=epoch_current_time, limit=limit, offset=offset)
            if health_response and health_response.response:
                devices_responses.extend(simplify_devices_health(dnac, health_response.response))
                if len(health_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return devices_responses

def get_simplified_fabric_site(dnac, site_name_hierarchy):
    """
    This function will retrieve the fabric site and simplify them
    :param dnac: Cisco DNAC SDK api
    :param site_name_hierarchy: site name hierarchy
    :return: fabric site response
    """
    response = {}
    try:
        fabric_site = dnac.sda.get_site(site_name_hierarchy)
        if fabric_site.get('status') == 'success':
            response['FabricSiteNameHierarchy'] = fabric_site.get('siteNameHierarchy') or ''
            response['FabricName'] = fabric_site.get('fabricName') or ''
            response['FabricType'] = fabric_site.get('fabricType') or ''
            response['FabricDomainType'] = fabric_site.get('fabricDomainType') or ''
        return response
    except Exception:
        return response


def is_different(state, item):
    if not isinstance(state, dict):
        return True
    if not isinstance(item, dict):
        return True
    keys = set(state.keys())
    keys = keys.union(set(item.keys()))
    properties = list(keys)
    for property in properties:
        if state.get(property) != item.get(property):
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

    # use default input_interval
    input_interval = 900
    try:
        input_interval = int(helper.get_arg("interval"))
    except ValueError as e:
        input_interval = 900

    dnac = api.DNACenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_dna_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug)

    # get the devices (health) and fabric sites associated with them
    devices_health = get_device_health(dnac, input_interval)

    r_json = []
    for item in devices_health:
        key = "{0}_{1}".format(opt_cisco_dna_center_host, item['DeviceIpAddress'])
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
    event = helper.new_event(json.dumps(devices_health), time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    ew.write_event(event)
