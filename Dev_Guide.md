# Telnyx LNP查询工具 - 项目计划书与开发指南

## 1. 项目概述

开发一个轻量级命令行工具，用于查询美国电话号码的LNP(Local Number Portability)信息。工具将使用Telnyx API获取号码的运营商信息和携号转网状态。这是个人使用的实用工具，无需复杂的GUI，通过命令行交互即可完成所有操作。

## 2. 功能需求

### 核心功能
- 用户自定义Telnyx API密钥配置
- 单个电话号码LNP查询
- CSV文件批量号码查询
- 查询结果美观展示
- 查询结果导出CSV功能
- 本地缓存减少API调用

### 交互需求
- 清晰简洁的命令行界面
- 彩色输出增强可读性
- 进度展示(批量查询时)
- 交互式API密钥设置

## 3. 技术栈选择

- **编程语言**: Python 3.8+
- **命令行框架**: Click
- **HTTP请求**: Requests
- **格式化输出**: Rich
- **CSV处理**: Pandas/CSV模块
- **本地存储**: SQLite或JSON文件

## 4. 项目结构

```
telnyx-lnp-tool/
├── lnptool/                # 主代码包
│   ├── __init__.py
│   ├── cli.py              # 命令行入口
│   ├── telnyx.py           # Telnyx API交互
│   ├── lookup.py           # 查询业务逻辑
│   ├── config.py           # 配置管理
│   ├── cache.py            # 缓存管理
│   └── utils.py            # 工具函数
├── setup.py                # 安装配置
├── README.md               # 说明文档
└── requirements.txt        # 依赖列表
```

## 5. 接口设计

### 命令行接口

```
lnp config         # 配置管理(API密钥等)
lnp lookup NUMBER  # 查询单个号码
lnp batch FILE     # 批量查询CSV文件
lnp cache          # 缓存管理
```

### Telnyx API接口

使用Telnyx Lookup API `/v2/number_lookup/{number}` 端点，请求参数设置`type=carrier`获取携号转网信息。

## 6. 开发阶段计划

### 阶段1: 基础框架
- 创建项目结构
- 实现命令行参数解析
- 实现配置管理

### 阶段2: 核心功能
- 实现Telnyx API调用
- 实现单个号码查询
- 实现结果格式化显示

### 阶段3: 高级功能
- 实现缓存机制
- 实现批量查询
- 实现CSV导出

### 阶段4: 完善与测试
- 增强错误处理
- 添加进度显示
- 完善交互体验

## 7. 开发指南

### 配置管理
- 使用`~/.lnptool/`目录存储配置
- 保存API密钥时考虑基本安全性(权限控制)
- 提供命令行界面管理配置

### Telnyx API交互
- 封装Requests库调用Telnyx API
- 处理API错误和重试逻辑
- 格式化API响应数据

### 缓存设计
- 使用SQLite或JSON文件本地缓存查询结果
- 默认24小时缓存过期时间
- 提供缓存清理功能

### 号码处理
- 标准化电话号码格式(例如: +1XXXXXXXXXX)
- 验证电话号码格式
- 支持多种输入格式

### 批量处理
- 使用Pandas或CSV模块处理CSV文件
- 合理控制API请求速率
- 实现断点续传功能

### 用户体验
- 使用Rich库提供彩色输出
- 添加进度条显示批量处理进度
- 清晰展示API响应状态和错误

## 8. 关键代码示例

### 命令行入口示例
```python
import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """Telnyx LNP查询工具"""
    pass

@cli.command()
@click.argument('number')
def lookup(number):
    """查询单个电话号码"""
    # 实现查询逻辑
    pass

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', default='results.csv')
def batch(file, output):
    """批量查询CSV文件中的号码"""
    # 实现批量查询逻辑
    pass

if __name__ == '__main__':
    cli()
```

### Telnyx API调用示例
```python
import requests

def lookup_number(number, api_key):
    """调用Telnyx API查询号码信息"""
    url = f"https://api.telnyx.com/v2/number_lookup/{number}"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"type": "carrier"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()
```

## 9. 部署与使用

### 安装方法
```bash
# 从源码安装
pip install -e .

# 或使用pip直接安装
pip install telnyx-lnp-tool
```

### 基本使用流程
1. 设置API密钥: `lnp config set-key`
2. 查询单个号码: `lnp lookup +14155552671`
3. 批量查询: `lnp batch numbers.csv -o results.csv`

## 10. 注意事项

### API限制
- Telnyx API有请求频率限制
- 批量查询时控制请求速率
- 考虑API费用因素

### 安全性
- 本地安全存储API密钥
- 不记录完整查询结果到日志
- 妥善处理CSV中的敏感数据

### 性能考虑
- 使用缓存减少重复API调用
- 批量查询时优化内存使用
- 大文件处理分批进行

## 11. 扩展思路

### 可能的功能扩展
- 添加更多Telnyx API功能(号码验证、欺诈检测等)
- 集成其他提供商的API(如Bandwidth、Neustar)
- 添加报表和统计功能

### 性能优化
- 实现并发查询
- 优化缓存策略
- 使用异步IO提高性能

## 12. 开发环境设置

建议使用虚拟环境:
```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 13. 依赖列表

**核心依赖:**
- click>=8.0.0
- requests>=2.25.0
- rich>=10.0.0
- pandas>=1.3.0

**开发依赖:**
- pytest>=6.0.0
- black>=21.5b2
- pylint>=2.8.0

---

这个项目计划书为你提供了开发Telnyx LNP查询工具的框架和指南。按照这个计划，你可以实现一个功能完整、交互友好、适合个人使用的命令行工具。