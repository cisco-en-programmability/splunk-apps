<p align="center" style="color: #343a40">
  <h1 align="center">Splunk App and Add-on</h1>
</p>
<h3 align="center" style="font-size: 1.2rem;">The official Cisco DNA Center Splunk App and Add-on</h3>

>This monorepo contains both the App and Add-on for Splunk

## Cisco Products & Services:

- Cisco DNA Center (>= 2.2.3.3)

### 📖 Documentation

https://cisco-en-programmability.github.io/splunk-apps/

### ⬇️ Download

- [Splunk App on SplunkBase](https://splunkbase.splunk.com/app/)
- [Splunk Add-on on SplunkBase](https://splunkbase.splunk.com/app/)

### 💬 Support

- [Troubleshooting Guide](https://splunk.paloaltonetworks.com/troubleshoot.html)
- [Ask a Question](https://answers.splunk.com/answers/ask.html?appid= )
- [Report a bug](https://github.com/cisco-en-programmability/splunk-apps/issues)

### 🐛 Bugs / Issues / Feature Requests

Ongoing development efforts and contributions for the App or Add-on are tracked as issues in this repository.
We welcome community contributions to them. If you find problems, need an enhancement or need a new dashboard.

### 📚 App and Add-on READMEs

- [Splunk App README](Splunk_CiscoDNACenter/README.md)
- [Splunk Add-on README](Splunk-TA-cisco-dnacenter/README.md)

### 📂 File structure of this repo

- **Splunk_CiscoDNACenter**: Official Splunk App
- **Splunk-TA-cisco-dnacenter**: Official Splunk Add-on (TA)
- **.github**: CI/CD workflows
- **scripts**: Build and AppInspect validation scripts

### ⚙️ Build the package

This builds a tarball named `Splunk_CiscoDNACenter.spl` and the renamed tarball `Splunk-TA-cisco-dnacenter.spl`.

```shell
$ scripts/build.sh -a addon -l -v 1.0.0
[2022-04-06 11:32:12 CST] [INFO] Building Splunk-TA-cisco-dnacenter version 1.0.0 build local from branch develop 
[2022-04-06 11:32:14 CST] [SUCCESS] SplunkBase package is ready at _build/Splunk-TA-cisco-dnacenter-1.0.0-develop-local.spl

$ scripts/build.sh -a app -l
[2022-04-06 12:45:39 CST] [INFO] Using version from app.conf 
[2022-04-06 12:45:39 CST] [INFO] Building Splunk_CiscoDNACenter version 1.0.0 build local from branch develop 
[2022-04-06 12:45:39 CST] [SUCCESS] SplunkBase package is ready at _build/Splunk_CiscoDNACenter-1.0.0-develop-local.spl 
```


### ⬆️ Installation

- Open Splunk
- Visit the Apps management page
- Click "Install App from file"
- Choose the `Splunk-TA-cisco-dnacenter.spl` file and check the box next to "Upgrade app. Checking this will overwrite the app if it already exists."
- Click the "Upload" button.
- Repeat for the `Splunk_CiscoDNACenter.spl` file.

### 🔑 License

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
