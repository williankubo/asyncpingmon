
import asyncio
import os
import sys
import time
output_stream = sys.stdout

# https://github.com/williankubo/asyncpingmon/
# https://raw.githubusercontent.com/williankubo/asyncpingmon/main/asyncpingmon.py

## custom variables

version = "v0.1"
delay_refresh = 1
wait_ping_return = 1

# disabel show traceback
sys.tracebacklimit = 0

# verify if there are argument
if len(sys.argv) < 2:
    # if not, show message
    print()
    print()
    print("-= AsyncPingMonitor", version , "=-")
    print()
    print("usage: python3 asyncpingmon.py [ip_list_file]")
    print()
    print("minimal version: Python 3.6")
    print()
    print()
    sys.exit() # and close program

# receive argument in variable
INPUT_FILE = sys.argv[1]

# opening the file in read mode
my_file = open(INPUT_FILE, "r")
  
# reading the file
data = my_file.read()

# replacing end splitting the text 
# when newline ('\n') is seen.
data_into_list_temp = data.split("\n")

# removing empty elements
data_into_list = [ele for ele in data_into_list_temp if ele.strip()]

# closing file
my_file.close()

# add two dimension to iplist:  list[ip] -> list[ip,status]
size_data = len(data_into_list)
col=2
new_data = [0] * size_data
for i in range(size_data):
    new_data[i] = [0] * col
    new_data[i][0]= data_into_list[i]

#print(new_data)

# class colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[40;92m'
    WARNING = '\033[93m'
    FAIL = '\033[40;91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_RED = '\033[1;41m'
    BG_GREEN = '\033[1;42m'
    BG_BLK = '\033[40;1m'

# function to clear screen
clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

# async function, receive index of list
async def ping(index):                              #add the "async" keyword to make a function asynchronous
    global new_data
    global wait_ping_return
    #host = str(host)                               #turn ip address object to string
    host = new_data[index][0]                               #turn ip address object to string
    proc = await asyncio.create_subprocess_shell(  #asyncio can smoothly call subprocess for you
            f'ping {host} -c 1 -W {wait_ping_return}',                   #ping command
            stderr=asyncio.subprocess.DEVNULL,     #silence ping errors
            stdout=asyncio.subprocess.DEVNULL      #silence ping output
            )
    stdout,stderr = await proc.communicate()       #get info from ping process
    if  proc.returncode == 0:                      #if process code was 0                      
        #print(f'{host} is alive!')                 #say it's alive!
        new_data[index][1] = 1                      #set status 1 (UP)
        #print(new_data[index])

    else:
        #print(f'{bcolors.FAIL}{host} is dead!{bcolors.ENDC}')
        new_data[index][1] = 0                      #set status 0 (Down)
        #print(new_data[index])


loop = asyncio.get_event_loop()                    #create an async loop

tasks = []                                         #list to hold ping tasks

# init variable pooling
pooling = 0

# init variable time_start
time_start = time.time()



# clone new_data to new_data2 (reference to detect changes)
new_data2 = list(map(list, new_data))

# main loop
while True:

    # verify time to execute all tasks
    time_finished = time.time()
    if (pooling==0):    # if first time, set time to igual refresh to not wait first screen
        time_range = delay_refresh
    else:    
        time_range = time_finished - time_start
    
    # to avoid ping storm e high cpu
    if time_range < delay_refresh:
        time_rest = delay_refresh - time_range
        time.sleep(time_rest)

    for index in range(len(new_data)):
        task = ping(index)                      #create async task from function we defined above
        tasks.append(task)                      #add task to list of tasks

    tasks = asyncio.gather(*tasks)                     #some magic to assemble the tasks


    if(new_data!=new_data2):            # new_data updated, print new screen

        clearConsole()
        #print(time_range)
        print("-= AsyncPingMonitor", version , "=-")
        print()

        for index2 in range(len(new_data)):
            ip = new_data[index2][0]
            status = new_data[index2][1]
            if status:
                print(f'{bcolors.OKGREEN}{ip} is UP!{bcolors.ENDC}')
            else:
                print(f'{bcolors.FAIL}{ip} is DOWN!{bcolors.ENDC}')

        print()
        new_data2 = list(map(list, new_data))

    else:
        if(pooling==0):             # print first screen

            clearConsole()
            #print(time_range)
            print("-= AsyncPingMonitor", version , "=-")
            print()

            for index2 in range(len(new_data)):
                ip = new_data[index2][0]
                status = new_data[index2][1]
                if status:
                    print(f'{bcolors.OKGREEN}{ip} is UP!{bcolors.ENDC}')
                else:
                    print(f'{bcolors.FAIL}{ip} is DOWN!{bcolors.ENDC}')
            
            print()
            #Update screen line Pooling
            output_stream.write('Pooling %s\r' % pooling)
            output_stream.flush()        

    #Update screen line Pooling
    output_stream.write('Pooling %s\r' % pooling)
    output_stream.flush()

    time_start = time.time()
    #print(time_start)

    pooling = pooling + 1

    loop.run_until_complete(tasks)                     #run all tasks (basically) at once

    tasks = [] 

