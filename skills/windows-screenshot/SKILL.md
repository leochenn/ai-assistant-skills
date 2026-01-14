---
name: windows-screenshot
description: 在 Windows 上进行截图。支持手动框选模式，并可选择是否隐藏命令行窗口。
---

# Windows 截图工具 (Windows Screenshot)

此 Skill 用于在 Windows 系统上调用 PowerShell 脚本进行截图。

## 核心操作模式

根据用户的指令，必须严格遵守以下两种模式：

### 1. 模式一：手动截图（隐藏窗口）—— 默认模式
- **触发指令**：用户说“截图”、“截图，隐藏窗口”或任何含义模糊的截图请求。
- **行为**：启动手动框选界面，并在框选前**隐藏**命令行窗口。
- **参数组合**：`-Interactive -HideConsole`

### 2. 模式二：手动截图（不隐藏窗口）
- **触发指令**：用户说“截图02”。
- **行为**：启动手动框选界面，但**保持**命令行窗口可见。
- **参数组合**：`-Interactive`（不带 -HideConsole）

## 使用方法

使用 `run_shell_command` 执行位于 `.gemini/skills/windows-screenshot/scripts/screenshot.ps1` 的脚本。

### 命令行语法

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Administrator\.gemini\skills\windows-screenshot\scripts\screenshot.ps1" -Path "<output_path>" [-Interactive] [-HideConsole]
```

### 参数说明

- `-Path`: (必填) 保存 PNG 图像的完整路径。
  - **约定**：始终保存到当前工作目录下的 `image` 目录。
  - **命名**：使用时间戳格式：`image/screenshot_yyyyMMdd_HHmmss.png`。
- `-Interactive`: 开启全屏遮罩，允许用户用鼠标手动框选区域。
- `-HideConsole`: 在截图界面出现前隐藏当前的 CLI/Terminal 窗口，截图完成后恢复。

## 注意事项

- **禁止自动截图**：除非用户提供具体的坐标（-Bounds），否则不要进行全屏自动截图。
- **路径创建**：脚本会自动创建不存在的目录。
- **.NET 要求**：依赖 Windows 预装的 .NET Framework。