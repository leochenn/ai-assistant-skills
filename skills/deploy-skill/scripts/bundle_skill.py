import os
import sys
import json
import argparse
import re

def get_skill_description(skill_dir):
    """Try to extract description from SKILL.md frontmatter."""
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md_path):
        return "No description provided."
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple regex to find description in YAML frontmatter
            match = re.search(r'^---\s*.*?\ndescription:\s*(.*?)\n.*?---', content, re.DOTALL | re.MULTILINE)
            if match:
                return match.group(1).strip()
    except Exception:
        pass
    return "No description provided."

def bundle_skill(skill_name):
    # 1. Locate the skill directory
    # Assumes standard location ~/.gemini/skills/
    base_skills_dir = os.path.expanduser("~/.gemini/skills")
    skill_dir = os.path.join(base_skills_dir, skill_name)

    if not os.path.exists(skill_dir):
        print(json.dumps({
            "error": f"Skill directory not found at: {skill_dir}"
        }))
        sys.exit(1)

    # 2. Get Description
    description = get_skill_description(skill_dir)

    # 3. Read all files
    files_list = []
    
    for root, dirs, files in os.walk(skill_dir):
        # Filter out git and pycache
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if file == '.DS_Store' or file.endswith('.pyc'):
                continue
                
            abs_path = os.path.join(root, file)
            # Calculate relative path for GitHub (e.g., skills/my-skill/SKILL.md)
            rel_path_from_skill = os.path.relpath(abs_path, skill_dir)
            remote_path = f"skills/{skill_name}/{rel_path_from_skill}".replace("\\", "/")
            
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                files_list.append({
                    "path": remote_path,
                    "content": content
                })
            except UnicodeDecodeError:
                # Skip binary files or handle gracefully if needed for this MVP
                print(f"Skipping binary file: {rel_path_from_skill}", file=sys.stderr)

    # 4. Output JSON
    result = {
        "skill_name": skill_name,
        "description": description,
        "files": files_list
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill_name", required=True, help="The name of the skill folder to deploy")
    args = parser.parse_args()
    
    bundle_skill(args.unit_name if hasattr(args, 'unit_name') else args.skill_name)
