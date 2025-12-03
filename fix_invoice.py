with open('modules/invoice.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 440-448 (orphaned except block and extra-indented code)
# Replace with properly indented code
new_lines = lines[:440] + [
    '        # Disable fields if read_only\n',
    '        if read_only:\n',
    '            form.save_btn.configure(state="disabled")\n',
    '            id_entry.configure(state="disabled")\n',
    '            client_combo.configure(state="disabled")\n',
    '            date_picker.entry.configure(state="disabled")\n',
    '            status_combo.configure(state="disabled")\n'
] + lines[454:]

with open('modules/invoice.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed invoice.py")
