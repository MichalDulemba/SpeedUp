#two threads - separate for reading and saving 

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

def save_image_file(ready_files_queue, number_of_files):

    for i in range(number_of_files*2):
        image,name = ready_files_queue.get()
        print ("writing", name)
        cv.imwrite('./result/'+name, image)
        ready_files_queue.task_done()
    print ("done writing")

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    number_of_files = 119
    left_upper_corner = 500

    read_files_queue = Queue(maxsize=1000)
    worker = Thread(target=read_image_files, args=(read_files_queue,))
    worker.setDaemon(True)
    worker.start()

    write_files_queue = Queue(maxsize=500)
    worker2 = Thread(target=save_image_file, args=(write_files_queue, number_of_files))
    worker2.setDaemon(True)
    worker2.start()

    for i in range(number_of_files):
        image, original_name = read_files_queue.get()
        read_files_queue.task_done()

        print("original name", original_name)
        small = rect_smaller(image)
        cut = rect_brighter(image, 500)

        image[0:small.shape[0],0:small.shape[1]] = small

        height, width = image.shape[:2]
        print("image width ", width, "height ", height)
        image[height-1000:height, width-1000:width] = cut

        write_files_queue.put((image, original_name+'.jpg'))
        small_name = 'smaller_'+original_name+str(time.time())+'.jpg'
        print ("smaller ver name",small_name)
        write_files_queue.put((small, small_name))


    read_files_queue.join()
    write_files_queue.join()

    worker.join()
    print ("read worker joined")

    worker2.join()
    print ("write worker joined")

    pr.disable()
    pr.print_stats()
