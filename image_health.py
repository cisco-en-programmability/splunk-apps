#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image health script.

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

from dnacentersdk import api


def read_config_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config

def get_device_image_details(dnac, device_id):
    """
    This function will retrieve the specific device image details using a custom method
    :param dnac: Cisco DNAC SDK api
    :param device_id: device id
    :return: device image response
    """
    def get_image_function(device_id):
        return dnac.custom_caller.call_api(
            'GET',
            '/api/v2/device-image/device',
            params={
                'id': device_id
            })
    try:
        device_image_details = get_image_function(device_id)
        if device_image_details and device_image_details.response:
            if len(device_image_details.response) > 0:
                return device_image_details.response[0]
        return None
    except:
        return None

def get_important_image_details(details):
    """
    This function will simplify the image details for Splunk searches
    :param details: image details
    :return: simplified image response
    """
    response = {}
    if details:
        response['DeviceImageUpgradeStatus'] = details.get('deviceImageUpgradeStatus') or ''
        response['UpgradeStatus'] = details.get('upgradeStatus') or ''
        response['DeviceInstalledInfoImageUuid'] = ''
        response['DeviceInstalledInfoName'] = ''
        response['DeviceInstalledInfoType'] = ''
        response['DeviceInstalledInfoVersion'] = ''
        response['DeviceInstalledInfoDisplayVersion'] = ''
        response['DeviceInstalledInfoFamily'] = ''
        response['DeviceInstalledInfoGolden'] = 'False'
        response['DeviceInstalledInfoSubpackageType'] = ''
        response['HasTargetImageInfo'] = 'False'
        response['ReadinessCheckStatusStatus'] = ''
        response['ReadinessCheckStatusIsReadyForUpgrade'] = 'False'
        if details.get('deviceInstalledInfo') and isinstance(details['deviceInstalledInfo'], list):
            if len(details['deviceInstalledInfo']) > 0:
                response['DeviceInstalledInfoImageUuid'] = details['deviceInstalledInfo'][0].get('imageUuid') or ''
                response['DeviceInstalledInfoName'] = details['deviceInstalledInfo'][0].get('name') or ''
                response['DeviceInstalledInfoType'] = details['deviceInstalledInfo'][0].get('type') or ''
                response['DeviceInstalledInfoVersion'] = details['deviceInstalledInfo'][0].get('version') or ''
                response['DeviceInstalledInfoDisplayVersion'] = details['deviceInstalledInfo'][0].get('displayVersion') or ''
                response['DeviceInstalledInfoFamily'] = details['deviceInstalledInfo'][0].get('family') or ''
                response['DeviceInstalledInfoGolden'] = str(details['deviceInstalledInfo'][0].get('golden')) or 'False'
                response['DeviceInstalledInfoSubpackageType'] = details['deviceInstalledInfo'][0].get('subpackageType') or ''
        if details.get('targetImageInfo') and isinstance(details['targetImageInfo'], list):
            response['HasTargetImageInfo'] = 'True'
            response['TargetImageInfo'] = details['targetImageInfo']
        if details.get('readinessCheckStatus') and isinstance(details['readinessCheckStatus'], dict):
            response['ReadinessCheckStatusStatus'] = details['readinessCheckStatus'].get('status')
            response['ReadinessCheckStatusIsReadyForUpgrade'] = str(details['readinessCheckStatus'].get('isReadyForUpgrade'))
    return response

def get_device_image_stack_details(dnac, device_id):
    """
    This function will retrieve the specific device image stack details
    :param dnac: Cisco DNAC SDK api
    :param device_id: device id
    :return: device image stack response
    """
    try:
        stack_details = dnac.devices.get_stack_details_for_device(device_id)
        if stack_details and stack_details.response:
            return stack_details.response
        return None
    except:
        return None

def get_devices(dnac):
    """
    This function will retrieve all the devices
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
    This function will simplify the device information for Splunk searches
    :param device_item: device information
    :return: simplified device response
    """
    response = {}
    response['DeviceID'] = device_item.get('id') or ''
    response['DeviceName'] = device_item.get('hostname') or 'NA'
    response['DeviceIpAddress'] = device_item.get('managementIpAddress') or device_item.get('ipAddress') or ''
    response['DeviceFamily'] = device_item.get('family') or ''
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
    return response

def get_important_stack_details(details):
    """
    This function will simplify the image stack details for Splunk searches
    :param details: image stack details
    :return: simplified image stack response
    """
    response = {'HasStack': 'False'}
    response['SwitchInfoAmount'] = 0
    response['StackSwitchInfoSoftwareImage'] = 'N/A'
    response['StackSwitchInfoRole'] = ''
    response['StackSwitchInfoState'] = ''
    response['StackSwitchInfoIsReady'] = 'False'
    response['SwitchInfo'] = []
    response['StackPortInfoAmount'] = 0
    response['StackPortInfo'] = []
    response['StackSvlSwitchInfoAmount'] = 0
    response['StackSvlSwitchInfo'] = []
    if details:
        if details.get('stackSwitchInfo'):
            response['HasStack'] = 'True'
            response['SwitchInfoAmount'] = len(details['stackSwitchInfo']) if isinstance(details['stackSwitchInfo'], list) else 0
            response['SwitchInfo'] = details['stackSwitchInfo']
            if len(details.get('stackSwitchInfo')) > 0:
                response['StackSwitchInfoSoftwareImage'] = details['stackSwitchInfo'][0].get('softwareImage') or 'N/A'
                response['StackSwitchInfoRole'] = details['stackSwitchInfo'][0].get('role') or ''
                response['StackSwitchInfoState'] = details['stackSwitchInfo'][0].get('state') or ''
                response['StackSwitchInfoIsReady'] = str(details['stackSwitchInfo'][0].get('state') == "READY")
        if details.get('stackPortInfo'):
            response['HasStack'] = 'True'
            response['StackPortInfoAmount'] = len(details['stackPortInfo']) if isinstance(details['stackPortInfo'], list) else 0
            response['StackPortInfo'] = details['stackPortInfo']
        if details.get('svlSwitchInfo'):
            response['HasStack'] = 'True'
            response['StackSvlSwitchInfoAmount'] = len(details['svlSwitchInfo']) if isinstance(details['svlSwitchInfo'], list) else 0
            response['StackSvlSwitchInfo'] = details['svlSwitchInfo']
    return response

def filter_data_as_images_2(dnac, images_items, devices_items):
    """
    This function will filter data to get the overall image health data.
    This function uses a private/custom API.
    :param dnac: Cisco DNAC SDK api
    :param images_items: images
    :param devices_items: devices
    :return: image health summary response
    """
    summary_response = []
    image_dict_summary = {}
    image_dict = {}

    for image_item in images_items:
        image_key = image_item['ImageName'].lower()
        image_dict_summary[image_key] = dict(image_item)
        image_dict_summary[image_key]['ImageDevicesAmount'] = 0
        image_dict_summary[image_key]['ImageSummary'] = 'True'
        image_dict[image_key] = dict(image_item)
        image_dict[image_key]['ImageDevicesAmount'] = 0
        image_dict[image_key]['ImageSummary'] = 'False'

    for device_item in devices_items:
        stack_detail = get_important_image_details(get_device_image_details(dnac, device_item.get('id')))
        stack_detail_key = 'DeviceInstalledInfoName'

        device_detail = get_important_device_values(device_item)

        if stack_detail.get(stack_detail_key) != "":
            software_image = stack_detail[stack_detail_key].lower()
            if image_dict_summary.get(software_image):
                image_dict_summary[software_image]['ImagePresent'] = 'False'
                image_dict_summary[software_image]['ImageDevicesAmount'] += 1
                image_dict[software_image]['ImageDevicesAmount'] = 1
                image_dict[software_image].update(device_detail)
                image_dict[software_image].update(stack_detail)
                summary_response.append(dict(image_dict[software_image]))
            else:
                image_key_2 = stack_detail[stack_detail_key].lower()
                if image_dict_summary.get(image_key_2) is None:
                    image_dict_summary[image_key_2] = {'ImageDevicesAmount': 0, 'ImageSummary': 'True', 'ImagePresent': 'False'}
                if image_dict_summary.get(image_key_2):
                    image_dict_summary[image_key_2]['ImageDevicesAmount'] += 1
                    image_dict_summary[image_key_2]['ImageName'] = 'N/A'
                    image_dict_summary[image_key_2]['ImageImageName'] = 'N/A'
                    image_dict_summary[image_key_2]['ImageImageUuid'] = ''
                    image_dict_summary[image_key_2]['ImageFamily'] = ''
                    image_dict_summary[image_key_2]['ImageVersion'] = ''
                    image_dict_summary[image_key_2]['ImageDisplayVersion'] = ''
                    image_dict_summary[image_key_2]['ImageSimpleName'] = image_key_2

                    image_dict[image_key_2] = dict(image_dict_summary[image_key_2])
                    image_dict[image_key_2]['ImageSummary'] = 'False'
                    image_dict[image_key_2]['ImageDevicesAmount'] = 1
                    image_dict[image_key_2].update(device_detail)
                    image_dict[image_key_2].update(stack_detail)
                    summary_response.append(dict(image_dict[image_key_2]))
    summary_response.extend(list(image_dict_summary.values()))
    return summary_response


def filter_data_as_images_1(dnac, images_items, devices_items):
    """
    This function will filter data to get the overall image health data.
    :param dnac: Cisco DNAC SDK api
    :param images_items: images
    :param devices_items: devices
    :return: image health summary response
    """
    summary_response = []
    image_dict_summary = {}
    image_dict = {}

    for image_item in images_items:
        image_key = image_item['ImageSimpleName'].lower()
        image_dict_summary[image_key] = dict(image_item)
        image_dict_summary[image_key]['ImageDevicesAmount'] = 0
        image_dict_summary[image_key]['ImageSummary'] = 'True'
        image_dict[image_key] = dict(image_item)
        image_dict[image_key]['ImageDevicesAmount'] = 0
        image_dict[image_key]['ImageSummary'] = 'False'

    for device_item in devices_items:
        stack_detail = get_important_stack_details(get_device_image_stack_details(dnac, device_item.get('id')))
        stack_detail_key = 'StackSwitchInfoSoftwareImage'

        device_detail = get_important_device_values(device_item)

        if stack_detail.get(stack_detail_key) != "N/A":
            software_image = stack_detail[stack_detail_key].lower()
            if image_dict_summary.get(software_image):
                image_dict_summary[software_image]['ImageDevicesAmount'] += 1
                image_dict[software_image]['ImageDevicesAmount'] = 1
                image_dict[software_image].update(device_detail)
                image_dict[software_image].update(stack_detail)
                summary_response.append(dict(image_dict[software_image]))
        else:
            image_key_2 = stack_detail[stack_detail_key].lower()
            if image_dict_summary.get(image_key_2) is None:
                image_dict_summary[image_key_2] = {'ImageDevicesAmount': 0, 'ImageSummary': 'True'}
            if image_dict_summary.get(image_key_2):
                image_dict_summary[image_key_2]['ImageDevicesAmount'] += 1
                image_dict_summary[image_key_2]['ImageName'] = 'N/A'
                image_dict_summary[image_key_2]['ImageImageName'] = 'N/A'
                image_dict_summary[image_key_2]['ImageImageUuid'] = ''
                image_dict_summary[image_key_2]['ImageFamily'] = ''
                image_dict_summary[image_key_2]['ImageVersion'] = ''
                image_dict_summary[image_key_2]['ImageDisplayVersion'] = ''
                image_dict_summary[image_key_2]['ImageSimpleName'] = image_key_2

                image_dict[image_key_2] = dict(image_dict_summary[image_key_2])
                image_dict[image_key_2]['ImageSummary'] = 'False'
                image_dict[image_key_2]['ImageDevicesAmount'] = 1
                image_dict[image_key_2].update(device_detail)
                image_dict[image_key_2].update(stack_detail)
                summary_response.append(dict(image_dict[image_key_2]))
    summary_response.extend(list(image_dict_summary.values()))
    return summary_response


def filter_data_as_images(dnac, images_items, devices_items):
    """
    This function will call another function that filters data to get the overall image health data.
    :param dnac: Cisco DNAC SDK api
    :param images_items: images
    :param devices_items: devices
    :return: image health summary response
    """
    return filter_data_as_images_1(dnac, images_items, devices_items)

def simplify_name(name, display_version):
    """
    This function trims from the image name, removing the display_version and other information, to use the new image name as an index.
    :param name: image name
    :param display_version: image display version
    :return: simplified image name
    """
    if name:
        if display_version:
            new_name = name.split(".{0}".format(display_version))[0]
            return new_name
        return name
    else:
        return ""

def get_images(dnac):
    """
    This function will retrieve the images found in SWIM
    :param dnac: Cisco DNAC SDK api
    :return: images response
    """
    responses = []
    images_response_fn = None
    images_response = None
    # Select function
    if hasattr(dnac, 'software_image_management_swim'):
        images_response_fn = dnac.software_image_management_swim.get_software_image_details
    elif hasattr(dnac, 'swim'):
        images_response_fn = dnac.swim.get_software_image_details
    # If not found return fast (fail silently)
    if images_response_fn is None:
        return responses

    limit = 20
    offset = 1
    do_request_next = True
    while do_request_next:
        try:
            images_response = images_response_fn(limit=limit, offset=offset)
            if images_response and images_response.response:
                for image_response in images_response.response:
                    response = {}
                    response['ImageName'] = image_response.get('name')
                    response['ImageImageName'] = image_response.get('imageName')
                    response['ImageImageUuid'] = image_response.get('imageUuid')
                    response['ImageFamily'] = image_response.get('family')
                    response['ImageVersion'] = image_response.get('version')
                    response['ImageDisplayVersion'] = image_response.get('displayVersion')
                    response['ImageSimpleName'] = simplify_name(image_response.get('name'), image_response.get('displayVersion'))
                    responses.append(response)
                if len(images_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return responses

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

    # get the devices
    devices_items = get_devices(dnac)
    # get the images
    images_items = get_images(dnac)
    # merge and simplify gathered information
    overall_result = filter_data_as_images(dnac, images_items, devices_items)
    print(json.dumps(overall_result))  # save the image health to Splunk App index


if __name__ == '__main__':
    main()
