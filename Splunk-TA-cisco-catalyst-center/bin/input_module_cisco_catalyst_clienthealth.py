
# encoding = utf-8

import os
import json
import sys
import time
import datetime
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


def get_epoch_current_time():
    """
    This function will return the epoch time for the {timestamp}
    :return: epoch time including msec
    """
    epoch = time.time() * 1000
    return "{0}".format(int(epoch))


def get_client_health(catalyst):
    """
    This function will retrieve the client health at the time the function is called
    :param catalyst: Cisco Catalyst SDK api
    :return: client health response
    """
    epoch_time = get_epoch_current_time()
    health_response = catalyst.clients.get_overall_client_health(timestamp=epoch_time)
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
        for score_item in response_item["scoreDetail"]:
            health_item = {}
            # Set default data
            health_item["siteId"] = response_item["siteId"]

            health_item["clientType"] = ""
            if score_item.scoreCategory:
                health_item["clientType"] = score_item.scoreCategory.value

            health_item["clientCount"] = score_item.clientCount
            health_item["clientUniqueCount"] = score_item.clientUniqueCount
            health_item["scoreValue"] = score_item.scoreValue
            health_item["starttime"] = score_item.starttime
            health_item["endtime"] = score_item.endtime
            health_item["scoreType"] = "ALL"

            # TODO: check value
            # If it is ALL skip, nothing more to do
            if score_item.scoreCategory and score_item.scoreCategory.value == "ALL":
                health_distribution.append(health_item)
                continue

            if score_item.scoreList:
                # Set artificial scoreType for general client
                health_distribution.append(health_item)
                for score_type in score_item.scoreList:
                    health_item_new = dict(health_item)

                    health_item_new["scoreType"] = ""
                    if score_type.scoreCategory:
                        health_item_new["scoreType"] = score_type.scoreCategory.value

                    health_item_new["clientCount"] = score_type.clientCount
                    health_item_new["clientUniqueCount"] = score_type.clientUniqueCount
                    health_item_new["scoreValue"] = score_type.scoreValue
                    health_item_new["starttime"] = score_type.starttime
                    health_item_new["endtime"] = score_type.endtime
                    health_distribution.append(health_item_new)
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
    current_version = "2.2.3.3"
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
    # get the overall client health
    overall_client_health = get_client_health(catalyst)
    # simplify gathered information
    response = filter_health_data(overall_client_health)

    for item in response:
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
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
