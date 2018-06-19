#!/usr/bin/env python
# -*- coding: cp1251 -*-

from PIL import Image, ImageChops, ImageDraw
import time

''' Возвращает бинаризированную копию изображения. '''
def binarize(img):
    
    # Инициализация переменных.
    imgRes = img.copy()             # Копирование входного изображения.
    histogram = img.histogram()     # Гистограмма изображения.
    pix = imgRes.load()             # Матрица пикселей.
    oldThreshold = 0                # Пороговое значение по умолчанию/старое.
    threshold = 127                 # Текущее пороговое значение.
    maxCorrelation = 3              # Наибольшее отклонение значения порога.
    
    # Выбор оптимального порогового значения.
    while abs(threshold - oldThreshold) > maxCorrelation:
        numBackPixels = 0   # Количество пикселей фона.
        numTextPixels = 0   # Количество пикселей текста.
        sumBackPixels = 0   # Сумма значений пикселей фона.
        sumTextPixels = 0   # Сумма значений пикселей текста.
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
    
    # Бимодальное пороговое преобразование изображения.
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if pix[i,j] < threshold:
                pix[i,j] = 0
            else:
                pix[i,j] = 255
    
    return imgRes

''' Возвращает коэффициент идентичности двух изображений. '''
def imgcmp(img1, img2):
    img1.resize((img2.size[0], img2.size[1]))
    dif = ImageChops.difference(img1, img2).convert('1')
    hist = [dif.histogram()[0], dif.histogram()[255]]
    return hist[0] / float(hist[0] + hist[1])

# Массив имён файлов *.bmp с образами распознаваемых символов.
characters = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
              "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", 
              "З", "И", "Й", "К", "Л", "М", "Н", "О", 
              "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", 
              "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю", "Я", 
              "а-", "б-", "в-", "г-", "д-", "е-", "ё-", "ж-", 
              "з-", "и-", "й-", "к-", "л-", "м-", "н-", "о-", 
              "п-", "р-", "с-", "т-", "у-", "ф-", "х-", "ц-", 
              "ч-", "ш-", "щ-", "ъ-", "ы-", "ь-", "э-", "ю-", "я-"]

# Массив значений выступов символов снизу (в пкс).
overhangs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
             0, 0, 0, 0, 8, 0, 0, 0, 
             1, 0, 0, 0, 0, 0, 0, 0, 
             0, 0, 0, 0, 1, 0, 0, 8, 
             0, 0, 8, 0, 0, 0, 1, 1, 0, 
             0, 0, 0, 0, 7, 0, 0, 0, 
             0, 0, 0, 0, 0, 0, 0, 0, 
             0, 10, 0, 0, 10, 10, 0, 7, 
             0, 0, 7, 0, 0, 0, 0, 0, 0]

minIdentityValue = 0.65             # Минимальное значение идентичности.

# Открытие и преобразование исходного изображения.
imgOrig = Image.open('C:\\YaDisk\\Работы\\СНИЛС\\Изображения\\example.jpg')
print (str(time.ctime()) + ' Исходное изображение открыто.')
imgOrig = imgOrig.convert('L')
print (str(time.ctime()) + ' Исходное изображение конвертировано RGB->L.')
imgBin = binarize(imgOrig)
print (str(time.ctime()) + ' Исходное изображение бинаризовано.')
imgDraw = imgBin.convert('RGBA')
drawRects = ImageDraw.Draw(imgDraw)

# Открытие коллекции шаблонов символов.
imgChar = []
dxChar = []
dyChar = []
for iChar in range(76):
    char = characters[iChar]
    imgChar.append(Image.open('C:\\YaDisk\\Работы\\СНИЛС\\Шаблоны\\' +
                              char + '.bmp'))
    dxChar.append(imgChar[iChar].size[0])
    dyChar.append(imgChar[iChar].size[1])
print (str(time.ctime()) + ' Коллекция символов открыта.')

# Сегментация исходного изображения.
print (str(time.ctime()) + ' Сегментация изображения...')
group = -1                      # Номер группы пикселей.
bounds = []                     # Границы рамок групп пикселей.
colRels = []                    # Коллекция связностей групп.
pix = imgBin.load()             # Матрица пикселей бинаризированного изображения.
pixGroups = []                  # Матрица принадлежности пикселей к группам.
for x in range(0, imgBin.size[0]):
    pixGroups.append([])
    for y in range(0, imgBin.size[1]):
        if pix[x, y] == 0:      # Если пиксель черный.
            
            isAlone = True
            mainGroup = 0
            
            # Номера групп у соседних пикселей [dx,dy,N].
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
                            # Определить номер группы пикселя,
                            # взятого за "главного" в окрестности.
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
            
            # Если пиксель единственный черный в своей полуокрестности,
            if isAlone:
                # то присвоить ему новый номер сегмента.
                group = group + 1
                pixGroups[x].append(group)
                bounds.append([x, y, x, y])
        else:
            pixGroups[x].append(0)

print (str(time.ctime()) + ' Объединение сегментов...')
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

print (str(time.ctime()) + ' Прорисовка границ сегментов...')
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
