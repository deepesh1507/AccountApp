"""
Quick script to fix theme colors across all modules
Replaces all fg_color="white" and fg_color="#f5f5f5" with theme-aware tuples
"""

import re
from pathlib import Path

# Define files to process
modules_dir = Path(__file__).parent
files_to_fix = [
    # New modules
    "journal_entries.py",
    "ledger.py",
    "gst_tax.py",
    "inventory.py",
    # Existing modules
    "chart_of_accounts.py",
    "clients.py",
    "invoice.py",
    "expenses.py",
    "home_screen.py",
    "select_company.py",
    "create_company.py",
    "company_login.py",
    "edit_company.py"
]

# Replacements to make
replacements = [
    # Main content frames (white to theme-aware)
    (r'fg_color="white"', 'fg_color=("white", "gray20")'),
    (r"fg_color='white'", 'fg_color=("white", "gray20")'),
    # Background frames (light gray to theme-aware)
    (r'fg_color="#f5f5f5"', 'fg_color=("gray90", "gray13")'),
    (r'fg_color="#e3f2fd"', 'fg_color=("#e3f2fd", "gray25")'),  # Light blue backgrounds
    (r'fg_color="#f0f0f0"', 'fg_color=("gray94", "gray15")'),
]

def fix_file(filepath):
    """Fix theme colors in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath.name}")
            return True
        else:
            print(f"⏭️  Skipped: {filepath.name} (no changes needed)")
            return False
    except Exception as e:
        print(f"❌ Error in {filepath.name}: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("🔧 Fixing theme colors across all modules...\n")
    
    fixed_count = 0
    for filename in files_to_fix:
        filepath = modules_dir / filename
        if filepath.exists():
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n✨ Done! Fixed {fixed_count} files.")
