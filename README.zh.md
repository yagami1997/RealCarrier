<h1 align="center">🌟 RealCarrier Alpha 🌟</h1>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a>
</p>

## 基于Telnyx LNP的美国电话号码查询工具

### 📞 项目概述：美国电话号码状态查询系统（支持中英文双语界面）

### 背景与原理

美国电话号码系统是一个复杂而动态的网络，了解号码的真实状态对于通信服务提供商、反欺诈系统以及市场营销合规至关重要。本项目旨在提供一个高效、准确的美国电话号码查询工具，帮助用户快速获取号码的运营商信息、类型和携号转网状态。

#### 携号转网(Local Number Portability, LNP)
携号转网是美国电信法规强制要求的服务，允许用户在更换运营商时保留原有电话号码。自1996年电信法案以来，这一服务成为美国电信市场竞争的基础。携号转网数据由行业共同维护的Number Portability Administration Center (NPAC)数据库管理，记录了超过6亿次的号码转移。

当号码被转移时，其路由信息会更新，但原始分配信息保持不变，这导致了识别真实运营商的挑战。例如，最初分配给AT&T的号码可能现在由T-Mobile提供服务。

#### 虚拟号码与实体号码
* **实体号码**：与实际SIM卡和物理设备关联的传统电话号码，由传统运营商(AT&T、Verizon、T-Mobile等)提供。
* **虚拟号码**：通过VoIP服务提供的号码，不依赖于特定物理位置或设备，由虚拟运营商(Twilio、Bandwidth、Telnyx等)提供。

区分这两种类型对于识别潜在的欺诈活动、验证用户身份和确保通信合规性至关重要。

#### 美国号码数据库系统
美国电话号码信息主要由以下数据库管理：
1. **NPAC (Number Portability Administration Center)**：记录所有携号转网的权威数据库
2. **LERG (Local Exchange Routing Guide)**：提供号码块分配信息
3. **OCN (Operating Company Number) 数据库**：识别运营商身份
4. **NANPA (North American Numbering Plan Administration)**：管理北美号码分配

### 技术路线

RealCarrier系统采用以下技术路线解决美国电话号码查询需求：

1. **API集成**：与Telnyx LNP API集成，Telnyx拥有NPAC数据库的直接访问权，提供最准确的号码携带信息
2. **多级缓存**：实现基于SQLite的持久化缓存和内存缓存，减少API调用成本
3. **并行处理**：采用异步并行技术处理批量查询，同时实现智能限流
4. **命令行界面**：基于Rich库构建现代化、用户友好的CLI界面
5. **模块化架构**：采用三层架构（表现层、业务逻辑层、数据访问层），便于扩展和维护

该系统不仅提供了号码查询的基本功能，还解决了行业内常见的API限流、数据新鲜度和大规模处理等挑战。

<p align="center">
  <img src="https://img.shields.io/badge/版本-0.1.0-blue" alt="版本">
  <img src="https://img.shields.io/badge/语言-Python-green" alt="语言">
  <img src="https://img.shields.io/badge/许可证-GPL%203.0-yellow" alt="许可证">
</p>

<p align="center">
  <i>轻量级高效的美国电话号码运营商信息查询工具（支持中英文双语界面）</i>
</p>

---

## 📋 功能概览

RealCarrier Alpha是一个轻量级命令行工具，用于查询美国电话号码的运营商信息和携号转网(LNP)状态。该工具基于Telnyx API，提供单个号码查询和批量查询功能。

| 功能 | 描述 |
|------|------|
| 🔑 API密钥管理 | 安全存储并管理您的Telnyx API密钥 |
| 🔍 单号查询 | 快速查询单个电话号码的运营商信息 |
| 📊 批量查询 | 从CSV文件高效批量查询多个号码 |
| 💾 缓存管理 | 智能缓存查询结果，减少API调用 |
| ℹ️ 系统信息 | 查看系统状态和配置信息 |
| 🌐 语言设置 | 支持中英文双语界面切换 |
| 🚀 Telnyx指南 | 获取Telnyx账户设置帮助 |

---

## 🌐 语言设置

程序支持中英文双语界面，您可以在主菜单中选择"语言设置"选项进行切换：

- 选择选项6进入语言设置
- 选择1切换到中文
- 选择2切换到英文

语言设置会被保存，下次启动程序时会自动应用上次选择的语言。

---

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

# 激活虚拟环境（在命令提示符CMD中）
venv\Scripts\activate.bat

# 激活虚拟环境（在PowerShell中）
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

---

## 🚀 使用方法

### 运行主程序

```bash
# 激活虚拟环境后
python main.py
```

运行后，您将看到交互式主菜单，提供以下功能选项：
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/aff0fd2e-5bea-4353-a07e-6ce4c8f88cc9" />

1. **🔑 API密钥管理** - 设置或更新您的Telnyx API密钥
2. **🔍 查询单个电话** - 查询单个美国电话号码信息
3. **📊 批量查询CSV文件** - 从CSV文件批量查询多个号码
4. **💾 缓存管理** - 管理本地查询结果缓存
5. **ℹ️  系统信息** - 查看系统状态和统计信息
6. **🌐 语言设置** - 切换中英文界面语言
0. **❌ 退出程序** - 退出应用程序

### 📝 配置API密钥

首次使用时，程序会提示您配置Telnyx API密钥：
![image](https://github.com/user-attachments/assets/48f4d0ee-1429-43cb-bd0d-ab2ec1b6784d)

1. 从主菜单选择 "**1. 🔑 API密钥管理**"
2. 根据提示输入您的Telnyx API密钥
3. 密钥将安全存储在本地配置文件中

### 🔍 查询单个号码
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/e2041685-9c12-4d09-a84e-5c312a8baff8" />

1. 从主菜单选择 "**2. 🔍 查询单个电话**"
2. 输入10位美国电话号码（例如：8772427372）
3. 系统将显示该号码的详细信息，包括运营商、号码类型和携号转网状态
4. 若您的Telnyx账户异常，包括不限于没有充值、KYC没有验证、API异常都会导致403错误，请先保证Telnyx账户正常

### 📊 批量查询
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/ed9cdc2b-8cf0-4037-a66a-16a57df067d1" />
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/3f29dd78-5098-43bc-99cf-342035650fad" />

1. 从主菜单选择 "**3. 📊 批量查询CSV文件**"
2. 输入包含电话号码的CSV文件路径
3. 指定结果输出文件路径
4. 系统将批量处理所有号码并生成结果文件

### 🧹 管理缓存
<img width="1114" alt="image" src="https://github.com/user-attachments/assets/a8c4140b-55a1-47d8-a89e-0ce4ca6cc91a" />

1. 从主菜单选择 "**4. 💾 缓存管理**"

2. 选择缓存操作：
   - 显示缓存统计信息
   - 清除全部缓存
   - 设置缓存过期时间

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

## LNP命令行工具使用 (高级用户)

除了交互式界面外，本项目也提供命令行工具(lnp)供高级用户使用：

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

---

## 👨‍💻 开发者指南

### 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境 (Linux/Mac)
source venv/bin/activate

# 激活环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
pytest
```

---

## 📝 使用流程

```
配置API密钥 → 查询号码 → 查看/导出结果 → 分析数据
```

---

## ⚖️ 许可证

本项目基于[GNU通用公共许可证第3版(GPL 3.0)](LICENSE)发布。

作为自由软件，您可以按照自由软件基金会(Free Software Foundation)发布的GNU通用公共许可证的条款，对本程序进行再分发和修改。本程序使用GPL 3.0许可证，使用GPL许可证是支持自由软件运动的重要方式，确保软件及其派生作品始终保持开放和自由。

---

## ⚠️ 免责声明

- 本工具使用Telnyx API，可能会产生API调用费用。使用前请了解Telnyx的计费政策。
- **特别提示**：Telnyx需要完成KYC和充值才能正常使用，遇到API调用失败多数都是这个原因，Telnyx会通过邮件通知账户欠费被停用。
- **免责声明**：本项目开发者对任何基于本代码的二次开发、商业化应用或其他形式的分享和使用不承担任何法律责任。使用本代码进行二次开发或商业应用需自行评估相关风险并遵守相关法律法规，包括但不限于数据隐私、电信法规和知识产权等方面的规定。

---

## 📅 文档信息
- **最后更新日期**: 2025-03-04 00:47:21 (Pacific Time)
- **时间戳**: 1741078041