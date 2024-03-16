
###	SCAN LOG FILE tool	###
------------------------------

Author: Alexey Schilp 
		alexey.schilp@gmail.com
		https://www.upwork.com/freelancers/~018a854d0e18abadd7?mp_source=share


COMMON INSTRUCTIONS
-------------------

1) You don't need to have Python installed on your PC, Python is inside the .exe file

2) Executable file scan_log_file_v3.exe and cofiguration settings file scanLogFile_settings_conf_json.txt should be in the same directory

3) Don't rename cofiguration settings file scanLogFile_settings_conf_json.txt

4) If you run .exe file, console window will be opened and will be providing you with information about how process is going.
Please don't close the console window until the program finishes (you will see the line with FINISHED or STOPPED in the window.


5) Output file naming convention:
logfile: qwerty.abc -> output file: qwerty_output.csv  


CONFIGURATION SETTINGS FILE INSTRUCTIONS
----------------------------------------

YOU SHOULD:

Cofiguration settings file scanLogFile_settings_conf_json.txt has a JSON structure inside, so please keep the structure:

1) Keep { at the begining and } at the end of the file.

2) Keep : before the pathes and before logfiles list.

3) Keep , after the pathes and between logfile names

4) Don't type , after the last logfile name.

5) Keep [ before and ] after the list of logfiles.

6) Keep all text, including the names of the parameters and their values (pathes, logfile names) in the quotes " " .


YOU CAN:

A) You can use / or \ in the pathes, both options are good.

B) You can add a slash ( \ or / ) at the end of the path or skip it, it doesn't matter.

C) Pathes anf logfiles names are not case-sensitive.



CONFIGURATION SETTINGS FILE EXAMPLE
-----------------------------------


{

"Path to directory which contains log files"		:	"C:\path1"	,

"Path to directory where output files will be created"	:	"C:\path2"	,

"Names of the logfiles to be scanned"			:

[

"20200202_DE1234567890_cut.log"	,
"20200202_DE1234567890.log"	,
"20200202.log"

]
}
    
