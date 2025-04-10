<div align="center">

# 🌟 RealCarrier Beta v1.1.0 🌟

<p>
  <a href="README.md">English Version</a> | <a href="README.zh.md">中文版</a>
</p>

<p>
  <img src="https://img.shields.io/badge/Version-Beta%20v1.1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Language-Python-green" alt="Language">
  <img src="https://img.shields.io/badge/License-GPL%203.0-yellow" alt="License">
</p>

<p>
  <i>Lightweight and efficient US phone number carrier information query tool (bilingual interface support)</i>
</p>

</div>

---

## 📝 Update Log

### Beta v1.1.0 (2025-04-10)
- Added geographic location information (city, state) display in query results
- Added port status and porting date information display
- Optimized carrier name display using more accurate spid_carrier_name
- Enhanced batch query results display for consistency with single number query

### Beta v1.0.1 (2025-04-09)
- **Enhanced Virtual Number Identification**: Added intelligent identification for 38 common virtual number providers
- **Improved UI Display**: Added specific labeling for virtual number providers in query results
- **Enhanced CSV Export**: Added "is_virtual" column to batch query results
- **Fixed Carrier Type Detection**: Corrected the issue where number types weren't properly identified

### Beta v1.0.0 (2025-03-06)
- Program completely restructured, now supports dual API providers: Telnyx and Twilio
- Users can choose to use one or both providers as needed
- Added provider switching functionality, easily switch in the main menu
- Optimized system information display, more accurately showing OS and processor information
- Improved error handling and internationalization support

## 📱 Project Overview

RealCarrier is a professional US phone number status query system that provides essential support for communication service providers, anti-fraud systems, and marketing compliance. Through a clean interface and powerful features, it helps users quickly obtain carrier information, number type, and local number portability status.

### Core Principles

#### Local Number Portability (LNP)

Local Number Portability is a service mandated by US telecommunications regulations that allows users to retain their original phone numbers when changing carriers. Since the Telecommunications Act of 1996, this service has become the foundation of the US telecommunications market competition, with the NPAC database recording over 600 million number transfers.

When a number is transferred, its routing information is updated while the original allocation information remains unchanged, creating challenges in identifying the real carrier. For example, a number originally assigned to AT&T may now be serviced by T-Mobile.

#### Number Types

| Type | Description |
|:------:|:-------------|
| **Physical Numbers** | Traditional phone numbers associated with actual SIM cards and physical devices, provided by traditional carriers (AT&T, Verizon, T-Mobile, etc.) |
| **Virtual Numbers** | Numbers provided through VoIP services, not dependent on specific physical locations or devices, offered by virtual operators (Twilio, Bandwidth, Telnyx, etc.) |

Distinguishing between these two types is essential for identifying potential fraudulent activities, verifying user identities, and ensuring communication compliance.

### API Providers

RealCarrier supports two leading telecommunications API providers:

- **Telnyx**: A global communications platform that provides direct access to the NPAC database, offering the most accurate number portability information
- **Twilio**: A world-leading communications API provider whose Lookup API offers phone number verification and carrier information query services
  
**Special Notice:** the IP address used during Telnyx registration and the payment method (credit card/PayPal) **must originate from the same country**. For example, if you register with a Singapore IP and pay with a US PayPal account, your registration will be rejected. However, if you register with a US IP and use a US PayPal account, it will not be rejected.

<img width="950" alt="image" src="https://github.com/user-attachments/assets/01273451-def5-45b8-9c68-efc0943229b6" />

```json
{
  "country_code": "US",
  "national_format": "(406) XXX-XXX",
  "phone_number": "+1406XXXXXXX",
  "fraud": null,
  "carrier": {
    "mobile_country_code": "",
    "mobile_network_code": "",
    "name": "T-MOBILE USA, INC.",
    "type": "mobile",
    "error_code": null,
    "normalized_carrier": "T-Mobile USA"
  },
  "caller_name": {
    "caller_name": "WIRELESS CALLER",
    "error_code": null
  },
  "nnid_override": null,
  "portability": {
    "lrn": null,
    "ported_status": "",
    "ported_date": "",
    "ocn": "6034",
    "line_type": "mobile",
    "spid": "",
    "spid_carrier_name": "SPRINT SPECTRUM L.P.- MT",
    "spid_carrier_type": "",
    "altspid": "",
    "altspid_carrier_name": "",
    "altspid_carrier_type": "",
    "city": "MISSOULA",
    "state": "Montana"
  },
  "valid_number": true,
  "record_type": "number_lookup"
}

```


## 🚀 Key Features

| Feature | Description |
|:---------|:-------------|
| 🔑 **API Key Management** | Securely store and manage your Telnyx and Twilio API keys |
| 🔄 **Dual API Providers** | Support for both Telnyx and Twilio, with flexible selection based on user needs |
| 🔍 **Single Number Query** | Quickly query carrier information for a single phone number |
| 📊 **Batch Query** | Efficiently query multiple numbers from a CSV file |
| 💾 **Smart Caching** | Multi-level caching strategy to reduce API calls and lower costs |
| 🌐 **Bilingual Interface** | Seamless switching between Chinese and English to meet different user needs |
| 💻 **Convenient CLI** | User-friendly CLI interface and advanced command-line tools |

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

# Activate virtual environment (CMD)
venv\Scripts\activate.bat
# Or (PowerShell)
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

## 💡 Usage Guide

### Launch Program

After activating the virtual environment, run the main program:

```bash
python main.py
```

<div align="center">
  <img width="900" alt="image" src="https://github.com/user-attachments/assets/69c705d0-b190-4605-9bfa-b396574970f2" />

</div>

### API Key Configuration

<div align="center">
  <img width="900" alt="API Key Configuration" src="https://github.com/user-attachments/assets/875dea2e-f086-410b-b1c6-ebabc5999074" />
</div>

1. Select "1. 🔑 API Key Management" from the main menu
2. Choose the API provider you want to configure (Telnyx or Twilio)
3. Enter the corresponding API key as prompted
4. The key will be securely stored in the local configuration file

### Single Number Query

<div align="center">
<img width="950" alt="image" src="https://github.com/user-attachments/assets/e00a0108-d180-45dc-8c69-02aff9be705d" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/a53c84a9-acb9-4c2e-a445-ed6048ee4e03" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/9bd0b913-c0ae-4917-9a19-2b6b95a788ec" />
</div>

1. Select "2. 🔍 Query Single Phone" from the main menu
2. Enter a 10-digit US phone number (e.g., 8772427372)
3. The system will display detailed information about the number, including carrier, number type, and LNP status

### Batch Query

<div align="center">
<img width="900" alt="image" src="https://github.com/user-attachments/assets/73601c3e-465c-44b1-99a8-538a55b0085f" />
</div>

<div align="center">
<img width="950" alt="image" src="https://github.com/user-attachments/assets/df1c71ab-e985-4cd6-8e76-199432f31073" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/04bd91f7-03db-4f97-b711-dc5c06131bde" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/2690e2c8-77f2-4e86-930f-cf52cef0bfd0" />
</div>

1. Select "3. 📊 Batch Query CSV File" from the main menu
2. Enter the path to the CSV file containing phone numbers
3. Specify the path for the output results file
4. The system will process all numbers in batch and generate a results file

### Cache Management

<div align="center">
  <img width="900" alt="image" src="https://github.com/user-attachments/assets/20924bcd-0e3f-4f24-8571-88eb7e571001" />

</div>

1. Select "4. 💾 Cache Management" from the main menu
2. Choose a cache operation:
   - Display cache statistics
   - Clear all cache
   - Set cache expiration time

### Language Settings

The program supports both Chinese and English interfaces. You can select "6. 🌐 Language Settings" in the main menu to switch:

- Select 1 to switch to Chinese
- Select 2 to switch to English

Language preferences will be saved and automatically applied when you restart the program.

## 📋 Advanced Usage

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
|:------------:|:-------:|:-----------:|:------:|:----------------:|
| +14155552671 | T-Mobile USA, Inc. | mobile | Yes | AT&T Mobility |
| +14155552672 | Verizon Wireless | mobile | No | - |

## 👨‍💻 Developer Resources

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
pytest
```

## ⚠️ Important Notes

- This tool uses the Telnyx and Twilio APIs, which may incur API call fees. Please understand their billing policies before use.
- **Critical Note**:
  - **Telnyx** requires completion of KYC and a deposit to function normally.
  - **Twilio** similarly requires identity verification and account funding to use API services.
- If your API account is abnormal (no deposit, incomplete verification, API anomalies, etc.), it will result in query failures. Please ensure your account status is normal first.

## ⚖️ License

This project is released under the [GNU General Public License v3.0 (GPL 3.0)](LICENSE).

## 📅 Document Information
- **Last Updated**: 2025-04-09 15:30:42 (Pacific Time)
- **Timestamp**: 1744145442
