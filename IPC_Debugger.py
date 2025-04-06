import os
import time
import socket
import tkinter as tk
from tkinter import scrolledtext
from multiprocessing import Process, Queue, Pipe, Semaphore, shared_memory


# Global list to track running processes
processes = []

# Clear output window
def clear_output(output_widget):
    """Clears the output log."""
    output_widget.delete(1.0, tk.END)

# Separate child function for multiprocessing
def child(pipe):
    """Child process sends data through pipe."""
    pid = os.getpid()
    pipe.send("Hello from child process through pipe")
    pipe.close()


# Monitor Pipes
def monitor_pipes(output_widget):
    """Monitors IPC using pipes."""
    parent_conn, child_conn = Pipe()

    proc = Process(target=child, args=(child_conn,))
    processes.append(proc)
    proc.start()
    proc.join()

    message = f"[PIPE] Received: {parent_conn.recv()}\n"
    update_output(output_widget, message)


# Monitor Shared Memory
def monitor_shared_memory(output_widget):
    """Monitors IPC using shared memory."""
    data = b"Shared Memory Data"
    shm = shared_memory.SharedMemory(create=True, size=len(data))  # Ensure correct size

    # Assign data to shared memory using memoryview
    memoryview(shm.buf)[:len(data)] = data

    message = f"[SHM] Written: {bytes(shm.buf[:len(data)]).decode()} (PID: {os.getpid()})\n"
    update_output(output_widget, message)

    # Clean up
    shm.close()
    shm.unlink()

def monitor_semaphore(output_widget):
    """Demonstrates Semaphore usage with multiple processes."""
    sem = Semaphore(1)
    queue = Queue()

    # Create child processes
    p1 = Process(target=semaphore_child, args=(sem, queue, "Process A"))
    p2 = Process(target=semaphore_child, args=(sem, queue, "Process B"))

    processes.extend([p1, p2])

    # Start and join processes
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # Display output from queue
    while not queue.empty():
        message = queue.get()
        update_output(output_widget, f"[SEMAPHORE] {message}")


# Socket server process (without GUI references)
def socket_server(queue, host, port):
    """Socket server process that sends messages to the queue."""
    pid = os.getpid()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()

        conn, addr = server.accept()
        with conn:
            data = conn.recv(1024)
            queue.put(f"[SOCKET] Received: {data.decode()} (PID: {pid})\n")

# Semaphore child function
def semaphore_child(sem, queue, name):
    sem.acquire()
    queue.put(f"{name} acquired lock (PID: {os.getpid()})\n")
    time.sleep(2)
    queue.put(f"{name} releasing lock (PID: {os.getpid()})\n")
    sem.release()

# Socket client process
def socket_client(host, port):
    """Socket client sends a message."""
    pid = os.getpid()
    time.sleep(1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        client.sendall(f"Hello from socket client! (PID: {pid})".encode())


# Monitor sockets with queue
def monitor_sockets(output_widget):
    """Monitors IPC using sockets with a Queue."""
    host = '127.0.0.1'
    port = 65432

    queue = Queue()

    server_process = Process(target=socket_server, args=(queue, host, port))
    client_process = Process(target=socket_client, args=(host, port))

    processes.append(server_process)  
    processes.append(client_process)

    server_process.start()
    client_process.start()

    client_process.join()
    server_process.join()

    # Display messages from the queue
    while not queue.empty():
        message = queue.get()
        update_output(output_widget, message)

# Stop running processes
def stop_debugger(output_widget):
    """Stops all running IPC processes."""
    for proc in processes:
        if proc.is_alive():
            proc.terminate()
    update_output(output_widget, "\n[STOPPED] All IPC processes terminated.\n")

# Run the IPC Debugger
def run_debugger(output_widget):
    """Runs the entire IPC debugger."""
    output_widget.delete(1.0, tk.END)
    update_output(output_widget, f"\n---- IPC Debugger (PID: {os.getpid()}) ----\n")
    monitor_pipes(output_widget)
    monitor_shared_memory(output_widget)
    monitor_semaphore(output_widget)
    monitor_sockets(output_widget)

    update_output(output_widget, "\nIPC Monitoring Completed!\n")

# GUI Setup
def setup_gui():
    """Creates the GUI window."""
    app = tk.Tk()
    app.title("🛠️ IPC Debugger (Windows Compatible)")
    app.geometry("900x600")
    app.configure(bg="#f0f0f0")

    # Output log area
    output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=100, height=25, font=("Consolas", 11))
    output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Control Buttons (Top Row)
    control_frame = tk.Frame(app, bg="#f0f0f0")
    control_frame.pack(pady=(0, 10))

    run_btn = tk.Button(control_frame, text="▶ Run Debugger", command=lambda: run_debugger(output_text),
                        bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), width=15)
    run_btn.pack(side=tk.LEFT, padx=10)

    stop_btn = tk.Button(control_frame, text="⛔ Stop Debugger", command=lambda: stop_debugger(output_text),
                         bg="#FF9800", fg="white", font=("Helvetica", 12, "bold"), width=15)
    stop_btn.pack(side=tk.LEFT, padx=10)

    clear_btn = tk.Button(control_frame, text="🧹 Clear Log", command=lambda: clear_output(output_text),
                          bg="#F44336", fg="white", font=("Helvetica", 12, "bold"), width=15)
    clear_btn.pack(side=tk.LEFT, padx=10)

    # IPC Buttons (Bottom Row)
    ipc_frame = tk.LabelFrame(app, text="Test Individual IPC Methods", bg="#f0f0f0", font=("Helvetica", 12, "bold"))
    ipc_frame.pack(padx=10, pady=(0, 20))

    tk.Button(ipc_frame, text="🧵 Pipes", command=lambda: monitor_pipes(output_text),
              bg="#2196F3", fg="white", font=("Helvetica", 11), width=18).pack(side=tk.LEFT, padx=10, pady=10)

    tk.Button(ipc_frame, text="💾 Shared Memory", command=lambda: monitor_shared_memory(output_text),
              bg="#9C27B0", fg="white", font=("Helvetica", 11), width=18).pack(side=tk.LEFT, padx=10, pady=10)

    tk.Button(ipc_frame, text="🔐 Semaphore", command=lambda: monitor_semaphore(output_text),
              bg="#3F51B5", fg="white", font=("Helvetica", 11), width=18).pack(side=tk.LEFT, padx=10, pady=10)

    tk.Button(ipc_frame, text="🌐 Sockets", command=lambda: monitor_sockets(output_text),
              bg="#795548", fg="white", font=("Helvetica", 11), width=18).pack(side=tk.LEFT, padx=10, pady=10)

    app.mainloop()



from datetime import datetime
def update_output(output_widget, message):
    """Updates the GUI output area with timestamps."""
    timestamp = datetime.now().strftime("[%H:%M:%S] ")
    output_widget.insert(tk.END, timestamp + message)
    output_widget.see(tk.END)

# Main Execution
if __name__ == "__main__":
    setup_gui()