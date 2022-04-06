#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DNACenterAPI class handler
"""

import errno
import json
import time
import urllib
from collections import OrderedDict

import requests

import mydict

__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


def dict_of_str(json_dict):
    """Given a dictionary; return a new dictionary with all items as strings.

    Args:
        json_dict(dict): Input JSON dictionary.

    Returns:
        A Python dictionary with the contents of the JSON object as strings.
    """
    result = {}
    for key, value in json_dict.items():
        result[key] = '{}'.format(value)
    return result


def apply_path_params(URL, path_params):
    if isinstance(URL, str) and isinstance(path_params, dict):
        for k in path_params:
            URL = URL.replace('${' + k + '}', str(path_params[k]))
            URL = URL.replace('{' + k + '}', str(path_params[k]))
        return URL
    else:
        raise TypeError(
            "'URL' must be a string; "
            "'path_params' must be a dictionary or valid JSON string; "
            "received: (URL={}, path_params={})".format(URL, path_params)
        )


def dict_from_items_with_values(*dictionaries, **items):
    """Creates a dict with the inputted items; pruning any that are `None`.

    Args:
        *dictionaries(dict): Dictionaries of items to be pruned and included.
        **items: Items to be pruned and included.

    Returns:
        dict: A dictionary containing all of the items with a 'non-None' value.

    """
    dict_list = list(dictionaries)
    dict_list.append(items)
    result = {}
    for d in dict_list:
        for key, value in d.items():
            if value is not None:
                result[key] = value
    return result


def extract_and_parse_json(response):
    """Extract and parse the JSON data from an requests.response object.

    Args:
        response(requests.response): The response object returned by a request
            using the requests package.
        stream(bool): If the request was to get a raw response content

    Returns:
        The parsed JSON data as the appropriate native Python data type.

    Raises:
        JSONDecodeError: caused by json.loads
        TypeError: caused by json.loads
    """
    try:
        return json.loads(response.text, object_hook=OrderedDict)
    except Exception as e:
        raise e


def object_factory(response):
    return mydict.MyDict(json_data=response).json_data


class Authentication(object):
    def __init__(self, base_url,
                 verify=True):
        super(Authentication, self).__init__()

        self._base_url = str(base_url)
        self._single_request_timeout = 60
        self._verify = verify
        self._request_kwargs = {"timeout": self._single_request_timeout,
                                "verify": verify}

        if verify is False:
            requests.packages.urllib3.disable_warnings()

    def authentication_api(self, username, password):
        """Exchange basic auth data for an Access Token(x-auth-token)
        that can be used to invoke the APIs.

        Args:
            username(basestring): HTTP Basic Auth username.
            password(basestring): HTTP Basic Auth password.

        Returns:
            AccessToken: An AccessToken object with the access token provided
            by the DNA Center cloud.

        Raises:
            TypeError: If the parameter types are incorrect.
            ApiError: If the DNA Center cloud returns an error.

        """
        temp_url = '/dna/system/api/v1/auth/token'
        self._endpoint_url = urllib.parse.urljoin(self._base_url, temp_url)

        # API request
        response = requests.post(self._endpoint_url, data=None,
                                 auth=(username, password),
                                 **self._request_kwargs)

        assert(response.status_code in [200, 201, 202, 204, 206])
        json_data = extract_and_parse_json(response)

        # Return a access_token object created from the response JSON data
        return object_factory(json_data)


class DNACenterAPI(object):
    def __init__(self,
                 username=None,
                 password=None,
                 base_url=None,
                 verify=None,
                 debug=None,
                 version=None):

        super(DNACenterAPI, self).__init__()

        # Step 1, basic properties
        self._username = username
        self._password = password
        # Step 2, Create authentication
        self._authentication = Authentication(base_url, verify)
        # Step 3, Call requests to get auth token
        self.session = RestSession(base_url,
            verify,
            get_access_token=self._get_access_token,
            access_token=self._get_access_token())
        # Use session on clients
        self.clients = Clients(self.session)
        self.compliance = Compliance(self.session)
        self.devices = Devices(self.session)
        self.issues = Issues(self.session)
        self.networks = Networks(self.session)
        self.sda = Sda(self.session)
        self.security_advisories = SecurityAdvisories(self.session)
        self.sensors = Sensors(self.session)
        self.sites = Sites(self.session)
        self.swim = Swim(self.session)
        self.topology = Topology(self.session)

    def _get_access_token(self):
        return self._authentication.authentication_api(self._username, self._password).Token


class RestSession(object):
    def __init__(self,
                 base_url=None,
                 verify=None,
                 get_access_token=None,
                 access_token=None):

        super(RestSession, self).__init__()

        self._base_url = str(base_url)
        self._get_access_token = get_access_token
        self._access_token = str(access_token)
        self._single_request_timeout = 60
        self._wait_on_rate_limit = True
        self._verify = verify

        # Initialize a new `requests` session
        self._req_session = requests.session()

        if verify is False:
            requests.packages.urllib3.disable_warnings()

        # Update the headers of the `requests` session
        self.update_headers({
            'X-Auth-Token': access_token,
            'Content-type': 'application/json;charset=utf-8'})

    def update_headers(self, headers):
        """Update the HTTP headers used for requests in this session.

        Note: Updates provided by the dictionary passed as the `headers`
        parameter to this method are merged into the session headers by adding
        new key-value pairs and/or updating the values of existing keys. The
        session headers are not replaced by the provided dictionary.

        Args:
             headers(dict): Updates to the current session headers.

        """
        self._req_session.headers.update(headers)

    def refresh_token(self):
        """Call the get_access_token method and update the session's
        auth header with the new token.
        """
        self._access_token = self._get_access_token()
        self.update_headers({'X-Auth-Token': self.access_token})

    def abs_url(self, url):
        """Given a relative or absolute URL; return an absolute URL.

        Args:
            url(basestring): A relative or absolute URL.

        Returns:
            str: An absolute URL.

        """
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme and not parsed_url.netloc:
            # url is a relative URL; combine with base_url
            return urllib.parse.urljoin(str(self._base_url), str(url))
        else:
            # url is already an absolute URL; return as is
            return url

    def request(self, method, url, custom_refresh, **kwargs):
        """Abstract base method for making requests to the DNA Center APIs.
        """
        # Ensure the url is an absolute URL
        abs_url = self.abs_url(url)

        # Update request kwargs with session defaults
        kwargs.setdefault('timeout', self._single_request_timeout)
        kwargs.setdefault('verify', self._verify)

        # Fixes requests inconsistent behavior with additional parameters
        if not kwargs.get('json'):
            kwargs.pop('json', None)

        if not kwargs.get('data'):
            kwargs.pop('data', None)

        c = custom_refresh
        while True:
            c += 1
            # Make the HTTP request to the API endpoint
            try:
                response = self._req_session.request(method, abs_url, **kwargs)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # EPIPE error
                    try:
                        c += 1
                        response = self._req_session.request(method, abs_url,
                                                             **kwargs)
                    except Exception as e:
                        raise e
                else:
                    raise e
            try:
                # Check the response code for error conditions
                assert(response.status_code < 400)
            except Exception:
                if response.status_code == 429:
                    time.sleep(response.retry_after)
                    continue
                if response.status_code == 401 and custom_refresh < 1:
                    self.refresh_token()
                    return self.request(method, url, 1, **kwargs)
                else:
                    # Re-raise the error
                    raise
            else:
                return response

    @property
    def headers(self):
        """The HTTP headers used for requests in this session."""
        return self._req_session.headers.copy()

    def get(self, url, params=None, **kwargs):
        response = self.request('GET', url, 0, params=params, **kwargs)
        return extract_and_parse_json(response)
    
    def post(self, url, params=None, json=None, data=None, **kwargs):
        response = self.request('POST', url, 0, params=params,
                                json=json, data=data, **kwargs)
        return extract_and_parse_json(response)

    def put(self, url, params=None, json=None, data=None, **kwargs):
        response = self.request('PUT', url, 0, params=params,
                                json=json, data=data, **kwargs)
        return extract_and_parse_json(response)

    def delete(self, url, params=None, **kwargs):
        response = self.request('DELETE', url, 0, params=params, **kwargs)
        return extract_and_parse_json(response)


class Clients(object):
    def __init__(self, session):
        super(Clients, self).__init__()
        self._session = session

    def get_overall_client_health(self, timestamp):
        _params = {
            'timestamp':
                timestamp,
        }

        if _params['timestamp'] is None:
            _params['timestamp'] = ''
        _params = dict_from_items_with_values(_params)
        path_params = {
        }
        e_url = ('/dna/intent/api/v1/client-health')
        endpoint_full_url = apply_path_params(e_url, path_params)
        json_data = self._session.get(endpoint_full_url, params=_params)
        return object_factory(json_data)


class Compliance(object):
    def __init__(self, session):
        super(Compliance, self).__init__()
        self._session = session

    def get_compliance_detail(self,
                              compliance_status=None,
                              compliance_type=None,
                              device_uuid=None,
                              limit=None,
                              offset=None):
        _params = {
            'complianceType':
                compliance_type,
            'complianceStatus':
                compliance_status,
            'deviceUuid':
                device_uuid,
            'offset':
                offset,
            'limit':
                limit,
        }
        _params = dict_from_items_with_values(_params)
        path_params = {
        }
        e_url = ('/dna/intent/api/v1/compliance/detail')
        endpoint_full_url = apply_path_params(e_url, path_params)
        json_data = self._session.get(endpoint_full_url, params=_params)
        return object_factory(json_data)


class Devices(object):
    def __init__(self, session):
        super(Devices, self).__init__()
        self._session = session

    def devices(self,
                device_role=None,
                end_time=None,
                health=None,
                limit=None,
                offset=None,
                site_id=None,
                start_time=None,
                headers=None,
                **request_parameters):
        _params = {
            'deviceRole':
                device_role,
            'siteId':
                site_id,
            'health':
                health,
            'startTime':
                start_time,
            'endTime':
                end_time,
            'limit':
                limit,
            'offset':
                offset,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }
        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/device-health')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)
        return object_factory(json_data)

    def get_device_by_id(self,
                         id,
                         headers=None,
                         **request_parameters):
        """Returns the network device details for the given device ID .

        Args:
            id(basestring): id path parameter. Device ID .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """
        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
            'id': id,
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/network-device/{id}')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

    def get_device_list(self,
                        associated_wlc_ip=None,
                        collection_interval=None,
                        collection_status=None,
                        device_support_level=None,
                        error_code=None,
                        error_description=None,
                        family=None,
                        hostname=None,
                        id=None,
                        license_name=None,
                        license_status=None,
                        license_type=None,
                        location=None,
                        location_name=None,
                        mac_address=None,
                        management_ip_address=None,
                        module_equpimenttype=None,
                        module_name=None,
                        module_operationstatecode=None,
                        module_partnumber=None,
                        module_servicestate=None,
                        module_vendorequipmenttype=None,
                        not_synced_for_minutes=None,
                        platform_id=None,
                        reachability_status=None,
                        role=None,
                        serial_number=None,
                        series=None,
                        software_type=None,
                        software_version=None,
                        type=None,
                        up_time=None,
                        headers=None,
                        **request_parameters):
        """Returns list of network devices based on filter criteria such as management IP address, mac address, hostname,
        etc. You can use the .* in any value to conduct a wildcard search. For example, to find all hostnames
        beginning with myhost in the IP address range 192.25.18.n, issue the following request: GET
        /dna/intent/api/v1/network-device?hostname=myhost.*&managementIpAddress=192.25.18..* If id parameter is
        provided with comma separated ids, it will return the list of network-devices for the given ids and
        ignores the other request parameters. .

        Args:
            hostname(basestring, list, set, tuple): hostname query parameter.
            management_ip_address(basestring, list, set, tuple): managementIpAddress query parameter.
            mac_address(basestring, list, set, tuple): macAddress query parameter.
            location_name(basestring, list, set, tuple): locationName query parameter.
            serial_number(basestring, list, set, tuple): serialNumber query parameter.
            location(basestring, list, set, tuple): location query parameter.
            family(basestring, list, set, tuple): family query parameter.
            type(basestring, list, set, tuple): type query parameter.
            series(basestring, list, set, tuple): series query parameter.
            collection_status(basestring, list, set, tuple): collectionStatus query parameter.
            collection_interval(basestring, list, set, tuple): collectionInterval query parameter.
            not_synced_for_minutes(basestring, list, set, tuple): notSyncedForMinutes query parameter.
            error_code(basestring, list, set, tuple): errorCode query parameter.
            error_description(basestring, list, set, tuple): errorDescription query parameter.
            software_version(basestring, list, set, tuple): softwareVersion query parameter.
            software_type(basestring, list, set, tuple): softwareType query parameter.
            platform_id(basestring, list, set, tuple): platformId query parameter.
            role(basestring, list, set, tuple): role query parameter.
            reachability_status(basestring, list, set, tuple): reachabilityStatus query parameter.
            up_time(basestring, list, set, tuple): upTime query parameter.
            associated_wlc_ip(basestring, list, set, tuple): associatedWlcIp query parameter.
            license_name(basestring, list, set, tuple): license.name query parameter.
            license_type(basestring, list, set, tuple): license.type query parameter.
            license_status(basestring, list, set, tuple): license.status query parameter.
            module_name(basestring, list, set, tuple): module+name query parameter.
            module_equpimenttype(basestring, list, set, tuple): module+equpimenttype query parameter.
            module_servicestate(basestring, list, set, tuple): module+servicestate query parameter.
            module_vendorequipmenttype(basestring, list, set, tuple): module+vendorequipmenttype query parameter.
            module_partnumber(basestring, list, set, tuple): module+partnumber query parameter.
            module_operationstatecode(basestring, list, set, tuple): module+operationstatecode query parameter.
            id(basestring): id query parameter. Accepts comma separated ids and return list of network-devices for
                the given ids. If invalid or not-found ids are provided, null entry will be returned in
                the list. .
            device_support_level(basestring): deviceSupportLevel query parameter.
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """
        _params = {
            'hostname':
                hostname,
            'managementIpAddress':
                management_ip_address,
            'macAddress':
                mac_address,
            'locationName':
                location_name,
            'serialNumber':
                serial_number,
            'location':
                location,
            'family':
                family,
            'type':
                type,
            'series':
                series,
            'collectionStatus':
                collection_status,
            'collectionInterval':
                collection_interval,
            'notSyncedForMinutes':
                not_synced_for_minutes,
            'errorCode':
                error_code,
            'errorDescription':
                error_description,
            'softwareVersion':
                software_version,
            'softwareType':
                software_type,
            'platformId':
                platform_id,
            'role':
                role,
            'reachabilityStatus':
                reachability_status,
            'upTime':
                up_time,
            'associatedWlcIp':
                associated_wlc_ip,
            'license.name':
                license_name,
            'license.type':
                license_type,
            'license.status':
                license_status,
            'module+name':
                module_name,
            'module+equpimenttype':
                module_equpimenttype,
            'module+servicestate':
                module_servicestate,
            'module+vendorequipmenttype':
                module_vendorequipmenttype,
            'module+partnumber':
                module_partnumber,
            'module+operationstatecode':
                module_operationstatecode,
            'id':
                id,
            'deviceSupportLevel':
                device_support_level,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/network-device')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

    def get_stack_details_for_device(self,
                                     device_id,
                                     headers=None,
                                     **request_parameters):
        """Retrieves complete stack details for given device ID .

        Args:
            device_id(basestring): deviceId path parameter. Device ID .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """
        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
            'deviceId': device_id,
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/network-device/{deviceId}/stack')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory('bpm_c07eaefa1fa45faa801764d9094336ae_v2_2_3_3', json_data)


class Issues(object):
    def __init__(self, session):
        super(Issues, self).__init__()
        self._session = session

    def get_issue_enrichment_details(self,
                                     headers=None,
                                     **request_parameters):
        """Enriches a given network issue context (an issue id or end user’s Mac Address) with details about the issue(s),
        impacted hosts and suggested actions for remediation .

        Args:
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/issue-enrichment-details')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

    def issues(self,
               ai_driven=None,
               device_id=None,
               end_time=None,
               issue_status=None,
               mac_address=None,
               priority=None,
               site_id=None,
               start_time=None,
               headers=None,
               **request_parameters):
        """Intent API to get a list of global issues, issues for a specific device, or issue for a specific client device's
        MAC address. .

        Args:
            start_time(int): startTime query parameter. Starting epoch time in milliseconds of query time window .
            end_time(int): endTime query parameter. Ending epoch time in milliseconds of query time window .
            site_id(basestring): siteId query parameter. Assurance UUID value of the site in the issue content .
            device_id(basestring): deviceId query parameter. Assurance UUID value of the device in the issue content
                .
            mac_address(basestring): macAddress query parameter. Client's device MAC address of the issue (format
                xx:xx:xx:xx:xx:xx) .
            priority(basestring): priority query parameter. The issue's priority value (One of P1, P2, P3, or
                P4)(Use only when macAddress and deviceId are not provided) .
            ai_driven(basestring): aiDriven query parameter. The issue's AI driven value (Yes or No)(Use only when
                macAddress and deviceId are not provided) .
            issue_status(basestring): issueStatus query parameter. The issue's status value (One of ACTIVE, IGNORED,
                RESOLVED) .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'startTime':
                start_time,
            'endTime':
                end_time,
            'siteId':
                site_id,
            'deviceId':
                device_id,
            'macAddress':
                mac_address,
            'priority':
                priority,
            'aiDriven':
                ai_driven,
            'issueStatus':
                issue_status,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/issues')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Networks(object):
    def __init__(self, session):
        super(Networks, self).__init__()
        self._session = session

    def get_overall_network_health(self,
                                   timestamp=None,
                                   headers=None,
                                   **request_parameters):
        """Returns Overall Network Health information by Device category (Access, Distribution, Core, Router, Wireless) for
        any given point of time .

        Args:
            timestamp(basestring): timestamp query parameter. Epoch time(in milliseconds) when the Network health
                data is required .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'timestamp':
                timestamp,
        }

        if _params['timestamp'] is None:
            _params['timestamp'] = ''
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/network-health')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Sda(object):
    def __init__(self, session):
        super(Sda, self).__init__()
        self._session = session

    def get_site(self,
                 site_name_hierarchy,
                 headers=None,
                 **request_parameters):
        """Get Site info from SDA Fabric .

        Args:
            site_name_hierarchy(basestring): siteNameHierarchy query parameter. Site Name Hierarchy .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """
        _params = {
            'siteNameHierarchy':
                site_name_hierarchy,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/business/sda/fabric-site')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class SecurityAdvisories(object):
    def __init__(self, session):
        super(SecurityAdvisories, self).__init__()
        self._session = session

    def get_advisories_list(self,
                            headers=None,
                            **request_parameters):
        """Retrieves list of advisories on the network .

        Args:
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/security-advisory/advisory')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

    def get_advisories_summary(self,
                               headers=None,
                               **request_parameters):
        """Retrieves summary of advisories on the network. .

        Args:
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/security-advisory/advisory/aggregate')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

    def get_devices_per_advisory(self,
                                 advisory_id,
                                 headers=None,
                                 **request_parameters):
        """Retrieves list of devices for an advisory .

        Args:
            advisory_id(basestring): advisoryId path parameter. Advisory ID .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
            'advisoryId': advisory_id,
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/security-'
                 + 'advisory/advisory/{advisoryId}/device')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Sensors(object):
    def __init__(self, session):
        super(Sensors, self).__init__()
        self._session = session

    def sensors(self,
                site_id=None,
                headers=None,
                **request_parameters):
        """Intent API to get a list of SENSOR devices .

        Args:
            site_id(basestring): siteId query parameter.
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'siteId':
                site_id,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/sensor')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Sites(object):
    def __init__(self, session):
        super(Sites, self).__init__()
        self._session = session

    def get_site(self,
                 limit=None,
                 name=None,
                 offset=None,
                 site_id=None,
                 type=None,
                 headers=None,
                 **request_parameters):
        """Get site using siteNameHierarchy/siteId/type ,return all sites if these parameters are not given as input. .

        Args:
            name(basestring): name query parameter. siteNameHierarchy (ex: global/groupName) .
            site_id(basestring): siteId query parameter. Site id to which site details to retrieve. .
            type(basestring): type query parameter. type (ex: area, building, floor) .
            offset(basestring): offset query parameter. offset/starting row .
            limit(basestring): limit query parameter. Number of sites to be retrieved .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'name':
                name,
            'siteId':
                site_id,
            'type':
                type,
            'offset':
                offset,
            'limit':
                limit,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/site')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Swim(object):
    def __init__(self, session):
        super(Swim, self).__init__()
        self._session = session

    def get_software_image_details(self,
                                   application_type=None,
                                   created_time=None,
                                   family=None,
                                   image_integrity_status=None,
                                   image_name=None,
                                   image_series=None,
                                   image_size_greater_than=None,
                                   image_size_lesser_than=None,
                                   image_uuid=None,
                                   is_cco_latest=None,
                                   is_cco_recommended=None,
                                   is_tagged_golden=None,
                                   limit=None,
                                   name=None,
                                   offset=None,
                                   sort_by=None,
                                   sort_order=None,
                                   version=None,
                                   headers=None,
                                   **request_parameters):
        """Returns software image list based on a filter criteria. For example: "filterbyName = cat3k%" .

        Args:
            image_uuid(basestring): imageUuid query parameter.
            name(basestring): name query parameter.
            family(basestring): family query parameter.
            application_type(basestring): applicationType query parameter.
            image_integrity_status(basestring): imageIntegrityStatus query parameter. imageIntegrityStatus FAILURE,
                UNKNOWN, VERIFIED .
            version(basestring): version query parameter. software Image Version .
            image_series(basestring): imageSeries query parameter. image Series .
            image_name(basestring): imageName query parameter. image Name .
            is_tagged_golden(bool): isTaggedGolden query parameter. is Tagged Golden .
            is_cco_recommended(bool): isCCORecommended query parameter. is recommended from cisco.com .
            is_cco_latest(bool): isCCOLatest query parameter. is latest from cisco.com .
            created_time(int): createdTime query parameter. time in milliseconds (epoch format) .
            image_size_greater_than(int): imageSizeGreaterThan query parameter. size in bytes .
            image_size_lesser_than(int): imageSizeLesserThan query parameter. size in bytes .
            sort_by(basestring): sortBy query parameter. sort results by this field .
            sort_order(basestring): sortOrder query parameter. sort order 'asc' or 'des'. Default is asc .
            limit(int): limit query parameter.
            offset(int): offset query parameter.
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'imageUuid':
                image_uuid,
            'name':
                name,
            'family':
                family,
            'applicationType':
                application_type,
            'imageIntegrityStatus':
                image_integrity_status,
            'version':
                version,
            'imageSeries':
                image_series,
            'imageName':
                image_name,
            'isTaggedGolden':
                is_tagged_golden,
            'isCCORecommended':
                is_cco_recommended,
            'isCCOLatest':
                is_cco_latest,
            'createdTime':
                created_time,
            'imageSizeGreaterThan':
                image_size_greater_than,
            'imageSizeLesserThan':
                image_size_lesser_than,
            'sortBy':
                sort_by,
            'sortOrder':
                sort_order,
            'limit':
                limit,
            'offset':
                offset,
        }
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/image/importation')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)


class Topology(object):
    def __init__(self, session):
        super(Topology, self).__init__()
        self._session = session

    def get_overall_network_health(self,
                                   timestamp=None,
                                   headers=None,
                                   **request_parameters):
        """Returns Overall Network Health information by Device category (Access, Distribution, Core, Router, Wireless) for
        any given point of time .

        Args:
            timestamp(basestring): timestamp query parameter. Epoch time(in milliseconds) when the Network health
                data is required .
            headers(dict): Dictionary of HTTP Headers to send with the Request
                .
            **request_parameters: Additional request parameters (provides
                support for parameters that may be added in the future).

        Returns:
            MyDict: JSON response. Access the object's properties by using
            the dot notation or the bracket notation.

        Raises:
            TypeError: If the parameter types are incorrect.
            MalformedRequest: If the request body created is invalid.
            ApiError: If the DNA Center cloud returns an error.
        """

        _params = {
            'timestamp':
                timestamp,
        }

        if _params['timestamp'] is None:
            _params['timestamp'] = ''
        _params.update(request_parameters)
        _params = dict_from_items_with_values(_params)

        path_params = {
        }

        with_custom_headers = False
        _headers = self._session.headers or {}
        if headers:
            _headers.update(dict_of_str(headers))
            with_custom_headers = True

        e_url = ('/dna/intent/api/v1/network-health')
        endpoint_full_url = apply_path_params(e_url, path_params)
        if with_custom_headers:
            json_data = self._session.get(endpoint_full_url, params=_params,
                                          headers=_headers)
        else:
            json_data = self._session.get(endpoint_full_url, params=_params)

        return object_factory(json_data)

