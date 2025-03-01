import sys
import re
import subprocess
import os
import json
from pathlib import Path

def ensure_git_history(from_ref: str, to_ref: str):
    try:
        subprocess.run(['git', 'fetch', '--depth=1', 'origin', from_ref],
                       check=True, capture_output=True)
        subprocess.run(['git', 'fetch', '--depth=1', 'origin', to_ref],
                       check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to fetch specific commits: {e.stderr}", file=sys.stderr)
        try:
            subprocess.run(['git', 'fetch', '--unshallow'],
                           check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to unshallow repository: {e.stderr}", file=sys.stderr)

def get_git_diff(from_ref: str, to_ref: str = None) -> str:
    """Get diff using git command"""
    if os.environ.get('GITHUB_ACTIONS'):
        ensure_git_history(from_ref, to_ref)
    
    cmd = ['git', 'diff', from_ref] if to_ref is None else ['git', 'diff', from_ref, to_ref]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Git diff failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def parse_git_diff(diff_content: str, source_path: str = "", target_path: str = ""):
    """Parse git diff output and return file changes with both source and target paths."""
    new_files = []
    modified_files = []
    deleted_files = []
    
    diff_sections = diff_content.split('diff --git ')
    
    for section in diff_sections[1:]:
        match = re.search(r'a/(.+?) b/(.+?)\n', section)
        if not match:
            continue
            
        file_a, file_b = match.groups()
        
        if not file_a.startswith(source_path):
            continue
            
        target_file = file_a.replace(source_path, target_path)
        
        if 'deleted file mode' in section:
            deleted_files.append({
                'source': file_a,
                'target': target_file
            })
        else:
            if not Path(target_file).exists():
                new_files.append({
                    'source': file_a,
                    'target': target_file
                })
            else:
                modified_files.append({
                    'source': file_a,
                    'target': target_file
                })
    
    return {
        'new': new_files,
        'modified': modified_files,
        'deleted': deleted_files
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Check files between source and target paths based on git diff.'
    )
    parser.add_argument('--source', default='',
                        help='Source path')
    parser.add_argument('--target', default='',
                        help='Target path')
    parser.add_argument('--from-ref', help='Starting git reference (commit/branch)')
    parser.add_argument('--to-ref', help='Ending git reference (commit/branch)')
    parser.add_argument('--format', choices=['text', 'json'], default='json',
                        help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        if args.from_ref:
            diff_content = get_git_diff(args.from_ref, args.to_ref)
        else:
            diff_content = sys.stdin.read()
            
        changes = parse_git_diff(diff_content, args.source, args.target)
        
        if args.format == 'json':
            print(json.dumps(changes))
        else:
            if changes['new']:
                print("\nNew files requiring action:")
                for file in changes['new']:
                    print(f"  {file['source']} -> {file['target']}")
            if changes['modified']:
                print("\nModified files requiring action:")
                for file in changes['modified']:
                    print(f"  {file['source']} -> {file['target']}")
            if changes['deleted']:
                print("\nFiles to delete:")
                for file in changes['deleted']:
                    print(f"  {file['source']} -> {file['target']}")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
