
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


def get_epoch_current_time():
    """
    This function will return the epoch time for the {timestamp}
    :return: epoch time including msec
    """
    epoch = time.time() * 1000
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
    # get the overall client health
    overall_client_health = get_client_health(dnac)
    # simplify gathered information
    response = filter_health_data(overall_client_health)

    for item in response:
        key = "{0}_{1}_{2}_{3}".format(
            opt_cisco_dna_center_host,
            item.get("siteId") or "N/A",
            item.get("clientType") or "N/A",
            item.get("scoreType") or "N/A",
        )
        state = helper.get_check_point(key)
        item["cisco_dnac_host"] = opt_cisco_dna_center_host
        if state is None:
            helper.save_check_point(key, item)
            r_json.append(item)
        elif is_different(helper, state, item):
            helper.save_check_point(key, item)
            r_json.append(item)
        # helper.delete_check_point(key)

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
