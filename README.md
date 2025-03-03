# RealCarrier Alpha 0.1.0
## 基于Telnyx LNP的美国电话号码查询工具

RealCarrier Alpha是一个轻量级命令行工具，用于查询美国电话号码的运营商信息和携号转网(LNP)状态。该工具基于Telnyx API，提供单个号码查询和批量查询功能。

## 功能特点

- 🔑 安全管理Telnyx API密钥
- 📱 查询单个电话号码的运营商信息
- 📊 从CSV文件批量查询号码
- 💾 本地缓存减少API调用
- 📄 查询结果导出为CSV
- 🌈 彩色命令行界面优化用户体验

## 安装

### 使用pip安装

```bash
pip install realcarrier
```

### 从源码安装

```bash
git clone https://github.com/yourusername/realcarrier.git
cd realcarrier
pip install -e .
```

## 使用方法

### 配置API密钥

首次使用时，需要配置Telnyx API密钥：

```bash
lnp config set-key
```

### 查询单个号码

```bash
lnp lookup +14155552671
```

### 批量查询

```bash
lnp batch numbers.csv -o results.csv
```

### 管理缓存

```bash
lnp cache clear  # 清除所有缓存
lnp cache info   # 显示缓存统计信息
```

## 输出示例

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

## 开发

### 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 许可证

[MIT](LICENSE)

## 免责声明

- 本工具使用Telnyx API，可能会产生API调用费用。使用前请了解Telnyx的计费政策。
- ⚠️友情提示，Telnyx需要完成KPY和充值才能正常使用，遇到API调用失败多数都是这个原因，而且Telnyx会给你发邮件说你的账户欠费被停用。