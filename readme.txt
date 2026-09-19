regex-pad portable package
==========================

Purpose:
regex-pad is a portable text editor focused on search, replace, and regular expressions.

How to start:
Run regex-pad.exe in this folder.

Portable runtime policy:
Python modules should be installed into runtime/venv by module_installer.py.
Settings, cache, logs, temporary files, and install records should stay inside this folder when possible.

Cleaner:
Use module_cleaner.exe before deleting this folder.

Recommended removal order:
1. Close regex-pad.exe.
2. Run module_cleaner.exe --scan.
3. Run module_cleaner.exe --dry-run.
4. If the listed candidates are safe, run module_cleaner.exe --clean.
5. Delete the whole regex-pad folder manually.

License:
See LICENSE.txt.
