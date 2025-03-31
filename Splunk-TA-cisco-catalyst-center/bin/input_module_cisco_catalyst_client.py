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


## This feature is commented due to discrepancies between the Splunk and Cat Lab time zones.
# def get_epoch_current_previous_times(interval_seconds):
#     """
#     This function will return the epoch time for the {timestamp} and a previous epoch time
#     :return: epoch time (now) including msec, epoch time (previous) including msec
#     """
#     # REVIEW: It is recommended that this time matches the Splunk's data input interval
#     now = datetime.datetime.now()
#     rounded = now - datetime.timedelta(
#         seconds=now.second % interval_seconds + interval_seconds
#         if interval_seconds > 0
#         else now.second
#     )
#     now = now.replace(microsecond=0)
#     rounded = rounded.replace(microsecond=0)
#     return (int(now.timestamp() * 1000), int(rounded.timestamp() * 1000))


def get_client(catalyst, input_interval):
    """
    This function will retrieve the client details at the time the function is called
    :param catalyst: Cisco Catalyst SDK api
    :param input_interval: interval in seconds
    :return: client details response
    """
    # (epoch_current_time, epoch_previous_time) = get_epoch_current_previous_times(
    #     input_interval
    # )
    limit = 20
    offset = 1
    client_responses = []
    do_request_next = True
    while do_request_next:
        try:
            client_response = catalyst.clients.get_clients(
                limit=limit,
                offset=offset,
            )
            if client_response and client_response.response:
                client_responses.extend(client_response.response)
                if len(client_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset += limit
    return client_responses


def filter_client_data(client_response):
    """
    This function will filter data to get the overall client data.
    :param client_response: client data
    :return: client distribution summary response
    """
    client_distribution = []

    for response_item in client_response:
        client_item = {}
        client_item["ClientID"] = response_item.get("id") or ""
        client_item["ClientMACAddress"] = response_item.get("macAddress") or ""
        client_item["ClientType"] = response_item.get("type") or ""
        client_item["ClientName"] = response_item.get("name") or "N/A"
        client_item["ClientUserID"] = response_item.get("userId") or ""
        client_item["ClientUsername"] = response_item.get("username") or ""
        client_item["ClientIPv4Address"] = response_item.get("ipv4Address") or ""
        client_item["ClientOSType"] = response_item.get("osType") or "Unclassified"
        client_item["ClientDeviceType"] = response_item.get("deviceType") or "Unclassified"
        client_item["ClientSiteHierarchy"] = response_item.get("siteHierarchy") or ""
        client_item["ClientLastUpdatedTime"] = response_item.get("lastUpdatedTime") or 0
        client_item["ClientConnectionStatus"] = response_item.get("connectionStatus") or ""
        client_item["ClientTrafficTXBytes"] = response_item.get("traffic", {}).get("txBytes") or 0
        client_item["ClientTrafficRXBytes"] = response_item.get("traffic", {}).get("rxBytes") or 0
        client_item["ClientTrafficUsage"] = response_item.get("traffic", {}).get("usage") or 0
        client_item["ClientTrafficRXPackets"] = response_item.get("traffic", {}).get("rxPackets") or 0
        client_item["ClientTrafficTXPackets"] = response_item.get("traffic", {}).get("txPackets") or 0
        client_item["ClientTrafficRXRate"] = response_item.get("traffic", {}).get("rxRate") or 0
        client_item["ClientTrafficTXRate"] = response_item.get("traffic", {}).get("txRate") or 0
        client_item["ClientTrafficRXLinkErrorPercentage"] = response_item.get("traffic", {}).get("rxLinkErrorPercentage") or 0
        client_item["ClientTrafficTXLinkErrorPercentage"] = response_item.get("traffic", {}).get("txLinkErrorPercentage") or 0
        client_item["ClientTrafficRXRetries"] = response_item.get("traffic", {}).get("rxRetries") or 0
        client_item["ClientTrafficRXRetryPercentage"] = response_item.get("traffic", {}).get("rxRetryPercentage") or 0
        client_item["ClientTrafficTXDrops"] = response_item.get("traffic", {}).get("txDrops") or 0
        client_item["ClientTrafficTXDropPercentage"] = response_item.get("traffic", {}).get("txDropPercentage") or 0
        client_item["ClientTrafficDNSRequestCount"] = response_item.get("traffic", {}).get("dnsRequestCount") or 0
        client_item["ClientTrafficDNSResponseCount"] = response_item.get("traffic", {}).get("dnsResponseCount") or 0
        client_item["ClientConnectedNetworkDeviceID"] = response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceId") or ""
        client_item["ClientConnectedNetworkDeviceName"] = response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceName") or ""
        client_item["ClientConnectedNetworkDeviceManagementIP"] = response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceManagementIp") or ""
        client_item["ClientConnectedNetworkDeviceMAC"] = response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceMac") or ""
        client_item["ClientConnectedNetworkDeviceType"] = response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceType") or ""
        client_item["ClientConnectionVLANID"] = response_item.get("connection", {}).get("vlanId") or ""
        client_item["ClientConnectionSessionDuration"] = response_item.get("connection", {}).get("sessionDuration") or 0
        client_item["ClientConnectionVNID"] = response_item.get("connection", {}).get("vnId") or ""
        client_item["ClientConnectionSecurityGroupTag"] = response_item.get("connection", {}).get("securityGroupTag") or ""
        client_item["ClientConnectionLinkSpeed"] = response_item.get("connection", {}).get("linkSpeed") or 0
        client_item["ClientConnectionBand"] = response_item.get("connection", {}).get("band") or "Unclassified"
        client_item["ClientConnectionSSID"] = response_item.get("connection", {}).get("ssid") or ""
        client_item["ClientConnectionAuthType"] = response_item.get("connection", {}).get("authType") or ""
        client_item["ClientConnectionAPMAC"] = response_item.get("connection", {}).get("apMac") or ""
        client_item["ClientConnectionAPEthernetMAC"] = response_item.get("connection", {}).get("apEthernetMac") or ""
        client_item["ClientConnectionChannel"] = response_item.get("connection", {}).get("channel") or ""
        client_item["ClientConnectionChannelWidth"] = response_item.get("connection", {}).get("channelWidth") or ""
        client_item["ClientConnectionProtocol"] = response_item.get("connection", {}).get("protocol") or "Unclassified"
        client_item["ClientConnectionRSSI"] = response_item.get("connection", {}).get("rssi") or 0
        client_item["ClientConnectionSNR"] = response_item.get("connection", {}).get("snr") or 0
        client_item["ClientConnectionDataRate"] = response_item.get("connection", {}).get("dataRate") or 0
        client_distribution.append(client_item)
    return client_distribution


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
    
    # use defaul input_interval
    input_interval = 3600
    try:
        input_interval = int(helper.get_arg("interval"))
    except ValueError:
        input_interval = 3600
    if input_interval < 3600:
        input_interval = 3600

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
    # get the overall client
    overall_client = get_client(catalyst, input_interval)
    # simplify gathered information
    response = filter_client_data(overall_client)

    for index, item in enumerate(response):
        item["cisco_catalyst_host"] = opt_cisco_catalyst_center_host
        done_flag = (index == len(response) - 1)
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
