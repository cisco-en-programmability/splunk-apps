#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sensors script.

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

def get_sensors(dnac):
    """
    This function will retrieve the sensor details
    :param dnac: Cisco DNAC SDK api
    :return: sensor details
    """
    responses = []
    sensor_response = dnac.sensors.sensors()
    if sensor_response and sensor_response.response:
        for sensor_item in sensor_response.response:
            sensor_item_new = dict(sensor_item)
            if sensor_item_new.get('sshConfig'):
                sensor_item_new['sshState'] = sensor_item_new['sshConfig'].get('sshState')
                sensor_item_new['sshUserName'] = sensor_item_new['sshConfig'].get('sshUserName')
                sensor_item_new['sshPassword'] = sensor_item_new['sshConfig'].get('sshPassword')
                sensor_item_new['enablePassword'] = sensor_item_new['sshConfig'].get('enablePassword')
            sensor_item_new.pop("sshConfig", None)
            if sensor_item_new.get('isLEDEnabled') is not None:
                sensor_item_new['isLEDEnabled'] = str(sensor_item_new['isLEDEnabled'])
            responses.append(sensor_item_new)
    return responses

def main():
    # it uses DNA Center URL, username and password, with the DNA Center API version specified
    dnac = connection()

    # get the sensor details
    overall_sensors = get_sensors(dnac)
    print(json.dumps(overall_sensors))  # save the data to Splunk App index

if __name__ == '__main__':
    main()
