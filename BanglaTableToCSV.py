#Python 3.11.3
import pandas as pd #version 2.0.3
import numpy as np #version 1.25.0
import csv #version 1.0
import os
import PIL #version 9.5.0
from PIL import Image, ImageChops, ImageOps, ImageDraw
import pytesseract #version 0.3.10
import os.path
import cv2 #version 4.8.1
import itertools



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#BASIC COMMANDS:

def unique(list1:list)->list:
    '''returns unique values from a list'''
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return unique_list

def PIL_to_cv2(PILimage):
    '''takes PIL image and converts it to a cv2 image. Only works for RGB mode'''
    cv2image = np.array(PILimage)
 
    # Convert RGB to BGR
    return cv2image[:, :, ::-1]


#The next three functions define a way cut up an image of a table into its distinct cells. We will apply an OCR to these cells later.


def getCellCoordsFromImage(im:str)->list:
    """This function takes a PIL image and returns a list of the of leftmost, topmost, rightmost, and bottomost pixel
    coordinates for each cell of the table. The list is order going right to left, bottom to top."""
    im = PIL_to_cv2(im)

    #Some code below is overly sophisticated. Images should already be made black and white.
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #filter noise
    contours = [cont for cont in contours if cv2.contourArea(cont) > 1000]

    #get rid of text

    contours = [cv2.convexHull(cont) for cont in contours]
    
    contours = contours[2:]  
    #Improve: ^ this removes the perimeter of the image and the perimeter of the table as a contour. 
    #           it might be better to remove these by filtering out contours with large areas. 
    
    lst=[]
    for cont in contours:
        R = cont[0][0][0]
        T = cont[0][0][1]
        L = cont[2][0][0]
        B = cont[2][0][1]
        if len(cont) == 4: #this if statement is just to fallible check on whether or not the contour is a box. Page 14 had the original issue
            lst.append((L,T,R,B))
        
    return lst

        
def getColumnListCoords(lst:list)->list:
    '''Input should come from getCellCoords. Takes cell coordinates and creates lists of cell coordinates
      according to right coordinate value. These lists (columns) are rearranged top to bottom.'''
    #makes this an nparray method later
    #Get right coords (each coorresponds to a column)
    listR = unique([coord[2] for coord in lst])
    listR.sort()
    #print(len(listR))
    
    #Get bottom coords (each corresponds to a row)
    L=[]
    counter = 0
    #return [coord for coord in ]    
    for Rval in listR:
        col = [coord for coord in lst if coord[2] == Rval][::-1]
        L.append(col)
        
    return L


def getColumnsOfCellCoordsFromImage(im)->list:
    '''Gets columns of cell coordinates (left-most,top-most,right-most,bottom-most) from an image.'''
    return getColumnListCoords(getCellCoordsFromImage(im))


########################################################################################################################################
########################################################################################################################################

#We now define a method for to take the images of Bangla appearing in cells an produce text. 
#Some of the approach may seem random, but pytesseract's OCR for Bangla often struggles to recognize when Bangla is in plainview.
#This method comes from a little insight, and much trial and error.

def trim(im):
    '''Trims images down to the text with some margins.'''
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    #diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        L,T,R,B = bbox
        im = PIL.ImageOps.invert(im)
        return PIL.ImageOps.invert(im.crop((L-5,T-10,R+5,B+10))) #no idea why this doesn't work without inverting image twice





    
def splitLines(im):
    '''Splits images accross lines of text. Returns list of images of each line'''
    im =trueBlackAndWhite(im)
    im = PIL.ImageOps.invert(im)
    bbox = im.getbbox()
    if bbox:
        L,T,R,B = bbox
        im = im.crop((L,T,R,B))
        array = np.array(im.getdata()).reshape((im.size[1], im.size[0])) #(ht,wdth)
        lineValues=[]
        for height in range(im.size[1]):
            line = array[height] #horizontal line at height = height
            val = list(line) == list(np.repeat(0,im.width)) #True if line is black (contains no letters)
            lineValues.append(val)
        dic={}
        position = 0   
        for v,s in itertools.groupby(lineValues):
            length = sum(1 for x in s)
            dic[(position,length)] = v
            position+=length
        blankH = [k for k, v in dic.items() if v == True]
        imList =[]
        h_0 = 0
        for p,l in blankH:
            imList.append(PIL.ImageOps.invert(im.crop([0,h_0,im.width,p+l//2 ])))
            h_0 = p+l//2
        imList.append(PIL.ImageOps.invert(im.crop([0,h_0,im.width,im.height])))

        return imList


    
#pytessract struggles mightily in recognizing when Bangla is present. Simply feeding the OCR images of the cells results in blanks
# roughly 20% of the time. It is necessary to manipulate the images. Through trial and error, one method surpassed all others.
# The ocr is great at recognize numbers, such as ৩৭৭, when present. Trimming the image of cell (containing a single line), and then 
# placing numbers both sides yielded text recognition in every instance (over 5000) tried. The method uses the same image on either
# but one could change this easily. We suggest using ৩৭৭. Some other numbers were translated in multiple ways.

 
#Image was created with: trim(Image.open("C:/Users/jonmo/OneDrive/Desktop/BengaliEl/BetterNames/page_8.png").crop((113, 373, 195, 445)))

imageL = Image.open("ThreeBanglaNumbers.png")

imageR = Image.open("ThreeBanglaNumbers.png")

#trim(Image.open("C:/Users/jonmo/OneDrive/Desktop/BengaliEl/BetterNames/page_8.png").crop((113, 373, 195, 445))).save('TESTING.png')

wL =  imageL.width
wR = imageR.width
hL = imageL.height
hR = imageR.height

def getTextFromCellWith1Line(im):
    '''Takes image of a cell with one line and returns Bangla text.'''
    midIm = trim(im)
    
    height =max([hR,hL,midIm.height])

    gluedIm = PIL.ImageOps.invert(Image.new('1', (wR + wL + midIm.width,height)))
    gluedIm.paste(imageL,(0,(height-hL)//2))
    gluedIm.paste(midIm,(wL,(height-midIm.height)//2))
    gluedIm.paste(imageR,(wL+midIm.width, (height-hR)//2))
    
    
    text = pytesseract.image_to_string(gluedIm,lang="ben").replace('\n','')

    text= text[3:-3]
    
    if len(text)>0:
        while text[-1] == " ":
            text = text[:-1]
        while text[0] == " ":
            text = text[1:]
    return text



def getTextFromCell(im):
    '''Takes an image of cell containing text (could be on multiple lines) and returns the Bangla text.'''
    imageList = splitLines(im)
    textList = [getTextFromCellWith1Line(image) for image in imageList]
    return ' '.join(textList)        

    
#########################################################################################################################################
#########################################################################################################################################

#

def isCellEmpty(im):
    '''checks if a cell is completely blank'''
    return PIL.ImageOps.invert(im).getbbox() is None


def trueBlackAndWhite(im):
    '''takes image (should be of table) and makes any pixel that is not black, white. Returns the place and white image.'''
    if im.mode != '1': 
        if im.mode != 'L':
            im = im.convert('L')

        imout = Image.new('1', im.size)
        imout.putdata(list(map(lambda pixel: 0 if pixel <225 else 255,im.getdata()) ) )

        im=imout
    return im



def getDataFrameFromImage(image):
    '''takes an image (should be black and and  white) of a table in Bangla, and returns a dataframe
      and a list of cell coordinates to cells whose text went unrecognized by the OCR.'''
    listOfColCoords = getColumnsOfCellCoordsFromImage(image)
    #table image preprocessing
    image = trueBlackAndWhite(image)

 
    dic={}
    ListOfUnread = []
    for colOfCoords in listOfColCoords:
        
        label = getTextFromCell(image.crop(colOfCoords[0]))

        colOfCoords = colOfCoords[1:]
        col = []
        for coord in colOfCoords:
            cell = image.crop(coord)
            if isCellEmpty(cell) == False: 

                bText = getTextFromCell(image.crop(coord))
                
                if bText == '':
                    ListOfUnread.append(coord)
                    bText ='OCR ERROR' + str(coord)

                    
                col.append(bText)
            else:
                col.append('')
        dic[label] = col
    return pd.DataFrame(dic), ListOfUnread 


