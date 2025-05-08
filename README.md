<p align="center" style="color: #343a40">
  <h1 align="center">Splunk App and Add-on</h1>
</p>
<h3 align="center" style="font-size: 1.2rem;">The official Cisco DNA Center Splunk App and Add-on</h3>

>This monorepo contains both the App and Add-on for Splunk

## Cisco Products & Services:

- Cisco DNA Center (>= 2.2.3.3)

### ⬇️ Download

- [Splunk App on GitHub](https://github.com/cisco-en-programmability/splunk-apps/releases/download/v1.0.7/cisco-dna-center-app_102.tgz)
- [Splunk Add-on on GitHub](https://github.com/cisco-en-programmability/splunk-apps/releases/download/v1.0.7/cisco-dna-center-add-on_106.tgz)

The add-on and app are on SplunkBase!

- **Cisco DNA Center App** on: [SplunkBase Classic](https://classic.splunkbase.splunk.com/app/6669/) or [New SplunkBase](https://splunkbase.splunk.com/app/6669)

- **Cisco DNA Center Add-on** on: [SplunkBase Classic](https://classic.splunkbase.splunk.com/app/6668/) or [New SplunkBase](https://splunkbase.splunk.com/app/6668)


### 💬 Support

- [Ask a Question](https://github.com/cisco-en-programmability/splunk-apps/issues)
- [Report a bug](https://github.com/cisco-en-programmability/splunk-apps/issues)

### 🐛 Bugs / Issues / Feature Requests

Ongoing development efforts and contributions for the App or Add-on are tracked as issues in this repository.
We welcome community contributions to them. If you find problems, need an enhancement or need a new dashboard.

### 📚 App and Add-on READMEs

- [Splunk App README](https://github.com/cisco-en-programmability/splunk-apps/blob/main/Splunk-cisco-catalyst-center/README.md)
- [Splunk Add-on README](https://github.com/cisco-en-programmability/splunk-apps/blob/main/Splunk-TA-cisco-catalyst-center/README.md)

### 📂 File structure of this repo

- **Splunk-cisco-catalyst-center**: Official Splunk App
- **Splunk-TA-cisco-catalyst-center**: Official Splunk Add-on (TA)
- **.github**: CI/CD workflows
- **scripts**: Build and AppInspect validation scripts

### ⚙️ Build the package

This builds a tarball named `Splunk-cisco-catalyst-center.spl` and the renamed tarball `Splunk-TA-cisco-catalyst-center.spl`.

```shell
$ make addon v=1.0.0
[2022-04-06 14:45:32 CST] [INFO] Building Splunk-TA-cisco-catalyst-center version 1.0.0 build local from branch main 
[2022-04-06 14:45:34 CST] [INFO] Changing version from 1.0.0 to 1.0.0 build 1000 on channel default 
[2022-04-06 14:45:34 CST] [SUCCESS] SplunkBase package is ready at _build/Splunk-TA-cisco-catalyst-center-1.0.0-main-local.spl

$ make app v=1.0.0
[2022-04-06 14:45:53 CST] [INFO] Building Splunk-cisco-catalyst-center version 1.0.0 build local from branch main 
[2022-04-06 14:45:53 CST] [INFO] Changing version from 1.0.0 to 1.0.0 build 1000 on channel default 
[2022-04-06 14:45:53 CST] [SUCCESS] SplunkBase package is ready at _build/Splunk-cisco-catalyst-center-1.0.0-main-local.spl 
```


### ⬆️ Installation

- Open Splunk
- Visit the Apps management page
- Click "Install App from file"
- Choose the `Splunk-TA-cisco-catalyst-center.spl` file and check the box next to "Upgrade app. Checking this will overwrite the app if it already exists."
- Click the "Upload" button.
- Repeat for the `Splunk-cisco-catalyst-center.spl` file.

### 🔑 License

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
