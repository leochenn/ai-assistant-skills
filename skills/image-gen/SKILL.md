---
name: image-gen
description: 使用 Gemini、豆包或千问进行 AI 绘画。支持 "生图"、"画图" 指令。
---

# Image Generation Skill

## Overview

此 Skill 包含用于生成图像的 Python 脚本。所有核心逻辑均位于 `scripts/` 目录下。

## Model Routing Logic (路由逻辑)

AI **必须**严格按照以下优先级选择模型：

1.  **Doubao (豆包)**: 仅当用户指令包含 "豆包"、"Doubao" 时触发。
    *   *Script*: `scripts/main-doubao.py`
2.  **Qwen (千问)**: 仅当用户指令包含 "千问"、"Qwen" 时触发。
    *   *Script*: `scripts/main-qianwen.py`
3.  **Gemini (默认)**: **任何其他情况**（包括未指定模型、仅说"生图"等），**必须**默认使用 Gemini。
    *   *Script*: `scripts/main-gemini.py`

## Execution Environment (CRITICAL / 核心规则)
**1. Interpreter Mandate (解释器强制):**
*   **🚫 禁止 (FORBIDDEN)**: 严禁直接使用 `python`、`python.exe` 或 `python3` 命令开头。这会导致环境错误。
*   **✅ 必须 (REQUIRED)**: **必须** 使用 PowerShell 变量调用语法 `& "$env:SKILLS_PYTHON"` 来启动脚本。

**2. Path Resolution Rules (路径解析规则):**
由于 Shell 的当前工作目录 (CWD) 可能与本 Skill 的安装目录不同，执行前必须：
*   **Locate**: 确认 `scripts/` 文件夹的**绝对路径**。
*   **Prepend**: 在构建命令时，将绝对路径添加到脚本文件名前。

## Usage Examples

> **⚠️ AI 执行前检查**:
> 1. 根据路由逻辑选择了正确的模型吗？(默认应为 Gemini)
> 2. 是否使用了 `$env:SKILLS_PYTHON`？
> 3. 是否使用了脚本的绝对路径？

**1. Gemini (Default / 默认)**
*用户: "画一只猫", "生图 赛博朋克"*
```powershell
& "$env:SKILLS_PYTHON" "scripts/main-gemini.py" "一只猫" "output.png"
```

**2. Doubao (豆包)**
*用户: "豆包生图", "用豆包画..."
```powershell
& "$env:SKILLS_PYTHON" "scripts/main-doubao.py" "赛博朋克风格" "output.png"
```

**3. Qwen (千问)**
*用户: "千问生图", "Qwen画..."
```powershell
& "$env:SKILLS_PYTHON" "scripts/main-qianwen.py" "水墨画" "output.png"
```
