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
    algorithm(processes, "FCFS", output_f)
    print
    algorithm(processes, "SJF", output_f)
    print
    algorithm(processes, "RR", output_f)


def algorithm(processes, name, output_f):
    global t

    ready_q = deque()
    running = None
    running_time = 0
    blocked = {}

    rem_num_bursts = {}
    for process in processes:
        rem_num_bursts[process] = process.num_bursts

    rem_t_burst = {}
    current_slice = 0

    cs_begin = 0
    cs_end = 0

    stats_procs = {}
    stats_total_burst_time = 0
    stats_total_bursts = 0
    stats_total_cs = 0
    stats_total_preemptions = 0

    # Map processes to their arrival times for ez lookup
    arrival_times = {}
    for process in processes:
        if process.t_arrival not in arrival_times:
            arrival_times[process.t_arrival] = [process]
        else:
            arrival_times[process.t_arrival].append(process)
        stats_procs[process.id] = {
                           "total_wait_time" : 0,
                           "total_turnaround_time" : 0,
                           "turnaround_entered_q" : None,
                           "wait_time_entered_q" : None
                          }
        stats_total_burst_time += (process.num_bursts * process.t_burst)
        stats_total_bursts += process.num_bursts

    # Loop 1 ms at a time
    t = 0
    print "time %dms: Simulator started for %s [Q %s]" % (t, name, queue_print(ready_q))
    while 1:
        # Check for new arrivals and processes finishing I/O
        if t in arrival_times:
            for process in arrival_times[t]:
                ready_q.append(process)
                stats_procs[process.id]["turnaround_entered_q"] = t
                stats_procs[process.id]["wait_time_entered_q"] = t
                sorted( ready_q,cmp=lambda x,y: cmp(x.t_burst, y.t_burst))
                print "time %dms: Process %s arrived [Q %s]" % (t, process.id, queue_print(ready_q))
            del arrival_times[t]
        if t in blocked:
            for process in blocked[t]:
                ready_q.append(process)
                stats_procs[process.id]["turnaround_entered_q"] = t
                stats_procs[process.id]["wait_time_entered_q"] = t
                print "time %dms: Process %s completed I/O [Q %s]" % (t, process.id, queue_print(ready_q))
            del blocked[t]

        if cs_begin > 0:  # Currently context switching to new process
            cs_begin -= 1
            if cs_begin == 0:  # Context switch complete, begin burst
                if running in rem_t_burst:
                    running_time = rem_t_burst[running]
                else:
                    running_time = running.t_burst
                current_slice = t_slice
                print "time %dms: Process %s started using the CPU [Q %s]" % (t, running.id, queue_print(ready_q))
        elif running_time <= 0 or (current_slice <= 0 and name == "RR"):  # Currently running burst OR waiting
            if running is not None:
                # Burst completed, if there are any remaining, block it on I/O, otherwise terminate
                if running_time <= 0:
                    rem_num_bursts[running] -= 1
                    stats_procs[running.id]["total_turnaround_time"] += (t - stats_procs[running.id]["turnaround_entered_q"])
                    if running in rem_t_burst:
                        del rem_t_burst[running]

                    # Block if bursts remain, terminate otherwise
                    if rem_num_bursts[running] > 0:
                        print "time %dms: Process %s completed a CPU burst; %d to go [Q %s]" \
                              % (t, running.id, rem_num_bursts[running], queue_print(ready_q))

                        # Block the process on I/O
                        blocked_until = t + running.t_io
                        if blocked_until not in blocked:
                            blocked[blocked_until] = [running]
                        else:
                            blocked[blocked_until].append(running)

                        print "time %dms: Process %s blocked on I/O until time %dms [Q %s]" \
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
                    rem_t_burst[running] = running_time
                    ready_q.append(running)
                    stats_procs[running.id]["wait_time_entered_q"] = t
                    stats_total_preemptions += 1
                    print "time %dms: Time slice expired; process %s preempted with %dms to go [Q %s]" \
                          % (t, running.id, running_time, queue_print(ready_q))

                cs_end = t_cs / 2
                running = None

            # If nothing is running and ready_q has an available process and not context switching,
            # context switch to new process
            if running is None and len(ready_q) > 0 and cs_end <= 0:
                if name == "SJF":
                    # get the process w/ the shortest time left
                    for process in ready_q:
                        if running is None or process.t_burst < running.t_burst:
                            running = process
                    ready_q.remove(running)
                    stats_procs[running.id]["total_wait_time"] += (t - stats_procs[running.id]["wait_time_entered_q"])
                else:
                    running = ready_q.popleft()
                    stats_procs[running.id]["total_wait_time"] += (t - stats_procs[running.id]["wait_time_entered_q"])
                cs_begin = t_cs / 2
                stats_total_cs += 1

            # If nothing running and nothing on any upcoming queue and not context switching, end simulator
            if running is None and len(ready_q) == len(blocked) == len(arrival_times) == 0 and cs_end <= 0:
                print "time %dms: Simulator ended for %s" % (t, name)
                break

        # Increment time, decrement running time and context switch
        t += 1
        running_time -= 1
        current_slice -= 1
        cs_end -= 1

    stats_print(output_f, name, stats_procs, stats_total_burst_time, stats_total_bursts, stats_total_cs, stats_total_preemptions)

def queue_print(ready_q):
    if len(ready_q) == 0:
        return 'empty'

    queue_string = ''
    for process in ready_q:
        queue_string += process.id + ' '
    return queue_string[:-1]

def stats_print(output_f, algorithm, stats_procs, stats_total_burst_time, stats_total_bursts, stats_total_cs, stats_total_preemptions):
    total_wait_time = 0
    total_turnaround_time = 0

    for key in stats_procs:
        total_wait_time += stats_procs[key]["total_wait_time"]
        total_turnaround_time += stats_procs[key]["total_turnaround_time"]

    print >> output_f, "Algorithm %s" % (algorithm)
    print >> output_f, "-- average CPU burst time: %.2f ms" % (float(stats_total_burst_time) / stats_total_bursts)
    print >> output_f, "-- average wait time: %.2f ms" % (float(total_wait_time) / stats_total_bursts)
    print >> output_f, "-- average turnaround time: %.2f ms" % (float(total_turnaround_time) / stats_total_bursts)
    print >> output_f, "-- total number of context switches: %d" % (stats_total_cs)
    print >> output_f, "-- total number of preemptions: %d" % (stats_total_preemptions)

if __name__ == "__main__":
    main()
