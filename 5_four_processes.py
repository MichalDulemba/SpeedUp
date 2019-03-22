# reading, writing, cutting out and scalling done in separate processes

import glob
import cv2 as cv
import cProfile
import time
import os
import sys
import multiprocessing as mp
from common_functions import rect_brighter, rect_smaller, prepare_list

def read_image_files(read_files_queue):
    total_list = prepare_list()

    for element in sorted(total_list):
        original_name=os.path.splitext(os.path.basename(element))[0]
        read_files_queue.put((original_name, cv.imread(element)))
    print ("Done reading")

def save_image_file(ready_files_queue):

    for i in range(119*2):
        name, image = ready_files_queue.get()
        cv.imwrite('./result/'+name+'.jpg', image)

def add_mini(read_files_queue, with_mini_queue):
    for i in range(119):
        original_name, original_image  = read_files_queue.get()
        image = original_image.copy()
        print("original name", original_name, " resizing now")

        small = rect_smaller(original_image)
        image[0:small.shape[0],0:small.shape[1]] = small
        small_name = 'smaller_'+original_name+str(time.time())# +'.jpg'
        print ("smaller ver name",small_name)
        write_files_queue.put((small_name, small))

        with_mini_queue.put((original_name,original_image, image))
    print ("finished mini")

def add_rect(with_mini_queue, write_files_queue):
    for i in range(119):
        original_name, original_image, image_with_small = with_mini_queue.get()
        height, width = original_image.shape[:2]
        print("image width ", width, "height ", height)


        print("original name", original_name, " white rectangle now")
        cut = rect_brighter(original_image, 500)
        image_with_small[height-1000:height, width-1000:width] = cut
        write_files_queue.put((original_name, image_with_small))
    print ("finished rect")

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    start =time.time()

    left_upper_corner = 500
    read_files_queue = mp.Queue(maxsize=1000)
    write_files_queue = mp.Queue(maxsize=500)
    with_mini_queue = mp.Queue(maxsize=500)

    worker = mp.Process(target=read_image_files, name = "reading", args=(read_files_queue,)) # queue to store read files
    worker.daemon=True
    worker.start()


    worker3 = mp.Process(target=add_mini, name="mini", args=(read_files_queue, with_mini_queue,)) #in and out queue
    worker3.start()

    worker4 = mp.Process(target=add_rect, name="rectangle", args=(with_mini_queue, write_files_queue,))
    worker4.start()


    worker2 = mp.Process(target=save_image_file, name="writing", args=(write_files_queue,)) #queue of the files to be written
    worker2.daemon=True
    worker2.start()


    worker.join()
    print ("reading joined")
    worker3.join()
    print ("mini joined")
    worker4.join()
    print ("rectangle joined")
    worker2.join()
    print ("saving joined")


    print(read_files_queue.qsize())
    print(write_files_queue.qsize())
    print(with_mini_queue.qsize())

    if write_files_queue.empty() is True:
        end =time.time()
    print ("total time", end-start)

    pr.disable()
    pr.print_stats()
