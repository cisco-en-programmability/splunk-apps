#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Issues script.

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
from datetime import datetime, timedelta

import api


def get_epoch_current_previous_times(interval_seconds):
    """
    This function will return the epoch time for the {timestamp} and a previous epoch time
    :return: epoch time (now) including msec, epoch time (previous) including msec
    """
    now = datetime.now()
    rounded = now - timedelta(minutes=now.minute,
                              seconds=now.second % interval_seconds + interval_seconds if interval_seconds > 0 else now.second,
                              microseconds=now.microsecond)
    return (int(now.timestamp() * 1000), int(rounded.timestamp() * 1000))

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

def simplify_issue(issue_responses):
    """
    This function will simplify the site data for Splunk searches
    :param issue_resp: Cisco DNAC SDK api
    :return: new site response
    """
    simplified_issue = {}
    if len(issue_responses) > 0 and isinstance(issue_responses[0], dict):
        issue_resp = issue_responses[0]
        simplified_issue['IssueID'] = issue_resp.get('issueId')
        simplified_issue['IssueSpecificCategory'] = issue_resp.get('issueCategory')
        simplified_issue['IssueSpecificSource'] = issue_resp.get('issueSource')
        simplified_issue['IssueSpecificName'] = issue_resp.get('issueName')
        simplified_issue['IssueSpecificDescription'] = issue_resp.get('issueDescription')
        simplified_issue['IssueSpecificEntity'] = issue_resp.get('issueEntity')
        simplified_issue['IssueSpecificEntityValue'] = issue_resp.get('issueEntityValue')
        simplified_issue['IssueSpecificSeverity'] = issue_resp.get('issueSeverity')
        simplified_issue['IssueSpecificPriority'] = issue_resp.get('issuePriority')
        simplified_issue['IssueSpecificSummary'] = issue_resp.get('issueSummary')
        simplified_issue['IssueSpecificTimestamp'] = issue_resp.get('issueTimestamp')
        return simplified_issue
    else:
        return {}

def simplify_site(site_resp):
    """
    This function will simplify the site data for Splunk searches
    :param site_resp: Cisco DNAC SDK api
    :return: new site response
    """
    simplified_site = {}
    if site_resp:
        simplified_site['SiteName'] = site_resp.get('name')
        simplified_site['SiteNameHierarchy'] = site_resp.get('siteNameHierarchy')
        simplified_site['SiteType'] = 'area'
        if site_resp.get('additionalInfo'):
            if len(site_resp['additionalInfo']) > 0:
                for additional_info in site_resp['additionalInfo']:
                    if isinstance(additional_info, dict) and additional_info.get('attributes'):
                        if isinstance(additional_info['attributes'], dict) and additional_info['attributes'].get('type'):
                            simplified_site['SiteType'] = additional_info['attributes'].get('type')
        return simplified_site
    else:
        return {}

def clean_dict_of_empty_strings(**kwargs):
    dict_ = {**kwargs}
    dict_new = {}
    for key,value in dict_.items():
        if isinstance(value, str) and value != "":
            dict_new[key] = value
    return dict_new

def get_issues(dnac, interval_seconds, **kwargs):
    """
    This function will retrieve the issue details and devices&site data as necessary
    :param dnac: Cisco DNAC SDK api
    :param interval_seconds: interval in seconds
    :return: simplified issues and device&site response
    """
    end_time, start_time = get_epoch_current_previous_times(interval_seconds)
    responses = []
    issues_response = dnac.issues.issues(start_time=start_time, end_time=end_time, **clean_dict_of_empty_strings(**kwargs))
    issue_info = {}
    site_info = {}
    device_info = {}
    if issues_response and issues_response.response:
        for issue_item in issues_response.response:
            response = {}
            issue_id = issue_item.get('issueId') or ''
            site_id = issue_item.get('siteId') or ''
            device_id = issue_item.get('deviceId') or ''
            if issue_id:
                if issue_info.get(issue_id):
                    response.update(issue_info[issue_id])
                else:
                    tmp_issue = dnac.issues.get_issue_enrichment_details(headers=dict(entity_type="issue_id", entity_value=issue_id))
                    if tmp_issue and isinstance(tmp_issue.get('issueDetails'), dict) and isinstance(tmp_issue['issueDetails'].get('issue'), list):
                        issue_info[issue_id] = simplify_issue(tmp_issue['issueDetails']['issue'])
                        issue_info[issue_id].update({
                            'IssueName': issue_item.get('name') or '',
                            'IssueDeviceRole': issue_item.get('deviceRole') or '',
                            'IssueAiDriven': issue_item.get('aiDriven') or '',
                            'IssueClientMac': issue_item.get('clientMac') or '',
                            'IssueCount': issue_item.get('issue_occurence_count') or '',
                            'IssueStatus': issue_item.get('status') or '',
                            'IssuePriority': issue_item.get('priority') or '',
                            'IssueCategory': issue_item.get('category') or '',
                        })
                        response.update(issue_info[issue_id])
            if site_id:
                if site_info.get(site_id):
                    response.update(site_info[site_id])
                else:
                    tmp_site = dnac.sites.get_site(site_id=site_id)
                    if tmp_site and tmp_site.response:
                        site_info[site_id] = simplify_site(tmp_site['response'])
                        response.update(site_info[site_id])
            if device_id:
                if device_info.get(device_id):
                    response.update(device_info[device_id])
                else:
                    tmp_device = dnac.devices.get_device_by_id(id=device_id)
                    if tmp_device and tmp_device.response:
                        device_info[device_id] = get_important_device_values(tmp_device['response'])
                        response.update(device_info[device_id])
            responses.append(response)
    return responses

def main():
    # it uses DNA Center URL, username and password, with the DNA Center API version specified
    dnac = connection()
    # If empty searches and records all priority values: P1, P2, P3, or P4
    priority = ""
    # If empty searches and records all ai_driven values: Yes or No
    ai_driven = ""
    # If empty searches and records all issue_status values: ACTIVE, IGNORED, RESOLVED
    issue_status = ""
    # REVIEW: It is recommended that this time matches the Splunk's data input interval
    interval_seconds = 300
    # get the issue details and devices&site data as necessary
    overall_issues = []
    overall_issues = get_issues(dnac, interval_seconds=interval_seconds, priority=priority, ai_driven=ai_driven, issue_status=issue_status)
    print(json.dumps(overall_issues))  # save the data to Splunk App index


if __name__ == '__main__':
    main()
