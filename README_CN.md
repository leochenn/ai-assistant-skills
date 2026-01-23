# AI 助手技能工具箱 (AI Assistant Skills Toolkit)

精选的技能和实用程序集合，旨在增强 AI 助手（如 Gemini、Claude、Codex 等）的功能。

## 📦 包含的技能

### 1. github-star-exporter
将你在 GitHub 上星标的仓库导出为格式化的 Markdown 文件。支持按日期或星标数量排序。非常适合在 Obsidian 等知识库中备份或整理你的星标内容。

### 2. json-canvas
用于处理 JSON Canvas 格式 (`.canvas`) 的工具。创建可视化的节点、边缘、组和连接。适用于思维导图和数据结构可视化。

### 3. obsidian-bases
操作 Obsidian Bases (`.base` 文件) 的实用程序。在 Obsidian 内创建类似数据库的视图、过滤器、公式和摘要。

### 4. obsidian-chat-archiver
将当前的聊天会话（如本次会话！）存档为 Obsidian 风格的 Markdown 文件。通过元数据保留对话的完整保真度。

### 5. obsidian-markdown
创建丰富的 Obsidian Markdown 的助手，包括支持维基链接 `[[Link]]`、提示框 (Callouts)、前置属性 (Frontmatter) 和嵌入内容。

### 6. skill-creator
用于创建新技能的元技能指南和模板。遵循定义工具、描述和说明的标准结构。

### 7. windows-screenshot
在 Windows 上进行截图的实用程序。支持特定区域选择和窗口处理。

### 8. deploy-skill
自动化将本地开发的 Skill 发布到 leochenn/ai-assistant-skills GitHub 仓库。支持自动打包文件、提取描述、更新 README 和 README_CN，并执行 Git 推送。

### 9. brainstorming
在进行任何创意工作（如创建功能、构建组件、添加功能或修改行为）之前，你必须使用此技能。在实施之前探索用户意图、需求和设计。

### 10. prompt-engineering
在编写命令、钩子、代理技能、子代理提示词或任何其他 LLM 交互时使用此技能，包括优化提示词、改进 LLM 输出或设计生产级提示词模板。

### 11. vercel-react-best-practices
来自 Vercel 工程团队的 React 和 Next.js 性能优化指南。此技能应在编写、审查或重构 React/Next.js 代码时使用，以确保最佳性能模式。在涉及 React 组件、Next.js 页面、数据获取、包大小优化或性能改进的任务时触发。

### 12. web-design-guidelines
根据 Web 界面指南审查 UI 代码。当被要求“审查我的 UI”、“检查无障碍性”、“审计设计”、“审查 UX”或“根据最佳实践检查我的网站”时使用。

### 13. docx
综合性的 Word 文档处理工具。支持创建、编辑和分析 .docx 文件，包括处理修订模式 (Track Changes)、添加评论、保留格式以及文本提取。适用于从头创建新文档或编辑具有复杂要求的现有文档。

### 14. image-gen
统一的 AI 生图工具，整合了 Gemini、豆包 (Doubao) 和千问 (Qwen) 的图像生成能力。支持根据用户指令自动路由到不同的模型，默认使用 Gemini。

## 🚀 使用方法

每个技能文件夹通常包含一个带有详细说明和元数据的 `SKILL.md` 文件。

## 🛡️ 隐私

这是一个个人工具包。请确保不要将敏感的 API 令牌或秘密提交到此仓库。请使用环境变量或命令行参数进行身份验证。
