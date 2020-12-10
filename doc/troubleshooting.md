# Troubleshooting

- If the program hung itself up or crashed (especially after adding/removing formulas), usually simply restarting it resolves the issue. In case the program doesn’t seem to respond, please note that tableaus for largish (sets of) formulas may take some time to compute. If problems persist, you can check whether there is useful information in the log file `pyPL/pyPL.log`. 
- If the formula or structure you entered won't update, you probably made a typo. Unfortunately there are no error messages from the parser telling you what exactly went wrong; you will have to check back with this documentation to see where the problem might be.  
- If no output file opens and a `.tex` file but no `.pdf` file was generated, compiling the `.tex` file via `pdflatex` probably went wrong. Try to compile the `.tex` file manually to see what the error is (perhaps a missing package). If LaTeX causes problems, select plain text instead of LaTeX PDF output in the settings. 
- If no output file opens, the automatic file opening via `xdg-open` probably isn't working on your machine. You can find all your output files in `pyPL/output`.  
