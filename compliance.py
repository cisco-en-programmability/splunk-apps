#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compliance script.

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


def connection():
    """
    Create a DNACenterAPI connection object
    """
    config = read_config_file()
    # Quick assertion to verify equal or above min version
    min_dnac_version = "2.2.2.3"
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

    # get the compliance details and devices data as necessary
    overall_compliance_details = get_compliance_and_device_details(dnac)
    print(json.dumps(overall_compliance_details))  # save the data to Splunk App index


if __name__ == '__main__':
    main()
