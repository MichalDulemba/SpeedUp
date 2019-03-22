#reading thread

import glob
import cv2 as cv
import cProfile
import time
import os
import sys
from threading import Thread
if sys.version_info >= (3,0):
    from queue import Queue
else:
    from Queue import queue
from common_functions import rect_brighter, rect_smaller, prepare_list


def read_image_files(read_files_queue):

    total_list = prepare_list()
    for element in sorted(total_list):
        original_name=os.path.splitext(os.path.basename(element))[0]
        read_files_queue.put((cv.imread(element), original_name))
    print ("Done reading")


if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()


    left_upper_corner = 500
    #right_bottom_corner = max_width - 500
    read_files_queue = Queue(maxsize=1000)
    worker = Thread(target=read_image_files, args=(read_files_queue,))
    worker.setDaemon(True)
    worker.start()

    for i in range(119):
        image, original_name = read_files_queue.get()

        print(original_name)
        small = rect_smaller(image)
        cut = rect_brighter(image, 500)

        image[0:small.shape[0],0:small.shape[1]] = small

        height, width = image.shape[:2]
        print("image width ", width, "height ", height)
        image[height-1000:height, width-1000:width] = cut
        cv.imwrite('./result/smaller_'+original_name+str(time.time())+'.jpg',small)
        cv.imwrite('./result/'+original_name+'.jpg',image )
        read_files_queue.task_done()

    read_files_queue.join()
    worker.join()

    pr.disable()
    pr.print_stats()
