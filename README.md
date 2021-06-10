# EarlyOften

Previous studies have shown that undergraduate students who work on their coding assignments earlier and more often tend to do better in the respective course. By keeping track of the size of each edit and the day (respective to the deadline) an edit was made, this code calculates the ealy/often metric (specified in the link below). In this metric, students with a higher score are those who worked on their assignments more often and earlier compared to other students. The data used to calculate this metric follows the ProgSnap 2 specification (linked below). <br/>

Early/Often Equation: https://users.csc.calpoly.edu/~ayaank/pubs/quantifying-incremental-development-procrastination.pdf <br/>
ProgSnap 2 Specification: https://cssplice.github.io/progsnap2/<br/>

-Please title main folder w/ data "Data" (will change later) <br/>

Files Needed:<br/>
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
-CodeStates.csv<br/>
-Required columns: <br/>
1.CodeStateID<br/>
2.Code <br/><br/>
-Deadline.csv<br/>
-Required Columns:<br/>
1.AssignmentID <br/>
2.X-Deadline <br/><br/>

How to run program: <br/>
In terminal: python3 eo.py<br>
-Will be prompted if you want to filter the data (Y/N): <br/>
-If yes, enter the minimum number of edits <br/>
-After running, will get a csv file titled "EO.csv" with results
