import cv2 as cv
import cProfile
import time
import os
from common_functions import rect_brighter, rect_smaller, prepare_list

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    total_list = prepare_list()
    left_upper_corner = 500

    for element in sorted(total_list):
        image = cv.imread(element)
        original_name=os.path.splitext(os.path.basename(element))[0]
        print(original_name)
        small = rect_smaller(image)
        cut = rect_brighter(image, 500)

        image[0:small.shape[0],0:small.shape[1]] = small

        height, width = image.shape[:2]
        print("image width ", width, "height ", height)
        image[height-1000:height, width-1000:width] = cut
        cv.imwrite('./result/smaller_'+original_name+str(time.time())+'.jpg',small)
        cv.imwrite('./result/'+original_name+'.jpg',image )

    pr.disable()
    pr.print_stats()
