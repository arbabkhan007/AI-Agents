BLANK SPREADSHEET SOURCE FOLDERS

The 11 project folders in sources/ build blank workbooks only. Python 3.11+ and XlsxWriter are required:

  python -m pip install "XlsxWriter>=3.1,<4"
  cd sources/31-landscaping
  python build_blank.py -o Blank.xlsx

Use build_blank.py --help for project-specific options. Use the same command in any other project folder. Omit --rows for normal capacity. Open the result in desktop Excel and allow recalculation. The default sheet password is premium. Do not sort, move, insert or delete ID-linked records. Save backups.

This ZIP contains no example workbooks or example transaction datasets. Editable reference data and assumptions remain, including the fitness food database and example rates in settings. Review them before use. Current-date selectors are initialized at build time where needed, and can be changed manually.

All 11 builders were run at their full default capacities and workbook ZIP/XML structure, protection, locked formulas and several common formula errors were checked. This is not proof of all calculations: Windows Excel opening, repair-free behavior, recalculation and printing were not tested in this environment. Test your important workflows in Excel and consult qualified professionals for health, tax, accounting, payroll or other regulated matters.

The standalone extract_sources.py restores the companion all-blank-spreadsheet-source-code.md with checksum verification; it is not needed to use these pre-extracted folders.
