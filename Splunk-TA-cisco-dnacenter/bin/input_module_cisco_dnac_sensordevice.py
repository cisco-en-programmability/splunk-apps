
# encoding = utf-8

import os
import json
import sys
import time
import datetime

import cisco_dnac_api as api

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''


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
            if sensor_item_new.get("sshConfig"):
                sensor_item_new["sshState"] = sensor_item_new["sshConfig"].get(
                    "sshState"
                )
                sensor_item_new["sshUserName"] = sensor_item_new["sshConfig"].get(
                    "sshUserName"
                )
                sensor_item_new["sshPassword"] = sensor_item_new["sshConfig"].get(
                    "sshPassword"
                )
                sensor_item_new["enablePassword"] = sensor_item_new["sshConfig"].get(
                    "enablePassword"
                )
            sensor_item_new.pop("sshConfig", None)
            if sensor_item_new.get("isLEDEnabled") is not None:
                sensor_item_new["isLEDEnabled"] = str(sensor_item_new["isLEDEnabled"])
            responses.append(sensor_item_new)
    return responses


def is_different(helper, state, item):
    if not isinstance(state, dict):
        helper.log_debug("is_different. The state is not a dictionary.")
        return True
    if not isinstance(item, dict):
        helper.log_debug("is_different. The item is not a dictionary.")
        return True
    keys = set(state.keys())
    keys = keys.union(set(item.keys()))
    properties = list(keys)
    for property_ in properties:
        if state.get(property_) != item.get(property_):
            helper.log_debug(
                "is_different. The state and item have different values for property '{0}', values are {1} and {2}.".format(
                    property_,
                    state.get(property_),
                    item.get(property_),
                )
            )
            return True
    return False


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    cisco_dna_center_host = definition.parameters.get("cisco_dna_center_host", None)
    cisco_dna_center_account = definition.parameters.get(
        "cisco_dna_center_account", None
    )
    # review: check cisco_dna_center_host
    if not isinstance(cisco_dna_center_host, str):
        raise TypeError("URL must be string")
    if not cisco_dna_center_host.startswith("https"):
        raise ValueError("URL must be HTTPS")
    pass


def collect_events(helper, ew):
    opt_cisco_dna_center_host = helper.get_arg("cisco_dna_center_host")
    opt_cisco_dna_center_account = helper.get_arg("cisco_dna_center_account")

    account_username = opt_cisco_dna_center_account.get("username", None)
    account_password = opt_cisco_dna_center_account.get("password", None)
    account_name = opt_cisco_dna_center_account.get("name", None)
    current_version = "2.2.3.3"
    current_verify = False
    current_debug = False

    dnac = api.DNACenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_dna_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug,
        helper=helper,
    )

    r_json = []

    # get the sensor details
    overall_sensors = get_sensors(dnac)

    for item in overall_sensors:
        item["cisco_dnac_host"] = opt_cisco_dna_center_host
        r_json.append(item)

    # To create a splunk event
    event = helper.new_event(
        json.dumps(r_json),
        time=None,
        host=None,
        index=None,
        source=None,
        sourcetype=None,
        done=True,
        unbroken=True,
    )
    ew.write_event(event)
