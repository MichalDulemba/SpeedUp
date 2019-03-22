#all in processes - 1 reading, 2 writing, 5 do_all processes (including all actions)
#SHARED COUNTER from https://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing


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

def save_image_file(ready_files_queue, total_counter,lock):
    this_process_name = mp.current_process().name
    while(total_counter.value <= 237 or ready_files_queue.qsize()>0):  #
        name = ''
        image = []
        print (this_process_name, "Counter before saving ",  total_counter.value)
        name, image = ready_files_queue.get(timeout=1)
        print (this_process_name, "Counter saving file ", name)
        if name:
                with lock:
                     total_counter.value = total_counter.value + 1
                print (this_process_name, "after saving ", total_counter.value)
                cv.imwrite('./result/'+name+'.jpg', image)
    print ("done saving", this_process_name)


def do_all(read_files_queue, write_files_queue, total_counter,lock):
    this_process_name = mp.current_process().name

    while(total_counter.value < 119):

        try:

                original_name, original_image  = read_files_queue.get()
                with lock:
                     print("before counter: ",total_counter.value)
                     total_counter.value = total_counter.value + 1
                     print("after counter: ",total_counter.value)

                image = original_image.copy()
                print("original name", original_name, " resizing now")

                small = rect_smaller(original_image)
                image[0:small.shape[0],0:small.shape[1]] = small
                small_name = 'smaller_'+original_name+str(time.time())# +'.jpg'
                print ("smaller ver name",small_name)
                write_files_queue.put((small_name, small))

                height, width = original_image.shape[:2]
                print("image width ", width, "height ", height)


                print("original name", original_name, " white rectangle now")
                cut = rect_brighter(original_image, 500)
                image[height-1000:height, width-1000:width] = cut

                write_files_queue.put((original_name, image))
        except:
                print ("wrong")

    print ("done processing", this_process_name)



if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    start =time.time()

    my_mp_manager = mp.Manager()
    lock = mp.Lock()
    lock2 = mp.Lock()
    lock3 = mp.Lock()

    saving_counter = my_mp_manager.Value('i',0)
    reading_counter = my_mp_manager.Value('i',0)
    total_counter = my_mp_manager.Value('i',0)


    left_upper_corner = 500
    #right_bottom_corner = max_width - 500

    read_files_queue = mp.Queue(maxsize=1000)
    read_worker = mp.Process(target=read_image_files, name = "reading", args=(read_files_queue, )) # queue to store read files reading_counter, lock3
    read_worker.daemon=True
    read_worker.start()


    write_files_queue = mp.Queue(maxsize=500)
    write_worker = mp.Process(target=save_image_file, name="writing", args=(write_files_queue, saving_counter, lock2)) #queue of the files to be written
    write_worker.daemon=True
    write_worker.start()

    write_worker_2 = mp.Process(target=save_image_file, name="writing_2", args=(write_files_queue, saving_counter, lock2)) #queue of the files to be written
    write_worker_2.daemon=True
    write_worker_2.start()

    do_all_workers = []

    for i in range(5):
        do_all_workers.append(mp.Process(target=do_all, name="do_all"+str(i), args=(read_files_queue, write_files_queue, total_counter,lock, )) )
        do_all_workers[i].start()

    read_worker.join()
    print ("read worker joined")

    for i in range(5):
        do_all_workers[i].join()
    print ("do all workers joined")

    write_worker.join()
    print ("write worker joined")

    write_worker_2.join()
    print ("write worker2 joined")

    if write_files_queue.empty() is True:
        end =time.time()
    print ("total time", end-start)

    pr.disable()
    pr.print_stats()
