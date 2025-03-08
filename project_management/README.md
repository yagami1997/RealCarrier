# RealCarrier 项目管理

本目录包含RealCarrier项目的管理文档和资源。

## 文档结构

### 模板文件（上传到Git）

这些是标准化的模板文件，用于创建实际的工作文档：

- **日报模板**：`templates/daily/daily_report_template.md` - 用于创建每日报告
- **周报模板**：`templates/weekly/weekly_report_template.md` - 用于创建每周报告
- **项目控制文档模板**：`templates/control/main_control_template.md` - 用于创建项目控制文档
- **项目进度模板**：`templates/PROJECT_PROGRESS_template.md` - 用于记录项目进度

### 实际文档（本地使用，不上传到Git）

这些是基于模板创建的实际工作文档，仅在本地使用：

- **日报**：`actuals/reports/daily/daily_report_YYYYMMDD.md` - 每日工作报告
- **周报**：`actuals/reports/weekly/weekly_report_weekN.md` - 每周工作总结
- **控制文档**：`control/MAIN_CONTROL.md` - 项目中央控制文档
- **项目进度**：`PROJECT_PROGRESS.md` - 项目进度跟踪文档（位于项目根目录）

### 目录说明

- `templates/` - 文档模板（上传到Git）
  - `daily/` - 日报模板
  - `weekly/` - 周报模板
  - `control/` - 控制文档模板
- `actuals/` - 实际执行的计划、进度和报告（本地使用）
  - `plans/` - 项目计划文档
  - `progress/` - 进度跟踪文档
  - `reports/` - 报告文档
    - `daily/` - 每日报告
    - `weekly/` - 每周报告
- `control/` - 项目控制文档（本地使用）
- `design/` - 设计文档
- `memos/` - 备忘录和会议记录

## 文档规范

### 命名规则

- **模板文件**：使用描述性名称，如`daily_report_template.md`
- **实际文档**：
  - 日报文件格式：`daily_report_YYYYMMDD.md`
  - 周报文件格式：`weekly_report_weekN.md`
  - 控制文档：`MAIN_CONTROL.md`
  - 项目进度文件：`PROJECT_PROGRESS.md`

### 内容规范

- **日报**：记录当天完成的工作、遇到的问题和解决方案
- **周报**：总结一周的工作进展，包括主要成就、挑战和下周计划
- **控制文档**：记录项目整体状态、关键任务和决策
- **项目进度**：详细记录项目各阶段的任务完成情况和里程碑

### 更新频率

- **日报**：每个工作日创建新文件
- **周报**：每周末创建新文件
- **控制文档**：每周更新一次，或在重大决策后更新
- **项目进度**：随时更新，反映最新的项目状态

## 使用指南

### 创建新的日报/周报

1. 从相应的模板复制内容
2. 按照命名规则命名文档（如`daily_report_20250307.md`）
3. 填写必要的基本信息
4. 添加详细的工作内容、问题和解决方案
5. 保存到相应的目录（`actuals/reports/daily/`或`actuals/reports/weekly/`）

### 文档同步

- 模板文件应当上传到Git仓库，供团队成员参考
- 实际工作文档仅在本地使用，不上传到Git仓库
- 可以使用`.gitignore`规则排除实际工作文档

## 注意事项

- 模板文件是公共资源，修改前应当与团队成员讨论
- 实际工作文档包含项目细节，应当注意保密
- 定期备份实际工作文档，避免数据丢失
- 项目进度文档(`PROJECT_PROGRESS.md`)位于项目根目录，方便查看

---

*最后更新: 2025-03-08* 