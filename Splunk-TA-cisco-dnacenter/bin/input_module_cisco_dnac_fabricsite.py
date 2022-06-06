
# encoding = utf-8

import datetime
import json
import os
import sys
import time

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


def simplify_site(site_resp):
    """
    This function will simplify the site data for Splunk searches
    :param site_resp: Cisco DNAC SDK api
    :return: new site response
    """
    simplified_site = {}
    if site_resp:
        simplified_site["SiteName"] = site_resp.get("name")
        simplified_site["SiteNameHierarchy"] = site_resp.get("siteNameHierarchy")
        simplified_site["SiteType"] = "area"
        if site_resp.get("additionalInfo"):
            if len(site_resp["additionalInfo"]) > 0:
                for additional_info in site_resp["additionalInfo"]:
                    if isinstance(additional_info, dict) and additional_info.get(
                        "attributes"
                    ):
                        if isinstance(
                            additional_info["attributes"], dict
                        ) and additional_info["attributes"].get("type"):
                            simplified_site["SiteType"] = additional_info[
                                "attributes"
                            ].get("type")
        return simplified_site
    else:
        return {}


def simplify_sites(helper, dnac, sites_response, seen):
    """
    This function will filter and simplify the sites data for Splunk searches
    :param dnac: Cisco DNAC SDK api
    :param sites_response: Cisco DNAC SDK api
    :param seen: set to filter previous SiteNameHierarchy values
    :return: new sites response
    """
    fabric_sites_response = []
    for site_response in sites_response:
        site = simplify_site(site_response)
        site_key = site["SiteNameHierarchy"]
        # if it was seen before, skip it
        if site_key in seen:
            continue
        # if not added
        seen.add(site_key)
        helper.log_debug(
            "Getting the fabric site data from the site name hierarchy {0}".format(
                site_key
            )
        )
        fabric_site = get_simplified_fabric_site(helper, dnac, site_key)
        fabric_site_new = dict(site)
        if fabric_site:
            fabric_site_new.update({"HasFabric": "True"})
            helper.log_debug(
                "Saved the fabric site data from the site name hierarchy {0}".format(
                    site_key
                )
            )
        else:
            fabric_site_new.update({"HasFabric": "False"})
        fabric_site_new.update(fabric_site)
        fabric_sites_response.append(fabric_site_new)
    return fabric_sites_response


def get_simplified_sites(helper, dnac):
    """
    This function will retrieve the sites and simplify them
    :param dnac: Cisco DNAC SDK api
    :return: sites response
    """
    limit = 20
    offset = 1
    sites_responses = []
    do_request_next = True
    seen = set()
    while do_request_next:
        try:
            sites_response = dnac.sites.get_site(limit=str(limit), offset=str(offset))
            if sites_response and sites_response.response:
                sites_responses.extend(
                    simplify_sites(helper, dnac, sites_response.response, seen)
                )
                if len(sites_response.response) < limit:
                    do_request_next = False
                    break
            else:
                do_request_next = False
                break
        except Exception:
            do_request_next = False
            break
        offset = offset + limit
    return sites_responses


def get_simplified_fabric_site(helper, dnac, site_name_hierarchy):
    """
    This function will retrieve the fabric site and simplify them
    :param dnac: Cisco DNAC SDK api
    :param site_name_hierarchy: site name hierarchy
    :return: fabric site response
    """
    response = {}
    try:
        fabric_site = dnac.sda.get_site(site_name_hierarchy)
        if fabric_site.get("status") == "success":
            response["FabricSiteNameHierarchy"] = (
                fabric_site.get("siteNameHierarchy") or ""
            )
            response["FabricName"] = fabric_site.get("fabricName") or ""
            response["FabricType"] = fabric_site.get("fabricType") or ""
            response["FabricDomainType"] = fabric_site.get("fabricDomainType") or ""
        return response
    except Exception as e:
        import traceback
        helper.log_error(traceback.format_exc())
        helper.log_error('Error getting site. ' + str(e))
        return response


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

    # get the sites and fabric sites associated with them
    simplified_sites = get_simplified_sites(helper, dnac)

    for item in simplified_sites:
        key = "{0}_{1}".format(opt_cisco_dna_center_host, item["SiteNameHierarchy"])
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
