#!/usr/bin/env python
# -*- coding: cp1251 -*-

from PIL import Image, ImageChops, ImageDraw
import time

''' ���������� ���������������� ����� �����������. '''
def binarize(img):
    
    # ������������� ����������.
    imgRes = img.copy()             # ����������� �������� �����������.
    histogram = img.histogram()     # ����������� �����������.
    pix = imgRes.load()             # ������� ��������.
    oldThreshold = 0                # ��������� �������� �� ���������/������.
    threshold = 127                 # ������� ��������� ��������.
    maxCorrelation = 3              # ���������� ���������� �������� ������.
    
    # ����� ������������ ���������� ��������.
    while abs(threshold - oldThreshold) > maxCorrelation:
        numBackPixels = 0   # ���������� �������� ����.
        numTextPixels = 0   # ���������� �������� ������.
        sumBackPixels = 0   # ����� �������� �������� ����.
        sumTextPixels = 0   # ����� �������� �������� ������.
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                valPixel = pix[i,j]
                if (valPixel < threshold):
                    numTextPixels = numTextPixels + 1
                    sumTextPixels = sumTextPixels + valPixel
                else:
                    numBackPixels = numBackPixels + 1
                    sumBackPixels = sumBackPixels + valPixel
        oldThreshold = threshold
        threshold = ((sumBackPixels/numBackPixels) +
                     (sumTextPixels/numTextPixels)) / 2
    
    # ����������� ��������� �������������� �����������.
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if pix[i,j] < threshold:
                pix[i,j] = 0
            else:
                pix[i,j] = 255
    
    return imgRes

''' ���������� ����������� ������������ ���� �����������. '''
def imgcmp(img1, img2):
    img1.resize((img2.size[0], img2.size[1]))
    dif = ImageChops.difference(img1, img2).convert('1')
    hist = [dif.histogram()[0], dif.histogram()[255]]
    return hist[0] / float(hist[0] + hist[1])

# ������ ��� ������ *.bmp � �������� �������������� ��������.
characters = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", 
              "�", "�", "�", "�", "�", "�", "�", "�", "�", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", 
              "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-", "�-"]

# ������ �������� �������� �������� ����� (� ���).
overhangs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
             0, 0, 0, 0, 8, 0, 0, 0, 
             1, 0, 0, 0, 0, 0, 0, 0, 
             0, 0, 0, 0, 1, 0, 0, 8, 
             0, 0, 8, 0, 0, 0, 1, 1, 0, 
             0, 0, 0, 0, 7, 0, 0, 0, 
             0, 0, 0, 0, 0, 0, 0, 0, 
             0, 10, 0, 0, 10, 10, 0, 7, 
             0, 0, 7, 0, 0, 0, 0, 0, 0]

minIdentityValue = 0.65             # ����������� �������� ������������.

# �������� � �������������� ��������� �����������.
imgOrig = Image.open('C:\\YaDisk\\������\\�����\\�����������\\example.jpg')
print (str(time.ctime()) + ' �������� ����������� �������.')
imgOrig = imgOrig.convert('L')
print (str(time.ctime()) + ' �������� ����������� �������������� RGB->L.')
imgBin = binarize(imgOrig)
print (str(time.ctime()) + ' �������� ����������� ������������.')
imgDraw = imgBin.convert('RGBA')
drawRects = ImageDraw.Draw(imgDraw)

# �������� ��������� �������� ��������.
imgChar = []
dxChar = []
dyChar = []
for iChar in range(76):
    char = characters[iChar]
    imgChar.append(Image.open('C:\\YaDisk\\������\\�����\\�������\\' +
                              char + '.bmp'))
    dxChar.append(imgChar[iChar].size[0])
    dyChar.append(imgChar[iChar].size[1])
print (str(time.ctime()) + ' ��������� �������� �������.')

# ����������� ��������� �����������.
print (str(time.ctime()) + ' ����������� �����������...')
group = -1                      # ����� ������ ��������.
bounds = []                     # ������� ����� ����� ��������.
colRels = []                    # ��������� ���������� �����.
pix = imgBin.load()             # ������� �������� ����������������� �����������.
pixGroups = []                  # ������� �������������� �������� � �������.
for x in range(0, imgBin.size[0]):
    pixGroups.append([])
    for y in range(0, imgBin.size[1]):
        if pix[x, y] == 0:      # ���� ������� ������.
            
            isAlone = True
            mainGroup = 0
            
            # ������ ����� � �������� �������� [dx,dy,N].
            groupsNear = [[0,-1,0],
                          [-1,-1,0],
                          [-1,0,0],
                          [-1,1,0]]
            for near in groupsNear:
                if near[0] + x < 0:
                    near[2] = 0
                elif near[1] + y < 0:
                    near[2] = 0
                else:
                    near[2] = pixGroups[near[0] + x][near[1] + y]
                    if near[2] > 0:
                        isAlone = False
                        if mainGroup == 0:
                            # ���������� ����� ������ �������,
                            # ������� �� "��������" � �����������.
                            mainGroup = near[2]
                            pixGroups[x].append(mainGroup)
                            if      bounds[mainGroup][0] > x:
                                    bounds[mainGroup][0] = x
                            elif    bounds[mainGroup][2] < x:
                                    bounds[mainGroup][2] = x
                            if      bounds[mainGroup][1] > y:
                                    bounds[mainGroup][1] = y
                            elif    bounds[mainGroup][3] < y:
                                    bounds[mainGroup][3] = y
                        elif near[2] <> mainGroup:
                            rel_found = False
                            for rel in colRels:
                                if mainGroup in rel and near[2] in rel:
                                    rel_found = True
                                    break
                            if not rel_found:
                                for rel in colRels:
                                    if mainGroup in rel:
                                        rel_found = True
                                        break
                                if rel_found:
                                    rel.append(near[2])
                                else:
                                    colRels.append([near[2]])
            
            # ���� ������� ������������ ������ � ����� ���������������,
            if isAlone:
                # �� ��������� ��� ����� ����� ��������.
                group = group + 1
                pixGroups[x].append(group)
                bounds.append([x, y, x, y])
        else:
            pixGroups[x].append(0)

print (str(time.ctime()) + ' ����������� ���������...')
for x in range(1, imgBin.size[0]-1):
    for y in range(1, imgBin.size[1]-1):
        if pixGroups[x][y] > 0:
            for rel in colRels:
                if pixGroups[x][y] in rel:
                    for elem in rel:
                        if pixGroups[x][y] == elem:
                            firster = rel[0]
                            pixGroups[x][y] = firster
                            if      bounds[firster][0] > bounds[elem][0]:
                                    bounds[firster][0] = bounds[elem][0]
                            elif    bounds[firster][2] < bounds[elem][2]:
                                    bounds[firster][2] = bounds[elem][2]
                            if      bounds[firster][1] > bounds[elem][1]:
                                    bounds[firster][1] = bounds[elem][1]
                            elif    bounds[firster][3] < bounds[elem][3]:
                                    bounds[firster][3] = bounds[elem][3]

print (str(time.ctime()) + ' ���������� ������ ���������...')
for rel in colRels:
    seg = rel[0]
    bound = bounds[seg]
    drawRects.rectangle((bound[0]-1, bound[1]-1, bound[2]+1, bound[3]+1),
                         fill=None, outline='#0000FF')
imgDraw.show()
exit(0)

matchY = 0
for y in range(90, imgOrig.size[1]-40, 3):
    matchX = 0
    matchChar = -1
    if y % 5 == 0:
        print 'y=' + str(y) + '/' + str(imgOrig.size[1])
    if matchY == 0 or (y > (matchY + dyChar[matchChar] * k)):
        for x in range(0, imgOrig.size[0]-20, 3):
            if matchX == 0 or (x > (matchX + dxChar[matchChar] * k)):
                matchValue = 0.0
                for iChar in range(43):
                    char = characters[iChar]
                    dx = int(dxChar[iChar] * k)
                    dy = int(dyChar[iChar] * k)
                    imgCrop = imgBin.crop((x, y, x+dx, y+dy))
                    identity = imgcmp(imgCrop, imgChar[iChar])
                    if matchValue < identity and minIdentityValue < identity:
                        matchValue = identity
                        matchChar = iChar
                        imgCropMax = imgCrop.copy()
                if matchValue <> 0.0:
                    drawRects.rectangle((x, y,
                                         x + int(dxChar[matchChar] * k),
                                         y + int(dyChar[matchChar] * k)),
                                        fill=None, outline='#0000FF')
                    imgGhost = imgChar[matchChar].copy().convert('RGBA')
                    imgGhost = imgGhost.resize((int(dxChar[matchChar] * k), 
                                                int(dyChar[matchChar] * k)))
                    imgMask = imgGhost.copy()
                    pix = imgMask.load()
                    for i in range(imgGhost.size[0]):
                        for j in range(imgGhost.size[1]):
                            if pix[i,j] == (0, 0, 0, 255):
                                pix[i,j] = (0, 0, 255, 64)
                            else:
                                pix[i,j] = (0, 0, 0, 0)
                    imgDraw.paste(imgGhost, (x,y), imgMask)
                    print characters[matchChar]
                    matchX = x
                    matchY = y
                    x = x + int(dxChar[matchChar] * k)
        if matchChar <> -1:
            y = y + int(dyChar[matchChar] * k)
        else:
            matchY = 0
imgDraw.show()
