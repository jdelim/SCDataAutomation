# STEAMSync
![status: pre-release](https://img.shields.io/badge/status-pre--release-yellow)
![version](https://img.shields.io/badge/version-v0.1.0-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

## Overview
**Current Version:** v0.1.0 (Pre-release)
**STEAMSync** is a data automation tool built for the **STEAM:CODERS** organization. It streamlines the process of preparing raw class and student data for database upload and analysis.

The application ingests raw **CSV files** containing student and class information, applies standardized cleaning rules, assists with column mapping, and outputs Snowflake-ready **TSV files**.

By automating repetitive data preparation tasks, STEAMSync reduces manual work, improves accuracy, and ensures consistent formatting across all instructor-submitted data.

![demo](https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzd0d3VvZ3IzdnN5cnVhZXE4dDlrcHJkZnEzYnJ4bzAxMTJ2Nm5jOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/etQCC26rha9c1V2fzM/giphy.gif)

---

## Current Progress

| Feature | Status | Notes |
|--------|--------|-------|
| CSV parsing logic | ✅ Complete | Stable CSV ingestion (Python `csv` module) |
| Data cleaning engine (`cleaner.py`) | ✅ Complete | Working version implemented; ORG_ID improvement pending *(orgs not found in JSON should retain raw value instead of defaulting to 382)* |
| Column mapping system | ✅ Complete | Exact matching + synonym/dictionary-based header matching |
| Manual column mapping UI | ✅ Complete | PySide6 dialog for user-guided mapping of unmapped fields |
| Full desktop UI | ✅ Complete | Upload → Clean → Preview → Export workflow functioning end-to-end |
| TSV export module | ⚙️ Testing | Converts cleaned CSV to Snowflake-formatted TSV with mapped headers |
| Snowflake integration | 🔜 Planned | Future pipeline to push files directly to Snowflake |


## Roadmap / Remaining Tasks

### 1. Build a standalone executable
A packaged version of STEAMSync (Windows `.exe`) still needs to be created.  
This will allow users to run the tool without installing Python or any dependencies.

Planned options:
- **PyInstaller** (fastest, most compatible)
- **Nuitka** (more optimized, slower builds)

---

### 2. Create an offline / no-Snowflake-required version
Currently, Snowflake integration is planned but optional.

A future update will include:
- A **fully offline mode**  
- A **sample local database or example dataset**  
- No Snowflake credentials required

This ensures that anyone can run the executable without needing access to the STEAM:CODERS Snowflake environment.

---

## Current Application Flow (UI Completed)

The new GUI supports the full cleaning workflow:

1. **Upload CSV**  
2. **Run automated cleaning (cleaner.py)**  
3. **Resolve unmapped columns via dropdown dialog**  
4. **Preview raw + cleaned tables side-by-side**  
5. **Export final cleaned TSV**

This replaces the temporary CLI flow and is now the primary way to use STEAMSync.

---

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


