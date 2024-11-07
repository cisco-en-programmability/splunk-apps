# encoding = utf-8

import os
import json
import sys
import time
import datetime
import utils

import mydict

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
    # client_response = catalyst.clients.get_clients()
    response = {
        "response": [
            {
                "id": "1",
                "macAddress": "00:1A:2B:3C:4D:5E",
                "type": "laptop",
                "name": "John's Laptop",
                "userId": "user123",
                "username": "john_doe",
                "ipv4Address": "192.168.1.2",
                "ipv6Addresses": ["fe80::1a2b:3c4d:5e6f"],
                "vendor": "Dell",
                "osType": "Windows",
                "osVersion": "10",
                "formFactor": "Laptop",
                "siteHierarchy": "Building 1 > Floor 2 > Room 3",
                "siteHierarchyId": "site123",
                "siteId": "site001",
                "lastUpdatedTime": 1627849200,
                "connectionStatus": "connected",
                "tracked": "yes",
                "isPrivateMacAddress": False,
                "health": {
                    "overallScore": 85,
                    "onboardingScore": 90,
                    "connectedScore": 80,
                    "linkErrorPercentageThreshold": 1,
                    "isLinkErrorIncluded": True,
                    "rssiThreshold": -70,
                    "snrThreshold": 25,
                    "isRssiIncluded": True,
                    "isSnrIncluded": True
                },
                "traffic": {
                    "txBytes": 1048576,
                    "rxBytes": 2097152,
                    "usage": 3145728,
                    "rxPackets": 1500,
                    "txPackets": 1200,
                    "rxRate": 100,
                    "txRate": 80,
                    "rxLinkErrorPercentage": 0.5,
                    "txLinkErrorPercentage": 0.3,
                    "rxRetries": 10,
                    "rxRetryPercentage": 0.2,
                    "txDrops": 5,
                    "txDropPercentage": 0.1,
                    "dnsRequestCount": 50,
                    "dnsResponseCount": 45
                },
                "connectedNetworkDevice": {
                    "connectedNetworkDeviceId": "device001",
                    "connectedNetworkDeviceName": "Switch 1",
                    "connectedNetworkDeviceManagementIp": "192.168.1.1",
                    "connectedNetworkDeviceMac": "00:1A:2B:3C:4D:5F",
                    "connectedNetworkDeviceType": "switch",
                    "interfaceName": "GigabitEthernet0/1",
                    "interfaceSpeed": 1000,
                    "duplexMode": "full"
                },
                "connection": {
                    "vlanId": "10",
                    "sessionDuration": 3600,
                    "vnId": "vn001",
                    "l2Vn": "l2vn001",
                    "l3Vn": "l3vn001",
                    "securityGroupTag": "sgt001",
                    "linkSpeed": 1000,
                    "bridgeVMMode": "enabled",
                    "band": "5GHz",
                    "ssid": "CorporateWiFi",
                    "authType": "WPA2",
                    "wlcName": "WLC1",
                    "wlcId": "wlc001",
                    "apMac": "00:1A:2B:3C:4D:60",
                    "apEthernetMac": "00:1A:2B:3C:4D:61",
                    "apMode": "local",
                    "radioId": 1,
                    "channel": "36",
                    "channelWidth": "40MHz",
                    "protocol": "802.11ac",
                    "protocolCapability": "HT",
                    "upnId": "upn001",
                    "upnName": "UPN1",
                    "upnOwner": "owner1",
                    "upnDuid": "duid001",
                    "rssi": -65,
                    "snr": 30,
                    "dataRate": 300,
                    "isIosAnalyticsCapable": True
                },
                "onboarding": {
                    "avgRunDuration": 10,
                    "maxRunDuration": 15,
                    "avgAssocDuration": 5,
                    "maxAssocDuration": 7,
                    "avgAuthDuration": 3,
                    "maxAuthDuration": 5,
                    "avgDhcpDuration": 2,
                    "maxDhcpDuration": 4,
                    "maxRoamingDuration": 8,
                    "aaaServerIp": "192.168.1.10",
                    "dhcpServerIp": "192.168.1.11",
                    "onboardingTime": 1627849200,
                    "authDoneTime": 1627849205,
                    "assocDoneTime": 1627849207,
                    "dhcpDoneTime": 1627849210,
                    "roamingTime": 1627849215,
                    "failedRoamingCount": 1,
                    "successfulRoamingCount": 5,
                    "totalRoamingAttempts": 6,
                    "assocFailureReason": "none",
                    "aaaFailureReason": "none",
                    "dhcpFailureReason": "none",
                    "otherFailureReason": "none",
                    "latestFailureReason": "none"
                },
                "latency": {
                    "video": 30,
                    "voice": 20,
                    "bestEffort": 50,
                    "background": 70
                }
            },
            {
                "id": "2",
                "macAddress": "00:1A:2B:3C:4D:6E",
                "type": "smartphone",
                "name": "Jane's Phone",
                "userId": "user456",
                "username": "jane_doe",
                "ipv4Address": "192.168.1.3",
                "ipv6Addresses": ["fe80::1a2b:3c4d:6e7f"],
                "vendor": "Apple",
                "osType": "iOS",
                "osVersion": "14.6",
                "formFactor": "Smartphone",
                "siteHierarchy": "Building 1 > Floor 2 > Room 4",
                "siteHierarchyId": "site124",
                "siteId": "site002",
                "lastUpdatedTime": 1627849300,
                "connectionStatus": "connected",
                "tracked": "yes",
                "isPrivateMacAddress": True,
                "health": {
                    "overallScore": 90,
                    "onboardingScore": 95,
                    "connectedScore": 85,
                    "linkErrorPercentageThreshold": 0.5,
                    "isLinkErrorIncluded": True,
                    "rssiThreshold": -65,
                    "snrThreshold": 30,
                    "isRssiIncluded": True,
                    "isSnrIncluded": True
                },
                "traffic": {
                    "txBytes": 524288,
                    "rxBytes": 1048576,
                    "usage": 1572864,
                    "rxPackets": 800,
                    "txPackets": 600,
                    "rxRate": 50,
                    "txRate": 40,
                    "rxLinkErrorPercentage": 0.2,
                    "txLinkErrorPercentage": 0.1,
                    "rxRetries": 5,
                    "rxRetryPercentage": 0.1,
                    "txDrops": 2,
                    "txDropPercentage": 0.05,
                    "dnsRequestCount": 30,
                    "dnsResponseCount": 28
                },
                "connectedNetworkDevice": {
                    "connectedNetworkDeviceId": "device002",
                    "connectedNetworkDeviceName": "Switch 2",
                    "connectedNetworkDeviceManagementIp": "192.168.1.2",
                    "connectedNetworkDeviceMac": "00:1A:2B:3C:4D:6F",
                    "connectedNetworkDeviceType": "switch",
                    "interfaceName": "GigabitEthernet0/2",
                    "interfaceSpeed": 1000,
                    "duplexMode": "full"
                },
                "connection": {
                    "vlanId": "20",
                    "sessionDuration": 1800,
                    "vnId": "vn002",
                    "l2Vn": "l2vn002",
                    "l3Vn": "l3vn002",
                    "securityGroupTag": "sgt002",
                    "linkSpeed": 1000,
                    "bridgeVMMode": "enabled",
                    "band": "2.4GHz",
                    "ssid": "GuestWiFi",
                    "authType": "WPA2",
                    "wlcName": "WLC2",
                    "wlcId": "wlc002",
                    "apMac": "00:1A:2B:3C:4D:70",
                    "apEthernetMac": "00:1A:2B:3C:4D:71",
                    "apMode": "local",
                    "radioId": 2,
                    "channel": "11",
                    "channelWidth": "20MHz",
                    "protocol": "802.11n",
                    "protocolCapability": "HT",
                    "upnId": "upn002",
                    "upnName": "UPN2",
                    "upnOwner": "owner2",
                    "upnDuid": "duid002",
                    "rssi": -60,
                    "snr": 35,
                    "dataRate": 150,
                    "isIosAnalyticsCapable": True
                },
                "onboarding": {
                    "avgRunDuration": 8,
                    "maxRunDuration": 12,
                    "avgAssocDuration": 4,
                    "maxAssocDuration": 6,
                    "avgAuthDuration": 2,
                    "maxAuthDuration": 4,
                    "avgDhcpDuration": 1,
                    "maxDhcpDuration": 3,
                    "maxRoamingDuration": 6,
                    "aaaServerIp": "192.168.1.12",
                    "dhcpServerIp": "192.168.1.13",
                    "onboardingTime": 1627849300,
                    "authDoneTime": 1627849304,
                    "assocDoneTime": 1627849306,
                    "dhcpDoneTime": 1627849309,
                    "roamingTime": 1627849312,
                    "failedRoamingCount": 0,
                    "successfulRoamingCount": 3,
                    "totalRoamingAttempts": 3,
                    "assocFailureReason": "none",
                    "aaaFailureReason": "none",
                    "dhcpFailureReason": "none",
                    "otherFailureReason": "none",
                    "latestFailureReason": "none"
                },
                "latency": {
                    "video": 25,
                    "voice": 15,
                    "bestEffort": 45,
                    "background": 60
                }
            },
            {
                "id": "3",
                "macAddress": "00:1A:2B:3C:4D:7E",
                "type": "tablet",
                "name": "Alice's Tablet",
                "userId": "user789",
                "username": "alice_smith",
                "ipv4Address": "192.168.1.4",
                "ipv6Addresses": ["fe80::1a2b:3c4d:7e8f"],
                "vendor": "Samsung",
                "osType": "Android",
                "osVersion": "11",
                "formFactor": "Tablet",
                "siteHierarchy": "Building 1 > Floor 3 > Room 5",
                "siteHierarchyId": "site125",
                "siteId": "site003",
                "lastUpdatedTime": 1627849400,
                "connectionStatus": "connected",
                "tracked": "yes",
                "isPrivateMacAddress": False,
                "health": {
                    "overallScore": 88,
                    "onboardingScore": 92,
                    "connectedScore": 84,
                    "linkErrorPercentageThreshold": 0.8,
                    "isLinkErrorIncluded": False,
                    "rssiThreshold": -68,
                    "snrThreshold": 28,
                    "isRssiIncluded": True,
                    "isSnrIncluded": True
                },
                "traffic": {
                    "txBytes": 786432,
                    "rxBytes": 1572864,
                    "usage": 2359296,
                    "rxPackets": 1000,
                    "txPackets": 800,
                    "rxRate": 75,
                    "txRate": 60,
                    "rxLinkErrorPercentage": 0.3,
                    "txLinkErrorPercentage": 0.2,
                    "rxRetries": 7,
                    "rxRetryPercentage": 0.15,
                    "txDrops": 3,
                    "txDropPercentage": 0.08,
                    "dnsRequestCount": 40,
                    "dnsResponseCount": 38
                },
                "connectedNetworkDevice": {
                    "connectedNetworkDeviceId": "device003",
                    "connectedNetworkDeviceName": "Switch 3",
                    "connectedNetworkDeviceManagementIp": "192.168.1.3",
                    "connectedNetworkDeviceMac": "00:1A:2B:3C:4D:7F",
                    "connectedNetworkDeviceType": "switch",
                    "interfaceName": "GigabitEthernet0/3",
                    "interfaceSpeed": 1000,
                    "duplexMode": "full"
                },
                "connection": {
                    "vlanId": "30",
                    "sessionDuration": 5400,
                    "vnId": "vn003",
                    "l2Vn": "l2vn003",
                    "l3Vn": "l3vn003",
                    "securityGroupTag": "sgt003",
                    "linkSpeed": 1000,
                    "bridgeVMMode": "enabled",
                    "band": "5GHz",
                    "ssid": "CorporateWiFi",
                    "authType": "WPA2",
                    "wlcName": "WLC3",
                    "wlcId": "wlc003",
                    "apMac": "00:1A:2B:3C:4D:80",
                    "apEthernetMac": "00:1A:2B:3C:4D:81",
                    "apMode": "local",
                    "radioId": 3,
                    "channel": "44",
                    "channelWidth": "40MHz",
                    "protocol": "802.11ac",
                    "protocolCapability": "HT",
                    "upnId": "upn003",
                    "upnName": "UPN3",
                    "upnOwner": "owner3",
                    "upnDuid": "duid003",
                    "rssi": -63,
                    "snr": 32,
                    "dataRate": 250,
                    "isIosAnalyticsCapable": True
                },
                "onboarding": {
                    "avgRunDuration": 9,
                    "maxRunDuration": 14,
                    "avgAssocDuration": 4,
                    "maxAssocDuration": 6,
                    "avgAuthDuration": 3,
                    "maxAuthDuration": 5,
                    "avgDhcpDuration": 2,
                    "maxDhcpDuration": 4,
                    "maxRoamingDuration": 7,
                    "aaaServerIp": "192.168.1.14",
                    "dhcpServerIp": "192.168.1.15",
                    "onboardingTime": 1627849400,
                    "authDoneTime": 1627849405,
                    "assocDoneTime": 1627849407,
                    "dhcpDoneTime": 1627849410,
                    "roamingTime": 1627849415,
                    "failedRoamingCount": 1,
                    "successfulRoamingCount": 4,
                    "totalRoamingAttempts": 5,
                    "assocFailureReason": "none",
                    "aaaFailureReason": "none",
                    "dhcpFailureReason": "none",
                    "otherFailureReason": "none",
                    "latestFailureReason": "none"
                },
                "latency": {
                    "video": 28,
                    "voice": 18,
                    "bestEffort": 48,
                    "background": 65
                }
            }
        ],
        "page": {
            "limit": 0,
            "offset": 0,
            "count": 0,
            "sortBy": [
                {
                    "name": "string",
                    "order": "string"
                }
            ]
        },
        "version": "1.0"
    }
    client_response = mydict.MyDict(json_data=response).json_data
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