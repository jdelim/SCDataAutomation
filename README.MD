# STEAMSync
![status: in development](https://img.shields.io/badge/status-in%20development-yellow)
![license](https://img.shields.io/badge/license-MIT-blue)

## Overview
**STEAMSync** is a data automation tool built for the **STEAM:CODERS** organization. It streamlines the process of preparing raw class and student data for database upload and analysis.

The program takes in **raw CSV files** containing student and class information, cleans and standardizes the data, and outputs ready-to-upload **TSV or CSV** files optimized for **Snowflake** ingestion.  

By automating repetitive data preparation tasks, STEAMSync reduces manual work, improves accuracy, and ensures consistent formatting across all data sources.

## Current Progress
| Feature | Status | Notes |
|----------|---------|-------|
| CSV parsing & cleaning logic | ✅ Complete | Handles basic data normalization |
| Column mapping system | ⚙️ In Progress | Exact + fuzzy header matching |
| TSV/CSV export module | ⚙️ Testing | Outputs formatted Snowflake-ready data |
| GUI for manual column matching | 🔜 Planned | For user-assisted mapping |
| Snowflake integration | 🔜 Planned | Upload pipeline connection |

## Connecting to the STEAM:CODERS Snowflake Database
Once you have created your Snowflake account and given access to the Snowflake database by an admin, you can use **key pair authentication** to connect securely.  
Follow these steps to generate your keys, upload your public key, and configure your environment.

---
### 1. Generate your keys
Run the provided script to create your private and public keys:
```
bash generate_snowflake_keys.sh
```
This script will generate three files in your current directory:

* private_key.pem - your RSA private key (keep this private)

* private_key.der - unencrypted PKCS#8 DER key (used in Python)

* public_key.pem - your public key (upload this to Snowflake)

---
### 2. Upload Your Public Key to Snowflake
After generating your keys, log into Snowflake and run the following SQL command (replace your username and key contents):
```
ALTER USER your_username SET RSA_PUBLIC_KEY='-----BEGIN PUBLIC KEY-----
<your public key contents here>
-----END PUBLIC KEY-----';
```
---
### 3. Configure Environment Variables
Create a .env file in the project root and add your Snowflake credentials and key path:
```
USER='your_snowflake_username'
ACCOUNT='your_snowflake_account'
PRIVATE_KEY_PATH='/absolute/path/to/private_key.der'
```


