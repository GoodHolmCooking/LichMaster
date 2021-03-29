import sqlite3
import tkinter as tk
import database
from tkinter import ttk
from tkinter import messagebox
from adversaries import AdversaryEditor
from combat import CombatTracker
from adjustments import AdjustDefense
from campaign import MainMenu
from campaign import NewCampaign
from campaign import SessionManager
from campaign import EncounterManager

class Root(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Lich Master")
        container = tk.Frame(self)
        container.pack()

        self.frames = {}

        for F in (MainMenu, AdversaryEditor, EncounterManager, CombatTracker, SessionManager):
            frame = F(container, self) # MainMenu(tk.Frame(lich_master), lich_master)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # switched to combattracker for bug testing, should normally be MainMenu
        self.show_frame(MainMenu)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

    def back_to_sessions(self):
        frame = self.frames[SessionManager]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

def main():
    lich_master = Root()
    lich_master.mainloop()

if __name__.endswith('__main__'):
    main()
