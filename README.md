# 🌟 RealCarrier Alpha 🌟
## 基于Telnyx LNP的美国电话号码查询工具

<p align="center">
  <img src="https://img.shields.io/badge/版本-0.1.0-blue" alt="版本">
  <img src="https://img.shields.io/badge/语言-Python-green" alt="语言">
  <img src="https://img.shields.io/badge/许可证-MIT-yellow" alt="许可证">
</p>

<p align="center">
  <i>轻量级高效的美国电话号码运营商信息查询工具</i>
</p>

---

## 📋 功能概览

RealCarrier Alpha是一个轻量级命令行工具，用于查询美国电话号码的运营商信息和携号转网(LNP)状态。该工具基于Telnyx API，提供单个号码查询和批量查询功能。

| 功能 | 描述 |
|------|------|
| 🔑 安全管理API密钥 | 安全存储并管理您的Telnyx API密钥 |
| 📱 单号查询 | 快速查询单个电话号码的运营商信息 |
| 📊 批量查询 | 从CSV文件高效批量查询多个号码 |
| 💾 本地缓存 | 智能缓存查询结果，减少API调用 |
| 📄 数据导出 | 将查询结果导出为CSV格式，方便分析 |
| 🌈 彩色界面 | 精美的彩色命令行界面，优化用户体验 |

---

## 📥 安装指南

### 方式一：使用pip安装（推荐）

```bash
pip install realcarrier
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/realcarrier.git
cd realcarrier

# 安装
pip install -e .
```

---

## 🚀 使用方法

### 📝 配置API密钥

首次使用时，需要配置Telnyx API密钥：

```bash
lnp config set-key
```

### 🔍 查询单个号码

```bash
lnp lookup +14155552671
```

### 📊 批量查询

```bash
lnp batch numbers.csv -o results.csv
```

### 🧹 管理缓存

```bash
# 清除所有缓存
lnp cache clear

# 显示缓存统计信息
lnp cache info
```

---

## 📊 输出示例

### 命令行输出

```
┌───────────────────────────┐
│ 电话号码: +14155552671     │
├───────────────────────────┤
│ 运营商: T-Mobile USA, Inc. │
│ 号码类型: mobile           │
│ 携号转网: 是               │
│ 原运营商: AT&T Mobility    │
└───────────────────────────┘
```

### CSV输出示例

| 电话号码 | 运营商 | 号码类型 | 携号转网 | 原运营商 |
|---------|-------|---------|---------|---------|
| +14155552671 | T-Mobile USA, Inc. | mobile | 是 | AT&T Mobility |
| +14155552672 | Verizon Wireless | mobile | 否 | - |

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

# 安装开发依赖
pip install -e ".[dev]"
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

[MIT](LICENSE)

---

## ⚠️ 免责声明

- 本工具使用Telnyx API，可能会产生API调用费用。使用前请了解Telnyx的计费政策。
- **特别提示**：Telnyx需要完成KYC和充值才能正常使用，遇到API调用失败多数都是这个原因，Telnyx会通过邮件通知账户欠费被停用。