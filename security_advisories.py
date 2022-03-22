#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Security Advisories script.

Compatibility with Cisco DNA Center: v2.2.2.3 - v2.3.2.x.
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

import api


def read_config_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config


def connection():
    """
    Create a DNACenterAPI connection object
    """
    config = read_config_file()
    # Quick assertion to verify equal or above min version
    min_dnac_version = "2.2.1"
    current_version = str(config.get('API', 'version'))
    assert min_dnac_version <= current_version
    # Create connection object
    return api.DNACenterAPI(username=str(config.get('API', 'username')),
                            password=str(config.get('API', 'password')),
                            base_url=str(config.get('API', 'host')),
                            version=current_version,
                            verify=bool(config.get('API', 'verify')=="True"),
                            debug=False)

def get_important_device_values(device_item):
    """
    This function will simplify the device data for Splunk searches
    :param device_item: device data
    :return: new device response
    """
    response = {}
    response['DeviceName'] = device_item.get('hostname') or 'NA'
    response['DeviceIpAddress'] = device_item.get('managementIpAddress') or device_item.get('ipAddress') or ''
    response['DeviceFamily'] = device_item.get('family') or ''
    response['DeviceReachability'] = device_item.get('reachabilityStatus') or ''
    response['DeviceReachabilityFailureReason'] = device_item.get('reachabilityFailureReason') or ''
    # Section to set the value of Manageability and ManageErrors
    response['DeviceManageErrors'] = ''
    if device_item.get('managementState') == "Managed":
        response['DeviceManageability'] = "Managed"
        if device_item.get('collectionStatus') and device_item['collectionStatus'] != "Managed":
            response['DeviceManageability'] = "Managed (With Errors)"
            response['DeviceManageErrors'] = device_item['collectionStatus']
    elif device_item.get('managementState') in ["Unmanaged", "Never Managed"]:
        response['DeviceManageability'] = "Unmanaged"
    else:
        response['DeviceManageability'] = "Managed (With Errors)"
    response['DeviceMACAddress'] = device_item.get('macAddress') or device_item.get('apEthernetMacAddress') or ''
    response['DeviceRole'] = device_item.get('role') or 'UNKNOWN'
    response['DeviceImageVersion'] = device_item.get('softwareVersion') or ''
    response['DeviceUptime'] = device_item.get('upTime') or ''
    if device_item.get('uptimeSeconds') is not None:
        response['DeviceUptimeSeconds'] = device_item.get('uptimeSeconds')
    else:
        response['DeviceUptimeSeconds'] = 0
    response['DeviceLastUpdated'] = device_item.get('lastUpdated') or ''
    if device_item.get('lastUpdateTime') is not None:
        response['DeviceLastUpdateTime'] = device_item.get('lastUpdateTime')
    else:
        response['DeviceLastUpdateTime'] = 0
    response['DeviceSerialNumber'] = device_item.get('serialNumber') or ''
    response['DeviceSeries'] = device_item.get('series') or ''
    response['DevicePlatform'] = device_item.get('platformId') or ''
    response['DeviceSupportType'] = device_item.get('deviceSupportLevel') or ''
    response['DeviceAssociatedWLCIP'] = device_item.get('associatedWlcIp') or ''
    return response

def get_advisories_summary(dnac):
    """
    This function will retrieve the advisories summary
    :param dnac: Cisco DNAC SDK api
    :return: simplified advisories summary response
    """
    advisories_summary = dnac.security_advisories.get_advisories_summary()
    responses = []
    if advisories_summary and advisories_summary.response:
        for category in advisories_summary.response:
            for subcategory in advisories_summary.response[category]:
                responses.append({'Summary': 'True', 'Category': category, 'SubCategory': subcategory, 'Amount': int(advisories_summary.response[category][subcategory])})
    return responses

def get_devices_per_advisory(dnac):
    """
    This function will retrieve the advisories data and devices data as necessary
    :param dnac: Cisco DNAC SDK api
    :return: simplified advisories and devices response
    """
    advisories_list = dnac.security_advisories.get_advisories_list()
    responses = []
    devices_retrieved = {}
    if advisories_list and advisories_list.response:
        for advisories_item in advisories_list.response:
            response = {}
            response['AdvisoryID'] = advisories_item.get('advisoryId') or ''
            response['AdvisoryDeviceCount'] = advisories_item.get('deviceCount') or 0
            # response['AdvisoryCves'] = advisories_item.get('cves') or []
            response['AdvisoryCvesStr'] = ', '.join(advisories_item.get('cves')) or ''
            response['AdvisoryPublicationUrl'] = advisories_item.get('publicationUrl') or ''
            response['AdvisorySir'] = advisories_item.get('sir') or ''
            response['AdvisoryDetectionType'] = advisories_item.get('detectionType') or ''
            response['AdvisoryDefaultDetectionType'] = advisories_item.get('defaultDetectionType') or ''
            if response['AdvisoryID']:
                advisory_device = dnac.security_advisories.get_devices_per_advisory(response['AdvisoryID'])
                if advisory_device and advisory_device.response:
                    for device_id in advisory_device.response:
                        # Manage device info ...
                        device_info = {}
                        # ... if already present, reuse
                        if devices_retrieved.get(device_id):
                            device_info = dict(devices_retrieved[device_id])
                        else:  # ... if not retrieve and save it
                            device_info = dnac.devices.get_device_by_id(id=device_id)
                            devices_retrieved[device_id] = device_info
                        if isinstance(device_info, dict) and device_info.get('response'):
                            response_device = dict(response)
                            response_device.update(get_important_device_values(device_info['response']))
                            response_device.update({'Summary': 'False'})
                            responses.append(response_device)
            else:
                responses.append(response)
    return responses

def main():
    # it uses DNA Center URL, username and password, with the DNA Center API version specified
    dnac = connection()

    # get the security advisories details and devices data as necessary
    overall_security_advisories = get_devices_per_advisory(dnac)
    overall_security_advisories.extend(get_advisories_summary(dnac))
    print(json.dumps(overall_security_advisories))  # save the data to Splunk App index


if __name__ == '__main__':
    main()
