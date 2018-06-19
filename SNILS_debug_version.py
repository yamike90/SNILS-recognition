#!/usr/bin/env python
# -*- coding: cp1251 -*-

from PIL import Image, ImageChops, ImageDraw
import time

# -------------------------------------------------------------------------------

def binarize(img):
    ''' Возвращает черно-белую копию изображения. '''
    
    # Инициализация переменных.
    imgRes = img.convert('L')   # Копирование исходного изображения.
    pix = img.load()   # Матрица исходных пикселей.
    pix2 = imgRes.load()   # Матрица черно-белых пикселей.
    histogram = img.histogram()   # Гистограмма исходного изображения.
    oldThreshold = 0   # Предыдущее пороговое значение.
    threshold = 127   # Текущее пороговое значение.
    maxCorrelation = 5   # Наибольшая разница между значениями порога.
    
    # Выбор оптимального порогового значения.
    while abs(threshold - oldThreshold) > maxCorrelation:
        
        # Параметры текущего разделения на фон и текст.
        numBackPixels = 0   # Количество пикселей фона.
        numTextPixels = 0   # Количество пикселей текста.
        sumBackPixels = 0   # Сумма значений пикселей фона.
        sumTextPixels = 0   # Сумма значений пикселей текста.
        
        # Сегментация по текущему пороговому значению.
        for val in range(256):
            
            numVal = histogram[val]   # Количество пикселей с оттенком val.
            
            # Определение параметров текущего разделения на фон и текст.
            if (val < threshold):
                # Количество и сумма значений пикселей текста.
                numTextPixels = numTextPixels + 1
                sumTextPixels = sumTextPixels + val
            else:
                # Количество и сумма значений пикселей фона.
                numBackPixels = numBackPixels + 1
                sumBackPixels = sumBackPixels + val
        
        # Расчет нового порогового значения.
        oldThreshold = threshold
        threshold = ((sumBackPixels/numBackPixels) +
                     (sumTextPixels/numTextPixels)) / 2
    
    # Бимодальное пороговое преобразование изображения.
    threshold = threshold + maxCorrelation
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            # Строгое присвоение пикселю черного или белого цвета.
            if pix[i,j] < threshold:
                pix2[i,j] = 0
            else:
                pix2[i,j] = 255
    
    return imgRes   # Вернуть полученное изображение.

# -------------------------------------------------------------------------------

def check_near(x, y, group):
    ''' Находит сегменты связности из смежных черных пикселей. '''
    
    pixGroups[x][y] = group   # Присвоить пикселю № группы.
    
    # Цикл по соседним пикселям.
    for near in nears:
        
        x2 = x + near[0]   # Абсолютные координаты
        y2 = y + near[1]   # соседнего пикселя.
        
        # Исключить координаты, выходящие за край изображения.
        if x2 < 0 or x2 >= imgBin.size[0]:
            continue
        if y2 < 0 or y2 >= imgBin.size[1]:
            continue
        
        # Если соседний пиксель - чёрный, и не входит в группу текущего.
        if (pix[x2, y2] == 0 and pixGroups[x2][y2] <> group):
            
            # Если сосед находится в группе с другим номером.
            if pixGroups[x2][y2] <> -1 and pixGroups[x2][y2] <> group:
                # то присваивать соседам меньший из двух номеров.
                if pixGroups[x2][y2] < group:
                    group = pixGroups[x2][y2]
                else:
                    pixGroups[x2][y2] = group
            
            # Расширение рамки сегмента.
            if      bounds[group][0] > x2:
                    bounds[group][0] = x2
            elif    bounds[group][2] < x2:
                    bounds[group][2] = x2
            if      bounds[group][1] > y2:
                    bounds[group][1] = y2
            elif    bounds[group][3] < y2:
                    bounds[group][3] = y2
            
            global depth   # Определить текущий уровень рекурсии.
            depth = depth + 1   # Новый уровень рекурсии.
            if depth < 500:   # Если глубина рекурсии не превышает 500,
                check_near(x2, y2, group)   # присвоить соседу тот же № группы.
            depth = depth - 1   # Возврат на предыдущий уровень рекурсии.

# -------------------------------------------------------------------------------

def imgcmp(img1, img2):
    ''' Возвращает коэффициент идентичности двух изображений. '''
    
    width = img2.size[0]   # Ширина шаблона.
    height = img2.size[1]   # Высота шаблона.
    img1 = img1.resize((width, height))   # Подогнать вырезку под размеры шаблона.
    
    dif = ImageChops.difference(img1, img2)   # Разностное преобразование.
    dif = dif.convert('1')   # Бинаризация.
    
    # Вернуть долю черных пикселей.
    return float(dif.histogram()[0]) / (width * height)

# -------------------------------------------------------------------------------

def print_field(label, left, top, right, bottom):
    ''' Отображает распознанный текст, заключенный в указанных границах поля. '''
    
    data = ''   # Строки значения поля.
    couples = []   # Массив сегментов в виде пар [символ, рамка].
    past = None   # Рамка предыдущего символа.
    for b in range(len(bounds)):
        bound = bounds[b]   # Рамка текущего сегмента.
        # Если сегмент полностью в указанных границах и достаточно большой.
        if (bound[0] > imgBin.size[0] * left and
            bound[1] > imgBin.size[1] * top and
            bound[2] < imgBin.size[0] * right and
            bound[3] < imgBin.size[1] * bottom and
            text[b] <> '.'):
            couples.append([text[b], bound])   # Добавить в массив сегментов.
    
    # Группировка символов по строкам и сортировка внутри строк.
    couples.sort(key=sortByY)   # Сортировать по вертикальному расположению.
    first = 0   # Индекс первого сегмента в строке.
    for c in range(len(couples)):
        couple = couples[c]   # Текущий сегмент.
        if c:   # Если это не первый символ массива.
            
            # Если между символами существенная разница по оси Y
            # Или символ последний из массива.
            if (couple[1][3] - past[3] > past[3] - past[1] or
                c == len(couples)-1):
                srez = couples[first:c]
                srez.sort(key=sortByX)   # Сортировать символы в строке по X.
                couples[first:c] = srez
                # Добавить знак-индикатор переноса строк.
                couples[c-1][0] = couples[c-1][0] + ('|'
                                  if c < (len(couples)-1) else '')
                first = c   # Определить индекс первого символа след. строки.
        past = couple[1]   # Определить текущую рамку как предыдущую.

    # Сформировать строку значения поля.
    for c in range(len(couples)):
        couple = couples[c]
        data = data + couple[0]   # Конкатенация очередного символа.
        if c:   # Если это не первый символ массива.
            # Если есть существенный разрыв по оси X,
            if couple[1][0] - past[2] > (past[2] - past[0]) / 2:
                couple[0] = ' ' + couple[0]   # определить его как пробел.        past = couple[1]   # Определить текущую рамку как предыдущую.
    print (label + ': ' + data)   # Вывести на экран значение поля.
    
    # Прорисовка прямоугольных границ поля.
    drawRects.rectangle((imgBin.size[0] * left, imgBin.size[1] * top,
                         imgBin.size[0] * right, imgBin.size[1] * bottom),
                        fill=None, outline='#00FF00')

# -------------------------------------------------------------------------------

def split_segment(b):
    ''' Разделяет горизонтальный сегмент на символы. '''
    
    global bounds   # Определить текущий массив границ сегментов.
    width = float(b[2] - b[0])   # Ширина сегмента.
    height = float(b[3] - b[1])   # Высота сегмента.

    # Цикл разделения символа, пока ширина сегмента превышает 0,9 от его высоты.
    while (width > height * 0.9):
        v_min = height   # Минимальное количество черных пикселей.
        x_min = b[0] + int(height * 0.8)   # Значение x разреза с v_min.
        
        # Поиск вертикального разреза с минимальным кол-вом пикселей текста.
        for x in range(b[0] + int(height * 0.35), b[0] + int(height * 1.4)):
            if x >= b[2]:
                break   # Завершить, если достигнут правый край.
            v = 0   # Счетчик черных пикселей.
            # Цикл по пикселям разреза.
            for y in range(b[1], b[3]+1):
                if (pix[x,y] == 0):
                    v = v + 1   # Найден ещё один чёрный пиксель.
            if (v_min > v):   # Запомнить срез, если пока он самый оптимальный.
                v_min = v
                x_min = x
        if (v_min <= 3):
            bounds.append([b[0], b[1], x_min-1, b[3]])   # Отрезание сегмента.
            b[0] = x_min + 1   # Пересчет рамок исходного сегмента.
            width = float(b[2] - b[0])   # Пересчёт ширины сегмента.
        else:
            break   # Пропустить нарезку, если в срезе больше 3-х пкс текста.

# -------------------------------------------------------------------------------

def sortByX(c):   # Сортировка сегментов-символов по x внутри строки.
    return c[1][0]

def sortByY(c):   # Сортировка сегментов-символов по y внутри поля.
    return c[1][3]

# ===============================================================================


# --- ОТКРЫТИЕ И ПРЕОБРАЗОВАНИЕ ИЗОБРАЖЕНИЯ -------------------------------------

imgOrig = Image.open(raw_input('Введите полное имя файла СНИЛС: '))   # Открыть.
imgOrig.draft('L', imgOrig.size)   # Приведение изображения к оттенкам серого.

imgBin = binarize(imgOrig)   # Бимодальная сегментация.
imgDraw = imgBin.convert('RGBA')   # Отладочное полотно № 1 (с рамками полей).
drawRects = ImageDraw.Draw(imgDraw)   # Объект рисования на полотне № 1.


# --- ОТКРЫТИЕ КОЛЛЕЦИИ ШАБЛОНОВ ------------------------------------------------

# Массив имён файлов-шаблонов (*.bmp).
characters = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
              "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", 
              "З", "И", "Й", "К", "Л", "М", "Н", "О", 
              "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", 
              "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю", "Я", 
              "а-", "б-", "в-", "г-", "д-", "е-", "ё-", "ж-", 
              "з-", "и-", "й-", "к-", "л-", "м-", "н-", "о-", 
              "п-", "р-", "с-", "т-", "у-", "ф-", "х-", "ц-", 
              "ч-", "ш-", "щ-", "ъ-", "ы-", "ь-", "э-", "ю-", "я-"]
listChars = []   # Массив изображений шаблонов.

# Поочередное открытие шаблонов символов в оттенках серого.
for iChar in range(len(characters)):
    char = characters[iChar]
    listChars.append(Image.open('patterns\\' + char + '.bmp'))
    listChars[-1].draft('L', listChars[-1].size)
    characters[iChar] = char.replace('-', '')


# --- СЕГМЕНТАЦИЯ ИЗОБРАЖЕНИЯ ---------------------------------------------------

group = -1   # Номер группы пикселей.
bounds = []   # Границы рамок групп пикселей.
pix = imgBin.load()   # Матрица пикселей бинаризированного изображения.
pixGroups = []   # Матрица принадлежности пикселей к группам.
for x in range(0, imgBin.size[0]):
    pixGroups.append([])
    for y in range(0, imgBin.size[1]):
        pixGroups[x].append(-1)

# Массив относительных координат смежных пикселей.
nears = [[-1, 0],
         [-1, -1],
         [0, -1],
         [1, -1],
         [1, 0],
         [1, 1],
         [0, 1],
         [-1, 1]]
depth = 0

# Разделение пикселей на сегменты связности.
for y in range(imgBin.size[1]):
    for x in range(imgBin.size[0]):
        # Если пиксель черный и ему не присвоена группа.
        if (pix[x, y] == 0 and pixGroups[x][y] == -1):
            depth = 0   # Инициализация значения глубины рекурсии.
            group = group + 1   # Увеличить счётчик групп.
            bounds.append([x, y, x, y])   # Начальные границы группы.
            # Присвоить новый № группы текущему и соседним пикселям.
            check_near(x, y, group)

# Обработка и прорисовка сегментов.
for b in bounds:
    
    width = float(b[2] - b[0])   # Ширина сегмента.
    height = float(b[3] - b[1])   # Высота сегмента.
    
    if (width < 3 or height < 5):
        continue   # Пропустить слишком маленький сегмент.
    
    if (width > height * 0.9):
        split_segment(b)   # Разделить склеенные символы.
    
    # Прорисовка прямоугольных границ сегментов.
    drawRects.rectangle((b[0]-1, b[1]-1, b[2]+1, b[3]+1),
                        fill=None, outline='#0000FF')


# --- СОПОСТАВЛЕНИЕ СЕГМЕНТОВ С ШАБЛОНАМИ ---------------------------------------

minIdentityValue = 0.65   # Минимально допустимое значение идентичности.
imgWhite = ImageChops.constant(imgDraw, 255)   # Отладочное полотно № 2.
text = ""   # Строка с распознанными символами.

# Цикл по сегментам.
for b in bounds:
    
    # Пропускать слишком маленькие сегменты.
    if (b[2]-b[0] < 3 or b[3]-b[1] < 5):
        text = text + '.'
        continue
    
    # Обрезка сегмента в отдельное изображение.
    imgCrop = imgBin.crop((b[0],b[1],b[2]+1,b[3]+1))
    
    # Сравнить сегмент с каждым шаблоном.
    matchValue = 0.0   # Наибольшее из найденных значение идентичности.
    for iChar in range(0, len(listChars)):
        
        imgChar = listChars[iChar]   # Изображения символа-шаблона.
        identity = imgcmp(imgCrop, imgChar)   # Идентичность шаблону.
        
        # Если идентичность больше допустимой и ранее найденной.
        if (identity > minIdentityValue and identity > matchValue):
            # Запомнить текущий шаблон.
            matchValue = identity
            matchChar = iChar
    
    # Пропустить отладочную прорисовку, если похожий символ не найден.
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


# --- ВЫВОД НЕОБХОДИМЫХ ПОЛЕЙ ---------------------------------------------------

print_field('№ СНИЛС', 100.0/700, 140.0/500, 600.0/700, 185.0/500)
print_field('Ф.И.О.', 150.0/700, 175.0/500, 600.0/700, 275.0/500)
print_field('Дата рождения', 300.0/700, 230.0/500, 600.0/700, 300.0/500)
print_field('Место рождения', 100.0/700, 285.0/500, 600.0/700, 360.0/500)
print_field('Пол', 100.0/700, 360.0/500, 500.0/700, 410.0/500)
print_field('Дата регистрации', 200.0/700, 400.0/500, 600.0/700, 480.0/500)

while 1:
    answer = raw_input('\nВведите № отладочного изображения (1, 2): ')
    if answer == '1':
        imgDraw.show()   # Показать рамки полей и сегментов.
    elif answer == '2':
        imgWhite.show()   # Показать наложение распознанных символов.
    else:
        exit(1)
