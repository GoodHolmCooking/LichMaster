import tkinter as tk
from tkinter import ttk
import sqlite3
import database

class AdjustDefense(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        self.avail_players = []

        fetched_players = database.fetch_player_stats("Terrinoth", database.fetch_active("Terrinoth",'campaign'))
        for player in fetched_players.keys():
            self.avail_players.append(player)

        self.player_defenses = {}
        for player in self.avail_players:
            self.player_defenses[player] = {"Melee":fetched_players[player][0], "Ranged":fetched_players[player][1]}

        self.player_def_widgets = {}

        i = 0

        for player in self.avail_players:
            self.name_label = tk.Label(self, text=player).grid(row=i, column=0)
            self.mel_def_label = tk.Label(self, text="Melee Defense").grid(row=i+1, column=0)
            self.rng_def_label = tk.Label(self, text="Ranged Defense").grid(row=i+1, column=1)

            self.mel_def_value = tk.Label(self, text=self.player_defenses[player]["Melee"])
            self.mel_def_value.grid(row=i+2, column=0)
            self.player_def_widgets['%s_%s' % (player, "Melee")] = self.mel_def_value

            self.rng_def_value = tk.Label(self, text=self.player_defenses[player]["Ranged"])
            self.rng_def_value.grid(row=i+2, column=1)
            self.player_def_widgets['%s_%s' % (player, "Ranged")] = self.rng_def_value

            self.minus_mel_btn = ttk.Button(self, text="+ M. Defense", command=lambda key=player:self.add_mel_defense(key)).grid(row=i, column=2)
            self.add_mel_btn = ttk.Button(self, text="- M. Defense", command=lambda key=player:self.minus_mel_defense(key)).grid(row=i+1, column=2)

            self.minus_rng_btn = ttk.Button(self, text="+ Rng. Defense", command=lambda key=player:self.add_rng_defense(key)).grid(row=i, column=3)
            self.add_rng_btn = ttk.Button(self, text="- Rng. Defense", command=lambda key=player:self.minus_rng_defense(key)).grid(row=i+1, column=3)

            self.minus_both_btn = ttk.Button(self, text="+ Both Defenses", command=lambda key=player:self.add_both_defenses(key)).grid(row=i, column=4)
            self.add_both_btn = ttk.Button(self, text="- Both Defenses", command=lambda key=player:self.minus_both_defenses(key)).grid(row=i+1, column=4)

            ttk.Separator(self, orient="horizontal").grid(row=i+3, columnspan=5, pady=10, sticky="ew")

            i += 4

        ttk.Button(self, text="Save & Close", command=self.save_defense).grid(row=i, column=3)

    def minus_mel_defense(self, key):
        old_defense = self.player_def_widgets['%s_%s' % (key, "Melee")].cget("text")
        if old_defense > 0:
            new_defense = old_defense - 1
            self.player_def_widgets['%s_%s' % (key, "Melee")].config(text=new_defense)

    def add_mel_defense(self, key):
        old_defense = self.player_def_widgets['%s_%s' % (key, "Melee")].cget("text")
        if old_defense < 4:
            new_defense = old_defense + 1
            self.player_def_widgets['%s_%s' % (key, "Melee")].config(text=new_defense)

    def minus_rng_defense(self, key):
        old_defense = self.player_def_widgets['%s_%s' % (key, "Ranged")].cget("text")
        if old_defense > 0:
            new_defense = old_defense - 1
            self.player_def_widgets['%s_%s' % (key, "Ranged")].config(text=new_defense)

    def add_rng_defense(self, key):
        old_defense = self.player_def_widgets['%s_%s' % (key, "Ranged")].cget("text")
        if old_defense < 4:
            new_defense = old_defense + 1
            self.player_def_widgets['%s_%s' % (key, "Ranged")].config(text=new_defense)

    def minus_both_defenses(self, key):
        self.minus_mel_defense(key)
        self.minus_rng_defense(key)

    def add_both_defenses(self, key):
        self.add_mel_defense(key)
        self.add_rng_defense(key)

    def save_defense(self, **defenses):
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()

        for player in self.avail_players:
            cur.execute("UPDATE campaign_players SET mel_def = (?), rng_def = (?) WHERE player = (?)", (self.player_def_widgets['%s_%s' % (player, 'Melee')].cget('text'), self.player_def_widgets['%s_%s' % (player, 'Ranged')].cget('text'), player))

        conn.commit()
        conn.close()
        self.destroy()
