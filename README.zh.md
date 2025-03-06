<div align="center">

# 🌟 RealCarrier Beta v1.0.0 🌟

<p>
  <a href="README.md">English Version</a> | <a href="README.zh.md">中文版</a>
</p>

<p>
  <img src="https://img.shields.io/badge/版本-Beta%20v1.0.0-blue" alt="版本">
  <img src="https://img.shields.io/badge/语言-Python-green" alt="语言">
  <img src="https://img.shields.io/badge/许可证-GPL%203.0-yellow" alt="许可证">
</p>

<p>
  <i>轻量级高效的美国电话号码运营商信息查询工具（支持中英文双语界面）</i>
</p>

</div>

---

## 📱 项目概述

RealCarrier是一款专业的美国电话号码状态查询系统，为通信服务提供商、反欺诈系统和市场营销合规提供必要支持。通过简洁的界面和强大的功能，帮助用户快速获取号码的运营商信息、类型和携号转网状态。

### 核心原理

#### 携号转网 (Local Number Portability, LNP)

携号转网是美国电信法规强制要求的服务，允许用户在更换运营商时保留原有电话号码。自1996年电信法案以来，这项服务已成为美国电信市场竞争的基础，NPAC数据库已记录超过6亿次号码转移。

当号码被转移时，路由信息会更新但原始分配信息保持不变，这导致了识别真实运营商的挑战。例如，最初分配给AT&T的号码可能现在由T-Mobile提供服务。

#### 号码类型

| 类型 | 描述 |
|------|------|
| **实体号码** | 与实际SIM卡和物理设备关联的传统电话号码，由AT&T、Verizon、T-Mobile等传统运营商提供 |
| **虚拟号码** | 通过VoIP服务提供的号码，不依赖特定物理位置或设备，由Twilio、Bandwidth、Telnyx等虚拟运营商提供 |

区分这两种类型对于识别潜在的欺诈活动、验证用户身份和确保通信合规性至关重要。

### API供应商

RealCarrier支持两家领先的电信API供应商：

- **Telnyx**: 全球通信平台，提供直接访问NPAC数据库的能力，是本工具的核心数据来源之一
- **Twilio**: 全球领先的通信API提供商，其Lookup API提供电话号码验证和运营商信息查询服务

## 🚀 功能亮点

| 功能 | 描述 |
|------|------|
| 🔑 **API密钥管理** | 安全存储并管理您的Telnyx和Twilio API密钥 |
| 🔄 **双API供应商** | 支持Telnyx和Twilio，用户可根据需求灵活选择 |
| 🔍 **单号查询** | 快速查询单个电话号码的运营商信息 |
| 📊 **批量查询** | 从CSV文件高效批量查询多个号码 |
| 💾 **智能缓存** | 采用多级缓存策略减少API调用，降低成本 |
| 🌐 **双语界面** | 支持中英文无缝切换，满足不同用户需求 |
| 💻 **便捷命令行** | 提供用户友好的CLI界面及高级命令行工具 |

## 📥 安装指南

### MacOS

```bash
# 克隆仓库
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### Windows 11

```bash
# 克隆仓库
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（CMD）
venv\Scripts\activate.bat
# 或（PowerShell）
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### Ubuntu

```bash
# 克隆仓库
git clone https://github.com/yagami1997/realcarrier.git
cd realcarrier

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 💡 使用指南

### 启动程序

激活虚拟环境后，运行主程序：

```bash
python main.py
```

<div align="center">
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/2a49eaa5-e27d-4970-8edf-a98d69fd7f29" />
</div>

### API密钥配置

<div align="center">
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/875dea2e-f086-410b-b1c6-ebabc5999074" />
</div>

1. 从主菜单选择 "1. 🔑 API密钥管理"
2. 选择要配置的API供应商(Telnyx或Twilio)
3. 根据提示输入相应的API密钥
4. 密钥将安全存储在本地配置文件中

### 单号查询

<div align="center">
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/2833c9a1-e58e-494b-b45d-1e76e18a1f73" />
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/c11cbb48-09fe-4457-9c5c-6213abe3d7d9" />
</div>

1. 从主菜单选择 "2. 🔍 查询单个电话"
2. 输入10位美国电话号码（例如：8772427372）
3. 系统将显示该号码的详细信息，包括运营商、号码类型和携号转网状态

### 批量查询

<div align="center">
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/6f83dd68-5b2b-4e3f-b5db-0a7673f11256" />
</div>

<div align="center">
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/cf8742f6-4eca-4d2f-99ee-5068491b7c8b" />
</div>

1. 从主菜单选择 "3. 📊 批量查询CSV文件"
2. 输入包含电话号码的CSV文件路径
3. 指定结果输出文件路径
4. 系统将批量处理所有号码并生成结果文件

### 缓存管理

<div align="center">
<img width="800" alt="缓存管理" src="https://github.com/user-attachments/assets/a8c4140b-55a1-47d8-a89e-0ce4ca6cc91a">
</div>

1. 从主菜单选择 "4. 💾 缓存管理"
2. 选择所需的缓存操作：
   - 显示缓存统计信息
   - 清除全部缓存
   - 设置缓存过期时间

### 语言设置

程序支持中英文双语界面，您可以在主菜单中选择"6. 🌐 语言设置"进行切换：

- 选择1切换到中文
- 选择2切换到英文

语言偏好会被保存，下次启动程序时自动应用。

## 📋 高级用法

除了交互式界面外，本项目还提供命令行工具(lnp)供高级用户使用：

```bash
# 配置API密钥
lnp config set-key

# 查询单个号码
lnp lookup +14155552671

# 批量查询
lnp batch numbers.csv -o results.csv

# 管理缓存
lnp cache clear
lnp cache info
```

## 📊 输出示例

### 命令行输出

```
┌────────────────────────────────┐
│ 电话号码: +14155552671         │
├────────────────────────────────┤
│ 运营商: T-Mobile USA, Inc.     │
│ 号码类型: mobile               │
│ 携号转网: 是                   │
│ 原运营商: AT&T Mobility        │
└────────────────────────────────┘
```

### CSV输出示例

| 电话号码 | 运营商 | 号码类型 | 携号转网 | 原运营商 |
|---------|-------|---------|---------|---------|
| +14155552671 | T-Mobile USA, Inc. | mobile | 是 | AT&T Mobility |
| +14155552672 | Verizon Wireless | mobile | 否 | - |

## 👨‍💻 开发者资源

### 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
pytest
```

## ⚠️ 注意事项

- 本工具使用Telnyx和Twilio API，可能会产生API调用费用。使用前请了解相关的计费政策。
- **重要提示**：
  - **Telnyx**需要完成KYC和充值才能正常使用。
  - **Twilio**同样需要完成身份验证和账户充值才能使用API服务。
- 若API账户异常（未充值、身份验证未完成、API异常等）都会导致查询失败，请先确保账户状态正常。

## 📝 更新日志

### Beta v1.0.0 (2025-03-06)
- 程序完成重构，现在支持双供应商API：Telnyx和Twilio
- 用户可以根据需要选择使用其中一个或两个供应商
- 添加了供应商切换功能，可在主菜单中轻松切换
- 优化了系统信息显示，更准确地显示操作系统和处理器信息
- 改进了错误处理和国际化支持

## ⚖️ 许可证

本项目基于[GNU通用公共许可证第3版(GPL 3.0)](LICENSE)发布。

## 📅 文档信息
- **最后更新**: 2025-03-06 12:30:00 (Pacific Time)
- **时间戳**: 1741264200
