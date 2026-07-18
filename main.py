import queue
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from scripts import aim_trainer

class ScriptManagerApp:
   def __init__(self, root):
      self.root = root
      self.root.title("Human Benchmark Scripts")
      self.root.geometry("650x450")
      self.root.minsize(550, 380)

      self.worker_thread = None
      self.stop_event = threading.Event()
      self.log_queue = queue.Queue()

      self.status_var = tk.StringVar(value="Stopped")
      self.create_widgets()
      self.process_log_queue()

      self.root.protocol("WM_DELETE_WINDOW", self.on_close)

   def create_widgets(self):
      main_frame = ttk.Frame(self.root, padding=15)
      main_frame.pack(fill="both", expand=True)
      title_label = ttk.Label(main_frame, text="Human Benchmark Scripts", font=("Arial", 18, "bold"),)
      title_label.pack(pady=(0, 15))

      script_frame = ttk.LabelFrame(main_frame, text="Available scripts", padding=10,)
      script_frame.pack(fill="x")

      self.script_list = tk.Listbox(script_frame, height=4, exportselection=False,)
      self.script_list.pack(fill="x")

      self.script_list.insert(tk.END, "Aim Trainer")
      self.script_list.selection_set(0)

      control_frame = ttk.Frame(main_frame)
      control_frame.pack(fill="x", pady=15)

      self.start_button = ttk.Button(control_frame, text="Start", command=self.start_script,)
      self.start_button.pack(side="left", padx=(0, 10))
      self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_script, state="disabled",)
      self.stop_button.pack(side="left")
      status_title = ttk.Label(control_frame, text="Status:", font=("Arial", 10, "bold"),)
      status_title.pack(side="left", padx=(25, 5))
      self.status_label = ttk.Label(control_frame, textvariable=self.status_var,)
      self.status_label.pack(side="left")
      
      log_frame = ttk.LabelFrame(main_frame, text="Logs", padding=10,)
      log_frame.pack(fill="both", expand=True)

      self.log_text = ScrolledText(log_frame, height=12, state="disabled", wrap="word",)
      self.log_text.pack(fill="both", expand=True)

   def start_script(self):
      if self.worker_thread and self.worker_thread.is_alive():
         self.add_log("Aim Trainer is already running.")
         return

      selected = self.script_list.curselection()

      if not selected:
         self.add_log("Select a script first.")
         return

      script_name = self.script_list.get(selected[0])

      if script_name != "Aim Trainer":
         self.add_log("This script is not implemented yet.")
         return
      
      self.stop_event.clear()
      self.status_var.set("Running")

      self.start_button.config(state="disabled")
      self.stop_button.config(state="normal")
      self.script_list.config(state="disabled")

      self.add_log("Starting Aim Trainer...")

      self.worker_thread = threading.Thread(target=self.run_aim_trainer, daemon=True,)
      self.worker_thread.start()

   def run_aim_trainer(self):
      try:
         aim_trainer.run(stop_event=self.stop_event, log_callback=self.thread_log,)
      except Exception as error:
         self.thread_log(f"Unexpected error: {error}")
      finally:
         self.log_queue.put(("finished", None))

   def stop_script(self):
      if not self.worker_thread or not self.worker_thread.is_alive():
         self.add_log("No script is currently running.")
         self.reset_controls()
         return

      self.add_log("Stopping Aim Trainer...")
      self.status_var.set("Stopping")
      self.stop_button.config(state="disabled")

      self.stop_event.set() 

   def thread_log(self, message):
      self.log_queue.put(("log", message))

   def process_log_queue(self):
      try:
         while True:
               message_type, message = self.log_queue.get_nowait()

               if message_type == "log":
                  self.add_log(message)

               elif message_type == "finished":
                  self.add_log("Script thread finished.")
                  self.reset_controls()

      except queue.Empty:
         pass

      self.root.after(50, self.process_log_queue)

   def add_log(self, message):
      self.log_text.config(state="normal")
      self.log_text.insert(tk.END, message + "\n")
      self.log_text.see(tk.END)
      self.log_text.config(state="disabled")

   def reset_controls(self):
      self.status_var.set("Stopped")
      self.start_button.config(state="normal")
      self.stop_button.config(state="disabled")
      self.script_list.config(state="normal")

   def on_close(self):
      self.stop_event.set()
      self.root.destroy()

def main():
   root = tk.Tk()
   app = ScriptManagerApp(root)
   root.mainloop()

if __name__ == "__main__":
   main()