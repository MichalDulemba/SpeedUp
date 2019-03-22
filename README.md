This repo is not meant to be "perfect code" but rather examples how to progress with speed up from
completely not optimised version to super-parallel version, that can be up to X times faster 
(where X is number of cores in your processor)

During those examples you will see how to get from 95s to 7s using threading and multiprocessing.
To better see speed up I added 0.2s delay in processing functions (common_functions) - one function is creating thumbnail and another one is cutting out a small rectangle, changes color and pastes it back in.

To make things easier i hardcoded number of files and send it to processes/threads. Usually it is less error prone than checking
if queue is already/yet empty etc.

Images are gathered "from internet" - if you are owner and want it to be removed - please email me. This was just for test/research.

### Some conclusions:
1) it matters order how you "join" your processes or threads
2) use traceback and try/except - without it there is no way to know what happened in the process/thread (why it hangs)
3) it is good to add "ending" print at the exit of thread/process - this way you will know for sure that it joined main process
4) even with lock there is a chance that on the last element you will have sort of race condition (annoying to debug/fix)
It is good to add checking if queue is empty and possibly catch "empty queue" exception (you will need to set timeout).
5) you probably want to name your processes and threads to see what happens where in your logs
6) if you want to profile program that is using threads or multiprocessing, you will probably need to profile each process/thread separately
- otherwise you will get incorrect results.




#### 1) Linear version (no speed up)
- 1_single_process_and_thread.py  
Time: around 95s  

#### 2) Version with one thread - for reading
2_reading_thread.py  
Time: around 75s  

#### 3) Two threads - one for reading and one for writing
3_two_threads_read_and_write.py  
Time: around 48s  

#### 4) Four separate threads - one for reading, writing, creating small version and cutting out a small piece
4_four_separate_threads.py  
Time: around 27s  

#### 5) Four separate processes - one for reading, writing, creating small version and cutting out a small piece
5_four_processes.py  
Time: around 48s  

#### 6) 8 processes - one for reading, two for writing, 5 for all other actions
6_8_processes_5_do_all_processes.py  
Time: around 20s  

#### 7) 16 processes - 4 reading, 5 writing, 7 do_all processes
7_16_processes.py  
Time: around 15s  

#### 8) 19 processes - 9 writing, 10 do_all processes
8_19_processes_10_do_all_processes.py  
Time: around 9s  

#### 9) 10 do_all processes 
9_global_list_all_processes_with_reading_thread.py  
Time: around 7s  


