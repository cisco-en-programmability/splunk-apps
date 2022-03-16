#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Client health script.

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

from dnacentersdk import api


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

def get_client_health(dnac):
    """
    This function will retrieve the client health at the time the function is called
    :param dnac: Cisco DNAC SDK api
    :return: client health response
    """
    epoch_time = get_epoch_current_time()
    health_response = dnac.clients.get_overall_client_health(timestamp=epoch_time)
    return health_response

def filter_health_data(network_health_response):
    """
    This function will filter data to get the overall client data.
    :param network_health_response: network health data
    :return: health distribution summary response
    """
    health_distribution = []

    for response_item in network_health_response.response:
        # Set siteId
        for score_item in response_item['scoreDetail']:
            health_item = {}
            # Set default data
            health_item['siteId'] = response_item['siteId']
            health_item['clientType'] = score_item.scoreCategory.value
            health_item['clientCount'] = score_item.clientCount
            health_item['clientUniqueCount'] = score_item.clientUniqueCount
            health_item['scoreValue'] = score_item.scoreValue
            health_item['starttime'] = score_item.starttime
            health_item['endtime'] = score_item.endtime
            health_item['scoreType'] = "ALL"

            # If it is ALL skip, nothing more to do
            if score_item.scoreCategory.value == "ALL":
                health_distribution.append(health_item)
                continue

            if score_item.scoreList:
                # Set artificial scoreType for general client
                health_distribution.append(health_item)
                for score_type in score_item.scoreList:
                    health_item_new = dict(health_item)
                    health_item_new['scoreType'] = score_type.scoreCategory.value
                    health_item_new['clientCount'] = score_type.clientCount
                    health_item_new['clientUniqueCount'] = score_type.clientUniqueCount
                    health_item_new['scoreValue'] = score_type.scoreValue
                    health_item_new['starttime'] = score_type.starttime
                    health_item_new['endtime'] = score_type.endtime
                    health_distribution.append(health_item_new)
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

    # get the overall client health
    overall_client_health = get_client_health(dnac)
    # simplify gathered information
    response = filter_health_data(overall_client_health)
    print(json.dumps(response))  # save the client health to Splunk App index


if __name__ == '__main__':
    main()
