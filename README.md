# Cisco DNA Center Add-On App for Splunk Enterprise

The project contains multiple Python scripts and dashboards.

## Cisco Products & Services:

- Cisco DNA Center

## Tools & Frameworks:

- Splunk Enterprise Server


## Usage

Knowledge of creating Splunk Add-On Apps is required.
It is recommended to have a recurring schedule for the app to collect real time data from Cisco DNA Center.

**NOTE:** The Splunk dashboards assume that your app name and index name are the followings, `CiscoDNACenter` for the app name and `cisco_dnac_index` for the index.

The repo includes:

- Config files:
    - [config.ini](./config.ini): Config file to set the Cisco DNA Center connection details for the SDK.

- Python wrappers:
    - [api.py](./api.py): Python file that wraps the session and the API's functions by DNACenter's subdomain.
    - [mydict.py](./mydict.py): Python file that wraps the mydict class. It is a data factory function.

- Python scripts:
    - [client_health.py](./client_health.py): script that will run on Splunk Enterprise to collect the overall client health data
    - [compliance.py](./compliance.py): script that will run on Splunk Enterprise to collect the compliance details and devices data
    - [device_health.py](./device_health.py): script that will run on Splunk Enterprise to collect the overall device health and devices data. **Review note below**.
    - [fabric_device.py](./fabric_device.py): script that will run on Splunk Enterprise to collect the devices (health) and fabric sites associated with them. **Review note below**.
    - [fabric_site.py](./fabric_site.py): script that will run on Splunk Enterprise to collect the sites and fabric sites associated with them
    - [image_health.py](./image_health.py): script that will run on Splunk Enterprise to collect the image health and their associated devices
    - [issues.py](./issues.py): script that will run on Splunk Enterprise to collect the issue details and devices&site data as necessary. **Review note below**.
    - [network_health.py](./network_health.py): script that will run on Splunk Enterprise to collect the overall network health
    - [security_advisories.py](./security_advisories.py): script that will run on Splunk Enterprise to collect the security advisories details and devices data as necessary
    - [security_advisories.py](./security_advisories.py): script that will run on Splunk Enterprise to collect the security advisories details and devices data as necessary
    - [sensors.py](./sensors.py): script that will run on the Splunk Enterprise to collect the sensor details

**NOTE:** Some scripts require inner changes to run at your specified interval -this should also reflect your Splunk data input interval-. The script files with those requirements are marked with a number sign or hashtag `#`. Modify the `interval_seconds` value as needed.

- Splunk Classic Dashboards:
    - [Cisco DNA Center Client Health.xml](./Cisco%20DNA%20Center%20Client%20Health.xml): sample dasboard that will display:
        + The health scores for all, for wired and for wireless devices in different graphs.
    - [Cisco DNA Center Compliance.xml](./Cisco%20DNA%20Center%20Compliance.xml): sample dasboard that will display:
        + The number of compliance devices
        + The number of compliance devices by status over time
        + The percentage of compliance devices by status
        + The number of compliance devices by type over time
        + The percentage of compliance devices by type
        + A compliance table summary
    - [Cisco DNA Center Device Health.xml](./Cisco%20DNA%20Center%20Device%20Health.xml): sample dasboard that will display:
        + The number of devices managed
        + The number of devices by family
        + The number of devices by role
        + The device's reachability status
        + The device's health, memory, and CPU utilization.
    - [Cisco DNA Center Fabric Device.xml](./Cisco%20DNA%20Center%20Fabric%20Device.xml): sample dasboard that will display:
        + The number of devices part of fabrics
    - [Cisco DNA Center Fabric Site.xml](./Cisco%20DNA%20Center%20Fabric%20Site.xml): sample dasboard that will display:
        + The number of fabrics
    - [Cisco DNA Center Image Health.xml](./Cisco%20DNA%20Center%20Image%20Health.xml): sample dasboard that will display:
        + The number of software images by state
        + The number of software images used by devices
    - [Cisco DNA Center Issues.xml](./Cisco%20DNA%20Center%20Issues.xml): sample dasboard that will display:
        + The number of issues received total
        + The number of issues by severity
        + The number of issues by priority
        + The number of issues by issue name
        + The number of issues by category
        + The number of issues by entity
        + Top 5 Issues
        + Top 5 devices impacted
    - [Cisco DNA Center Network Health.xml](./Cisco%20DNA%20Center%20Network%20Health.xml): sample dasboard that will display:
        + The network device health
    - [Cisco DNA Center Security Advisories.xml](./Cisco%20DNA%20Center%20Security%20Advisories.xml): sample dasboard that will display:
        + The number of security advisories by category
            + The number of critical security advisories
            + The number of high security advisories
            + The number of medium security advisories
        + The security advisories filtered table
    - [Cisco DNA Center Sensors.xml](./Cisco%20DNA%20Center%20Sensors.xml): sample dasboard that will display:
        + The number of sensor devices by status
        + The number of sensor devices by type
        + The number of sensor devices by location
        + The number of sensor devices by backhaul type


## License

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).

