# encoding = utf-8

import os
import json
import sys
import time
import datetime
import utils

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


def get_client(catalyst):
    """
    This function will retrieve the client details at the time the function is called
    :param catalyst: Cisco Catalyst SDK api
    :return: client details response
    """
    # epoch_time = get_epoch_current_time()
    client_response = catalyst.clients.get_client()
    return client_response


def filter_client_data(client_response):
    """
    This function will filter data to get the overall client data.
    :param client_response: client data
    :return: client distribution summary response
    """
    client_distribution = []

    for response_item in client_response.response:
        client_item = {
            "ClientID": response_item.get("id", ""),
            "ClientMACAddress": response_item.get("macAddress", ""),
            "ClientType": response_item.get("type", ""),
            "ClientName": response_item.get("name", ""),
            "ClientUserID": response_item.get("userId", ""),
            "ClientUsername": response_item.get("username", ""),
            "ClientIPv4Address": response_item.get("ipv4Address", ""),
            "ClientIPv6Addresses": response_item.get("ipv6Addresses", []),
            "ClientVendor": response_item.get("vendor", ""),
            "ClientOSType": response_item.get("osType", ""),
            "ClientOSVersion": response_item.get("osVersion", ""),
            "ClientFormFactor": response_item.get("formFactor", ""),
            "ClientSiteHierarchy": response_item.get("siteHierarchy", ""),
            "ClientSiteHierarchyID": response_item.get("siteHierarchyId", ""),
            "ClientSiteID": response_item.get("siteId", ""),
            "ClientLastUpdatedTime": response_item.get("lastUpdatedTime", 0),
            "ClientConnectionStatus": response_item.get("connectionStatus", ""),
            "ClientTracked": response_item.get("tracked", ""),
            "ClientIsPrivateMACAddress": response_item.get("isPrivateMacAddress", False),
            "ClientHealthOverallScore": response_item.get("health", {}).get("overallScore", 0),
            "ClientHealthOnboardingScore": response_item.get("health", {}).get("onboardingScore", 0),
            "ClientHealthConnectedScore": response_item.get("health", {}).get("connectedScore", 0),
            "ClientHealthLinkErrorPercentageThreshold": response_item.get("health", {}).get("linkErrorPercentageThreshold", 0),
            "ClientHealthIsLinkErrorIncluded": response_item.get("health", {}).get("isLinkErrorIncluded", False),
            "ClientHealthRSSIThreshold": response_item.get("health", {}).get("rssiThreshold", 0),
            "ClientHealthSNRThreshold": response_item.get("health", {}).get("snrThreshold", 0),
            "ClientHealthIsRSSIIncluded": response_item.get("health", {}).get("isRssiIncluded", False),
            "ClientHealthIsSNRIncluded": response_item.get("health", {}).get("isSnrIncluded", False),
            "ClientTrafficTXBytes": response_item.get("traffic", {}).get("txBytes", 0),
            "ClientTrafficRXBytes": response_item.get("traffic", {}).get("rxBytes", 0),
            "ClientTrafficUsage": response_item.get("traffic", {}).get("usage", 0),
            "ClientTrafficRXPackets": response_item.get("traffic", {}).get("rxPackets", 0),
            "ClientTrafficTXPackets": response_item.get("traffic", {}).get("txPackets", 0),
            "ClientTrafficRXRate": response_item.get("traffic", {}).get("rxRate", 0),
            "ClientTrafficTXRate": response_item.get("traffic", {}).get("txRate", 0),
            "ClientTrafficRXLinkErrorPercentage": response_item.get("traffic", {}).get("rxLinkErrorPercentage", 0),
            "ClientTrafficTXLinkErrorPercentage": response_item.get("traffic", {}).get("txLinkErrorPercentage", 0),
            "ClientTrafficRXRetries": response_item.get("traffic", {}).get("rxRetries", 0),
            "ClientTrafficRXRetryPercentage": response_item.get("traffic", {}).get("rxRetryPercentage", 0),
            "ClientTrafficTXDrops": response_item.get("traffic", {}).get("txDrops", 0),
            "ClientTrafficTXDropPercentage": response_item.get("traffic", {}).get("txDropPercentage", 0),
            "ClientTrafficDNSRequestCount": response_item.get("traffic", {}).get("dnsRequestCount", 0),
            "ClientTrafficDNSResponseCount": response_item.get("traffic", {}).get("dnsResponseCount", 0),
            "ClientConnectedNetworkDeviceID": response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceId", ""),
            "ClientConnectedNetworkDeviceName": response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceName", ""),
            "ClientConnectedNetworkDeviceManagementIP": response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceManagementIp", ""),
            "ClientConnectedNetworkDeviceMAC": response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceMac", ""),
            "ClientConnectedNetworkDeviceType": response_item.get("connectedNetworkDevice", {}).get("connectedNetworkDeviceType", ""),
            "ClientConnectedNetworkDeviceInterfaceName": response_item.get("connectedNetworkDevice", {}).get("interfaceName", ""),
            "ClientConnectedNetworkDeviceInterfaceSpeed": response_item.get("connectedNetworkDevice", {}).get("interfaceSpeed", 0),
            "ClientConnectedNetworkDeviceDuplexMode": response_item.get("connectedNetworkDevice", {}).get("duplexMode", ""),
            "ClientConnectionVLANID": response_item.get("connection", {}).get("vlanId", ""),
            "ClientConnectionSessionDuration": response_item.get("connection", {}).get("sessionDuration", 0),
            "ClientConnectionVNID": response_item.get("connection", {}).get("vnId", ""),
            "ClientConnectionL2VN": response_item.get("connection", {}).get("l2Vn", ""),
            "ClientConnectionL3VN": response_item.get("connection", {}).get("l3Vn", ""),
            "ClientConnectionSecurityGroupTag": response_item.get("connection", {}).get("securityGroupTag", ""),
            "ClientConnectionLinkSpeed": response_item.get("connection", {}).get("linkSpeed", 0),
            "ClientConnectionBridgeVMMode": response_item.get("connection", {}).get("bridgeVMMode", ""),
            "ClientConnectionBand": response_item.get("connection", {}).get("band", ""),
            "ClientConnectionSSID": response_item.get("connection", {}).get("ssid", ""),
            "ClientConnectionAuthType": response_item.get("connection", {}).get("authType", ""),
            "ClientConnectionWLCName": response_item.get("connection", {}).get("wlcName", ""),
            "ClientConnectionWLCID": response_item.get("connection", {}).get("wlcId", ""),
            "ClientConnectionAPMAC": response_item.get("connection", {}).get("apMac", ""),
            "ClientConnectionAPEthernetMAC": response_item.get("connection", {}).get("apEthernetMac", ""),
            "ClientConnectionAPMode": response_item.get("connection", {}).get("apMode", ""),
            "ClientConnectionRadioID": response_item.get("connection", {}).get("radioId", 0),
            "ClientConnectionChannel": response_item.get("connection", {}).get("channel", ""),
            "ClientConnectionChannelWidth": response_item.get("connection", {}).get("channelWidth", ""),
            "ClientConnectionProtocol": response_item.get("connection", {}).get("protocol", ""),
            "ClientConnectionProtocolCapability": response_item.get("connection", {}).get("protocolCapability", ""),
            "ClientConnectionUPNID": response_item.get("connection", {}).get("upnId", ""),
            "ClientConnectionUPNName": response_item.get("connection", {}).get("upnName", ""),
            "ClientConnectionUPNOwner": response_item.get("connection", {}).get("upnOwner", ""),
            "ClientConnectionUPNDUID": response_item.get("connection", {}).get("upnDuid", ""),
            "ClientConnectionRSSI": response_item.get("connection", {}).get("rssi", 0),
            "ClientConnectionSNR": response_item.get("connection", {}).get("snr", 0),
            "ClientConnectionDataRate": response_item.get("connection", {}).get("dataRate", 0),
            "ClientConnectionIsIOSAnalyticsCapable": response_item.get("connection", {}).get("isIosAnalyticsCapable", False),
            "ClientOnboardingAvgRunDuration": response_item.get("onboarding", {}).get("avgRunDuration", 0),
            "ClientOnboardingMaxRunDuration": response_item.get("onboarding", {}).get("maxRunDuration", 0),
            "ClientOnboardingAvgAssocDuration": response_item.get("onboarding", {}).get("avgAssocDuration", 0),
            "ClientOnboardingMaxAssocDuration": response_item.get("onboarding", {}).get("maxAssocDuration", 0),
            "ClientOnboardingAvgAuthDuration": response_item.get("onboarding", {}).get("avgAuthDuration", 0),
            "ClientOnboardingMaxAuthDuration": response_item.get("onboarding", {}).get("maxAuthDuration", 0),
            "ClientOnboardingAvgDHCPDuration": response_item.get("onboarding", {}).get("avgDhcpDuration", 0),
            "ClientOnboardingMaxDHCPDuration": response_item.get("onboarding", {}).get("maxDhcpDuration", 0),
            "ClientOnboardingMaxRoamingDuration": response_item.get("onboarding", {}).get("maxRoamingDuration", -1),
            "ClientOnboardingAAAServerIP": response_item.get("onboarding", {}).get("aaaServerIp", ""),
            "ClientOnboardingDHCPServerIP": response_item.get("onboarding", {}).get("dhcpServerIp", ""),
            "ClientOnboardingTime": response_item.get("onboarding", {}).get("onboardingTime", 0),
            "ClientOnboardingAuthDoneTime": response_item.get("onboarding", {}).get("authDoneTime", 0),
            "ClientOnboardingAssocDoneTime": response_item.get("onboarding", {}).get("assocDoneTime", 0),
            "ClientOnboardingDHCPDoneTime": response_item.get("onboarding", {}).get("dhcpDoneTime", 0),
            "ClientOnboardingRoamingTime": response_item.get("onboarding", {}).get("roamingTime", 0),
            "ClientOnboardingFailedRoamingCount": response_item.get("onboarding", {}).get("failedRoamingCount", 0),
            "ClientOnboardingSuccessfulRoamingCount": response_item.get("onboarding", {}).get("successfulRoamingCount", 0),
            "ClientOnboardingTotalRoamingAttempts": response_item.get("onboarding", {}).get("totalRoamingAttempts", 0),
            "ClientOnboardingAssocFailureReason": response_item.get("onboarding", {}).get("assocFailureReason", ""),
            "ClientOnboardingAAAFailureReason": response_item.get("onboarding", {}).get("aaaFailureReason", ""),
            "ClientOnboardingDHCPFailureReason": response_item.get("onboarding", {}).get("dhcpFailureReason", ""),
            "ClientOnboardingOtherFailureReason": response_item.get("onboarding", {}).get("otherFailureReason", ""),
            "ClientOnboardingLatestFailureReason": response_item.get("onboarding", {}).get("latestFailureReason", ""),
            "ClientLatencyVideo": response_item.get("latency", {}).get("video", 0),
            "ClientLatencyVoice": response_item.get("latency", {}).get("voice", 0),
            "ClientLatencyBestEffort": response_item.get("latency", {}).get("bestEffort", 0),
            "ClientLatencyBackground": response_item.get("latency", {}).get("background", 0),
        }
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
    if not cisco_catalyst_center_host.startswith("https"):
        raise ValueError("URL must be HTTPS")
    pass


def collect_events(helper, ew):
    opt_cisco_catalyst_center_host = helper.get_arg("cisco_catalyst_center_host")
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
    # get the overall client
    overall_client = get_client(catalyst)
    # simplify gathered information
    response = filter_client_data(overall_client)

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