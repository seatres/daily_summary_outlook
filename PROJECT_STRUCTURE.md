# 项目目录结构

本文档说明项目的文件组织结构。

## 📁 目录结构

```
daily_summary_outlook/
├── 📄 核心文件
│   ├── main.py                 # 主程序入口
│   ├── config.py               # 配置文件
│   ├── requirements.txt        # Python 依赖
│   ├── env.example            # 环境变量模板
│   ├── README.md              # 项目说明
│   ├── CLAUDE.md              # Claude AI 开发指南
│   └── PROJECT_STRUCTURE.md   # 本文件
│
├── 📚 docs/                   # 文档目录
│   ├── README.md              # 文档索引
│   ├── 使用说明.md            # 使用指南
│   ├── 安装完成总结.md        # 安装总结
│   ├── 快速开始.md            # 快速上手
│   ├── INSTALL_IMPROVEMENTS.md # 安装改进说明
│   ├── LAUNCHD_SETUP.md       # LaunchD 设置
│   ├── IMAP快速开始.md        # IMAP 快速配置
│   ├── IMAP配置指南.md        # IMAP 详细配置
│   ├── IMAP实施完成.md        # IMAP 实施说明
│   ├── QQ邮箱配置指南.md      # QQ 邮箱配置
│   ├── 切换到QQ邮箱指南.md    # 邮箱切换指南
│   ├── 配置QQ邮箱步骤.md      # QQ 配置步骤
│   └── 配置文档索引.md        # 配置索引
│
├── 🧪 tests/                  # 测试目录
│   ├── README.md              # 测试说明
│   ├── test_outlook_imap.py   # Outlook IMAP 测试
│   └── test_qq_email.py       # QQ 邮箱测试
│
├── 🔧 scripts/                # 脚本目录
│   ├── README.md              # 脚本说明
│   ├── install_launchd.sh     # LaunchD 安装脚本
│   ├── test_installation.sh   # 安装测试脚本
│   └── com.user.dailysummary.plist # LaunchD 配置模板
│
├── 📦 workflow-tools/         # 可重用工具包
│   ├── README.md              # 工具包说明
│   ├── setup.py               # 安装配置
│   ├── validate_config.py     # 配置验证工具
│   ├── validate_dependencies.py # 依赖验证工具
│   ├── GEMINI_MODEL_CONFIG.md # Gemini 配置说明
│   ├── DEPENDENCY_*.md        # 依赖管理文档
│   ├── SECURITY_FIX_ODATA.md  # 安全修复说明
│   ├── examples/              # 使用示例
│   ├── tests/                 # 工具包测试
│   └── workflow_tools/        # 源代码
│       ├── ai_models/         # AI 模型模块
│       ├── email/             # 邮件处理模块
│       ├── notes/             # 笔记管理模块
│       ├── scheduler/         # 调度器模块
│       ├── storage/           # 存储模块
│       ├── exceptions/        # 异常定义
│       └── utils/             # 工具函数
│
├── 📊 logs/                   # 日志目录
│   ├── workflow_YYYYMMDD.log  # 工作流日志
│   ├── launchd_out.log        # LaunchD 输出
│   └── launchd_err.log        # LaunchD 错误
│
├── 📜 history/                # 历史记录目录
│   └── history_YYYYMMDD_HHMMSS.json # 执行历史
│
└── 🗂️ archived/              # 归档目录
    ├── README.md              # 归档说明
    ├── docs/                  # 已过时文档
    └── tests/                 # 已过时测试
```

## 📝 文件说明

### 核心文件
- **main.py**: 工作流主程序，协调各个模块完成邮件读取、AI 分析和结果发送
- **config.py**: 集中管理所有配置项（邮件筛选、调度时间、AI 提示词等）
- **requirements.txt**: 主程序的 Python 依赖包列表
- **env.example**: 环境变量配置模板，包含所有敏感信息的占位符

### 文档目录 (docs/)
包含所有用户文档和配置指南，方便查阅和维护。每个文档都有明确的用途。

### 测试目录 (tests/)
包含针对邮件客户端的集成测试脚本，用于验证配置和连接。

### 脚本目录 (scripts/)
包含安装、配置和维护脚本，简化部署流程。

### 工具包 (workflow-tools/)
可重用的模块化组件，采用插件式设计，可以在其他项目中复用。

### 运行时目录
- **logs/**: 自动创建，存储运行日志
- **history/**: 自动创建，存储执行历史（可配置详细程度）

### 归档目录 (archived/)
存放已过时或被替代的文件，保留以供参考。

## 🔍 查找文件

### 查找配置信息
1. 快速上手: `docs/快速开始.md`
2. 邮箱配置: `docs/IMAP配置指南.md` 或 `docs/QQ邮箱配置指南.md`
3. 定时任务: `docs/LAUNCHD_SETUP.md`

### 查找测试脚本
1. 测试 Outlook: `tests/test_outlook_imap.py`
2. 测试 QQ: `tests/test_qq_email.py`

### 查找安装脚本
1. 自动安装: `scripts/install_launchd.sh`
2. 验证安装: `scripts/test_installation.sh`

### 查找代码模块
1. 邮件处理: `workflow-tools/workflow_tools/email/`
2. AI 模型: `workflow-tools/workflow_tools/ai_models/`
3. 工具函数: `workflow-tools/workflow_tools/utils/`

## 📋 维护建议

### 添加新文档
- 放在 `docs/` 目录
- 在 `docs/README.md` 中添加索引
- 使用描述性的中文文件名

### 添加新测试
- 放在 `tests/` 目录
- 在 `tests/README.md` 中说明用途
- 遵循现有测试的命名规范

### 添加新脚本
- 放在 `scripts/` 目录
- 添加执行权限: `chmod +x script_name.sh`
- 在 `scripts/README.md` 中说明用途

### 归档文件
- 移到 `archived/` 相应子目录
- 更新 `archived/README.md` 说明归档原因
- 考虑是否完全删除

## 🎯 最佳实践

1. **保持根目录整洁**: 只保留核心配置文件
2. **文档分类清晰**: 按用途组织到相应目录
3. **及时归档**: 定期整理过时文件
4. **添加 README**: 每个目录都有说明文件
5. **使用中文命名**: 文档和说明使用中文，便于理解

