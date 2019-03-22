import cv2 as cv
import time
import os
import glob

main_delay = 0.2

def rect_smaller(image, delay=main_delay):
    smaller_image = cv.resize(image,(0,0), fx=0.1,fy=0.1)
    time.sleep(main_delay)
    return smaller_image

def rect_brighter(image,size, delay=main_delay):
    height, width = image.shape[:2]
    cut = image[height-1000:height, width-1000:width]
    cv.rectangle(cut, (0,0),(cut.shape[0],cut.shape[1]), (255,255,255), 5)
    cut = cv.add(cut,100)
    time.sleep(main_delay)
    return cut

def prepare_list(mode="REGULAR"):
    folder= "./images/"
    target = "./result/"

    if os.path.isdir(target)==False:
       os.makedirs(target)

    total_list = glob.glob("./images/*.*")

    if mode=="DEBUG":
       print(total_list)
       print(len(total_list))

    return total_list
