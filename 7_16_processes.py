#16 separate processes
#SHARED COUNTER https://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing


import glob
import cv2 as cv
import cProfile
import time
import os
import sys
import multiprocessing as mp
import queue # needed for queue empty exception
from common_functions import rect_brighter, rect_smaller, prepare_list


def read_image_files(read_files_queue, all_files_queue,total_counter,lock):
    thisprocessname = mp.current_process().name
    while(total_counter.value < 119):
        element = all_files_queue.get()
        print (thisprocessname, " ", element, "total counter", total_counter.value)
        with lock:
                 total_counter.value = total_counter.value + 1
        original_name=os.path.splitext(os.path.basename(element))[0]
        read_files_queue.put((original_name, cv.imread(element)))

    print ("\n ###### Done reading", thisprocessname, '\n')

def save_image_file(ready_files_queue, total_counter,lock):
        name = ''
        image = []

        thisprocessname = mp.current_process().name
        while(total_counter.value < 238):  #

             name = ''
             image = []
             with lock:
                print (thisprocessname, " SSSS before saving ",  total_counter.value)
                try:
               #if total_counter.value >= 238:
               #    break
                   name, image = ready_files_queue.get(timeout=1)
                except queue.Empty:
                   print ("empty")

                print (thisprocessname, " SSSS saving file ", name)

                total_counter.value = total_counter.value + 1
                print (thisprocessname, " after saving ", total_counter.value)
             if name:
                 cv.imwrite('./result/'+name+'.jpg', image)



        print ("\n ###### done saving ", thisprocessname, '\n')



def do_all(read_files_queue, write_files_queue, total_counter,lock):

    while(total_counter.value < 119):
        thisprocessname = mp.current_process().name
        print ("Process", thisprocessname)
        print("           Entering with before counter: ",total_counter.value)
        try:
             if read_files_queue.empty is not True:
                original_name, original_image  = read_files_queue.get(timeout=1) # waits for element max 1s - if nothing - raise queue empty exception
             with lock:
                print("            processing ", original_name)
                total_counter.value = total_counter.value + 1
                print("         after counter: ",total_counter.value)
        except queue.Empty:
             print ("empty")
             break

        image = original_image.copy()


        small = rect_smaller(original_image)
        image[0:small.shape[0],0:small.shape[1]] = small
        small_name = 'smaller_'+original_name+str(time.time())# +'.jpg'

        write_files_queue.put((small_name, small))

        height, width = original_image.shape[:2]

        cut = rect_brighter(original_image, 500)
        image[height-1000:height, width-1000:width] = cut

        write_files_queue.put((original_name, image))
        if total_counter.value >= 119:
                        break


    print ("\n ###### done processing ", thisprocessname, '\n')


if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    start =time.time()

    my_mp_manager = mp.Manager()
    lock = mp.Lock()
    lock2 = mp.Lock()
    lock3 = mp.Lock()
    lock4 = mp.Lock()


    saving_counter = my_mp_manager.Value('i',0)
    reading_counter = my_mp_manager.Value('i',0)
    total_counter = my_mp_manager.Value('i',0)
    all_files_queue = mp.Queue(maxsize=1000)

    left_upper_corner = 500
    #right_bottom_corner = max_width - 500

    total_list = prepare_list()

    for element in sorted(total_list):
        all_files_queue.put(element)

    read_workers = []
    do_all_workers = []
    write_workers = []

    read_files_queue = mp.Queue(maxsize=1000)
    write_files_queue = mp.Queue(maxsize=1000)

    for i in range(4):
        read_workers.append(mp.Process(target=read_image_files, name = "reading_"+str(i), args=(read_files_queue, all_files_queue, reading_counter, lock4)))
        read_workers[i].start()

    for i in range(7):
        do_all_workers.append(mp.Process(target=do_all, name="do_all_"+str(i), args=(read_files_queue, write_files_queue, total_counter,lock, )))
        do_all_workers[i].start()

    for i in range(5):
        write_workers.append(mp.Process(target=save_image_file, name="writing_"+str(i), args=(write_files_queue, saving_counter, lock2)))
        write_workers[i].start()


    for i in range(4):
        read_workers[i].join()
        print ("read_worker_"+str(i)+" joined")

    for i in range(7):
        do_all_workers[i].join()
        print ("do_all_worker_"+str(i)+" joined")

    for i in range(5):
        write_workers[i].join()
        print ("write_worker_"+str(i)+" joined")



    if write_files_queue.empty() is True:
        end =time.time()
    print ("total time", end-start)

    pr.disable()
    pr.print_stats()
