import tkinter as tk
from tkinter import messagebox, filedialog
import pyautogui
import threading
import time
import math
import keyboard
import json
import os

class MultiPointClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Touch")
        self.root.geometry("500x450")
        self.root.minsize(500, 450)

        self.points = []          # [x, y, repeat]
        self.markers = []
        self.is_running = False
        self.click_thread = None
        self.stop_tracking = False

        self.mouse_move_threshold = 300
        self.last_mouse_pos = None

        self.timer_thread = None
        self.timer_running = False

        self.total_rounds = 0
        self.stop_reason = ""

        self.control_buttons = []
        self.modify_buttons = []

        self.setup_ui()
        self.update_mouse_position()

        try:
            keyboard.add_hotkey('space', self.add_point)
            keyboard.add_hotkey('esc', self.toggle_click)
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to register global hotkeys. Please run as administrator.\nError: {e}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Row 1: Control buttons + checkboxes
        row1 = tk.Frame(self.root)
        row1.pack(pady=6)

        btn_add = tk.Button(row1, text="Add (Space)", command=self.add_point,
                            width=12, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_add.pack(side=tk.LEFT, padx=2)
        self.control_buttons.append(btn_add)

        btn_del = tk.Button(row1, text="Delete Selected", command=self.delete_selected,
                            width=12, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        btn_del.pack(side=tk.LEFT, padx=2)
        self.control_buttons.append(btn_del)

        btn_clear = tk.Button(row1, text="Clear", command=self.clear_points,
                              width=10, bg="#ff9800", fg="white", font=("Arial", 10, "bold"))
        btn_clear.pack(side=tk.LEFT, padx=2)
        self.control_buttons.append(btn_clear)

        self.topmost_var = tk.IntVar(value=1)
        self.loop_var = tk.IntVar(value=1)

        chk_top = tk.Checkbutton(row1, text="Pin", variable=self.topmost_var,
                                 command=self.toggle_topmost, font=("Arial", 9))
        chk_top.pack(side=tk.LEFT, padx=(8, 0))

        chk_loop = tk.Checkbutton(row1, text="Loop", variable=self.loop_var,
                                  font=("Arial", 9))
        chk_loop.pack(side=tk.LEFT, padx=8)

        self.root.attributes('-topmost', True)

        # Row 2: Parameters
        row2 = tk.Frame(self.root)
        row2.pack(pady=4)

        tk.Label(row2, text="Clicks per second:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.rate_var = tk.StringVar(value="2.0")
        tk.Entry(row2, textvariable=self.rate_var, width=6).pack(side=tk.LEFT, padx=2)
        tk.Label(row2, text="clicks/s", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        tk.Label(row2, text="Interval between points (s):", font=("Arial", 9)).pack(side=tk.LEFT, padx=(10,2))
        self.between_interval_var = tk.StringVar(value="0.5")
        tk.Entry(row2, textvariable=self.between_interval_var, width=6).pack(side=tk.LEFT, padx=2)

        tk.Label(row2, text="Timer (min):", font=("Arial", 9)).pack(side=tk.LEFT, padx=(10,2))
        self.timer_var = tk.StringVar(value="0")
        tk.Entry(row2, textvariable=self.timer_var, width=5).pack(side=tk.LEFT, padx=2)
        self.timer_btn = tk.Button(row2, text="Timer", command=self.start_timer,
                                   width=6, bg="#FFA500", fg="white", font=("Arial", 9, "bold"))
        self.timer_btn.pack(side=tk.LEFT, padx=2)

        # Row 3: Point count, mouse position, modify count
        row3 = tk.Frame(self.root)
        row3.pack(pady=4)

        self.count_label = tk.Label(row3, text="Points: 0", font=("Arial", 9))
        self.count_label.pack(side=tk.LEFT, padx=10)

        self.pos_label = tk.Label(row3, text="Mouse position: (0, 0)", font=("Arial", 9))
        self.pos_label.pack(side=tk.LEFT, padx=15)

        tk.Label(row3, text="Modify count:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(15,2))
        self.repeat_var = tk.StringVar(value="1")
        tk.Entry(row3, textvariable=self.repeat_var, width=5).pack(side=tk.LEFT, padx=2)
        btn_apply = tk.Button(row3, text="Apply", command=self.apply_repeat,
                              width=6, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"))
        btn_apply.pack(side=tk.LEFT, padx=2)
        self.modify_buttons.append(btn_apply)

        # Status bar
        self.status_label = tk.Label(self.root, text="Status: Stopped", fg="gray", font=("Arial", 9))
        self.status_label.pack(pady=2)

        # Point list
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10,
                                  font=("Arial", 9))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Bottom row: Start, Help, Save, Load
        row5 = tk.Frame(self.root)
        row5.pack(pady=6)

        self.toggle_btn = tk.Button(row5, text="▶ Start", command=self.toggle_click,
                                    width=10, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.toggle_btn.pack(side=tk.LEFT, padx=3)

        help_btn = tk.Button(row5, text="📖 Help", command=self.show_help,
                             width=12, bg="#607D8B", fg="white", font=("Arial", 10, "bold"))
        help_btn.pack(side=tk.LEFT, padx=3)

        save_btn = tk.Button(row5, text="💾 Save Config", command=self.save_config,
                             width=12, bg="#388E3C", fg="white", font=("Arial", 10, "bold"))
        save_btn.pack(side=tk.LEFT, padx=3)

        load_btn = tk.Button(row5, text="📂 Load Config", command=self.load_config,
                             width=12, bg="#1976D2", fg="white", font=("Arial", 10, "bold"))
        load_btn.pack(side=tk.LEFT, padx=3)

        tk.Label(self.root, text="Global hotkeys: Space to add | ESC to toggle | Mouse movement auto-stop",
                 font=("Arial", 8), fg="blue").pack(pady=(0, 5))
        tk.Label(self.root, text="Tip: markers are draggable (left-click drag) to update coordinates",
                 font=("Arial", 8), fg="gray").pack()

    # ---------- Save/Load Config ----------
    def save_config(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot save configuration while running")
            return
        if not self.points:
            messagebox.showwarning("Warning", "No points to save")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Configuration"
        )
        if not file_path:
            return
        try:
            data = {"points": self.points}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", f"Configuration saved to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def load_config(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot load configuration while running")
            return
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Configuration"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            new_points = data.get("points", [])
            if not isinstance(new_points, list) or not all(isinstance(p, list) and len(p) == 3 for p in new_points):
                raise ValueError("Invalid configuration format")
            for marker in self.markers:
                try:
                    marker.destroy()
                except:
                    pass
            self.markers.clear()
            self.points.clear()
            for x, y, repeat in new_points:
                self.points.append([x, y, repeat])
                marker = self.create_marker(x, y, len(self.points))
                self.markers.append(marker)
            self.update_listbox()
            self.count_label.config(text=f"Points: {len(self.points)}")
            messagebox.showinfo("Success", f"Loaded {len(self.points)} points")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")

    # ---------- Enable/Disable controls ----------
    def set_controls_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.control_buttons:
            try:
                btn.config(state=state)
            except:
                pass
        for btn in self.modify_buttons:
            try:
                btn.config(state=state)
            except:
                pass

    # ---------- Pin toggle ----------
    def toggle_topmost(self):
        if self.topmost_var.get() == 1:
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)
        for marker in self.markers:
            try:
                marker.attributes('-topmost', self.root.attributes('-topmost'))
            except:
                pass

    # ---------- Apply repeat count ----------
    def apply_repeat(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot modify while running")
            return
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a point from the list")
            return
        try:
            new_repeat = int(self.repeat_var.get())
            if new_repeat < 1:
                raise ValueError
        except:
            messagebox.showwarning("Warning", "Please enter a positive integer (≥1)")
            return
        index = selection[0]
        if 0 <= index < len(self.points):
            self.points[index][2] = new_repeat
            self.update_listbox()

    # ---------- Timer ----------
    def start_timer(self):
        try:
            minutes = float(self.timer_var.get())
        except:
            messagebox.showwarning("Warning", "Please enter a valid number for minutes")
            return
        if minutes <= 0:
            messagebox.showwarning("Warning", "Minutes must be greater than 0")
            return
        if self.timer_running:
            messagebox.showinfo("Info", "Timer already running")
            return
        if not self.is_running:
            self.start_click()
            if not self.is_running:
                return
        self.timer_running = True
        self.timer_btn.config(text="Timer...", state=tk.DISABLED)
        self.status_label.config(text=f"Stopping in {minutes} min", fg="purple")

        def timer_loop():
            time.sleep(minutes * 60)
            if self.timer_running:
                self.stop_reason = "Timer expired"
                self.root.after(0, self.stop_click)
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()

    # ---------- Marker creation (no offset) ----------
    def create_marker(self, x, y, index):
        marker = tk.Toplevel(self.root)
        marker.overrideredirect(True)
        marker.attributes('-topmost', self.root.attributes('-topmost'))
        marker.attributes('-alpha', 0.75)
        marker.config(bg='yellow')
        label = tk.Label(marker, text=str(index), font=("Arial", 12, "bold"),
                         bg='yellow', fg='black', padx=4, pady=2)
        label.pack()
        marker.index = index - 1
        marker.offset_x = 0
        marker.offset_y = 0

        label.bind('<Button-1>', lambda e, m=marker: self.on_marker_press(e, m))
        label.bind('<B1-Motion>', lambda e, m=marker: self.on_marker_drag(e, m))
        label.bind('<ButtonRelease-1>', lambda e, m=marker: self.on_marker_release(e, m))
        marker.bind('<Button-1>', lambda e, m=marker: self.on_marker_press(e, m))
        marker.bind('<B1-Motion>', lambda e, m=marker: self.on_marker_drag(e, m))
        marker.bind('<ButtonRelease-1>', lambda e, m=marker: self.on_marker_release(e, m))

        # Exact alignment (no offset)
        marker.geometry(f"+{x}+{y}")
        marker.current_x = x
        marker.current_y = y
        return marker

    def on_marker_press(self, event, marker):
        marker.offset_x = event.x
        marker.offset_y = event.y

    def on_marker_drag(self, event, marker):
        x = event.x_root - marker.offset_x
        y = event.y_root - marker.offset_y
        marker.geometry(f"+{x}+{y}")
        marker.current_x = x
        marker.current_y = y

    def on_marker_release(self, event, marker):
        idx = marker.index
        if 0 <= idx < len(self.points):
            self.points[idx][0] = marker.current_x
            self.points[idx][1] = marker.current_y
            self.update_listbox()
            self.count_label.config(text=f"Points: {len(self.points)}")

    # ---------- Point management ----------
    def add_point(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot add points while running")
            return
        x, y = pyautogui.position()
        self.points.append([x, y, 1])
        marker = self.create_marker(x, y, len(self.points))
        self.markers.append(marker)
        self.update_listbox()
        self.listbox.see(tk.END)
        self.count_label.config(text=f"Points: {len(self.points)}")

    def delete_selected(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot delete points while running")
            return
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.markers):
                self.markers[index].destroy()
                del self.markers[index]
            del self.points[index]
            self.rebuild_markers()
            self.update_listbox()
            self.count_label.config(text=f"Points: {len(self.points)}")

    def clear_points(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Cannot clear points while running")
            return
        if self.points:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all points?"):
                for marker in self.markers:
                    try:
                        marker.destroy()
                    except:
                        pass
                self.markers.clear()
                self.points.clear()
                self.listbox.delete(0, tk.END)
                self.count_label.config(text="Points: 0")

    def rebuild_markers(self):
        for marker in self.markers:
            try:
                marker.destroy()
            except:
                pass
        self.markers.clear()
        for i, (x, y, _) in enumerate(self.points, 1):
            marker = self.create_marker(x, y, i)
            marker.index = i - 1
            self.markers.append(marker)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, (x, y, repeat) in enumerate(self.points, 1):
            self.listbox.insert(tk.END, f"Point {i}: ({x}, {y}) repeat {repeat}")

    # ---------- Help ----------
    def show_help(self):
        help_text = """
        📌 Help

        1. Add click points
           • Move the mouse to the target position, press [Space] (global hotkey) or click "Add (Space)"
           • A semi-transparent numbered label will appear exactly at the cursor position
           • Labels are draggable (left-click drag) to fine-tune coordinates

        2. Start / Stop clicking
           • Click "▶ Start" or press [ESC] (global) to start looping
           • Click "⏹ Stop" (the button toggles) or press [ESC] again to stop
           • Upon stop, the total rounds executed will be displayed

        3. Pin window
           • Check "Pin" to keep the window always on top (enabled by default)

        4. Auto-stop features
           • If you move the mouse more than 300 pixels while clicking, the program stops automatically
           • Move the mouse to the top-left corner of the screen for an emergency stop

        5. Manage points
           • Select a point in the list and click "Delete Selected" to remove it (marker disappears)
           • Click "Clear" to remove all points (with confirmation)

        6. Speed & intervals
           • "Clicks per second" controls the click rate for each point (e.g., 2 clicks/s = 0.5s interval)
           • "Interval between points (s)" sets the delay after finishing one point before starting the next

        7. Loop mode
           • Check "Loop" to repeat endlessly; uncheck to stop after one full round

        8. Timer stop
           • Enter minutes in "Timer (min)" and click "Timer" to start a countdown
           • The program will stop automatically when the time runs out (starts automatically if not running)

        9. Save / Load configuration
           • "Save Config" saves all points (coordinates + repeat counts) to a .json file
           • "Load Config" restores points from a previously saved .json file
        """
        messagebox.showinfo("Help", help_text)

    # ---------- Core control ----------
    def toggle_click(self):
        if self.is_running:
            self.stop_reason = "Manually stopped"
            self.stop_click()
        else:
            self.start_click()

    def start_click(self):
        if self.is_running:
            return
        if not self.points:
            messagebox.showwarning("Warning", "Please add at least one click point first!")
            return
        self.is_running = True
        self.total_rounds = 0
        self.stop_reason = ""
        self.toggle_btn.config(text="⏹ Stop", bg="#f44336", fg="white")
        self.status_label.config(text="Status: Starting...", fg="green")
        try:
            self.last_mouse_pos = pyautogui.position()
        except:
            self.last_mouse_pos = None

        self.set_controls_enabled(False)

        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

    def stop_click(self):
        if not self.is_running:
            return
        self.is_running = False
        self.toggle_btn.config(text="▶ Start", bg="#2196F3", fg="white")
        self.set_controls_enabled(True)

        reason = self.stop_reason if self.stop_reason else "Manually stopped"
        total = self.total_rounds
        self.status_label.config(text=f"Stopped: {reason}, Total rounds: {total}", fg="gray")
        self.last_mouse_pos = None
        if self.timer_running:
            self.timer_running = False
            self.timer_btn.config(text="Timer", state=tk.NORMAL)

    # ---------- Click loop ----------
    def click_loop(self):
        try:
            rate = float(self.rate_var.get())
            if rate <= 0:
                rate = 2.0
        except:
            rate = 2.0
        interval = 1.0 / rate

        try:
            between = float(self.between_interval_var.get())
            if between < 0:
                between = 0.0
        except:
            between = 0.0

        loop = (self.loop_var.get() == 1)

        self.update_status("Executing clicks...", "green")

        click_count = 0
        round_count = 0
        while self.is_running:
            round_count += 1
            self.total_rounds = round_count
            points_snapshot = self.points.copy()
            if not points_snapshot:
                self.stop_reason = "Point list empty"
                self.root.after(0, self.stop_click)
                break

            for i, (x, y, repeat) in enumerate(points_snapshot, 1):
                if not self.is_running:
                    break
                for _ in range(repeat):
                    if not self.is_running:
                        break
                    try:
                        pyautogui.click(x, y)
                        click_count += 1
                        self.update_status(
                            f"Round {round_count} Point {i}/{len(points_snapshot)} (Total {click_count} clicks)",
                            "green"
                        )
                        try:
                            self.last_mouse_pos = pyautogui.position()
                        except:
                            pass
                        time.sleep(interval)
                    except pyautogui.FailSafeException:
                        self.stop_reason = "Mouse moved to top-left (emergency stop)"
                        self.root.after(0, self.stop_click)
                        return
                    except Exception as e:
                        self.stop_reason = f"Click exception at ({x},{y}): {str(e)}"
                        self.root.after(0, self.stop_click)
                        return
                if i < len(points_snapshot):
                    time.sleep(between)
                    try:
                        self.last_mouse_pos = pyautogui.position()
                    except:
                        pass
                if self.last_mouse_pos is not None:
                    try:
                        cur_x, cur_y = pyautogui.position()
                        prev_x, prev_y = self.last_mouse_pos
                        distance = math.hypot(cur_x - prev_x, cur_y - prev_y)
                        if distance >= self.mouse_move_threshold:
                            self.stop_reason = f"Mouse moved {distance:.0f}px (auto-stop)"
                            self.root.after(0, self.stop_click)
                            return
                    except:
                        pass
            if not loop:
                self.stop_reason = f"One round completed (round {round_count}), loop disabled"
                self.root.after(0, self.stop_click)
                break
        if self.is_running:
            self.root.after(0, self.stop_click)

    def update_status(self, text, color=None):
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color if color else "black"))

    def update_mouse_position(self):
        if not self.stop_tracking:
            try:
                x, y = pyautogui.position()
                self.pos_label.config(text=f"Mouse position: ({x}, {y})")
            except:
                pass
            self.root.after(100, self.update_mouse_position)

    def on_closing(self):
        self.stop_tracking = True
        self.is_running = False
        self.timer_running = False
        try:
            keyboard.remove_all_hotkeys()
        except:
            pass
        for marker in self.markers:
            try:
                marker.destroy()
            except:
                pass
        self.markers.clear()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiPointClickerGUI(root)
    root.mainloop()
