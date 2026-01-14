import argparse
import requests
import os
import datetime
import html
import sys

# Ensure requests is available
try:
    import requests
except ImportError:
    print("Error: 'requests' library is missing. Please run 'pip install requests'.")
    sys.exit(1)

def get_all_starred_repos(token):
    """
    Fetch all starred repos for the authenticated user, handling pagination.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.star+json"
    }
    
    repos = []
    page = 1
    per_page = 100
    
    print(f"Connecting to GitHub API...")
    
    while True:
        url = "https://api.github.com/user/starred"
        params = {"page": page, "per_page": per_page}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            repos.extend(data)
            print(f"Fetched page {page}, current total: {len(repos)} repositories...")
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            if hasattr(e.response, 'status_code') and e.response.status_code == 401:
                print("Error: Invalid or expired Token.")
            return []

    return repos

def format_number(count):
    if count >= 1000:
        return f"{count/1000:.1f}k"
    return str(count)

def format_date(iso_time_str):
    if not iso_time_str:
        return "N/A"
    return iso_time_str.split('T')[0]

def generate_obsidian_markdown(items, output_file, sort_by):
    # Sorting logic
    if sort_by == 'star_date':
        sorted_items = sorted(items, key=lambda x: x['starred_at'], reverse=True)
        sort_desc = "Ordered by Star Date (Newest First)"
    elif sort_by == 'stars':
        sorted_items = sorted(items, key=lambda x: x['repo']['stargazers_count'], reverse=True)
        sort_desc = "Ordered by Star Count (Highest First)"
    else:
        sorted_items = sorted(items, key=lambda x: x['starred_at'], reverse=True)
        sort_desc = "Ordered by Star Date (Newest First)"

    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Awesome GitHub Stars\n\n")
            f.write(f"> 💡 **Info:** Total {len(items)} repositories | {sort_desc} | Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            for item in sorted_items:
                repo = item['repo']
                
                name = html.escape(repo['name'])
                url = repo['html_url']
                stars_str = format_number(repo['stargazers_count'])
                lang = html.escape(repo.get("language") or "Others")
                
                star_date = format_date(item['starred_at'])
                # Use pushed_at for actual code updates, updated_at is often just metadata changes
                update_date = format_date(repo.get('pushed_at') or repo.get('updated_at'))
                
                desc_raw = repo.get('description') or "No description provided."
                desc = html.escape(desc_raw).replace('\n', ' ')

                # HTML Card Template using Obsidian CSS Variables
                card_html = (
                    '<div style="'
                    '    border: 1px solid var(--background-modifier-border);'
                    '    border-radius: 8px;'
                    '    padding: 16px;'
                    '    margin-bottom: 16px;'
                    '    background-color: var(--background-secondary);'
                    '    box-shadow: 0 1px 3px rgba(0,0,0,0.05);'
                    '    transition: all 0.2s ease;'
                    '">'
                    '    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">'
                    '        <div style="flex-grow: 1; margin-right: 10px;">'
                    f'            <a href="{url}" style="'
                    '                font-weight: 600;'
                    '                font-size: 1.1em;'
                    '                color: var(--interactive-accent);'
                    '                text-decoration: none;'
                    '                display: block;'
                    '                margin-bottom: 4px;'
                    f'            ">{name}</a>'
                    '        </div>'
                    '        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85em;">'
                    '            <span style="'
                    '                padding: 2px 8px;'
                    '                border-radius: 12px;'
                    '                background-color: var(--background-primary);'
                    '                color: var(--text-muted);'
                    '                border: 1px solid var(--background-modifier-border);'
                    f'            ">{lang}</span>'
                    f'            <span style="color: var(--text-muted);">★ {stars_str}</span>'
                    '        </div>'
                    '    </div>'
                    '    <div style="'
                    '        font-size: 0.95em;'
                    '        color: var(--text-normal);'
                    '        line-height: 1.6;'
                    '        margin-bottom: 14px;'
                    f'    ">{desc}</div>'
                    '    <div style="'
                    '        display: flex;'
                    '        justify-content: space-between;'
                    '        font-size: 0.8em;'
                    '        color: var(--text-faint);'
                    '        border-top: 1px solid var(--background-modifier-border);'
                    '        padding-top: 10px;'
                    f'    "><span>📅 Starred: {star_date}</span><span>🔄 Updated: {update_date}</span></div>'
                    '</div>'
                )
                f.write(card_html + "\n")
                
        print(f"Success! File generated: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export GitHub starred repos to Obsidian-optimized Markdown.")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--output", help="Output Markdown filename")
    parser.add_argument("--sort", choices=['star_date', 'stars'], default='star_date', help="Sort order")
    
    args = parser.parse_args()
    
    if not args.output:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Obsidian_github_star_{timestamp}.md"
    else:
        output_filename = args.output
        
    all_repos = get_all_starred_repos(args.token)
    
    if all_repos:
        generate_obsidian_markdown(all_repos, output_filename, args.sort)