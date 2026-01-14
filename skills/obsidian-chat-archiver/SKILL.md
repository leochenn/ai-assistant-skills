---
name: obsidian-chat-archiver
description: Archives the current chat session to an Obsidian-formatted Markdown file. Saves to 'chat/' directory with auto-generated metadata. ENSURES FULL FIDELITY of the conversation (no summarization).
---

# Obsidian Chat Archiver

This skill guides the Agent to archive the current conversation context into a structured Obsidian Markdown file.

## Core Principle: FULL FIDELITY
*   **NO SUMMARIZATION**: You must preserve the **exact** content of the conversation. Do not use ellipses `...` or placeholders like `(rest of the content)`.
*   **NO OMISSIONS**: Include every list item, table row, and code block line from the original message.
*   **EXCLUDE INTERNALS**: Do NOT include `<thought>` blocks or tool usage logs (e.g., `run_shell_command`). Only archive the conversational text exchanged between User and Agent.

## Workflow

When this skill is activated, you MUST follow these steps in order:

### Step 1: Analyze & Present History
1.  Review the conversation history currently in your context.
2.  Identify the last **5 to 10** distinct requests/messages from the User.
3.  Present them to the User as a numbered list with a short preview (first 50 chars).
    *   *Format:* `[Index] <Short Summary of User Request>`
4.  **STOP** and ask the User: "Please select the start index (e.g., 1) to archive from that point onwards."

### Step 2: Generate Content (After User Input)
Once the User provides an index:
1.  **Scope**: Select all messages (User and Agent) starting from the chosen index up to the present.
2.  **Analyze for Metadata**:
    *   **Topic**: Extract a concise 2-5 word topic.
    *   **Summary**: Generate a 1-sentence summary of the archived segment.
    *   **Tags**: Generate relevant tags (e.g., `#gemini`, `#cli`, `#education`).
3.  **Format Content**:
    *   **User Messages**: Wrap in a question Callout for visual distinction.
        ```markdown
        > [!question] User
        > Original user text here...
        ```
    *   **Gemini Messages**: Use a Level 3 heading with an emoji, followed by the **raw, unindented** text. This ensures tables and code blocks render perfectly.
        ```markdown
        ### 🤖 Gemini
        
        Full original response text here...
        ```
4.  **Construct File**:
    *   **Frontmatter**:
        ```yaml
        ---
        created: YYYY-MM-DD HH:mm
        tags: [chat, gemini, ...generated_tags]
        source: Gemini-CLI
        summary: ...
        ---
        ```
    *   **Body**: The formatted conversation sequence.

### Step 3: Save File
1.  **Generate Filename**: `chat/YYYYMMDD_{Topic}.md` (Sanitize the topic for filenames).
2.  **Check Directory**: Ensure the `chat` directory exists.
3.  **Write File**: Use the `write_file` tool to save the content.

## Example Output

**Filename**: `chat/20260113_Demo_Archive.md`

```markdown
---
created: 2026-01-13 17:45
tags: [chat, gemini, demo]
source: Gemini-CLI
summary: A full archive of the demo conversation.
---

> [!question] User
> Can you write a long list of fruits?

### 🤖 Gemini

Certainly! Here is the list you requested:

1. Apple
2. Banana
3. Cherry
4. Date
5. Elderberry
... (and so on, listing ALL items actually generated)
```