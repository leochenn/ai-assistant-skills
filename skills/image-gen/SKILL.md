---
name: image-gen
description: 统一的 AI 生图 Skill，支持 Gemini、豆包 (Doubao) 和千问 (Qwen)。当用户指令包含“生图”、“生成图片”或“生成图”时触发。
---

# Image Gen

此 Skill 是一个全能的生图工具，整合了 Gemini、豆包和千问的生图能力。

## 触发逻辑与路由 (Routing Logic)

**AI 请遵循以下逻辑处理用户请求：**

1.  **触发条件**：当用户输入包含 “生图”、“生成图片”、“生成图” 等关键词。
2.  **意图识别与路由**：
    *   如果指令包含 **“豆包”** (例如：“豆包生图”、“用豆包画...”) -> 执行 `scripts/main-doubao.py`
    *   如果指令包含 **“千问”** (例如：“千问生图”、“Qwen画图...”) -> 执行 `scripts/main-qianwen.py`
    *   如果指令包含 **“Gemini”** (例如：“Gemini生图...”) -> 执行 `scripts/main-gemini.py`
    *   **默认情况**：如果未指定模型 (例如：“帮我生图...”) -> **默认执行 `scripts/main-gemini.py`**

3.  **提示词清洗 (Prompt Cleaning)**：
    *   在执行脚本前，**必须**从用户的原始指令中**移除**以下触发词，只保留描述画面的核心内容：
        *   移除词汇：`Gemini生图`, `豆包生图`, `千问生图`, `生图`, `生成图片`, `生成图`, `Gemini`, `豆包`, `千问`
        *   去除首尾空格。

## 环境要求 (Prerequisites)

执行前请确保 Windows 系统环境变量已配置：
- **`SKILLS_PYTHON`**: Python 解释器绝对路径 (必需)

## 执行指令 (Usage)

请根据路由结果选择对应的脚本执行。

### 1. Gemini 生图 (默认)

```powershell
# 原始指令: "Gemini生图 画一只猫" -> 清洗后: "画一只猫"
& "$env:SKILLS_PYTHON" "scripts\main-gemini.py" "画一只猫" "output_gemini.png"
```

### 2. 豆包 (Doubao) 生图

```powershell
# 原始指令: "豆包生图 赛博朋克风格" -> 清洗后: "赛博朋克风格"
& "$env:SKILLS_PYTHON" "scripts\main-doubao.py" "赛博朋克风格" "output_doubao.png"
```

### 3. 千问 (Qwen) 生图

```powershell
# 原始指令: "千问生图 水墨画" -> 清洗后: "水墨画"
& "$env:SKILLS_PYTHON" "scripts\main-qianwen.py" "水墨画" "output_qianwen.png"
```
