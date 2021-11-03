# EarlyOften

Previous studies have shown that undergraduate students who work on their coding assignments earlier and more often tend to do better in the respective course. By keeping track of the size of each edit and the day (respective to the deadline) an edit was made, this program calculates the ealy/often metric (specified in the link below). In this metric, students with a higher score are those who worked on their assignments more often and earlier compared to other students. The data used to calculate this metric follows the ProgSnap2 specification (linked below). <br/>

Early/Often Paper: https://users.csc.calpoly.edu/~ayaank/pubs/quantifying-incremental-development-procrastination.pdf <br/>
ProgSnap2 Specification: https://cssplice.github.io/progsnap2/<br/>

Python version: Python 3.8.2
Packages needed: pandas

How to run program: <br/>
In terminal: python3 eo.py<br>
Optional: Can specify a different input directory (as the first argument) and output file (as second argument)<br/>
Example: python3 eo.py ./input_dir output<br/>
The default directory the program will read in is "Data" and the default write file path will be "out/EO.csv"<br/>
-Next, you will be prompted if you want to filter the data (Y/N): <br/>
-If yes, enter the minimum number of edits <br/>

-Note: Currently the codestates directory only works with the table format. <br/>

Files Needed (in ProgSnap2 format):<br/><br/>
-MainTable.csv: <br/>
Required Columns:<br/>
1.Subject ID<br/>
2.Order<br/>
3.EventType<br/>
4.EventID<br/>
5.AssignmentID<br/>
6.ParentEventID<br/>
7.EditType (For edit events only)<br/> <br/>
-Files in LinkTable folder:<br/>
-Deadline.csv<br/>
-Required Columns:<br/>
1.AssignmentID <br/>
2.X-Deadline <br/><br/>
-Files in CodeStates Directory:
-CodeStates.csv<br/>
-Required columns: <br/>
1.CodeStateID<br/>
2.Code <br/><br/>
