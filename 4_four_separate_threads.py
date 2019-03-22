#all is done in separate threads - 4 of them, read, save, create_mini, create_rect
#it matters order how you "join" your processes or threads


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
        read_files_queue.put((original_name, cv.imread(element)))

    print ("Done reading")

def save_image_file(start, ready_files_queue, file_number):

    for i in range(file_number*2):
        name, image = ready_files_queue.get()
        cv.imwrite('./result/'+name+'.jpg', image)
        print ("saved", name)
        ready_files_queue.task_done()
    print ("Finished writing")

    if ready_files_queue.empty() is True:
        end = time.time()
        print ("total time", end-start)


def add_mini(read_files_queue, with_mini_queue, write_files_queue, file_number):
    for i in range(file_number):
        original_name, original_image  = read_files_queue.get()
        image = original_image.copy()
        print("original name", original_name, " resizing now")

        small = rect_smaller(original_image)
        image[0:small.shape[0],0:small.shape[1]] = small
        small_name = 'smaller_'+original_name+str(time.time())# +'.jpg'
        print ("smaller ver name",small_name)
        write_files_queue.put((small_name, small))

        with_mini_queue.put((original_name,original_image, image))
        read_files_queue.task_done()
    print ("mini finished")

def add_rect(with_mini_queue, write_files_queue, file_number):
    for i in range(file_number):
        original_name, original_image, image_with_small = with_mini_queue.get()
        height, width = original_image.shape[:2]
        print("image width ", width, "height ", height)


        print("original name", original_name, " white rectangle now")
        cut = rect_brighter(original_image, 500)
        image_with_small[height-1000:height, width-1000:width] = cut
        write_files_queue.put((original_name, image_with_small))
        with_mini_queue.task_done()
    print ("rect finished")

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    start =time.time()
    file_number = 119

    left_upper_corner = 500
    #right_bottom_corner = max_width - 500
    read_files_queue = Queue(maxsize=1000)
    worker = Thread(target=read_image_files, name = "reading", args=(read_files_queue,)) # queue to store read files
    worker.setDaemon(True)
    worker.start()

    write_files_queue = Queue(maxsize=500)
    worker2 = Thread(target=save_image_file, name="writing", args=(start, write_files_queue,file_number,)) #queue of the files to be written
    worker2.setDaemon(True)
    worker2.start()

    with_mini_queue = Queue(maxsize=500)
    worker3 = Thread(target=add_mini, name="mini", args=(read_files_queue, with_mini_queue, write_files_queue,file_number,)) #in and out queue
    #worker3.setDaemon(True)
    worker3.start()

    with_rect_queue = Queue(maxsize=500)
    worker4 = Thread(target=add_rect, name="rectangle", args=(with_mini_queue, write_files_queue,file_number,))
    #worker4.setDaemon(True)
    worker4.start()

    with_mini_queue.join()
    with_rect_queue.join()
    write_files_queue.join()
    read_files_queue.join()

    worker.join()
    worker3.join()
    worker4.join()
    worker2.join()

    pr.disable()
    pr.print_stats()
