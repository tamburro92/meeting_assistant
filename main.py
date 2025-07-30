import tkinter as tk
from meeting_assistant.ui.gui import MeetingApp

if __name__ == "__main__":
    root = tk.Tk()
    app = MeetingApp(root)
    root.mainloop()
