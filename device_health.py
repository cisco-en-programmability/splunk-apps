#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Device health script.

Compatibility with Cisco DNA Center: v2.1.2 - v2.3.2.x.
Tested on: v2.2.3.4

Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import configparser
import json
import os.path
from datetime import datetime, timedelta

import api


def read_config_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config

def get_epoch_current_previous_times():
    """
    This function will return the epoch time for the {timestamp} and a previous epoch time
    :return: epoch time (now) including msec, epoch time (previous) including msec
    """
    # REVIEW: It is recommended that this time matches the Splunk's data input interval
    interval_minutes = 0
    interval_seconds = 300
    now = datetime.now()
    rounded = now - timedelta(minutes=now.minute % interval_minutes + interval_minutes if interval_minutes > 0 else now.minute,
                              seconds=now.second % interval_seconds + interval_seconds if interval_seconds > 0 else now.second,
                              microseconds=now.microsecond)
    return (int(now.timestamp() * 1000), int(rounded.timestamp() * 1000))

def get_device_health(dnac):
    """
    This function will retrieve the device health from a previous time to the time the function is called
    :param dnac: Cisco DNAC SDK api
    :return: device health response
    """
    (epoch_current_time, epoch_previous_time) = get_epoch_current_previous_times()
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

def connection():
    """
    Create a DNACenterAPI connection object
    """
    config = read_config_file()
    # Quick assertion to verify equal or above min version
    min_dnac_version = "2.1.2"
    current_version = str(config.get('API', 'version'))
    assert min_dnac_version <= current_version
    # Create connection object
    return api.DNACenterAPI(username=str(config.get('API', 'username')),
                            password=str(config.get('API', 'password')),
                            base_url=str(config.get('API', 'host')),
                            version=current_version,
                            verify=bool(config.get('API', 'verify')=="True"),
                            debug=False)

def main():
    # it uses DNA Center URL, username and password, with the DNA Center API version specified
    dnac = connection()

    # get the overall device health
    health_devices = get_device_health(dnac)
    # get the information of all devices
    devices_items = get_devices(dnac)
    # merge and simplify gathered information
    overall_device_health = filter_health_data(health_devices, devices_items)
    print(json.dumps(overall_device_health))  # save the device health to Splunk App index


if __name__ == '__main__':
    main()
