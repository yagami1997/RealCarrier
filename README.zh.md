<div align="center">

# 🌟 RealCarrier Beta v1.1.0 🌟

<p>
  <a href="README.md">English Version</a> | <a href="README.zh.md">中文版</a>
</p>

<p>
  <img src="https://img.shields.io/badge/版本-Beta%20v1.1.0-blue" alt="版本">
  <img src="https://img.shields.io/badge/语言-Python-green" alt="语言">
  <img src="https://img.shields.io/badge/许可证-GPL%203.0-yellow" alt="许可证">
</p>

<p>
  <i>轻量级高效的美国电话号码运营商信息查询工具（支持中英文双语界面）</i>
</p>

</div>

---

## 更新日志

### Beta v1.1.0 (2025-04-10)
- 添加地理位置信息（城市、州）显示
- 添加携号转网状态和日期信息显示
- 优化运营商名称显示，使用更准确的spid_carrier_name
- 改进批量查询结果展示，与单个号码查询保持一致

### Beta v1.0.1 (2025-04-09)
- **增强虚拟号码识别**: 添加了针对38家常见虚拟号码提供商的智能识别功能
- **改进界面显示**: 在查询结果中为虚拟号码提供商添加了专门标识
- **增强CSV导出**: 在批量查询结果中添加了"is_virtual"列
- **修复运营商类型检测**: 解决了号码类型未被正确识别的问题

### Beta v1.0.0 (2025-03-06)
- 程序完成重构，现在支持双供应商API：Telnyx和Twilio
- 用户可以根据需要选择使用其中一个或两个供应商
- 添加了供应商切换功能，可在主菜单中轻松切换
- 优化了系统信息显示，更准确地显示操作系统和处理器信息
- 改进了错误处理和国际化支持

## 📱 项目概述

RealCarrier是一款专业的美国电话号码状态查询系统，为通信服务提供商、反欺诈系统和市场营销合规提供必要支持。通过简洁的界面和强大的功能，帮助用户快速获取号码的运营商信息、类型和携号转网状态。

### 核心原理

#### 携号转网 (Local Number Portability, LNP)

携号转网是美国电信法规强制要求的服务，允许用户在更换运营商时保留原有电话号码。自1996年电信法案以来，这项服务已成为美国电信市场竞争的基础，NPAC数据库已记录超过6亿次号码转移。

当号码被转移时，路由信息会更新但原始分配信息保持不变，这导致了识别真实运营商的挑战。例如，最初分配给AT&T的号码可能现在由T-Mobile提供服务。

#### 号码类型

| 类型 | 描述 |
|:------:|:------|
| **实体号码** | 与实际SIM卡和物理设备关联的传统电话号码，由AT&T、Verizon、T-Mobile等传统运营商提供 |
| **虚拟号码** | 通过VoIP服务提供的号码，不依赖特定物理位置或设备，由Twilio、Bandwidth、Telnyx等虚拟运营商提供 |

区分这两种类型对于识别潜在的欺诈活动、验证用户身份和确保通信合规性至关重要。

### API供应商

RealCarrier支持两家领先的电信API供应商：

- **Telnyx**: 全球通信平台，提供直接访问NPAC数据库的能力，可获取最准确的号码携带信息
- **Twilio**: 全球领先的通信API提供商，其Lookup API提供电话号码验证和运营商信息查询服务
- 特别提示：注册Telnyx时候的IP地址和支付使用的银行卡/Paypal信息必须在一个国家，例如：用新加坡IP注册Telnyx，用Paypal US支付就会被拒绝。用美国IP注册Telnyx，用Paypal注册就不会被拒绝。

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
## 📱 Telnyx Number Lookup API 开发者指南

本指南为开发者提供将Telnyx Number Lookup API集成到RealCarrier项目的必要信息。Number Lookup API可检索美国电话号码的综合信息，包括运营商详情、号码携带状态和地理位置信息。

### 🔑 前提条件与账户设置

1. **创建Telnyx账户**
   - 在[Telnyx.com](https://telnyx.com/sign-up)注册
   - 完成KYC（了解您的客户）验证流程
   - 为账户充值所需的最低金额

2. **API密钥获取**
   - 在Telnyx管理门户中导航至API密钥部分
   - 为您的应用程序生成新的API密钥
   - 安全存储此密钥，因为所有API请求都需要它

3. **IP兼容性注意事项**
   - 确保注册过程中使用的IP地址与您的支付方式所在国家匹配
   - 例如，使用美国境内的PayPal账户应该搭配美国IP地址进行注册

### 📋 理解Number Lookup API

Number Lookup API提供美国电话号码的详细信息，特别强调以下方面：

1. **运营商信息**
   - 当前运营商详情
   - 线路类型（移动、固定、VoIP）
   - 移动国家和网络代码（如适用）

2. **号码携带数据**
   - 本地号码携带（LNP）状态
   - 通过SPID获取原始运营商信息
   - 携带日期（当号码被转移时）
   - OCN（运营公司编号）

3. **地理详情**
   - 城市和州信息
   - 资费中心数据

4. **可选功能**
   - 来电者姓名信息
   - 欺诈风险评估
   - 附加运营商详情

### 📊 API响应结构

API返回的JSON响应包含以下关键部分：

1. **基本号码信息**
   - `country_code`：国家代码（例如"US"）
   - `national_format`：号码的格式化显示
   - `phone_number`：完整的E.164格式号码
   - `valid_number`：表示号码有效性的布尔值

2. **运营商部分**
   - `name`：运营商的官方名称
   - `normalized_carrier`：运营商名称的标准化版本
   - `type`：线路类型（移动、固定、voip）

3. **号码携带部分**
   - `ported_status`：表示号码是否已被携带
   - `ported_date`：最近一次携带的日期
   - `spid_carrier_name`：原始运营商名称（最准确）
   - `city`和`state`：地理位置

4. **附加信息**
   - `caller_name`：注册名称信息（如可用）
   - `fraud`：风险评估数据（如请求）

### 💡 集成最佳实践

1. **错误处理**
   - 实现针对API速率限制的强大错误处理
   - 考虑可能的网络连接问题
   - 优雅地处理无效电话号码格式

2. **缓存策略**
   - 实现本地缓存以存储查询结果
   - 为缓存数据设置适当的过期时间
   - 考虑为频繁查询的号码使用数据库存储

3. **速率限制管理**
   - 跟踪API使用情况，避免超出限制
   - 为重试尝试实现指数退避策略
   - 考虑对多个号码进行批量处理

4. **数据解释**
   - 关注`spid_carrier_name`获取最准确的运营商信息
   - 使用`portability`数据确定号码是否已被转移
   - 利用地理信息进行区域分析

### 📊 虚拟号码检测

识别虚拟号码（由VoIP服务提供的号码）：

1. 查找API响应中的以下指标：
   - `carrier.type`值为"voip"
   - 与虚拟提供商相关的特定运营商名称

2. 参考RealCarrier中包含的虚拟运营商数据库：
   - 系统维护着38+个常见虚拟号码提供商的列表
   - 将运营商名称与此数据库进行比对，以进行准确识别

### 📝 在RealCarrier中的配置

1. **API提供商选择**
   - 在RealCarrier主菜单中，选择"API密钥管理"
   - 选择"Telnyx"作为您的提供商
   - 在提示时输入您的API密钥

2. **测试您的集成**
   - 使用单个号码查询功能测试您的API密钥
   - 验证是否返回所有预期的数据字段
   - 确认正确处理不同类型的号码

3. **调整缓存设置**
   - 根据您的需求配置缓存过期时间
   - 平衡减少API调用和保持数据新鲜度之间的关系

### ⚠️ 重要考虑因素

1. **API成本**
   - 请注意，每次查询都会根据Telnyx的定价产生费用
   - 监控使用情况以控制开支

2. **数据准确性**
   - 号码携带信息通常在24小时内更新
   - 某些虚拟号码可能无法100%准确识别

3. **账户要求**
   - 确保您的Telnyx账户保持资金充足
   - 完成所有验证步骤以维持API访问权限

### 通过遵循本指南，您将能够有效地在RealCarrier项目中集成和利用Telnyx Number Lookup API，为美国电话号码提供准确的运营商和号码携带信息。

---

## 🚀 功能亮点

| 功能 | 描述 |
|:------:|:------|
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
 <img width="900" alt="image" src="https://github.com/user-attachments/assets/69c705d0-b190-4605-9bfa-b396574970f2" />
</div>

### API密钥配置

<div align="center">
  <img width="900" alt="API密钥配置" src="https://github.com/user-attachments/assets/875dea2e-f086-410b-b1c6-ebabc5999074" />
</div>

1. 从主菜单选择 "1. 🔑 API密钥管理"
2. 选择要配置的API供应商(Telnyx或Twilio)
3. 根据提示输入相应的API密钥
4. 密钥将安全存储在本地配置文件中

### 单号查询

<div align="center">
<img width="950" alt="image" src="https://github.com/user-attachments/assets/e00a0108-d180-45dc-8c69-02aff9be705d" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/a53c84a9-acb9-4c2e-a445-ed6048ee4e03" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/0252d2dc-bda1-4179-a129-9e813f66c52f" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/9bd0b913-c0ae-4917-9a19-2b6b95a788ec" />
</div>

1. 从主菜单选择 "2. 🔍 查询单个电话"
2. 输入10位美国电话号码（例如：8772427372）
3. 系统将显示该号码的详细信息，包括运营商、号码类型和携号转网状态

### 批量查询

<div align="center">
<img width="950" alt="image" src="https://github.com/user-attachments/assets/73601c3e-465c-44b1-99a8-538a55b0085f" />
</div>

<div align="center">
<img width="950" alt="image" src="https://github.com/user-attachments/assets/df1c71ab-e985-4cd6-8e76-199432f31073" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/04bd91f7-03db-4f97-b711-dc5c06131bde" />
<img width="950" alt="image" src="https://github.com/user-attachments/assets/2690e2c8-77f2-4e86-930f-cf52cef0bfd0" />
</div>

1. 从主菜单选择 "3. 📊 批量查询CSV文件"
2. 输入包含电话号码的CSV文件路径
3. 指定结果输出文件路径
4. 系统将批量处理所有号码并生成结果文件

### 缓存管理

<div align="center">
  <img width="900" alt="image" src="https://github.com/user-attachments/assets/20924bcd-0e3f-4f24-8571-88eb7e571001" />
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
|:-------:|:-----:|:-------:|:-------:|:-------:|
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
  - **Telnyx** 需要完成KYC和充值才能正常使用。
  - **Twilio** 同样需要完成身份验证和账户充值才能使用API服务。
- 若API账户异常（未充值、身份验证未完成、API异常等）都会导致查询失败，请先确保账户状态正常。

## ⚖️ 许可证

本项目基于[GNU通用公共许可证第3版(GPL 3.0)](LICENSE)发布。

## 📅 文档信息
- **最后更新**: 2025-04-09 15:30:42 (Pacific Time)
- **时间戳**: 1744145442
