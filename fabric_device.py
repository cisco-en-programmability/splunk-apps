#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fabric device script.

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

from dnacentersdk import api


def read_config_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config_primelab.ini'))
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

    # get the devices (health) and fabric sites associated with them
    devices_health = get_device_health(dnac)
    print(json.dumps(devices_health))  # save the data to Splunk App index


if __name__ == '__main__':
    main()
