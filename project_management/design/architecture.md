# RealCarrier Alpha - 架构设计
## 基于Telnyx LNP的美国电话号码查询工具

## 文档信息

**项目名称**: RealCarrier Alpha
**副标题**: 基于Telnyx LNP的美国电话号码查询工具
**文档类型**: 架构设计文档
**版本**: 1.0.0
**日期**: 2025-03-03
**作者**: 我

## 1. 概述

### 1.1 项目简介

Telnyx LNP查询工具是一个命令行应用程序，用于查询电话号码的运营商信息和携号转网(Local Number Portability, LNP)状态。该工具利用Telnyx提供的API服务获取电话号码信息，同时提供本地缓存功能，支持批量查询和多种输出格式。

### 1.2 设计目标

- 提供简洁的命令行界面，方便用户查询电话号码信息
- 支持单个和批量查询模式
- 实现本地缓存，减少API调用，提高性能，支持离线操作
- 支持多种输出格式，满足不同场景需求
- 优化错误处理，提供友好的用户反馈
- 确保代码结构清晰，便于维护和扩展

## 2. 系统架构

### 2.1 整体架构

系统采用分层架构设计，主要包含以下层次：

1. **命令行界面层(CLI Layer)**: 处理用户输入和参数解析
2. **应用逻辑层(Application Layer)**: 实现核心业务逻辑
3. **服务层(Service Layer)**: 封装外部API调用和缓存机制
4. **数据访问层(Data Access Layer)**: 管理本地数据存储
5. **格式化层(Formatting Layer)**: 处理输出格式转换

![架构图](https://placeholder-for-architecture-diagram.com)

### 2.2 模块组织

项目模块组织如下：

```
lnptool/
├── __init__.py           # 包初始化文件
├── cli.py                # 命令行界面实现
├── config.py             # 配置管理
├── telnyx_api.py         # Telnyx API接口封装
├── cache.py              # 缓存管理
├── formatter.py          # 输出格式化
├── models.py             # 数据模型定义
├── processors.py         # 批处理实现
├── utils.py              # 通用工具函数
└── exceptions.py         # 异常定义
```

## 3. 模块设计

### 3.1 命令行界面(CLI)模块

**职责**: 解析命令行参数，调用相应的应用逻辑处理请求，显示结果

**主要功能**:
- 参数解析
- 命令分发
- 结果展示
- 错误提示

**关键类/函数**:
- `cli.main()`: 应用入口点
- `cli.lookup_command()`: 处理单个号码查询
- `cli.batch_command()`: 处理批量查询
- `cli.clear_cache_command()`: 处理缓存清理

### 3.2 Telnyx API模块

**职责**: 封装与Telnyx API的交互

**主要功能**:
- API请求构建
- 响应解析
- 错误处理
- 结果转换

**关键类/函数**:
- `TelnyxAPI`: API客户端类
- `lookup_number()`: 查询单个号码
- `CarrierInfo`: 运营商信息数据类
- `PortabilityInfo`: 携号转网信息数据类

### 3.3 缓存模块

**职责**: 管理本地缓存，减少API调用

**主要功能**:
- 缓存存储
- 缓存查询
- 缓存更新
- 缓存过期处理

**关键类/函数**:
- `Cache`: 缓存管理类
- `get_from_cache()`: 从缓存获取数据
- `save_to_cache()`: 保存数据到缓存
- `clear_cache()`: 清理缓存

### 3.4 格式化模块

**职责**: 处理不同输出格式的转换

**主要功能**:
- JSON格式化
- CSV格式化
- 表格格式化
- 自定义格式支持

**关键类/函数**:
- `Formatter`: 格式化基类
- `JSONFormatter`: JSON格式化
- `CSVFormatter`: CSV格式化
- `TableFormatter`: 表格格式化

### 3.5 处理器模块

**职责**: 实现批量处理逻辑

**主要功能**:
- 并行处理
- 错误处理
- 进度跟踪
- 结果聚合

**关键类/函数**:
- `BatchProcessor`: 批处理类
- `process_batch()`: 处理批量查询
- `parallelize()`: 并行执行查询

## 4. 数据模型

### 4.1 主要数据结构

**CarrierInfo**:
```python
class CarrierInfo:
    name: str
    type: str
    mobile_network_code: str
    mobile_country_code: str
    previous_carrier: Optional[Dict]
```

**PortabilityInfo**:
```python
class PortabilityInfo:
    portable: bool
    ported: bool
    spid: str
    ocn: str
    lrn: str
```

**LookupResult**:
```python
class LookupResult:
    phone_number: str
    carrier: CarrierInfo
    portability: PortabilityInfo
    success: bool
    error: Optional[str]
```

### 4.2 缓存数据结构

缓存采用JSON格式存储，结构如下：

```json
{
  "phone_number": {
    "timestamp": "ISO-format-timestamp",
    "data": {
      // LookupResult serialized data
    },
    "ttl": 86400
  }
}
```

## 5. 接口设计

### 5.1 命令行接口

**单个查询**:
```
lnp lookup <phone_number> [--format <format>] [--output <file>]
```

**批量查询**:
```
lnp batch <input_file> [--format <format>] [--output <file>] [--parallel <num>]
```

**缓存管理**:
```
lnp cache clear [--older-than <days>]
```

### 5.2 API接口

**Telnyx API Endpoint**:
```
GET https://api.telnyx.com/v2/number_lookup/{phone_number}
```

**请求头**:
```
Authorization: Bearer YOUR_API_KEY
Accept: application/json
```

**响应结构**:
```json
{
  "data": {
    "phone_number": "+1234567890",
    "carrier": {
      "name": "Carrier Name",
      "type": "mobile",
      "mobile_network_code": "123",
      "mobile_country_code": "456",
      "previous_carrier": {...}
    },
    "portability": {
      "portable": true,
      "ported": false,
      "spid": "123456",
      "ocn": "1234",
      "lrn": "1234567890"
    }
  }
}
```

## 6. 错误处理

### 6.1 错误类型

- `APIError`: API调用相关错误
- `CacheError`: 缓存操作错误
- `ValidationError`: 输入验证错误
- `FormatError`: 格式转换错误
- `ConfigError`: 配置相关错误

### 6.2 错误处理策略

- 所有错误都包含明确的错误代码和描述信息
- CLI层捕获所有异常并提供友好的错误信息
- 批处理模式下，单个号码的错误不会中断整体处理
- 关键错误记录到日志文件
- 网络错误支持自动重试

## 7. 安全设计

### 7.1 API密钥管理

- API密钥存储在用户主目录下的配置文件中
- 配置文件权限限制为仅当前用户可读
- 支持通过环境变量设置API密钥
- 不在日志中记录API密钥

### 7.2 数据保护

- 缓存数据存储在用户主目录下的应用数据目录中
- 敏感信息不持久化存储
- 支持定期清理缓存数据

## 8. 性能考虑

### 8.1 并行处理

- 批量查询支持并行处理，默认并行度根据CPU核心数设置
- 使用线程池管理并行任务
- 实现限流机制，避免超出API调用限制

### 8.2 缓存优化

- 缓存采用分级结构，提高查询效率
- 支持可配置的缓存过期时间
- 实现缓存预热机制，提高首次查询性能
- 大型缓存文件采用分片存储，避免内存溢出

## 9. 扩展性设计

### 9.1 插件架构

- 格式化器采用插件架构，便于添加新的输出格式
- 支持自定义缓存后端
- 提供事件钩子，便于集成外部系统

### 9.2 API适配器

- 使用适配器模式封装API调用，便于支持其他API提供商
- 配置驱动的API连接器，无需修改代码即可切换API提供商

## 10. 部署与配置

### 10.1 安装方式

- 提供PyPI包安装: `pip install telnyx-lnp-tool`
- 支持从源码安装: `pip install -e .`

### 10.2 配置选项

- API密钥配置
- 缓存目录配置
- 缓存过期时间配置
- 并行处理线程数配置
- 日志级别配置

### 10.3 依赖管理

- 关键依赖:
  - requests: HTTP请求
  - click: 命令行接口
  - tabulate: 表格格式化
  - pydantic: 数据验证
  - ujson: 高性能JSON处理

## 11. 测试策略

### 11.1 单元测试

- 使用pytest框架
- 为每个模块编写单元测试
- 使用mock对象模拟外部依赖

### 11.2 集成测试

- 测试模块间交互
- 测试缓存与API调用的协作
- 测试命令行界面与应用逻辑的集成

### 11.3 性能测试

- 批量处理性能测试
- 并行处理性能测试
- 缓存性能测试

## 12. 文档计划

### 12.1 用户文档

- 安装指南
- 基本使用教程
- 命令参考
- 配置指南
- 常见问题解答

### 12.2 开发者文档

- 架构概述
- API参考
- 扩展指南
- 贡献指南

## 13. 项目里程碑

- **里程碑1**: 基础功能实现（单个查询）
- **里程碑2**: 缓存机制实现
- **里程碑3**: 批量处理功能实现
- **里程碑4**: 多格式输出支持
- **里程碑5**: 性能优化和测试
- **里程碑6**: 文档完善和发布

## 14. 参考资料

- [Telnyx API文档](https://developers.telnyx.com/docs/api)
- [Python Click文档](https://click.palletsprojects.com/)
- [Python Requests文档](https://requests.readthedocs.io/)
- [Number Portability概念解释](https://en.wikipedia.org/wiki/Local_number_portability)

---

## 版本历史

| 版本 | 日期 | 描述 | 作者 |
|------|------|------|------|
| 1.0.0 | 2025-03-03 | 初始版本 | 我 | 

## 时间信息
- 文档生成时间（PST）: 2025-03-03 17:20:00
- 最后更新时间（PST）: 2025-03-03 17:20:00 