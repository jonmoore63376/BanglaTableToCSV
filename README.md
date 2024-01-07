# BanglaTableToCSV
This repository contains python code to create CSV files from images of Bangla data tables. 

Tools are found in BanglaTableToCSV.py, which requires ThreeBanglaNumbers.png to run. Also, the user should check the path for path\Tesseract-OCR\tesseract.exe.

BanglaTableExample.py applies getDataFrameFromImage to BangladeshiElection24.pdf. This takes roughly half an hour to run and requires poppler to be installed.
Consider test getDataFrameFromImage on a single image beforehand. The resulting csv, BangladeshiElection24.csv, is also included.




