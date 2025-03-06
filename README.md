<div align="center">

# 🌟 RealCarrier Beta v1.0.0 🌟

<p>
  <a href="README.md">English Version</a> | <a href="README.zh.md">中文版</a>
</p>

<p>
  <img src="https://img.shields.io/badge/Version-Beta%20v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Language-Python-green" alt="Language">
  <img src="https://img.shields.io/badge/License-GPL%203.0-yellow" alt="License">
</p>

<p>
  <i>Lightweight and efficient US phone number carrier information query tool (bilingual interface support)</i>
</p>

</div>

---

## 📱 Project Overview

RealCarrier is a professional US phone number status query system that provides essential support for communication service providers, anti-fraud systems, and marketing compliance. Through a clean interface and powerful features, it helps users quickly obtain carrier information, number type, and local number portability status.

### Core Principles

#### Local Number Portability (LNP)

Local Number Portability is a service mandated by US telecommunications regulations that allows users to retain their original phone numbers when changing carriers. Since the Telecommunications Act of 1996, this service has become the foundation of the US telecommunications market competition, with the NPAC database recording over 600 million number transfers.

When a number is transferred, its routing information is updated while the original allocation information remains unchanged, creating challenges in identifying the real carrier. For example, a number originally assigned to AT&T may now be serviced by T-Mobile.

#### Number Types

| Type | Description |
|------|-------------|
| **Physical Numbers** | Traditional phone numbers associated with actual SIM cards and physical devices, provided by traditional carriers (AT&T, Verizon, T-Mobile, etc.) |
| **Virtual Numbers** | Numbers provided through VoIP services, not dependent on specific physical locations or devices, offered by virtual operators (Twilio, Bandwidth, Telnyx, etc.) |

Distinguishing between these two types is essential for identifying potential fraudulent activities, verifying user identities, and ensuring communication compliance.

### API Providers

RealCarrier supports two leading telecommunications API providers:

- **Telnyx**: A global communications platform that provides direct access to the NPAC database, offering the most accurate number portability information
- **Twilio**: A world-leading communications API provider whose Lookup API offers phone number verification and carrier information query services

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
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
  <img width="800" alt="Main Interface" src="https://github.com/user-attachments/assets/aff0fd2e-5bea-4353-a07e-6ce4c8f88cc9">
</div>

### API Key Configuration

<div align="center">
  <img width="800" alt="API Key Configuration" src="https://github.com/user-attachments/assets/48f4d0ee-1429-43cb-bd0d-ab2ec1b6784d">
</div>

1. Select "1. 🔑 API Key Management" from the main menu
2. Choose the API provider you want to configure (Telnyx or Twilio)
3. Enter the corresponding API key as prompted
4. The key will be securely stored in the local configuration file

### Single Number Query

<div align="center">
  <img width="800" alt="Single Number Query" src="https://github.com/user-attachments/assets/e2041685-9c12-4d09-a84e-5c312a8baff8">
</div>

1. Select "2. 🔍 Query Single Phone" from the main menu
2. Enter a 10-digit US phone number (e.g., 8772427372)
3. The system will display detailed information about the number, including carrier, number type, and LNP status

### Batch Query

<div align="center">
  <img width="800" alt="Batch Query" src="https://github.com/user-attachments/assets/ed9cdc2b-8cf0-4037-a66a-16a57df067d1">
</div>

<div align="center">
  <img width="800" alt="Batch Query Results" src="https://github.com/user-attachments/assets/3f29dd78-5098-43bc-99cf-342035650fad">
</div>

1. Select "3. 📊 Batch Query CSV File" from the main menu
2. Enter the path to the CSV file containing phone numbers
3. Specify the path for the output results file
4. The system will process all numbers in batch and generate a results file

### Cache Management

<div align="center">
  <img width="800" alt="Cache Management" src="https://github.com/user-attachments/assets/a8c4140b-55a1-47d8-a89e-0ce4ca6cc91a">
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
|--------------|---------|-------------|--------|-----------------|
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

## 📝 Update Log

### Beta v1.0.0 (2025-03-06)
- Program completely restructured, now supports dual API providers: Telnyx and Twilio
- Users can choose to use one or both providers as needed
- Added provider switching functionality, easily switch in the main menu
- Optimized system information display, more accurately showing OS and processor information
- Improved error handling and internationalization support

## ⚖️ License

This project is released under the [GNU General Public License v3.0 (GPL 3.0)](LICENSE).

## 📅 Document Information
- **Last Updated**: 2025-03-06 12:30:00 (Pacific Time)
- **Timestamp**: 1741264200
