#!/usr/bin/env python
# -*- coding: cp1251 -*-

from PIL import Image, ImageChops, ImageDraw
import time

# -------------------------------------------------------------------------------

def binarize(img):
    ''' ���������� �����-����� ����� �����������. '''
    
    # ������������� ����������.
    imgRes = img.convert('L')   # ����������� ��������� �����������.
    pix = img.load()   # ������� �������� ��������.
    pix2 = imgRes.load()   # ������� �����-����� ��������.
    histogram = img.histogram()   # ����������� ��������� �����������.
    oldThreshold = 0   # ���������� ��������� ��������.
    threshold = 127   # ������� ��������� ��������.
    maxCorrelation = 5   # ���������� ������� ����� ���������� ������.
    
    # ����� ������������ ���������� ��������.
    while abs(threshold - oldThreshold) > maxCorrelation:
        
        # ��������� �������� ���������� �� ��� � �����.
        numBackPixels = 0   # ���������� �������� ����.
        numTextPixels = 0   # ���������� �������� ������.
        sumBackPixels = 0   # ����� �������� �������� ����.
        sumTextPixels = 0   # ����� �������� �������� ������.
        
        # ����������� �� �������� ���������� ��������.
        for val in range(256):
            
            numVal = histogram[val]   # ���������� �������� � �������� val.
            
            # ����������� ���������� �������� ���������� �� ��� � �����.
            if (val < threshold):
                # ���������� � ����� �������� �������� ������.
                numTextPixels = numTextPixels + 1
                sumTextPixels = sumTextPixels + val
            else:
                # ���������� � ����� �������� �������� ����.
                numBackPixels = numBackPixels + 1
                sumBackPixels = sumBackPixels + val
        
        # ������ ������ ���������� ��������.
        oldThreshold = threshold
        threshold = ((sumBackPixels/numBackPixels) +
                     (sumTextPixels/numTextPixels)) / 2
    
    # ����������� ��������� �������������� �����������.
    threshold = threshold + maxCorrelation
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            # ������� ���������� ������� ������� ��� ������ �����.
            if pix[i,j] < threshold:
                pix2[i,j] = 0
            else:
                pix2[i,j] = 255
    
    return imgRes   # ������� ���������� �����������.

# -------------------------------------------------------------------------------

def check_near(x, y, group):
    ''' ������� �������� ��������� �� ������� ������ ��������. '''
    
    pixGroups[x][y] = group   # ��������� ������� � ������.
    
    # ���� �� �������� ��������.
    for near in nears:
        
        x2 = x + near[0]   # ���������� ����������
        y2 = y + near[1]   # ��������� �������.
        
        # ��������� ����������, ��������� �� ���� �����������.
        if x2 < 0 or x2 >= imgBin.size[0]:
            continue
        if y2 < 0 or y2 >= imgBin.size[1]:
            continue
        
        # ���� �������� ������� - ������, � �� ������ � ������ ��������.
        if (pix[x2, y2] == 0 and pixGroups[x2][y2] <> group):
            
            # ���� ����� ��������� � ������ � ������ �������.
            if pixGroups[x2][y2] <> -1 and pixGroups[x2][y2] <> group:
                # �� ����������� ������� ������� �� ���� �������.
                if pixGroups[x2][y2] < group:
                    group = pixGroups[x2][y2]
                else:
                    pixGroups[x2][y2] = group
            
            # ���������� ����� ��������.
            if      bounds[group][0] > x2:
                    bounds[group][0] = x2
            elif    bounds[group][2] < x2:
                    bounds[group][2] = x2
            if      bounds[group][1] > y2:
                    bounds[group][1] = y2
            elif    bounds[group][3] < y2:
                    bounds[group][3] = y2
            
            global depth   # ���������� ������� ������� ��������.
            depth = depth + 1   # ����� ������� ��������.
            if depth < 500:   # ���� ������� �������� �� ��������� 500,
                check_near(x2, y2, group)   # ��������� ������ ��� �� � ������.
            depth = depth - 1   # ������� �� ���������� ������� ��������.

# -------------------------------------------------------------------------------

def imgcmp(img1, img2):
    ''' ���������� ����������� ������������ ���� �����������. '''
    
    width = img2.size[0]   # ������ �������.
    height = img2.size[1]   # ������ �������.
    img1 = img1.resize((width, height))   # ��������� ������� ��� ������� �������.
    
    dif = ImageChops.difference(img1, img2)   # ���������� ��������������.
    dif = dif.convert('1')   # �����������.
    
    # ������� ���� ������ ��������.
    return float(dif.histogram()[0]) / (width * height)

# -------------------------------------------------------------------------------

def print_field(label, left, top, right, bottom):
    ''' ���������� ������������ �����, ����������� � ��������� �������� ����. '''
    
    data = ''   # ������ �������� ����.
    couples = []   # ������ ��������� � ���� ��� [������, �����].
    past = None   # ����� ����������� �������.
    for b in range(len(bounds)):
        bound = bounds[b]   # ����� �������� ��������.
        # ���� ������� ��������� � ��������� �������� � ���������� �������.
        if (bound[0] > imgBin.size[0] * left and
            bound[1] > imgBin.size[1] * top and
            bound[2] < imgBin.size[0] * right and
            bound[3] < imgBin.size[1] * bottom and
            text[b] <> '.'):
            couples.append([text[b], bound])   # �������� � ������ ���������.
    
    # ����������� �������� �� ������� � ���������� ������ �����.
    couples.sort(key=sortByY)   # ����������� �� ������������� ������������.
    first = 0   # ������ ������� �������� � ������.
    for c in range(len(couples)):
        couple = couples[c]   # ������� �������.
        if c:   # ���� ��� �� ������ ������ �������.
            
            # ���� ����� ��������� ������������ ������� �� ��� Y
            # ��� ������ ��������� �� �������.
            if (couple[1][3] - past[3] > past[3] - past[1] or
                c == len(couples)-1):
                srez = couples[first:c]
                srez.sort(key=sortByX)   # ����������� ������� � ������ �� X.
                couples[first:c] = srez
                # �������� ����-��������� �������� �����.
                couples[c-1][0] = couples[c-1][0] + ('|'
                                  if c < (len(couples)-1) else '')
                first = c   # ���������� ������ ������� ������� ����. ������.
        past = couple[1]   # ���������� ������� ����� ��� ����������.

    # ������������ ������ �������� ����.
    for c in range(len(couples)):
        couple = couples[c]
        data = data + couple[0]   # ������������ ���������� �������.
        if c:   # ���� ��� �� ������ ������ �������.
            # ���� ���� ������������ ������ �� ��� X,
            if couple[1][0] - past[2] > (past[2] - past[0]) / 2:
                couple[0] = ' ' + couple[0]   # ���������� ��� ��� ������.        past = couple[1]   # ���������� ������� ����� ��� ����������.
    print (label + ': ' + data)   # ������� �� ����� �������� ����.
    
    # ���������� ������������� ������ ����.
    drawRects.rectangle((imgBin.size[0] * left, imgBin.size[1] * top,
                         imgBin.size[0] * right, imgBin.size[1] * bottom),
                        fill=None, outline='#00FF00')

# -------------------------------------------------------------------------------

def split_segment(b):
    ''' ��������� �������������� ������� �� �������. '''
    
    global bounds   # ���������� ������� ������ ������ ���������.
    width = float(b[2] - b[0])   # ������ ��������.
    height = float(b[3] - b[1])   # ������ ��������.

    # ���� ���������� �������, ���� ������ �������� ��������� 0,9 �� ��� ������.
    while (width > height * 0.9):
        v_min = height   # ����������� ���������� ������ ��������.
        x_min = b[0] + int(height * 0.8)   # �������� x ������� � v_min.
        
        # ����� ������������� ������� � ����������� ���-��� �������� ������.
        for x in range(b[0] + int(height * 0.35), b[0] + int(height * 1.4)):
            if x >= b[2]:
                break   # ���������, ���� ��������� ������ ����.
            v = 0   # ������� ������ ��������.
            # ���� �� �������� �������.
            for y in range(b[1], b[3]+1):
                if (pix[x,y] == 0):
                    v = v + 1   # ������ ��� ���� ������ �������.
            if (v_min > v):   # ��������� ����, ���� ���� �� ����� �����������.
                v_min = v
                x_min = x
        if (v_min <= 3):
            bounds.append([b[0], b[1], x_min-1, b[3]])   # ��������� ��������.
            b[0] = x_min + 1   # �������� ����� ��������� ��������.
            width = float(b[2] - b[0])   # �������� ������ ��������.
        else:
            break   # ���������� �������, ���� � ����� ������ 3-� ��� ������.

# -------------------------------------------------------------------------------

def sortByX(c):   # ���������� ���������-�������� �� x ������ ������.
    return c[1][0]

def sortByY(c):   # ���������� ���������-�������� �� y ������ ����.
    return c[1][3]

# ===============================================================================


# --- �������� � �������������� ����������� -------------------------------------

imgOrig = Image.open(raw_input('������� ������ ��� ����� �����: '))   # �������.
imgOrig.draft('L', imgOrig.size)   # ���������� ����������� � �������� ������.

imgBin = binarize(imgOrig)   # ����������� �����������.
imgDraw = imgBin.convert('RGBA')   # ���������� ������� � 1 (� ������� �����).
drawRects = ImageDraw.Draw(imgDraw)   # ������ ��������� �� ������� � 1.


# --- �������� �������� �������� ------------------------------------------------

# ������ ��� ������-�������� (*.bmp).
characters = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", "�", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-"]
listChars = []   # ������ ����������� ��������.

# ����������� �������� �������� �������� � �������� ������.
for iChar in range(len(characters)):
    char = characters[iChar]
    listChars.append(Image.open('patterns\\' + char + '.bmp'))
    listChars[-1].draft('L', listChars[-1].size)
    characters[iChar] = char.replace('-', '')


# --- ����������� ����������� ---------------------------------------------------

group = -1   # ����� ������ ��������.
bounds = []   # ������� ����� ����� ��������.
pix = imgBin.load()   # ������� �������� ����������������� �����������.
pixGroups = []   # ������� �������������� �������� � �������.
for x in range(0, imgBin.size[0]):
    pixGroups.append([])
    for y in range(0, imgBin.size[1]):
        pixGroups[x].append(-1)

# ������ ������������� ��������� ������� ��������.
nears = [[-1, 0],
         [-1, -1],
         [0, -1],
         [1, -1],
         [1, 0],
         [1, 1],
         [0, 1],
         [-1, 1]]
depth = 0

# ���������� �������� �� �������� ���������.
for y in range(imgBin.size[1]):
    for x in range(imgBin.size[0]):
        # ���� ������� ������ � ��� �� ��������� ������.
        if (pix[x, y] == 0 and pixGroups[x][y] == -1):
            depth = 0   # ������������� �������� ������� ��������.
            group = group + 1   # ��������� ������� �����.
            bounds.append([x, y, x, y])   # ��������� ������� ������.
            # ��������� ����� � ������ �������� � �������� ��������.
            check_near(x, y, group)

# ��������� � ���������� ���������.
for b in bounds:
    
    width = float(b[2] - b[0])   # ������ ��������.
    height = float(b[3] - b[1])   # ������ ��������.
    
    if (width < 3 or height < 5):
        continue   # ���������� ������� ��������� �������.
    
    if (width > height * 0.9):
        split_segment(b)   # ��������� ��������� �������.
    
    # ���������� ������������� ������ ���������.
    drawRects.rectangle((b[0]-1, b[1]-1, b[2]+1, b[3]+1),
                        fill=None, outline='#0000FF')


# --- ������������� ��������� � ��������� ---------------------------------------

minIdentityValue = 0.65   # ���������� ���������� �������� ������������.
imgWhite = ImageChops.constant(imgDraw, 255)   # ���������� ������� � 2.
text = ""   # ������ � ������������� ���������.

# ���� �� ���������.
for b in bounds:
    
    # ���������� ������� ��������� ��������.
    if (b[2]-b[0] < 3 or b[3]-b[1] < 5):
        text = text + '.'
        continue
    
    # ������� �������� � ��������� �����������.
    imgCrop = imgBin.crop((b[0],b[1],b[2]+1,b[3]+1))
    
    # �������� ������� � ������ ��������.
    matchValue = 0.0   # ���������� �� ��������� �������� ������������.
    for iChar in range(0, len(listChars)):
        
        imgChar = listChars[iChar]   # ����������� �������-�������.
        identity = imgcmp(imgCrop, imgChar)   # ������������ �������.
        
        # ���� ������������ ������ ���������� � ����� ���������.
        if (identity > minIdentityValue and identity > matchValue):
            # ��������� ������� ������.
            matchValue = identity
            matchChar = iChar
    
    # ���������� ���������� ����������, ���� ������� ������ �� ������.
    if (matchValue == 0.0):
        text = text + '?'
        continue
    
    imgChar = listChars[matchChar]
    charRatio = float(imgChar.size[0]) / imgChar.size[1]
    text = text + characters[matchChar]
    imgGhost = imgChar.copy().convert('RGBA')
    imgGhost = imgGhost.resize((b[2]-b[0], b[3]-b[1]))
    imgMask = imgGhost.copy()
    pix = imgMask.load()
    for i in range(imgGhost.size[0]):
        for j in range(imgGhost.size[1]):
            if (pix[i,j] == (0, 0, 0, 255)):
                pix[i,j] = (0, 0, 255, 255)
            else:
                pix[i,j] = (0, 0, 0, 0)
    imgWhite.paste(imgGhost, (b[0],b[1]), imgMask)


# --- ����� ����������� ����� ---------------------------------------------------

print_field('� �����', 100.0/700, 140.0/500, 600.0/700, 185.0/500)
print_field('�.�.�.', 150.0/700, 175.0/500, 600.0/700, 275.0/500)
print_field('���� ��������', 300.0/700, 230.0/500, 600.0/700, 300.0/500)
print_field('����� ��������', 100.0/700, 285.0/500, 600.0/700, 360.0/500)
print_field('���', 100.0/700, 360.0/500, 500.0/700, 410.0/500)
print_field('���� �����������', 200.0/700, 400.0/500, 600.0/700, 480.0/500)

while 1:
    answer = raw_input('\n������� � ����������� ����������� (1, 2): ')
    if answer == '1':
        imgDraw.show()   # �������� ����� ����� � ���������.
    elif answer == '2':
        imgWhite.show()   # �������� ��������� ������������ ��������.
    else:
        exit(1)
