# Cisco DNA Center Add-On App for Splunk Enterprise

The project contains multiple Python scripts and dashboards.

**Cisco Products & Services:**

- Cisco DNA Center

**Tools & Frameworks:**

- Cisco DNA Center SDK - dnacentersdk -
- Splunk Enterprise Server

**Usage**

Knowledge of creating Splunk Add-On Apps is required.
It is recommended to have a recurring schedule for the app to collect real time data from Cisco DNA Center.

The repo includes:

- config.ini: Config file to set the Cisco DNA Center connection details for the SDK.
- client_health.py: script that will run on Splunk Enterprise to collect the overall client health data
- Cisco DNA Center Client Health.xml: dashboard.
- compliance.py: script that will run on Splunk Enterprise to collect the compliance details and devices data
- Cisco DNA Center Compliance.xml:
- device_health.py: script that will run on Splunk Enterprise to collect the overall device health and devices data
- Cisco DNA Center Device Health.xml:
- fabric_device.py: script that will run on Splunk Enterprise to collect the devices (health) and fabric sites associated with them
- Cisco DNA Center Fabric Device.xml:
- fabric_site.py: script that will run on Splunk Enterprise to collect the sites and fabric sites associated with them
- Cisco DNA Center Fabric Site.xml:
- image_health.py: script that will run on Splunk Enterprise to collect the image health and their associated devices
- Cisco DNA Center Image Health.xml:
- issues.py: script that will run on Splunk Enterprise to collect the issue details and devices&site data as necessary
- Cisco DNA Center Issues.xml:
- network_health.py: script that will run on Splunk Enterprise to collect the overall network health
- Cisco DNA Center Network Health.xml:
- security_advisories.py: script that will run on Splunk Enterprise to collect the security advisories details and devices data as necessary
- Cisco DNA Center Security Advisories.xml:
- sensors.py: script that will run on the Splunk Enterprise to collect the sensor details
- Cisco DNA Center Sensors.xml:


**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).

