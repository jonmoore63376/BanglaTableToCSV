#Python 3.11.3
import pandas as pd #version 2.0.3
import numpy as np #version 1.25.0
import csv #version 1.0
import os
import PIL #version 9.5.0
from PIL import Image, ImageChops, ImageOps
import pytesseract #version 0.3.10
import os.path
import cv2 #version 4.8.1
from pdf2image import convert_from_path
from BanglaTableToCSV import *
import time

time1=time.time()

cwd=os.getcwd()

poppler_path = cwd + "/Downloads/Release-23.11.0-0/poppler-23.11.0/Library/bin"

 
# Store Pdf with convert_from_path function
images = convert_from_path('BangladeshiElection24.pdf',poppler_path=poppler_path)

#initialize dataframe. Note: In this example some later pages are missing the final column.
counter = 0
ErrorDic ={}
df, ErrorList = getDataFrameFromImage(images[0])

# Add error list for the first (0-th) page as a value to the dictionary

ErrorDic[counter] = ErrorList

#get column names:

ColumnNames = df.columns

for image in images[1:]:
    counter +=1
    dfNew,ErrorList = getDataFrameFromImage(image)
    ErrorDic[counter] = ErrorList
    if dfNew.shape[1] !=6:
        dfNew['newCol'] = ""
    dfNew.columns = ColumnNames
    df = pd.merge(df, dfNew, how='outer')

df.to_csv('BangladeshiElection24.csv', sep='\t',index=False)


print('The table has shape (rows,columns)=',df.shape)


print("Bangla Text Recognition Failures:", ErrorDic)

print("time to complete:", time.time()-time1)



