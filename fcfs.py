def fcfs_scheduling(processes, burst_times):
    n = len(processes)
    waiting_time = [0] * n
    turnaround_time = [0] * n

    # Calculate Waiting Time
    for i in range(1, n):
        waiting_time[i] = waiting_time[i - 1] + burst_times[i - 1]

    # Calculate Turnaround Time
    for i in range(n):
        turnaround_time[i] = waiting_time[i] + burst_times[i]

    # Print Results
    print("Process\tBurst Time\tWaiting Time\tTurnaround Time")
    for i in range(n):
        print(f"{processes[i]}\t\t{burst_times[i]}\t\t{waiting_time[i]}\t\t{turnaround_time[i]}")

    # Calculate and Print Average Times
    avg_waiting_time = sum(waiting_time) / n
    avg_turnaround_time = sum(turnaround_time) / n
    print(f"\nAverage Waiting Time: {avg_waiting_time:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")

# Example Input
processes = [1, 2, 3, 4]
burst_times = [5, 8, 6, 3]

fcfs_scheduling(processes, burst_times)
