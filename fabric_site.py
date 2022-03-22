#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fabric site script.

Compatibility with Cisco DNA Center: v1.3.3 - v2.3.2.x.
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

def simplify_sites(dnac, sites_response, seen):
    """
    This function will filter and simplify the sites data for Splunk searches
    :param dnac: Cisco DNAC SDK api
    :param sites_response: Cisco DNAC SDK api
    :param seen: set to filter previous SiteNameHierarchy values
    :return: new sites response
    """
    fabric_sites_response = []
    for site_response in sites_response:
        site = simplify_site(site_response)
        site_key = site['SiteNameHierarchy']
        # if it was seen before, skip it
        if site_key in seen:
            continue
        # if not added
        seen.add(site_key)
        fabric_site = get_simplified_fabric_site(dnac, site_key)
        fabric_site_new = dict(site)
        if fabric_site:
            fabric_site_new.update({'HasFabric': 'True'})
        else:
            fabric_site_new.update({'HasFabric': 'False'})
        fabric_site_new.update(fabric_site)
        fabric_sites_response.append(fabric_site_new)
    return fabric_sites_response

def get_simplified_sites(dnac):
    """
    This function will retrieve the sites and simplify them
    :param dnac: Cisco DNAC SDK api
    :return: sites response
    """
    limit = 20
    offset = 1
    sites_responses = []
    do_request_next = True
    seen = set()
    while do_request_next:
        try:
            sites_response = dnac.sites.get_site(limit=str(limit), offset=str(offset))
            if sites_response and sites_response.response:
                sites_responses.extend(simplify_sites(dnac, sites_response.response, seen))
                if len(sites_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return sites_responses

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
    min_dnac_version = "1.3.3"
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
    # get the sites and fabric sites associated with them
    simplified_sites = get_simplified_sites(dnac)
    print(json.dumps(simplified_sites))  # save the data to Splunk App index


if __name__ == '__main__':
    main()
