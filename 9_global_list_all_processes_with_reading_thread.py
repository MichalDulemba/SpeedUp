


import glob
import cv2 as cv
import cProfile
import time
import os
import sys
import multiprocessing as mp
import threading
import queue # needed for queue empty exception
import traceback
from common_functions import rect_brighter, rect_smaller, prepare_list


def better_saving(fast_saving_queue, thisprocessname, writing_message_queue, writing_files_finished):
    thisthreadname = threading.currentThread().getName()
    try:
        close_message = ""
        while True:
          name = False
          try:
             close_message= writing_message_queue.get_nowait()
             if close_message =="Finito" and fast_saving_queue.qsize()==0:
                  print ( thisprocessname," ", thisthreadname, "- got finito")
                  break
          except queue.Empty:
             print (thisprocessname," ", thisthreadname, " - keep writing")

          print(thisprocessname," ", thisthreadname, ">>> Saving queue:", fast_saving_queue.qsize())
          try:
            name, image = fast_saving_queue.get(timeout=1)
            fast_saving_queue.task_done()
          except Exception as e:   #queue.Empty:
            print (thisprocessname," ", thisthreadname, "EXC", e )
            traceback.print_exc(file=sys.stdout)
            print (thisprocessname," ", thisthreadname, "empty saving")
            print (thisprocessname," ", thisthreadname, "close message", close_message)
            break

          print (thisprocessname," ", thisthreadname, " saving: ", name)

          if name:
            cv.imwrite('./result/'+name+'.jpg', image)
    except Exception as e:
        print (thisprocessname," ", thisthreadname," saving E", e)
        traceback.print_exc(file=sys.stdout)

    writing_files_finished.set()
    print (thisprocessname," ", thisthreadname, "^^^^ finished writing ")



def fast_reading(reading_queue, thisprocessname, reading_files_finished, reading_files_started):

    thisthreadname = threading.currentThread().getName()
    files_read = 0 # read files counter
    try:
        while True:
            try:
                    element = all_files_queue.get(timeout=1) #timeout=1
                    original_name=os.path.splitext(os.path.basename(element))[0]
                    original_image = cv.imread(element)
                    reading_queue.put((original_image, original_name))
                    files_read +=1
                    if files_read == 1:
                        reading_files_started.set() #let know to the main thread that first file is coming and it can start processing
                        print (thisprocessname," ", thisthreadname, " first file in")
                    print (thisprocessname," ", thisthreadname, " ", original_name)

            except queue.Empty:
                 print (thisprocessname," ", thisthreadname, " - empty reading queue ")
                 traceback.print_exc(file=sys.stdout)
                 break

    except Exception as e:
        print (thisprocessname," ", thisthreadname, "reading total e", e)
        traceback.print_exc(file=sys.stdout)

    reading_files_finished.set() #set flag that this read has stopped reading files
    print (thisprocessname," ", thisthreadname, "********************************************************* finished reading ")

def do_all(all_files_queue, total_counter,lock):
    try:
        #pr1 = cProfile.Profile()
        #pr1.enable()
        start = time.time()
        thisprocessname = mp.current_process().name

        reading_files_started = threading.Event()
        reading_files_finished = threading.Event()

        reading_queue = queue.Queue(maxsize=1)
        reading_thread = threading.Thread(target = fast_reading , name = "reading", args=(reading_queue, thisprocessname, reading_files_finished, reading_files_started, )) # , arg=(i,)
        reading_thread.start()



        #writing_files_started = threading.Event()
        writing_files_finished = threading.Event()

        writing_fast_queue = queue.Queue(maxsize=1000)
        writing_message_queue = queue.Queue(maxsize=1)

        writing_thread = threading.Thread(target = better_saving, name = "writing", args=(writing_fast_queue, thisprocessname, writing_message_queue, writing_files_finished, ))
        writing_thread.start()


        while(total_counter.value < 119 ): #and writing_fast_queue.qsize() > 0

            print(thisprocessname, "  Entering with before counter: ",total_counter.value)
            print (thisprocessname, "reading queue size", reading_queue.qsize())


            try:


                 # wait for the first file (setting flag "reading files started")
                 while reading_files_started.is_set()==False:
                     time.sleep(0.001)
                 else:
                     print (thisprocessname,"waiting for the first file is over")

                 print (thisprocessname, "emtpy reading queue", reading_queue.empty())
                 print (thisprocessname, "is set finished reading", reading_files_finished.is_set())
                 print (thisprocessname, "is set started reading", reading_files_started.is_set())

                # get files as long as reading thread is working (with timeout for the last deadly files)
                 if reading_files_started.is_set() is True and reading_files_finished.is_set() is False : # reading_queue.qsize() !=0   and reading_queue.empty() is not True
                     original_image, original_name = reading_queue.get(timeout=1)
                 else:
                        print (thisprocessname, "nothing to take - will  break __________________________________________")
                        break
                 print (thisprocessname, " >>>>>>>>>>>>>>>>>>> original name", original_name)
                 with lock:
                          total_counter.value = total_counter.value + 1
            except Exception as e:
                 print (thisprocessname, "Quting Error ", e)
                 traceback.print_exc(file=sys.stdout)
                 break

            reading_queue.task_done()
            image = original_image.copy()
            print (thisprocessname, "lock in")


            print(thisprocessname, "  after counter: ",total_counter.value)
            small = rect_smaller(original_image)
            image[0:small.shape[0],0:small.shape[1]] = small
            small_name = '/smaller_'+original_name+str(time.time())# +'.jpg'
                    #print ("smaller ver name",small_name)
            try:
                writing_fast_queue.put((small_name, small))
                pass
            except Exception as e:
                print (thisprocessname, "error in putting small to write ", e)

            height, width = original_image.shape[:2]
                    #print("image width ", width, "height ", height)


                    #print("original name", original_name, " white rectangle now")
            cut = rect_brighter(original_image, 500)
            image[height-1000:height, width-1000:width] = cut
            print (thisprocessname, " >>>>>>>>>>>>>>>>>>> original name put big", original_name)
            try:
                writing_fast_queue.put((original_name, image))
                pass
            except Exception as e:
                print(thisprocessname, "error in putting ready image ", e)
            if total_counter.value > 119:
                            break
        print("!!!!!\n\n")

        print(thisprocessname, " total_counter.value ", total_counter.value)
        print (thisprocessname,"\n ################################################################### done processing \n")

        end=time.time()
        print ("do all time", end-start)


        print(thisprocessname, " Threads step1: ",len(threading.enumerate()))

        reading_thread.join()
        print(thisprocessname, "after joining reading thread: ",len(threading.enumerate()))

        writing_thread.join()

        print(thisprocessname, "after joining writing: ",len(threading.enumerate()))

        try:
          reading_queue.join()
        except Exception as e:
          print ("joining q", e)

        print (thisprocessname, " total end")

    except Exception as e:
        print (thisprocessname, "************************ >>>>>>>>>>>>>>>>>>>>> failed ",e)
        traceback.print_exc(file=sys.stdout)


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


    left_upper_corner = 500

    total_list = prepare_list()

    all_files_queue = mp.Queue(maxsize=1000)
    for element in sorted(total_list):
        all_files_queue.put(element)

    print ("------------------------------- > All file  names in the queue")

    workers = []

    for i in range(10):
        workers.append(mp.Process(target=do_all, name="do_all_"+str(i), args=(all_files_queue, total_counter, lock,)))
        workers[i].start()

    for i in range(10):
        workers[i].join()
        print ("worker_"+str(i)+" joined")

    end =time.time()
    print ("total time", end-start)

    pr.disable()
    pr.print_stats()
