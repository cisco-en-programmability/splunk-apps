#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Network health script.

Compatibility with Cisco DNA Center: v1.2.10 - v2.3.2.x.
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
import time

import api


def read_config_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config

def get_epoch_current_time():
    """
    This function will return the epoch time for the {timestamp}
    :return: epoch time including msec
    """
    epoch = time.time()*1000
    return "{0}".format(int(epoch))

def get_overall_network_health(dnac):
    """
    This function will retrieve the network health
    :param dnac: Cisco DNAC SDK api
    :return: network health response
    """
    epoch_time = get_epoch_current_time()
    network_health_fn = None
    # Select function
    if hasattr(dnac, 'topology') and hasattr(dnac.topology, 'get_overall_network_health'):
        network_health_fn = dnac.topology.get_overall_network_health
    elif hasattr(dnac, 'networks') and hasattr(dnac.networks, 'get_overall_network_health'):
        network_health_fn = dnac.networks.get_overall_network_health
    # If not function was found return None
    if network_health_fn is None:
        return None

    network_health_response = network_health_fn(epoch_time)
    return network_health_response

def filter_health_data(network_health_response):
    """
    This function will filter data to get the overall network data.
    :param network_health_response: network health response
    :return: health summary response
    """
    health_distribution = []
    # Capture possible None
    if network_health_response is None:
        return health_distribution

    if network_health_response.healthDistirubution:
        health_distribution = list(network_health_response.healthDistirubution)

    if network_health_response.response:
        if len(network_health_response.response) > 0:
            if network_health_response.response[0]:
                key_list = ["healthScore", "totalCount", "goodCount", "noHealthCount", "fairCount", "badCount"]
                overall_health = {"category": "All"}
                tmp = dict(network_health_response.response[0])
                for i in key_list:
                    if tmp[i]:
                        overall_health[i] = tmp[i]
                health_distribution.append(overall_health)
    return health_distribution

def connection():
    """
    Create a DNACenterAPI connection object
    """
    config = read_config_file()
    # Quick assertion to verify equal or above min version
    min_dnac_version = "1.2.10"
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

    # get the overall network health
    overall_network_health = get_overall_network_health(dnac)
    # simplify gathered information
    network_health_summary = filter_health_data(overall_network_health)
    print(json.dumps(network_health_summary))  # save the network health to Splunk App index


if __name__ == '__main__':
    main()
