
# encoding = utf-8

import os
import json
import sys
import time
import datetime

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
        minutes=now.minute,
        seconds=now.second % interval_seconds + interval_seconds if interval_seconds > 0 else now.second,
        microseconds=now.microsecond)
    return (int(now.timestamp() * 1000), int(rounded.timestamp() * 1000))

def get_device_health(dnac, input_interval):
    """
    This function will retrieve the device health from a previous time to the time the function is called
    :param dnac: Cisco DNAC SDK api
    :param input_interval: interval in seconds
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
                devices_responses.extend(health_response.response)
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

def get_devices(dnac):
    """
    This function will retrieve the devices
    :param dnac: Cisco DNAC SDK api
    :return: devices response
    """
    limit = 20
    offset = 1
    devices_responses = []
    do_request_next = True
    while do_request_next:
        try:
            device_response = dnac.devices.get_device_list(limit=limit, offset=offset)
            if device_response and device_response.response:
                devices_responses.extend(device_response.response)
                if len(device_response.response) < limit:
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

def get_health_device_values(health_device):
    """
    This function will simplify the health device data for Splunk searches
    :param health_device: health device data
    :return: new health device response
    """
    response = {'HasHealthReport': 'True'}
    if health_device.get('overallHealth') is not None:
        response['OverallHealth'] = health_device.get('overallHealth')
    else:
        response['OverallHealth'] = 0
    response['HealthScore'] = response['OverallHealth']
    response['IssueCount'] = health_device.get('issueCount') or 0
    response['Site'] = health_device.get('location') or ''
    response['Location'] = health_device.get('location') or ''

    response['InterfaceLinkErrHealth'] = health_device.get('interfaceLinkErrHealth') or 0
    response['CPUUtilization'] = health_device.get('cpuUlitilization') or health_device.get('cpuUtilization') or 0
    response['CPUHealth'] = health_device.get('cpuHealth') or 0
    response['MemoryUtilizationHealth'] = health_device.get('memoryUtilizationHealth') or 0
    response['MemoryUtilization'] = health_device.get('memoryUtilization') or 0
    response['InterDeviceLinkAvailHealth'] = health_device.get('interDeviceLinkAvailHealth') or 0

    client_count = health_device.get('clientCount') or {}
    response['HasClientCount'] = str(len(client_count) > 0)
    response['ClientCountRadio0'] = client_count.get('radio0') or 0
    response['ClientCountRadio1'] = client_count.get('radio1') or 0
    response['ClientCountGhz24'] =  client_count.get('Ghz24') or 0
    response['ClientCountGhz50'] =  client_count.get('Ghz50') or 0

    interference_health = health_device.get('interferenceHealth') or {}
    response['HasInterferenceHealth'] = str(len(interference_health) > 0)
    response['InterferenceHealthRadio0'] = interference_health.get('radio0') or 0
    response['InterferenceHealthRadio1'] = interference_health.get('radio1') or 0
    response['InterferenceHealthGhz24'] =  interference_health.get('Ghz24') or 0
    response['InterferenceHealthGhz50'] =  interference_health.get('Ghz50') or 0

    noise_health = health_device.get('noiseHealth') or {}
    response['HasNoiseHealth'] = str(len(noise_health) > 0)
    response['NoiseHealthRadio1'] = noise_health.get('radio1') or 0
    response['NoiseHealthGhz50'] =  noise_health.get('Ghz50') or 0
    # following attribute is not present in documentation
    response['NoiseHealthRadio0'] = noise_health.get('radio0') or 0
    # following attribute is not present in documentation
    response['NoiseHealthGhz24'] =  noise_health.get('Ghz24') or 0

    air_quality_health = health_device.get('airQualityHealth') or {}
    response['HasAirQualityHealth'] = str(len(air_quality_health) > 0)
    response['AirQualityHealthRadio0'] = air_quality_health.get('radio0') or 0
    response['AirQualityHealthRadio1'] = air_quality_health.get('radio1') or 0
    response['AirQualityHealthGhz24'] =  air_quality_health.get('Ghz24') or 0
    response['AirQualityHealthGhz50'] =  air_quality_health.get('Ghz50') or 0

    utilization_health = health_device.get('utilizationHealth') or {}
    response['HasUtilization'] = str(len(utilization_health) > 0)
    response['UtilizationRadio0'] = utilization_health.get('radio0') or 0
    response['UtilizationRadio1'] = utilization_health.get('radio1') or 0
    response['UtilizationGhz24'] =  utilization_health.get('Ghz24') or 0
    response['UtilizationGhz50'] =  utilization_health.get('Ghz50') or 0

    # NOTE: Properties that are already present
    # NOTE: WARNING: data maybe have slightly different format
    # response['DeviceFamily'] = health_device.get('deviceFamily') or ''
    # response['DeviceSeries'] = health_device.get('deviceType') or health_device.get('model') or ''
    # response['MACAddress'] = health_device.get('macAddress') or ''
    # response['DeviceName'] = health_device.get('name') or 'NA'
    # response['ImageVersion'] = health_device.get('osVersion') or ''
    # response['IpAddress'] = health_device.get('ipAddress') or ''
    # response['Reachability'] = health_device.get('reachabilityHealth') or ''
    return response

def filter_health_data(health_devices, devices_items):
    """
    This function will filter data to get the overall device data.
    :param health_devices: health devices data
    :param devices_items: devices data
    :return: health summary response
    """
    health_summary_response = []
    device_dict = {}
    for device_item in devices_items:
        ip_address_key = device_item.get('managementIpAddress') or device_item.get('ipAddress')
        device_dict[ip_address_key] = dict(get_important_device_values(device_item))
    for health_device in health_devices:
        ip_address_key = health_device.get('ipAddress') or health_device.get('managementIpAddress')
        if device_dict.get(ip_address_key):
            device_dict[ip_address_key].update(get_health_device_values(health_device))
        else:
            device_dict[ip_address_key].update({'HasHealthReport': 'False'})
    health_summary_response = list(device_dict.values())
    return health_summary_response

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

    # get the overall device health
    health_devices = get_device_health(dnac, input_interval)
    # get the information of all devices
    devices_items = get_devices(dnac)
    # merge and simplify gathered information
    overall_device_health = filter_health_data(health_devices, devices_items)

    r_json = []
    for item in overall_device_health:
        key = "{0}_{1}".format(opt_cisco_dna_center_host, item['IpAddress'])
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
