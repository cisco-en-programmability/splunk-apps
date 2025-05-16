
Cisco Catalyst Center Add-on for Splunk
==================================

* **Authors:** - Cisco Systems

### Description ###
 
The Cisco Catalyst Center Add-on for Splunk allows a Splunk® Enterprise
or Splunk Cloud administrator to collect data from Cisco Catalyst Center APIs.

The add-on collects:
- the overall client health data
- the overall client summary data
- the compliance details and devices data
- the overall device health and devices data.
- the issue details and devices & site data as necessary.
- the overall network health
- the security advisories details and devices data as necessary

After Splunk indexes the events, you can consume the data using the
pre-built dashboard panels included with the add-on, with Splunk Enterprise
Security, or with the Cisco Catalyst Center App for Splunk.

### SSL Configuration ###
1. By default, the API calls from the Cisco Catalyst Add-on for Splunk would be verified by SSL. The configurations are present in `$SPLUNK_HOME/etc/apps/Splunk-TA-cisco-catalyst-center/default/splunk_ta_cisco_catalyst_center_settings.conf` file:
```
[additional_parameters]
verify_ssl = True
```
2. In order to make unverified calls, change the SSL verification to False. To do that, navigate to `$SPLUNK_HOME/etc/apps/Splunk-TA-cisco-catalyst-center/local/splunk_ta_cisco_catalyst_center_settings.conf` file and change the verify_ssl parameter value to `False` under additional_parameters stanza. Create a stanza if its not present already.
3. To add a custom SSL certificate to the certificate chain, use the option available in the user interface while configuring a Catalyst Center or Cyber Vision account.
4. Restart the Splunk in order for the changes to take effect.

### Documentation ###

**Release Notes:** https://github.com/cisco-en-programmability/splunk-apps/releases

Copyright (C) 2022 Cisco Systems. All Rights Reserved.