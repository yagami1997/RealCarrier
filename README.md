<h1 align="center">🌟 RealCarrier Alpha 🌟</h1>

<p align="center">
  <a href="README.md">English Version</a> | <a href="README.zh.md">中文版</a>
</p>

## US Phone Number Query Tool Based on Telnyx LNP

### 📞 Project Overview: US Phone Number Status Query System (Bilingual Interface Support)

### Background & Principles

The US phone number system is a complex and dynamic network. Understanding the real status of phone numbers is crucial for communication service providers, anti-fraud systems, and marketing compliance. This project aims to provide an efficient and accurate US phone number query tool that helps users quickly obtain carrier information, number type, and local number portability status.

#### Local Number Portability (LNP)
Local Number Portability is a service mandated by US telecommunications regulations that allows users to retain their original phone numbers when changing carriers. Since the Telecommunications Act of 1996, this service has become the foundation of competition in the US telecommunications market. LNP data is managed by the industry-maintained Number Portability Administration Center (NPAC) database, which has recorded over 600 million number transfers.

When a number is transferred, its routing information is updated while the original allocation information remains unchanged, creating challenges in identifying the real carrier. For example, a number originally assigned to AT&T may now be serviced by T-Mobile.

#### Virtual Numbers vs. Physical Numbers
* **Physical Numbers**: Traditional phone numbers associated with actual SIM cards and physical devices, provided by traditional carriers (AT&T, Verizon, T-Mobile, etc.).
* **Virtual Numbers**: Numbers provided through VoIP services, not dependent on specific physical locations or devices, offered by virtual operators (Twilio, Bandwidth, Telnyx, etc.).

Distinguishing between these two types is essential for identifying potential fraudulent activities, verifying user identities, and ensuring communication compliance.

#### US Number Database Systems
US phone number information is primarily managed by the following databases:
1. **NPAC (Number Portability Administration Center)**: The authoritative database recording all number portability
2. **LERG (Local Exchange Routing Guide)**: Provides information on number block allocation
3. **OCN (Operating Company Number) Database**: Identifies carrier identities
4. **NANPA (North American Numbering Plan Administration)**: Manages North American number allocation

### Technical Approach

The RealCarrier system adopts the following technical approach to address US phone number query needs:

1. **API Integration**: Integration with Telnyx LNP API, which has direct access to the NPAC database, providing the most accurate number portability information
2. **Multi-level Caching**: Implementation of SQLite-based persistent cache and memory cache to reduce API call costs
3. **Parallel Processing**: Using asynchronous parallel technology for batch queries with intelligent rate limiting
4. **Command Line Interface**: Modern, user-friendly CLI interface built on the Rich library
5. **Modular Architecture**: Three-tier architecture (presentation layer, business logic layer, data access layer) for easy extension and maintenance

This system not only provides basic number query functionality but also addresses common industry challenges such as API rate limiting, data freshness, and large-scale processing.

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Language-Python-green" alt="Language">
  <img src="https://img.shields.io/badge/License-GPL%203.0-yellow" alt="License">
</p>

<p align="center">
  <i>Lightweight and efficient US phone number carrier information query tool (bilingual interface support)</i>
</p>

---

## 📋 Feature Overview

RealCarrier Alpha is a lightweight command-line tool for querying US phone number carrier information and Local Number Portability (LNP) status. The tool is based on the Telnyx API and provides single number and batch query capabilities.

| Feature | Description |
|---------|-------------|
| 🔑 API Key Management | Securely store and manage your Telnyx API key |
| 🔍 Single Number Query | Quickly query carrier information for a single phone number |
| 📊 Batch Query | Efficiently query multiple numbers from a CSV file |
| 💾 Cache Management | Intelligently cache query results to reduce API calls |
| ℹ️ System Information | View system status and configuration information |
| 🌐 Language Settings | Switch between Chinese and English interfaces |
| 🚀 Telnyx Guide | Get help with Telnyx account setup |

---

## 🌐 Language Settings

The program supports both Chinese and English interfaces. 
You can switch languages by selecting the "Language Settings" option in the main menu:

- Select option 6 to enter language settings
- Select 1 to switch to Chinese
- Select 2 to switch to English

Language preferences will be saved and automatically applied when you restart the program.

---

## 📥 Installation Guide

### MacOS

```bash
# Clone repository
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Windows 11

```bash
# Clone repository
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# Create virtual environment
python -m venv venv

# Activate virtual environment (in Command Prompt)
venv\Scripts\activate.bat

# Activate virtual environment (in PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Ubuntu

```bash
# Clone repository
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage Instructions

### Run the Main Program

```bash
# After activating the virtual environment
python main.py
```

After running, you will see an interactive main menu providing the following function options:
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/aff0fd2e-5bea-4353-a07e-6ce4c8f88cc9" />

1. **🔑 API Key Management** - Set or update your Telnyx API key
2. **🔍 Query Single Phone** - Query information for a single US phone number
3. **📊 Batch Query CSV File** - Batch query multiple numbers from a CSV file
4. **💾 Cache Management** - Manage local query result cache
5. **ℹ️ System Information** - View system status and statistics
6. **🌐 Language Settings** - Switch between Chinese and English interfaces
0. **❌ Exit Program** - Exit the application

### 📝 Configure API Key

When using for the first time, the program will prompt you to configure a Telnyx API key:
![image](https://github.com/user-attachments/assets/48f4d0ee-1429-43cb-bd0d-ab2ec1b6784d)

1. Select "**1. 🔑 API Key Management**" from the main menu
2. Enter your Telnyx API key as prompted
3. The key will be securely stored in the local configuration file

### 🔍 Query a Single Number
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/e2041685-9c12-4d09-a84e-5c312a8baff8" />

1. Select "**2. 🔍 Query Single Phone**" from the main menu
2. Enter a 10-digit US phone number (e.g., 8772427372)
3. The system will display detailed information about the number, including carrier, number type, and LNP status
4. If your Telnyx account has issues, including but not limited to no deposit, unverified KYC, or API abnormalities, it will result in a 403 error. Please ensure your Telnyx account is functioning normally first.

### 📊 Batch Query
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/ed9cdc2b-8cf0-4037-a66a-16a57df067d1" />
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/3f29dd78-5098-43bc-99cf-342035650fad" />

1. Select "**3. 📊 Batch Query CSV File**" from the main menu
2. Enter the path to the CSV file containing phone numbers
3. Specify the path for the output results file
4. The system will process all numbers in batch and generate a results file

### 🧹 Manage Cache
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/a8c4140b-55a1-47d8-a89e-0ce4ca6cc91a" />

1. Select "**4. 💾 Cache Management**" from the main menu

2. Choose a cache operation:
   - Display cache statistics
   - Clear all cache
   - Set cache expiration time

## 📊 Output Examples

### Command Line Output

```
┌────────────────────────────────┐
│ Phone Number: +14155552671     │
├────────────────────────────────┤
│ Carrier: T-Mobile USA, Inc.    │
│ Number Type: mobile            │
│ Ported: Yes                    │
│ Original Carrier: AT&T Mobility│
└────────────────────────────────┘
```

### CSV Output Example

| Phone Number | Carrier | Number Type | Ported | Original Carrier |
|--------------|---------|-------------|--------|-----------------|
| +14155552671 | T-Mobile USA, Inc. | mobile | Yes | AT&T Mobility |
| +14155552672 | Verizon Wireless | mobile | No | - |

## LNP Command Line Tool Usage (Advanced Users)

In addition to the interactive interface, this project also provides a command-line tool (lnp) for advanced users:

```bash
# Configure API key
lnp config set-key

# Query a single number
lnp lookup +14155552671

# Batch query
lnp batch numbers.csv -o results.csv

# Manage cache
lnp cache clear
lnp cache info
```

---

## 👨‍💻 Developer Guide

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment (Linux/Mac)
source venv/bin/activate

# Activate environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
pytest
```

---

## 📝 Usage Workflow

```
Configure API Key → Query Numbers → View/Export Results → Analyze Data
```

---

## ⚖️ License

This project is released under the [GNU General Public License v3.0 (GPL 3.0)](LICENSE).

As free software, you can redistribute and/or modify this program under the terms of the GNU General Public License as published by the Free Software Foundation. This program uses the GPL 3.0 license, which is an important way to support the free software movement and ensure that the software and its derivatives remain open and free.

---

## ⚠️ Disclaimer

- This tool uses the Telnyx API, which may incur API call fees. Please understand Telnyx's billing policy before use.
- **Special Note**: Telnyx requires completion of KYC and a deposit to function normally. Most API call failures are due to this reason. Telnyx will notify you by email if your account is suspended due to non-payment.
- **Disclaimer**: The developers of this project do not assume any legal responsibility for any secondary development, commercial applications, or other forms of sharing and use based on this code. Using this code for secondary development or commercial applications requires self-assessment of relevant risks and compliance with relevant laws and regulations, including but not limited to data privacy, telecommunications regulations, and intellectual property rights.

---

## 📅 Document Information
- **Last Updated**: March 4, 2025 00:47:21 (Pacific Time)
- **Timestamp**: 1741078041