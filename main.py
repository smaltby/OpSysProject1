import sys
from collections import deque

n = 0			# Number of processes
m = 1			# Number of processors
t_cs = 8		# Time (ms) it takes to perform a context switch
t_slice = 84    # Time slice (ms) for Round Robin algorithm
t = 0 			# Elapsed time (ms)


class Process:
    def __init__(self, id, t_arrival, t_burst, num_bursts, t_io):
        self.id = id
        self.t_arrival = t_arrival
        self.t_burst = t_burst
        self.num_bursts = num_bursts
        self.t_io = t_io


def main():
    if len(sys.argv) != 3:
        print >> sys.stderr, 'ERROR: Invalid arguments\nUSAGE: ./a.out <input-file> <output-file>'
        exit()

    # Open input and output files
    input_name = sys.argv[1]
    output_name = sys.argv[2]
    input_f = open(input_name, 'r')
    output_f = open(output_name, 'w')
    processes = []

    # Read processes from file and parse into Processes
    for line in input_f:
        if not line.startswith("#") and not line.isspace():
            args = line.split("|")
            if len(args) != 5:
                print >> sys.stderr, 'ERROR: Invalid formatting'
                exit()
            processes.append(Process(args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4])))

    # Run algorithms
<<<<<<< HEAD
    # fcfs(processes)
    # sjf(processes)
    print
    rr(processes)


def rr(processes):
    global t

    ready_q = deque()
    running = None
    running_time = 0
    blocked = {}

    current_slice = 0
    rem_burst = {}

    cs_begin = 0
    cs_end = 0

    # Map processes to their arrival times for ez lookup
    arrival_times = {}
    for process in processes:
        if process.t_arrival not in arrival_times:
            arrival_times[process.t_arrival] = [process]
        else:
            arrival_times[process.t_arrival].append(process)

    # Loop 1 ms at a time
    t = 0
    print "time %dms: Simulator started for RR [Q %s]" % (t, queue_print(ready_q))
    while 1:
        # Check for new arrivals and processes finishing I/O
        if t in arrival_times:
            for process in arrival_times[t]:
                ready_q.append(process)
                print "time %dms: Process %s arrived [Q %s]" % (t, process.id, queue_print(ready_q))
            del arrival_times[t]
        if t in blocked:
            for process in blocked[t]:
                ready_q.append(process)
                print "time %dms: Process %s completed I/O [Q %s]" % (t, process.id, queue_print(ready_q))
            del blocked[t]

        if cs_begin > 0:  # Currently context switching to new process
            cs_begin -= 1
            if cs_begin == 0:  # Context switch complete, begin burst
                if running in rem_burst:
                    running_time = rem_burst[running]
                else:
                    running_time = running.t_burst
                current_slice = t_slice
                print "time %dms: Process %s started using the CPU [Q %s]" % (t, running.id, queue_print(ready_q))
        elif running_time <= 0 or current_slice <= 0:  # Currently running burst OR waiting
            if running is not None:
                # Burst completed, if there are any remaining, block it on I/O, otherwise terminate
                if running_time <= 0:
                    running.num_bursts -= 1
                    if running in rem_burst:
                        del rem_burst[running]

                    # Block if bursts remain, terminate otherwise
                    if running.num_bursts > 0:
                        print "time %dms: Process %s completed a CPU burst; %d to go [Q %s]" \
                              % (t, running.id, running.num_bursts, queue_print(ready_q))

                        # Block the process on I/O
                        blocked_until = t + running.t_io
                        if blocked_until not in blocked:
                            blocked[blocked_until] = [running]
                        else:
                            blocked[blocked_until].append(running)

                        print "time %dms: Process %s blocked on I/O  until time %dms [Q %s]" \
                              % (t, running.id, blocked_until, queue_print(ready_q))
                    else:
                        print "time %dms: Process %s terminated [Q %s]" % (t, running.id, queue_print(ready_q))
                elif len(ready_q) == 0:
                    # If the ready queue is empty when the time slice expired, renew the time slice for the current
                    # running process
                    print "time %dms: Time slice expired; no preemption because ready queue is empty [Q %s]" \
                          % (t, queue_print(ready_q))
                    current_slice = t_slice
                    continue
                else:
                    rem_burst[running] = running_time
                    ready_q.append(running)
                    print "time %dms: Time slice expired; process %s preempted with %dms to go [Q %s]" \
                          % (t, running.id, running_time, queue_print(ready_q))

                cs_end = t_cs / 2
                running = None

            # If nothing is running and ready_q has an available process and not context switching,
            # context switch to new process
            if running is None and len(ready_q) > 0 and cs_end <= 0:
                running = ready_q.popleft()
                cs_begin = t_cs / 2

            # If nothing running and nothing on any upcoming queue and not context switching, end simulator
            if running is None and len(ready_q) == len(blocked) == len(arrival_times) == 0 and cs_end <= 0:
                print "time %dms: Simulator ended for RR" % (t,)
                break

        # Increment time, decrement running time and context switch
        t += 1
        running_time -= 1
        current_slice -= 1
        cs_end -= 1
=======
    #fcfs(processes)
    sjf(processes)
    #rr(processes)
>>>>>>> 9d6715c92af4b653bcff7430335cb3fac6844c62

def sjf(processes):

    global t

    ready_q = deque()
    running = None
    running_time = 0
    blocked = {}    

    cs_begin = 0
    cs_end = 0

    arrival_times = {}
    for process in processes:
        if process.t_arrival not in arrival_times:
            arrival_times[process.t_arrival] = [process]
        else:
            arrival_times[process.t_arrival].append(process)

    t=0
    print "time %dms: Simulator started for SJF [Q %s]" % (t, queue_print(ready_q))

    while 1:
        # Check for new arrivals and processes finishing I/O
        if t in arrival_times:
            for process in arrival_times[t]:
                ready_q.append(process)
                print "time %dms: Process %s arrived [Q %s]" % (t, process.id, queue_print(ready_q))
            del arrival_times[t]
        if t in blocked:
            for process in blocked[t]:
                ready_q.append(process)
                print "time %dms: Process %s completed I/O [Q %s]" % (t, process.id, queue_print(ready_q))
            del blocked[t]


        if cs_begin > 0:    # Currently context switching to new process
            cs_begin -= 1
            if cs_begin == 0:   # Context switch complete, begin burst
                running_time = running.t_burst
                print "time %dms: Process %s started using the CPU [Q %s]" % (t, running.id, queue_print(ready_q))
        elif running_time <= 0:     # Currently running burst OR waiting
            if running is not None:
                # Burst completed, if there are any remaining, block it on I/O, otherwise terminate
                running.num_bursts -= 1
                if running.num_bursts > 0:
                    print "time %dms: Process %s completed a CPU burst; %d to go [Q %s]"\
                          % (t, running.id, running.num_bursts, queue_print(ready_q))

                    # Block the process on I/O
                    blocked_until = t + running.t_io
                    if blocked_until not in blocked:
                        blocked[blocked_until] = [running]
                    else:
                        blocked[blocked_until].append(running)

                    print "time %dms: Process %s blocked on I/O  until time %dm/s [Q %s]" \
                          % (t, running.id, blocked_until, queue_print(ready_q))
                else:
                    print "time %dms: Process %s terminated [Q %s]" % (t, running.id, queue_print(ready_q))

                cs_end = t_cs / 2
                running = None


        # If nothing is running and ready_q has an available process and not context switching,
            # context switch to new process
        if running is None and len(ready_q) > 0 and cs_end <= 0:
            #get the process w/ the shortest time left
            for process in ready_q:
                # time remaining = t_burst*num_bursts
                if running == None or process.t_burst < running.t_burst:
                    running = process
            ready_q.remove(running)
            cs_begin = t_cs / 2

            # If nothing running and nothing on any upcoming queue and not context swiching, end simulator
        if running is None and len(ready_q) == len(blocked) == len(arrival_times) == 0 and cs_end <= 0:
                print "time %dms: Simulator ended for SJF" % (t,)
                break

        # Increment time, decrement running time and context switch
        t += 1
        running_time -= 1
        cs_end -= 1


def fcfs(processes):
    global t

    ready_q = deque()
    running = None
    running_time = 0
    blocked = {}

    cs_begin = 0
    cs_end = 0

    # Map processes to their arrival times for ez lookup
    arrival_times = {}
    for process in processes:
        if process.t_arrival not in arrival_times:
            arrival_times[process.t_arrival] = [process]
        else:
            arrival_times[process.t_arrival].append(process)

    # Loop 1 ms at a time
    t = 0
    print "time %dms: Simulator started for FCFS [Q %s]" % (t, queue_print(ready_q))
    while 1:
        # Check for new arrivals and processes finishing I/O
        if t in arrival_times:
            for process in arrival_times[t]:
                ready_q.append(process)
                print "time %dms: Process %s arrived [Q %s]" % (t, process.id, queue_print(ready_q))
            del arrival_times[t]
        if t in blocked:
            for process in blocked[t]:
                ready_q.append(process)
                print "time %dms: Process %s completed I/O [Q %s]" % (t, process.id, queue_print(ready_q))
            del blocked[t]

        if cs_begin > 0:    # Currently context switching to new process
            cs_begin -= 1
            if cs_begin == 0:   # Context switch complete, begin burst
                running_time = running.t_burst
                print "time %dms: Process %s started using the CPU [Q %s]" % (t, running.id, queue_print(ready_q))
        elif running_time <= 0:     # Currently running burst OR waiting
            if running is not None:
                # Burst completed, if there are any remaining, block it on I/O, otherwise terminate
                running.num_bursts -= 1
                if running.num_bursts > 0:
                    print "time %dms: Process %s completed a CPU burst; %d to go [Q %s]"\
                          % (t, running.id, running.num_bursts, queue_print(ready_q))

                    # Block the process on I/O
                    blocked_until = t + running.t_io
                    if blocked_until not in blocked:
                        blocked[blocked_until] = [running]
                    else:
                        blocked[blocked_until].append(running)

                    print "time %dms: Process %s blocked on I/O  until time %dms [Q %s]" \
                          % (t, running.id, blocked_until, queue_print(ready_q))
                else:
                    print "time %dms: Process %s terminated [Q %s]" % (t, running.id, queue_print(ready_q))

                cs_end = t_cs / 2
                running = None

            # If nothing is running and ready_q has an available process and not context switching,
            # context switch to new process
            if running is None and len(ready_q) > 0 and cs_end <= 0:
                running = ready_q.popleft()
                cs_begin = t_cs / 2

            # If nothing running and nothing on any upcoming queue and not context swiching, end simulator
            if running is None and len(ready_q) == len(blocked) == len(arrival_times) == 0 and cs_end <= 0:
                print "time %dms: Simulator ended for FCFS" % (t,)
                sys.stdout.flush()
                break

        # Increment time, decrement running time and context switch
        t += 1
        running_time -= 1
        cs_end -= 1


def queue_print(ready_q):
    if len(ready_q) == 0:
        return 'empty'

    queue_string = ''
    for process in ready_q:
        queue_string += process.id + ' '
    return queue_string[:-1]

if __name__ == "__main__":
    main()
