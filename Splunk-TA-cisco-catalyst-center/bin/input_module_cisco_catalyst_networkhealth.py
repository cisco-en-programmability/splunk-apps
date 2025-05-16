
# encoding = utf-8

import datetime
import json
import os
import sys
import time
import utils
import re

import cisco_catalyst_api as api

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


## timestamp
# def get_epoch_current_time():
#     """
#     This function will return the epoch time for the {timestamp} from 10 minutes ago.
#     :return: epoch time including msec
#     """
#     # Subtract 10 minutes (600 seconds) from current time.
#     epoch = (time.time() - 600) * 1000
#     return "{0}".format(int(epoch))


def get_overall_network_health(catalyst):
    """
    This function will retrieve the network health
    :param catalyst: Cisco Catalyst SDK api
    :return: network health response
    """
    network_health_fn = None
    # Select function
    if hasattr(catalyst, "topology") and hasattr(
        catalyst.topology, "get_overall_network_health"
    ):
        network_health_fn = catalyst.topology.get_overall_network_health
    elif hasattr(catalyst, "networks") and hasattr(
        catalyst.networks, "get_overall_network_health"
    ):
        network_health_fn = catalyst.networks.get_overall_network_health
    # If not function was found return None
    if network_health_fn is None:
        return None

    network_health_response = network_health_fn()
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
                key_list = [
                    "healthScore",
                    "totalCount",
                    "goodCount",
                    "noHealthCount",
                    "fairCount",
                    "badCount",
                ]
                overall_health = {"category": "All"}
                tmp = dict(network_health_response.response[0])
                for i in key_list:
                    if tmp[i]:
                        overall_health[i] = tmp[i]
                health_distribution.append(overall_health)
    return health_distribution


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    cisco_catalyst_center_host = definition.parameters.get("cisco_catalyst_center_host", None)
    cisco_catalyst_center_account = definition.parameters.get(
        "cisco_catalyst_center_account", None
    )
    # review: check cisco_catalyst_center_host
    if not isinstance(cisco_catalyst_center_host, str):
        raise TypeError("URL must be string")
    regex = re.compile(
        r'^(https:\/\/)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$|^(?:\d{1,3}\.){3}\d{1,3}$'
    )
    if not regex.match(cisco_catalyst_center_host):
        raise ValueError("URL does not match the required pattern")
    pass


def collect_events(helper, ew):
    opt_cisco_catalyst_center_host = helper.get_arg("cisco_catalyst_center_host")
    if opt_cisco_catalyst_center_host:
        opt_cisco_catalyst_center_host = opt_cisco_catalyst_center_host.strip()
        if not opt_cisco_catalyst_center_host.startswith("https://"):
            opt_cisco_catalyst_center_host = "https://" + opt_cisco_catalyst_center_host
    opt_cisco_catalyst_center_account = helper.get_arg("cisco_catalyst_center_account")

    account_username = opt_cisco_catalyst_center_account.get("username", None)
    account_password = opt_cisco_catalyst_center_account.get("password", None)
    account_name = opt_cisco_catalyst_center_account.get("name", None)
    current_version = "v2.3.7.6"
    session_key = helper.context_meta['session_key']
    current_verify = utils.get_sslconfig(session_key, helper)
    current_debug = False

    catalyst = api.CatalystCenterAPI(
        username=account_username,
        password=account_password,
        base_url=opt_cisco_catalyst_center_host,
        version=current_version,
        verify=current_verify,
        debug=current_debug,
        helper=helper,
    )

    r_json = []
    # epoch_time = get_epoch_current_time()
    # get the overall network health
    overall_network_health = get_overall_network_health(catalyst)
    # simplify gathered information
    network_health_summary = filter_health_data(overall_network_health)

    for index, item in enumerate(network_health_summary):
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
        done_flag = (index == len(network_health_summary) - 1)
        event = helper.new_event(
            json.dumps(item),
            time=None,
            host=None,
            index=None,
            source=None,
            sourcetype=None,
            done=done_flag,
            unbroken=False,
        )
        ew.write_event(event)
