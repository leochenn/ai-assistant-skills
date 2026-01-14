---
name: deploy-skill
description: 自动化将本地开发的 Skill 发布到 leochenn/ai-assistant-skills GitHub 仓库。支持自动打包文件、提取描述、更新 README 和 README_CN，并执行 Git 推送。
---

# Deploy Skill (技能发布工具)

此技能用于将用户本地开发好的 Skill 一键发布到远程 GitHub 仓库。

## 触发条件
- 当用户说“上传 skills”、“发布技能”、“deploy skill”或指定要上传某个技能时。

## 执行流程

### 第一步：打包本地技能
1.  首先，确定用户想要上传的 **技能名称** (folder name)。
2.  执行脚本 `scripts/bundle_skill.py` 读取本地文件和元数据。
    ```bash
    python .gemini/skills/deploy-skill/scripts/bundle_skill.py --skill_name "<skill_name>"
    ```
3.  **脚本将返回 JSON 数据**，包含：
    - `files`: 该技能下所有文件的路径和内容列表。
    - `description`: 从 `SKILL.md` 提取的英文描述。

### 第二步：获取远程仓库状态
1.  调用 GitHub MCP 工具 `get_file_contents` 读取以下两个文件：
    - `README.md`
    - `README_CN.md`
    - **Owner**: `leochenn`
    - **Repo**: `ai-assistant-skills`

### 第三步：更新 README 文档
在内存中修改读取到的 README 内容：
1.  **检查重复**：如果 README 中已存在该技能名称，则**跳过添加条目**（仅更新文件）。
2.  **确定序号**：查找当前列表的最后一个序号（例如 "### 7."），新技能为 "### 8."。
3.  **追加内容**：
    - **README.md (英文)**:
        ```markdown
        ### [Index]. [skill_name]
        [description from script]
        ```
    - **README_CN.md (中文)**:
        - 你必须将英文描述翻译成**简体中文**。
        ```markdown
        ### [Index]. [skill_name]
        [翻译后的中文描述]
        ```

### 第四步：推送到 GitHub
调用 `push_files` 工具一次性提交所有更改。

- **Owner**: `leochenn`
- **Repo**: `ai-assistant-skills`
- **Branch**: `main`
- **Message**: `Deploy skill: [skill_name]`
- **Files**: 
    - 包含脚本返回的 `files` 列表（注意：脚本返回的路径 is 相对路径，直接使用即可）。
    - 包含更新后的 `README.md` 和 `README_CN.md`。

## 异常处理
- 如果脚本报错（如找不到目录），请直接告知用户检查 `~/.gemini/skills/` 下是否存在该文件夹。
- 如果是更新现有技能，只需覆盖文件，不要在 README 中重复添加条目。
