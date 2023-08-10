import cv2
from matplotlib import pyplot as plt
import Levenshtein
# from skimage.metrics import structural_similarity as ssim

def lateximage(index):

    img = cv2.imread(f'images/{index}/ground.png')
    img_1 = cv2.imread(f'images/{index}/predict.png')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    gray_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)
    
    cols, rows, channal = img.shape
    cols_1, rows_1, channal_1 = img_1.shape
    if(cols > cols_1):
        gray_1 = cv2.copyMakeBorder(gray_1, 0, cols - cols_1, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif(cols < cols_1):
        gray = cv2.copyMakeBorder(gray, 0, (cols_1 - cols), 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    if(rows > rows_1):
        gray_1 = cv2.copyMakeBorder(gray_1, 0, 0, 0, rows - rows_1, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif(rows < rows_1):
        gray = cv2.copyMakeBorder(gray, 0, 0, 0, rows_1 - rows, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    truth = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
    truth_1 = cv2.threshold(gray_1, 127, 255, cv2.THRESH_BINARY)[1]

    a = list(truth.tolist())
    b = list(truth_1.tolist())

    count = 0
    for i in range(len(a)):
        c = Levenshtein.ratio(a[i], b[i])
        count += c
    
    # (score, diff) = ssim(gray, gray_1, full=True)
    
    return count/len(a)
    