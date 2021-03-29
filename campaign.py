import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import re
from combat import CombatTracker
from adversaries import AdversaryEditor
from adjustments import AdjustDefense
import database

# Data used by multiple classes
setting = ""
campaign = ""
session = ""
encounter = ""
encounter_adversaries = []
talents_to_save = {}
talent_string_for_ui = ""

# TODO: Manage adversaries should refer to the setting, right now is just a generic adversary manager I think hard coded to Terrinoth

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.build_campaign_window(controller, parent)
        self.load_settings()
        self.load_campaigns()

    def build_campaign_window(self, controller, parent):
        global campaign

        menu = tk.Menu(self)
        controller.config(menu=menu)

        file_menu_options = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Navigate", menu=file_menu_options)
        file_menu_options.add_command(label="Main Menu", command=lambda:controller.show_frame(MainMenu))
        file_menu_options.add_command(label="Session Manager", command=lambda:controller.show_frame(SessionManager))

        player_menu_options = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Players", menu=player_menu_options)
        player_menu_options.add_command(label="Adjust Defense", command=lambda:self.adjust_defenses(controller))

        # Setting
        self.setting_label = tk.Label(self, text="Settings")
        self.setting_label.grid(row=0, column=0)
        self.setting_listbox = tk.Listbox(self, height=4, width=65)
        self.setting_listbox.grid(row=1, column=0, rowspan=2)
        self.setting_scrollbar = tk.Scrollbar(self)
        self.setting_scrollbar.grid(row=1, column=1, rowspan=2, sticky="ns")
        self.setting_listbox.configure(yscrollcommand=self.setting_scrollbar.set)
        self.setting_scrollbar.configure(command=self.setting_listbox.yview)
        self.new_setting_btn = ttk.Button(self, text="New setting", command=lambda:self.new_setting(controller)).grid(row=1, column=2, sticky="n")
        self.delete_setting_btn = ttk.Button(self, text="Manage setting", command=self.manage_setting).grid(row=2, column=2, sticky="n")

        # Campaign
        self.campaign_label = tk.Label(self, text="Campaigns")
        self.campaign_label.grid(row=3, column=0)
        self.campaign_listbox = tk.Listbox(self, height=4, width=65)
        self.campaign_listbox.grid(row=4, column=0, rowspan=2)
        self.campaign_scrollbar = tk.Scrollbar(self)
        self.campaign_scrollbar.grid(row=4, column=1, rowspan=2, sticky="ns")
        self.campaign_listbox.configure(yscrollcommand=self.campaign_scrollbar.set)
        self.campaign_scrollbar.configure(command=self.campaign_listbox.yview)
        self.new_campaign_btn = ttk.Button(self, text="New Campaign", command=lambda:self.new_campaign(controller)).grid(row=4, column=2, sticky="n")
        self.delete_campaign_btn = ttk.Button(self, text="Delete Campaign", command=self.run_delete_campaign).grid(row=5, column=2, sticky="n")

        # Current players
        self.present_player_label = tk.Label(self, text="Players at session").grid(row=6, column=0)
        self.present_player_listbox = tk.Listbox(self, height=4, width=65)
        self.present_player_listbox.grid(row=7, column=0)
        self.present_player_scrollbar = tk.Scrollbar(self)
        self.present_player_scrollbar.grid(row=7, column=1, sticky="ns")
        self.present_player_listbox.configure(yscrollcommand=self.present_player_scrollbar.set)
        self.present_player_scrollbar.configure(command=self.present_player_listbox.yview)
        self.present_player_inactive_btn = ttk.Button(self, text="Not at session", command=self.deactivate_player).grid(row=7, column=2, sticky="n")

        # All players
        self.avail_player_label = tk.Label(self, text="Players not present").grid(row=8, column=0)
        self.avail_player_listbox = tk.Listbox(self, height=4, width=65)
        self.avail_player_listbox.grid(row=9, column=0, rowspan=3)
        self.avail_player_scrollbar = tk.Scrollbar(self)
        self.avail_player_scrollbar.grid(row=9, column=1, rowspan=3, sticky="ns")
        self.avail_player_listbox.configure(yscrollcommand=self.avail_player_scrollbar.set)
        self.avail_player_scrollbar.configure(command=self.avail_player_listbox.yview)
        self.avail_player_active_btn = ttk.Button(self, text="At session", command=self.activate_player).grid(row=9, column=2, sticky="n")
        self.new_player_btn = ttk.Button(self, text="New player", command=self.create_new_player).grid(row=10, column=2, sticky="s")
        self.delete_player_btn = ttk.Button(self, text="Delete player", command=self.delete_player).grid(row=11, column=2)

        # Footer
        self.session_btn = ttk.Button(self, text="Manage Sessions", command=lambda:self.manage_sessions(controller, parent))
        self.session_btn.grid(row=12, column=0, columnspan=3)
        self.adversary_btn = ttk.Button(self, text="Adversary Editor", command=lambda:controller.show_frame(AdversaryEditor))
        self.adversary_btn.grid(row=13, column=0, columnspan=3)

        self.campaign_listbox.bind('<<ListboxSelect>>', self.set_active_campaign)

    def load_settings(self):
        for setting in database.view_table('master', 'settings'):
            self.setting_listbox.insert(tk.END, setting)

    def load_campaigns(self):
        if database.view_table("Terrinoth", "campaigns"):
            for c in database.view_table("Terrinoth", "campaigns"):
                self.campaign_listbox.insert(tk.END, c[0])

    def new_setting(self, controller):
        root = NewSetting(controller)

    def manage_setting(self):
        pass

    def set_active_campaign(self, event):
        global campaign

        campaign_selection = self.campaign_listbox.curselection()
        # Is any campaign selected?
        if campaign_selection:
            index = self.campaign_listbox.curselection()[0]
            campaign = self.campaign_listbox.get(index)

            database.switch_to_active("Terrinoth", 'campaign', campaign)

            self.show_active_players()
        # If not let's change the active campaign to blank. In theory meaning nothing is selected.
        else:
            campaign = ""

    def show_active_players(self):
        # show players for active campaign
        fetched_players = database.fetch_players("Terrinoth", campaign)
        # clear the listboxes
        self.present_player_listbox.delete(0, tk.END)
        self.avail_player_listbox.delete(0, tk.END)
        for player in fetched_players.keys():
            if fetched_players[player] == 1:
                self.present_player_listbox.insert(tk.END, player)
            else:
                self.avail_player_listbox.insert(tk.END, player)


    def run_delete_campaign(self):
        global campaign
        database.delete_campaign("Terrinoth", campaign)
        self.present_player_listbox.delete(0, tk.END)
        self.avail_player_listbox.delete(0, tk.END)
        self.campaign_listbox.delete(0, tk.END)
        if database.view_table("Terrinoth", "campaigns"):
            for c in database.view_table("Terrinoth", "campaigns"):
                self.campaign_listbox.insert(tk.END, c[0])

    def deactivate_player(self):
        index = self.present_player_listbox.curselection()
        player = self.present_player_listbox.get(index)
        self.present_player_listbox.delete(index)
        self.avail_player_listbox.insert(tk.END, player)
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        cur.execute("UPDATE campaign_players SET attending = 0 WHERE player = ?", (player,))
        conn.commit()
        conn.close()

    def activate_player(self):
        index = self.avail_player_listbox.curselection()
        player = self.avail_player_listbox.get(index)
        self.avail_player_listbox.delete(index)
        self.present_player_listbox.insert(tk.END, player)
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        cur.execute("UPDATE campaign_players SET attending = 1 WHERE player = ?", (player,))
        conn.commit()
        conn.close()

    def new_campaign(self, controller):
        global campaign
        # global player_list
        root = NewCampaign(controller)
        self.wait_window(root)
        self.campaign_listbox.insert(tk.END, campaign)

    def manage_sessions(self, controller, parent):
        # print("Running manage_sessions")
        global campaign
        index = self.campaign_listbox.curselection()
        if index:
            campaign = self.campaign_listbox.get(index)
            controller.show_frame(SessionManager)
        else:
            messagebox.showwarning("No campaign selected", "No campaign selected; please select a campaign.")

    def adjust_defenses(self, controller):
        root = AdjustDefense(controller)

    def create_new_player(self):
        self.create_new_player_window()
        self.add_new_player_to_listbox()

    def create_new_player_window(self):
        global campaign
        self.new_player_window = NewPlayerWindow(self)

    def add_new_player_to_listbox(self):
        self.wait_window(self.new_player_window)

        fetched_players = database.fetch_players("Terrinoth", campaign)

        # Check to see if the player is in the listbox already, if they aren't add them.
        for player in fetched_players.keys():
            if fetched_players[player] == 1:
                if not player in self.present_player_listbox.get(0, tk.END):
                    self.present_player_listbox.insert(tk.END, player)
            else:
                if not player in self.avail_player_listbox.get(0, tk.END):
                    self.avail_player_listbox.insert(tk.END, player)

    def delete_player(self):
        self.delete_from_present_player_listbox()
        self.delete_from_avail_player_listbox()
        self.update_present_players_in_db()

    def delete_from_present_player_listbox(self):
        if self.present_player_listbox.curselection():
            index = self.present_player_listbox.curselection()
            player = self.present_player_listbox.get(index)
            self.present_player_listbox.delete(index)

    def delete_from_avail_player_listbox(self):
        if self.avail_player_listbox.curselection():
            index = self.avail_player_listbox.curselection()
            player = self.avail_player_listbox.get(index)
            self.avail_player_listbox.delete(index)

    def update_present_players_in_db(self):
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        cur.execute("DELETE FROM campaign_players WHERE player = (?)", (player,))
        conn.commit()
        conn.close()

class NewSetting(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        # Header
        self.base_label = tk.Label(self, text="Base")
        # self.base_label.grid(row=0, column=0)
        self.selected_base = tk.StringVar(self)
        fetched_settings = database.fetch_settings()
        avail_settings = []
        avail_settings.append("Select a setting")
        for setting in fetched_settings:
            avail_settings.append(setting[0])
        self.base_options = ttk.OptionMenu(self, self.selected_base, *avail_settings)
        # self.base_options.grid(row=0, column=1)
        self.import_btn = ttk.Button(self, text="Import Setting as Base")
        # self.import_btn.grid(row=0, column=6)
        self.name_label = tk.Label(self, text="Setting Name").grid(row=1, column=0)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=1, column=1)
        ttk.Separator(self).grid(row=2, columnspan=7)

        # Skills
        # New skill area
        self.skill_add_label = tk.Label(self, text="Skill to Add").grid(row=3, column=0)
        self.skill_add_entry = tk.Entry(self)
        self.skill_add_entry.grid(row=3, column=1)
        self.selected_char = tk.StringVar(self)
        self.avail_char = ('Select linked characteristic', 'Brawn', 'Agility', 'Intellect', 'Cunning', 'Willpower', 'Presence')
        self.char_options = ttk.OptionMenu(self, self.selected_char, *self.avail_char)
        self.char_options.grid(row=3, column=3)
        self.selected_skill_type = tk.StringVar(self)
        self.skill_types = ('Select skill type', 'General', 'Magic/Power', 'Combat', 'Social', 'Knowledge')
        self.skill_add_options = ttk.OptionMenu(self, self.selected_skill_type, *self.skill_types)
        self.skill_add_options.grid(row=3, column=4)
        self.skill_add_btn = ttk.Button(self, text="Add Skill", command=self.add_skill).grid(row=3, column=6)

        # General skills
        self.gen_skill_label = tk.Label(self, text="General Skills").grid(row=4, column=0, columnspan=2, sticky="e")
        self.gen_skill_listbox = tk.Listbox(self, width=30)
        self.gen_skill_listbox.grid(row=5, column=0, columnspan=2, sticky="e")
        self.gen_skill_sb = tk.Scrollbar(self)
        self.gen_skill_sb.grid(row=5, column=2, sticky="ns")
        self.gen_skill_listbox.configure(yscrollcommand=self.gen_skill_sb.set)
        self.gen_skill_sb.configure(command=self.gen_skill_listbox.yview)

        # Combat skills
        self.combat_skill_label = tk.Label(self, text="Combat Skills").grid(row=4, column=3, columnspan=2, sticky="e")
        self.combat_skill_listbox = tk.Listbox(self, width=30)
        self.combat_skill_listbox.grid(row=5, column=3, columnspan=2, sticky="e")
        self.combat_skill_sb = tk.Scrollbar(self)
        self.combat_skill_sb.grid(row=5, column=5, sticky="nsw")
        self.combat_skill_listbox.configure(yscrollcommand=self.combat_skill_sb.set)
        self.combat_skill_sb.configure(command=self.combat_skill_listbox.yview)

        # Social skills
        self.social_skill_label = tk.Label(self, text="Social Skills").grid(row=4, column=6, columnspan=2, sticky="e")
        self.social_skill_listbox = tk.Listbox(self, width=30)
        self.social_skill_listbox.grid(row=5, column=6, columnspan=2)
        self.social_skill_sb = tk.Scrollbar(self)
        self.social_skill_sb.grid(row=5, column=8, sticky="ns")
        self.social_skill_listbox.configure(yscrollcommand=self.social_skill_sb.set)
        self.social_skill_sb.configure(command=self.social_skill_listbox.yview)

        # Magic/Power skills
        self.magic_skill_label = tk.Label(self, text="Magic/Power Skills").grid(row=6, column=0, columnspan=2, sticky="e")
        self.magic_skill_listbox = tk.Listbox(self, width=30)
        self.magic_skill_listbox.grid(row=7, column=0, columnspan=2, sticky="e")
        self.magic_skill_sb = tk.Scrollbar(self)
        self.magic_skill_sb.grid(row=7, column=2, sticky="ns")
        self.magic_skill_listbox.configure(yscrollcommand=self.magic_skill_sb.set)
        self.magic_skill_sb.configure(command=self.magic_skill_listbox.yview)

        # Knowledge skills
        self.know_skill_label = tk.Label(self, text="Knowledge Skills").grid(row=6, column=3, columnspan=2, sticky="e")
        self.know_skill_listbox = tk.Listbox(self, width=30)
        self.know_skill_listbox.grid(row=7, column=3, columnspan=2, sticky="e")
        self.know_skill_sb = tk.Scrollbar(self)
        self.know_skill_sb.grid(row=7, column=5, sticky="ns")
        self.know_skill_listbox.configure(yscrollcommand=self.know_skill_sb.set)
        self.know_skill_sb.configure(command=self.know_skill_listbox.yview)

        self.remove_skill_btn = ttk.Button(self, text="Remove Skill").grid(row=7, column=6, sticky="s")

        ttk.Separator(self).grid(row=8, columnspan=7)

        # Talent buttons
        self.talent_add_btn = ttk.Button(self, text="Add Talent", command=self.new_talent).grid(row=13, column=6)
        self.talent_remove_btn = ttk.Button(self, text="Remove Talent").grid(row=14, column=6, sticky="n")

        # Setting talents
        self.talent_label = tk.Label(self, text="Talents").grid(row=12, column=0, columnspan=6)
        self.talent_listbox = tk.Listbox(self)
        self.talent_listbox.grid(row=13, column=0, columnspan=5, rowspan=2, sticky="ew")
        self.talent_sb = tk.Scrollbar(self)
        self.talent_sb.grid(row=13, column=5, rowspan=2, sticky="ns")
        self.talent_listbox.configure(yscrollcommand=self.talent_sb.set)
        self.talent_sb.configure(command=self.talent_listbox.yview)

        self.talent_hsb = tk.Scrollbar(self, orient="horizontal")
        self.talent_hsb.grid(row=15, column=0, columnspan=5, sticky="ew")
        self.talent_listbox.configure(xscrollcommand=self.talent_hsb.set)
        self.talent_hsb.configure(command=self.talent_listbox.xview)

        self.save_btn = ttk.Button(self, text="Save Setting").grid(row=15, column=6, sticky="s")

        # insert initial universal values
        self.abbreviations = {"Brawn":"Br", "Agility":"Ag", "Intellect":"Int", "Cunning":"Cun", "Willpower":"Will", "Presence":"Pr"}
        self.general_skills = []
        self.magic_skills = []
        self.combat_skills = []
        self.social_skills = []
        self.knowledge_skills = []
        self.set_inital_skills()



    def set_inital_skills(self):
        universal_skills = database.fetch_univ_skills()
        for name, linked_char, skill_type in universal_skills:
            skill_string = "%s (%s)" % (name, self.abbreviations[linked_char])
            if skill_type == 'General':
                self.general_skills.append(skill_string)
            elif skill_type == 'Combat':
                self.combat_skills.append(skill_string)
            elif skill_type == 'Social':
                self.social_skills.append(skill_string)

        for skill in self.general_skills:
            self.gen_skill_listbox.insert(tk.END, skill)
        for skill in self.combat_skills:
            self.combat_skill_listbox.insert(tk.END, skill)
        for skill in self.social_skills:
            self.social_skill_listbox.insert(tk.END, skill)

    def add_skill(self):
        # name
        name = self.skill_add_entry.get()

        # linked characteristic
        linked_char = self.selected_char.get()

        # skill type
        skill_type = self.selected_skill_type.get()

        skill_string = "%s (%s)" % (name, self.abbreviations[linked_char])

        if skill_type == 'General':
            if not skill_string in self.general_skills:
                self.general_skills.append(skill_string)
                self.general_skills.sort()
                self.gen_skill_listbox.delete(0, tk.END)
                for skill in self.general_skills:
                    self.gen_skill_listbox.insert(tk.END, skill)

        elif skill_type == 'Magic/Power':
            if not skill_string in self.magic_skills:
                self.magic_skills.append(skill_string)
                self.magic_skills.sort()
                self.magic_skill_listbox.delete(0, tk.END)
                for skill in self.magic_skills:
                    self.gen_skill_listbox.insert(tk.END, skill)

        elif skill_type == 'Combat':
            if not skill_string in self.combat_skills:
                self.combat_skills.append(skill_string)
                self.combat_skills.sort()
                self.combat_skill_listbox.delete(0, tk.END)
                for skill in self.combat_skills:
                    self.combat_skill_listbox.insert(tk.END, skill)

        elif skill_type == 'Social':
            if not skill_string in self.social_skills:
                self.social_skills.append(skill_string)
                self.social_skills.sort()
                self.social_skill_listbox.delete(0, tk.END)
                for skill in self.social_skills:
                    self.social_skill_listbox.insert(tk.END, skill)

        elif skill_type == 'Knowledge':
            if not skill_string in self.knowledge_skills:
                self.knowledge_skills.append(skill_string)
                self.knowledge_skills.sort()
                self.knowledge_skill_listbox.delete(0, tk.END)
                for skill in self.knowledge_skills:
                    self.knowledge_skill_listbox.insert(tk.END, skill)

    def new_talent(self):
        root = NewTalent(self)
        self.wait_window(root)
        global talents_to_save
        for talent in talents_to_save.keys():
            talent_description = talents_to_save[talent][2]
            talent_string = "%s (%s)" % (talent, talent_description)
            if not talent_string in self.talent_listbox.get(0, tk.END):
                self.talent_listbox.insert(tk.END, talent_string)

class NewTalent(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        self.talent_name_label = tk.Label(self, text="New Talent Name").grid(row=0, column=0)
        self.talent_name_entry = tk.Entry(self)
        self.talent_name_entry.grid(row=0, column=1, sticky="ew")
        self.selected_ranked_option = tk.StringVar(self)
        self.talent_ranked_choices = ['Is the talent ranked?', 'Yes', 'No']
        self.talent_ranked_options = ttk.OptionMenu(self, self.selected_ranked_option, *self.talent_ranked_choices)
        self.talent_ranked_options.grid(row=1, column=1)

        self.selected_activation_option = tk.StringVar(self)
        self.talent_activation_choices = ['Select the talent\'s activation', 'Passive', 'Active (Incidental, Out of Turn)', 'Active (Incidental)', 'Active (Maneuver)', 'Active (Action)']
        self.talent_activation_options = ttk.OptionMenu(self, self.selected_activation_option, *self.talent_activation_choices)
        self.talent_activation_options.grid(row=1, column=0)

        self.talent_descr_label = tk.Label(self, text="New Talent Description").grid(row=2, column=0, columnspan=2, sticky="ew")
        self.talent_descr_text = tk.Text(self, width=50)
        self.talent_descr_text.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.save_btn = ttk.Button(self, text="Add Talent", command=self.save_talent).grid(row=4, column=0, columnspan=2)

    def save_talent(self):
        # name
        name = self.talent_name_entry.get()

        # is_ranked
        if self.selected_ranked_option.get() == 'Yes':
            is_ranked = 1
        else:
            is_ranked = 0

        # activation
        activation = self.selected_activation_option.get()

        # description
        description = self.talent_descr_text.get("1.0", tk.END)

        # Talent (Description)
        global talents_to_save
        talents_to_save[name] = (is_ranked, activation, description)

        self.destroy()

class NewPlayerWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        top_padding=(10,10)

        self.player_name_label = tk.Label(self, text="Player name:").grid(row=0, column=0, pady=top_padding)
        self.player_name_entry = ttk.Entry(self)
        self.player_name_entry.grid(row=0, column=1, pady=top_padding)
        self.mel_def_label = tk.Label(self, text="M. Defense").grid(row=1, column=0)
        self.selected_mel_def = tk.IntVar(self)
        self.mel_def_options = (0, 0, 1, 2, 3, 4)
        self.mel_def_menu = ttk.OptionMenu(self, self.selected_mel_def, *self.mel_def_options)
        self.mel_def_menu.grid(row=1, column=1)

        self.rng_def_label = tk.Label(self, text="Rng. Defense").grid(row=2, column=0)
        self.selected_rng_def = tk.IntVar(self)
        self.rng_def_options = (0, 0, 1, 2, 3, 4)
        self.rng_def_menu = ttk.OptionMenu(self, self.selected_rng_def, *self.rng_def_options)
        self.rng_def_menu.grid(row=2, column=1)

        self.presence_label = tk.Label(self, text="Presence").grid(row=3, column=0)
        self.selected_presence = tk.IntVar(self)
        self.presence_options = (1, 1, 2, 3, 4, 5)
        self.presence_menu = ttk.OptionMenu(self, self.selected_presence, *self.presence_options)
        self.presence_menu.grid(row=3, column=1)

        self.willpower_label = tk.Label(self, text="Willpower").grid(row=4, column=0)
        self.selected_willpower = tk.IntVar(self)
        self.willpower_options = (1, 1, 2, 3, 4, 5)
        self.willpower_menu = ttk.OptionMenu(self, self.selected_willpower, *self.willpower_options)
        self.willpower_menu.grid(row=4, column=1)

        self.cool_label = tk.Label(self, text="Cool").grid(row=5, column=0)
        self.selected_cool = tk.IntVar(self)
        self.cool_options = (0, 0, 1, 2, 3, 4, 5)
        self.cool_menu = ttk.OptionMenu(self, self.selected_cool, *self.cool_options)
        self.cool_menu.grid(row=5, column=1)

        self.vigilance_label = tk.Label(self, text="Vigilance").grid(row=6, column=0)
        self.selected_vigilance = tk.IntVar(self)
        self.vigilance_options = (0, 0, 1, 2, 3, 4, 5)
        self.vigilance_menu = ttk.OptionMenu(self, self.selected_vigilance, *self.vigilance_options)
        self.vigilance_menu.grid(row=6, column=1)

        self.player_add_btn = ttk.Button(self, text="Add player", command=self.add_player).grid(row=7, column=0, columnspan=2, pady=top_padding, sticky="e")

        self.player_stats = {}

    def add_player(self):
        name = self.player_name_entry.get()
        mel_def = self.selected_mel_def.get()
        rng_def = self.selected_rng_def.get()
        presence = self.selected_presence.get()
        willpower = self.selected_willpower.get()
        cool = self.selected_cool.get()
        vigilance = self.selected_vigilance.get()
        attending = 1

        self.player_stats[name] = (mel_def, rng_def, presence, willpower, cool, vigilance, attending)

        global campaign

        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        cur.execute("INSERT INTO campaign_players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (campaign, name, self.player_stats[name][0], self.player_stats[name][1], self.player_stats[name][2], self.player_stats[name][3], self.player_stats[name][4], self.player_stats[name][5], self.player_stats[name][6]))
        conn.commit()
        conn.close()
        self.destroy()

    def save_campaign(self):
        global campaign
        setting = self.selected_setting.get()
        campaign = self.campaign_entry.get()

        conn = sqlite3.connect(setting)
        cur = conn.cursor()
        cur.execute("SELECT * from campaigns WHERE campaign = ?", (campaign,))
        data = cur.fetchone()
        if data is None:
            cur.execute("INSERT INTO campaigns VALUES (?, ?)", (campaign, 0))
        for player in self.player_listbox.get(0, tk.END):
            cur.execute("INSERT INTO campaign_players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (campaign, player, self.player_stats[player][0], self.player_stats[player][1], self.player_stats[player][2], self.player_stats[player][3], self.player_stats[player][4], self.player_stats[player][5], self.player_stats[player][6]))
        conn.commit()
        conn.close()
        self.destroy()

class NewCampaign(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        self.campaign_name_label = tk.Label(self, text="Campaign name:").grid(row=0, column=0)
        self.campaign_entry = ttk.Entry(self)
        self.campaign_entry.grid(row=0, column=1)

        self.campaign_setting_label = tk.Label(self, text="Setting:").grid(row=1, column=0)

        self.selected_setting = tk.StringVar(self)
        self.avail_settings = ("Terrinoth", "Terrinoth")
        self.setting_options = ttk.OptionMenu(self, self.selected_setting, *self.avail_settings)
        self.setting_options.grid(row=1, column=1)

        self.player_listlabel = tk.Label(self, text="Players").grid(row=2, column=0)
        self.player_listbox = tk.Listbox(self, width=65)
        self.player_listbox.grid(row=3, column=0, columnspan=2)
        self.player_scrollbar = tk.Scrollbar(self)
        self.player_scrollbar.grid(row=3, column=2, sticky="ns")
        self.player_listbox.configure(yscrollcommand=self.player_scrollbar.set)
        self.player_scrollbar.configure(command=self.player_listbox.yview)
        self.player_remove_btn = ttk.Button(self, text="Remove player").grid(row=4, column=1, sticky="e")

        top_padding = (10, 0)

        self.player_name_label = tk.Label(self, text="Player name:").grid(row=5, column=0, pady=top_padding)
        self.player_name_entry = ttk.Entry(self)
        self.player_name_entry.grid(row=5, column=1, pady=top_padding)
        self.mel_def_label = tk.Label(self, text="M. Defense").grid(row=6, column=0)
        self.selected_mel_def = tk.IntVar(self)
        self.mel_def_options = (0, 0, 1, 2, 3, 4)
        self.mel_def_menu = ttk.OptionMenu(self, self.selected_mel_def, *self.mel_def_options)
        self.mel_def_menu.grid(row=6, column=1)

        self.rng_def_label = tk.Label(self, text="Rng. Defense").grid(row=7, column=0)
        self.selected_rng_def = tk.IntVar(self)
        self.rng_def_options = (0, 0, 1, 2, 3, 4)
        self.rng_def_menu = ttk.OptionMenu(self, self.selected_rng_def, *self.rng_def_options)
        self.rng_def_menu.grid(row=7, column=1)

        self.presence_label = tk.Label(self, text="Presence").grid(row=8, column=0)
        self.selected_presence = tk.IntVar(self)
        self.presence_options = (1, 1, 2, 3, 4, 5)
        self.presence_menu = ttk.OptionMenu(self, self.selected_presence, *self.presence_options)
        self.presence_menu.grid(row=8, column=1)

        self.willpower_label = tk.Label(self, text="Willpower").grid(row=9, column=0)
        self.selected_willpower = tk.IntVar(self)
        self.willpower_options = (1, 1, 2, 3, 4, 5)
        self.willpower_menu = ttk.OptionMenu(self, self.selected_willpower, *self.willpower_options)
        self.willpower_menu.grid(row=9, column=1)

        self.cool_label = tk.Label(self, text="Cool").grid(row=10, column=0)
        self.selected_cool = tk.IntVar(self)
        self.cool_options = (0, 0, 1, 2, 3, 4, 5)
        self.cool_menu = ttk.OptionMenu(self, self.selected_cool, *self.cool_options)
        self.cool_menu.grid(row=10, column=1)

        self.vigilance_label = tk.Label(self, text="Vigilance").grid(row=11, column=0)
        self.selected_vigilance = tk.IntVar(self)
        self.vigilance_options = (0, 0, 1, 2, 3, 4, 5)
        self.vigilance_menu = ttk.OptionMenu(self, self.selected_vigilance, *self.vigilance_options)
        self.vigilance_menu.grid(row=11, column=1)

        self.player_add_btn = ttk.Button(self, text="Add player", command=self.add_player).grid(row=12, column=0, columnspan=2, pady=top_padding, sticky="e")
        self.save_btn = ttk.Button(self, text="Save", command=self.save_campaign).grid(row=13, column=0, columnspan=2, sticky="e")

        self.player_stats = {}

    def add_player(self):
        if self.selected_setting.get():
            setting = self.selected_setting.get()
            if self.campaign_entry.get():
                # Apply and save
                campaign = self.campaign_entry.get()
                name = self.player_name_entry.get()
                self.player_listbox.insert(tk.END, name)

                mel_def = self.selected_mel_def.get()
                rng_def = self.selected_rng_def.get()
                presence = self.selected_presence.get()
                willpower = self.selected_willpower.get()
                cool = self.selected_cool.get()
                vigilance = self.selected_vigilance.get()
                attending = 1

                self.player_stats[name] = (mel_def, rng_def, presence, willpower, cool, vigilance, attending)

                # Clear
                self.player_name_entry.delete(0, tk.END)
                self.selected_mel_def.set(0)
                self.selected_rng_def.set(0)
                self.selected_presence.set(0)
                self.selected_willpower.set(0)
                self.selected_cool.set(0)
                self.selected_vigilance.set(0)

            else:
                messagebox.showwarning("No campaign name entered", "Please enter a campaign name")
        else:
            messagebox.showwarning("No setting selected", "Please select a setting")

    def delete_player(self):
        index = self.player_listbox.curselection()
        player = self.player_listbox.get(index)
        self.player_listbox.delete(index)

        del self.player_stats[player]

    def save_campaign(self):
        global campaign
        setting = self.selected_setting.get()
        campaign = self.campaign_entry.get()
        # print("Campaign variable under save is: " + campaign)

        conn = sqlite3.connect(setting)
        cur = conn.cursor()
        cur.execute("SELECT * from campaigns WHERE campaign = ?", (campaign,))
        data = cur.fetchone()
        if data is None:
            cur.execute("INSERT INTO campaigns VALUES (?, ?)", (campaign, 0))
        for player in self.player_listbox.get(0, tk.END):
            cur.execute("INSERT INTO campaign_players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (campaign, player, self.player_stats[player][0], self.player_stats[player][1], self.player_stats[player][2], self.player_stats[player][3], self.player_stats[player][4], self.player_stats[player][5], self.player_stats[player][6]))
        conn.commit()
        conn.close()
        self.destroy()

class SessionManager(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.campaign_name = tk.Label(self)
        self.campaign_name.grid(row=0, column=0)

        self.sessions_label = tk.Label(self, text="Sessions:")
        self.sessions_label.grid(row=1, column=0)
        self.sessions_list = tk.Listbox(self, width=50, height=12)
        self.sessions_list.grid(row=2, column=0)
        self.sessions_sby = tk.Scrollbar(self)
        self.sessions_sby.grid(row=2, column=1, sticky="ns")
        self.sessions_list.configure(yscrollcommand=self.sessions_sby.set)
        self.sessions_sby.configure(command=self.sessions_list.yview)

        self.sessions_list.bind('<<ListboxSelect>>', self.update_session_select)

        self.add_session = tk.Button(self, text="Add Session", command=lambda:self.add_session_func(self.sessions_list, "Terrinoth"))
        self.add_session.grid(row=3, column=0)
        self.remove_session = tk.Button(self, text="Remove Session", command=self.remove_session)
        self.remove_session.grid(row=4, column=0)

        self.encounters_label = tk.Label(self, text="Encounters:")
        self.encounters_label.grid(row=5, column=0)
        self.encounters_list = tk.Listbox(self, width=50, height=12)
        self.encounters_list.grid(row=6, column=0)
        self.encounters_sby = tk.Scrollbar(self)
        self.encounters_sby.grid(row=6, column=1, sticky="ns")
        self.encounters_list.configure(yscrollcommand=self.encounters_sby.set)
        self.encounters_sby.configure(command=self.encounters_list.yview)

        self.add_encounter_btn = tk.Button(self, text="Add Encounter", command=lambda:self.add_encounter(controller), state="disabled")
        self.add_encounter_btn.grid(row=7, column=0)
        self.remove_encounter_btn = tk.Button(self, text="Remove Encounter", command=self.remove_encounter, state="disabled")
        self.remove_encounter_btn.grid(row=8, column=0)


        self.encounters_list.bind('<<ListboxSelect>>', self.update_encounter_select)

        self.encounters_list.bind('<Double-Button-1>', lambda x:self.activate_encounter(controller))

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        global campaign

        # Configure name
        self.campaign_name.config(text=campaign)
        # Fetch and insert current campaign sessions
        if self.sessions_list.get(0, tk.END):
            pass
        else:
            fetched_session_list = database.fetch_campaign_sessions("Terrinoth", campaign)
            for s in fetched_session_list:
                if s not in self.sessions_list.get(0, tk.END):
                    self.sessions_list.insert(tk.END, s)
        # update encounters
        if self.encounters_list.get(0, tk.END):
            self.encounters_list.delete(0, tk.END)
            encounters = database.fetch_session_encounters("Terrinoth", database.fetch_active("Terrinoth", 'session', campaign))
            for e in encounters:
                self.encounters_list.insert(tk.END, e)


    def update_encounter_select(self, event): # Session 1: Muffin Man
        if self.encounters_list.curselection():
            global encounter
            index = self.encounters_list.curselection()[0]
            encounter = self.encounters_list.get(index).split("(")[0][:-1] # Dead in the Dark (Structured) --> ['Dead in the Dark ', Structured)] --> 'Dead in the Dark'

    def activate_encounter(self, controller):
        database.switch_to_active("Terrinoth", 'encounter', encounter)
        controller.show_frame(EncounterManager)

    def update_session_select(self, event): # Session 1: Muffin Man
        global session

        # This makes sure that if you have no sessions, you can't add an encounter. If you have any sessions, the encounter button gets enabled.

        if self.sessions_list.get(0, tk.END):
            if self.add_encounter_btn.cget("state") == "disabled":
                self.add_encounter_btn.config(state="active")
            if self.remove_encounter_btn.cget("state") == "disabled":
                self.remove_encounter_btn.config(state="active")
            if self.sessions_list.curselection():
                index = self.sessions_list.curselection()[0]
                session = self.sessions_list.get(index)
                database.switch_to_active("Terrinoth", 'session', session)

                # clear previous list
                self.encounters_list.delete(0, tk.END)
                encounters_to_add = database.fetch_session_encounters("Terrinoth", session)
                for encounter in encounters_to_add:
                    if encounter not in self.encounters_list.get(0, tk.END):
                        self.encounters_list.insert(tk.END, encounter)
        else:
            if self.add_encounter_btn.cget("state") == "active":
                self.add_encounter_btn.config(state="disabled")
            if self.remove_encounter_btn.cget("state") == "active":
                self.remove_encounter_btn.config(state="disabled")

    def add_session_func(self, listbox, db):
        def save_session_name():
            print("Running save session")
            global campaign
            campaign = database.fetch_active('Terrinoth', 'campaign')
            session_name = name_label_data.get()
            if session_name:
                root.destroy()

                if listbox.get(0, tk.END):
                    prev_session_list = listbox.get(0, tk.END)
                    i = 1

                    for session in prev_session_list:
                        i += 1

                    session_name = "Session " + str(i) + ": " + session_name
                    listbox.insert(tk.END, session_name)

                    conn = sqlite3.connect(db)
                    cur = conn.cursor()
                    cur.execute("INSERT INTO campaign_sessions (campaign, session, active) VALUES (?, ?, ?)", (campaign, session_name, 0))
                    conn.commit()
                    conn.close()

                else:
                    session_name = "Session 1: " + session_name
                    listbox.insert(tk.END, session_name)

                    conn = sqlite3.connect(db)
                    cur = conn.cursor()
                    cur.execute("INSERT INTO campaign_sessions (campaign, session, active) VALUES (?, ?, ?)", (campaign, session_name, 0))
                    conn.commit()
                    conn.close()

                # print("Session saved")

            else:
                messagebox.showwarning("Name not entered", "Enter a session name before continuing.")

        # TODO: Double click to edit name
        root = tk.Toplevel()

        name_label = tk.Label(root, text="Session Name:")
        name_label.grid(row=0, column=0)

        name_label_data = tk.Entry(root)
        name_label_data.grid(row=0, column=1)

        apply_button = tk.Button(root, text="Apply", command=save_session_name)
        apply_button.grid(row=1, column=1)

        root.mainloop()

    def remove_session(self):
        index = self.sessions_list.curselection()
        session = self.sessions_list.get(index)
        # clear database
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        # gather list of encounters
        cur.execute("SELECT * FROM session_encounters WHERE session = (?)", (session,))
        encounters = cur.fetchall()
        # clear encounters of data then delete
        for encounter in encounters:
            cur.execute("DELETE FROM encounter_data WHERE encounter = (?)", (encounter[1],))
            cur.execute("DELETE FROM session_encounters WHERE encounter = (?)", (encounter[1],))
        # delete sessions
        cur.execute("DELETE FROM campaign_sessions WHERE session = (?)", (session,))
        conn.commit()
        conn.close()

        # clear ui
        self.sessions_list.delete(index)
        self.encounters_list.delete(0, tk.END)

    def add_encounter(self, controller):
        global encounter
        encounter = ""
        controller.show_frame(EncounterManager)

    def remove_encounter(self):
        index = self.encounters_list.curselection()
        encounter = self.encounters_list.get(index).split("(")[0][:-1] # 'Bone Brains (Structured)' -- > 'Bone Brains ' --> 'Bone Brains'
        # print("Encounter is: " +str(encounter))
        # clear database
        conn = sqlite3.connect("Terrinoth")
        cur = conn.cursor()
        cur.execute("DELETE FROM encounter_data WHERE encounter = ?", (encounter,))
        cur.execute("DELETE FROM session_encounters WHERE encounter = ?", (encounter,))
        cur.execute("DELETE FROM encounter_injuries WHERE encounter = ?", (encounter,))
        conn.commit()
        conn.close()
        # clear ui
        self.encounters_list.delete(index)

class EncounterManager(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        global session

        self.adversary_list = []

        # Header
        campaign_label = tk.Label(self, text="Campaign:").grid(row=0, column=0)
        # TODO: I thought I fixed the campaign title to read in. Does that mean this placeholder is reduntant? Check when you can.
        campaign_title = tk.Label(self, text="Campaign Placeholder").grid(row=0, column=1)
        session_label = tk.Label(self, text="Session:").grid(row=1, column=0)
        self.session_title = tk.Label(self)
        self.session_title.grid(row=1, column=1)
        encounter_label = tk.Label(self, text="Encounter:").grid(row=2, column=0)
        self.encounter_title = tk.Entry(self)
        self.encounter_title.grid(row=2, column=1)
        type_label = tk.Label(self, text="Type:").grid(row=2, column=3)
        self.selected_type = tk.StringVar(self)
        avail_types = ("Structured", "Structured")
        type_menu = ttk.OptionMenu(self, self.selected_type, *avail_types)
        type_menu.grid(row=2, column=4)

        # Adversaries
        adversary_label = tk.Label(self, text="Adversaries:").grid(row=3, column=0)
        self.adversary_listbox = tk.Listbox(self)
        self.adversary_listbox.grid(row=4, column=0, rowspan=3, columnspan=2, sticky="ew")
        adversary_scrollbar = tk.Scrollbar(self)
        adversary_scrollbar.grid(row=4, column=2, rowspan=3, sticky="ns")
        self.adversary_listbox.configure(yscrollcommand=adversary_scrollbar.set)
        adversary_scrollbar.configure(command=self.adversary_listbox.yview)

        # Adversary Buttons
        add_adversary_btn = tk.Button(self, text="Add Adversary", command=self.add_adversary)
        add_adversary_btn.grid(row=4, column=4)
        remove_adversary_btn = tk.Button(self, text="Remove Adversary", command=self.remove_adversary)
        remove_adversary_btn.grid(row=5, column=4)

        # # Environment
        # environment_label = tk.Label(self, text="Environment:").grid(row=7, column=0)
        # environment_list = tk.Listbox(self)
        # environment_list.grid(row=8, column=0, rowspan=2, columnspan=2, sticky="ew")
        # environment_scrollbar = tk.Scrollbar(self)
        # environment_scrollbar.grid(row=8, column=2, rowspan=3, sticky="ns")
        # environment_list.configure(yscrollcommand=environment_scrollbar.set)
        # environment_scrollbar.configure(command=environment_list.yview)
        #
        # # Environment Buttons
        # add_object_btn = tk.Button(self, text="Add Object", command=self.add_object)
        # add_object_btn.grid(row=8, column=4)
        # remove_object_btn = tk.Button(self, text="Remove Object", command=self.remove_object)
        # remove_object_btn.grid(row=9, column=4)

        # Footer
        save_encounter_btn = tk.Button(self, text="Save Encounter", command=lambda:self.save_encounter("Terrinoth"))
        save_encounter_btn.grid(row=11, column=0)
        run_encounter_btn = tk.Button(self, text="Run Encounter", command=lambda:self.run_encounter(controller))
        run_encounter_btn.grid(row=11, column=4)
        back_btn = tk.Button(self, text="Back to Sessions", command=lambda:controller.show_frame(SessionManager))
        back_btn.grid(row=12, column=0)

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        global encounter
        print("Encounter is: " + str(encounter))
        self.adversary_listbox.delete(0, tk.END)
        self.session_title.config(text=session)

        # self.adversary_list = []

        if encounter:
            self.encounter_title.delete(0, tk.END)
            self.encounter_title.insert(tk.END, encounter)

            fetched_encounter_data = database.fetch_encounter_data("Terrinoth", encounter)

            for adversary in fetched_encounter_data:
                # self.adversary_list.append(adversary)
                self.adversary_listbox.insert(tk.END, adversary)
            fetched_session_type = database.fetch_session_type("Terrinoth", encounter)
            self.selected_type.set(fetched_session_type)
            # load adversaries
            # print("Loaded adversary list is: " + str(self.adversary_list))
        else:
            self.encounter_title.delete(0, tk.END)

    def remove_adversary(self):
        global encounter
        index = self.adversary_listbox.curselection()[0]
        self.adversary_listbox.delete(index)

    def add_adversary(self):
        def add_adversary():
            def submit_group():
                grp_amt = str(selected.get())
                window.destroy()
                adversary = selected_adver.split(":")[0].split(" ")[:-1] # Wild Thing (Minion): Latari --> ['Wild Thing (Minion)', ' Latari'] --> 'Wild Thing (Minion)' --> ['Wild', 'Thing', '(Minion)']
                adversary = " ".join(adversary)

                adversary_grp = adversary + " x " + grp_amt # Reanimate x 3
                id = len(self.adversary_listbox.get(0, tk.END)) + 1
                input = str(id) + "-" + adversary_grp + " (%s)" % adversary_type # 2-Reanimate x 3 (Minion)

                self.adversary_listbox.insert(tk.END, input)

            index = listbox.curselection()[0]
            selected_adver = listbox.get(index) # Wild Thing (Minion): Latari
            print(selected_adver)
            adversary_type = selected_adver.split(":")[0].split()[-1][1:-1] # Wild Thing (Minion): Latari --> ['Wild Thing (Minion)', ' Latari'] --> Wild Thing (Minion) --> ['Wild', 'Thing', '(Minion)']
            print(adversary_type)
            root.destroy()

            if adversary_type == 'Minion':
                window = tk.Toplevel(self)
                label = tk.Label(window, text="How many in group?").pack()
                selected = tk.IntVar(window)
                selected.set(1)
                options = (1,2,3,4,5)
                options_menu = tk.OptionMenu(window, selected, *options)
                options_menu.pack()
                button = tk.Button(window, text="Submit", command=submit_group)
                button.pack()
                # window.mainloop()

            else:
                # print("running else function")
                adversary = selected_adver.split(":")[0] # Raider (Rival): Outlaws --> Raider (Rival)
                id = str(len(self.adversary_listbox.get(0, tk.END)) + 1)
                input = id + "-" + adversary # 2-Raider (Rival)
                self.adversary_listbox.insert(tk.END, input)


        # Build window
        root = tk.Toplevel(self)
        title_label = tk.Label(root, text="Adversary List").grid(row=0, column=0, columnspan=2)
        grp_label = tk.Label(root, text="Group").grid(row=1, column=0)
        selected_grp = tk.StringVar(root)
        selected_grp.set("All")
        # TODO: limit display on select. Doesn't do anything at the moment.
        grps_to_add = ["Undead", "Outlaws", "Daqan"]
        grps_to_add.sort()
        grp_list = ["All"]
        grp_list = grp_list + grps_to_add
        grp_menu = tk.OptionMenu(root, selected_grp, *grp_list)
        grp_menu.grid(row=1, column=1)

        listbox = tk.Listbox(root, height=25, width=75)
        listbox.grid(row=2, column=0, columnspan=3)
        scrollbar = tk.Scrollbar(root)
        scrollbar.grid(row=2, column=3, sticky="ns")
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=listbox.yview)
        button = tk.Button(root, text="Add Adversary", command=add_adversary).grid(row=3, column=1)


        # Populate available adversaries
        avail_adversaries = database.fetch_adversaries()

        if type(avail_adversaries) is list:
            avail_adversaries.sort()
            for adversary in avail_adversaries:
                listbox.insert(tk.END, adversary)
        else:
            listbox.insert(tk.END, avail_adversaries)

        # root.mainloop()
    #
    # def remove_object(self):
    #     print("You removed that object")

    def save_encounter(self, db):
        global session
        enc_name = self.encounter_title.get() # Uptown Bandits
        enc_type = self.selected_type.get() # Structured
        enc_string = enc_name + " (%s)" % enc_type

        conn = sqlite3.connect(db)
        cur = conn.cursor()

        cur.execute("DELETE FROM session_encounters WHERE encounter = (?)", (enc_name,))
        cur.execute("DELETE FROM encounter_data WHERE encounter = (?)", (enc_name,))
        cur.execute("INSERT INTO session_encounters VALUES (?, ?, ?, ?)", (session, enc_name, enc_type, 0))

        for adversary in self.adversary_listbox.get(0, tk.END): # 2-Wild Thing x 3 (Minion) OR # 3-Greyhaven Wizard (Nemesis)
            base = adversary[:adversary.rfind("(")].rstrip() # 2-Wild Thing x 3 (Minion) --> '2-Wild Thing x 3 ' --> '2-Wild Thing x 3'
            id = base.split("-")[0] # ['2', 'Wild Thing x 3'] --> 2
            name = base[base.find("-")+1:] # 2-Wild Thing x 3
            if name[-1].isdigit():
                name = name[:-4]
            print("name is: '%s'" % name)
            fetched_type = database.fetch_adversary_type("Terrinoth", name)
            if fetched_type == "Minion":
                amt_regex = re.compile(r'(x\s)(\d)')
                mo = amt_regex.search(adversary)
                amt = mo.group(2)
            else:
                amt = "1"
            cur.execute("INSERT INTO encounter_data VALUES (?, ?, ?, ?, ?)", (enc_name, id, name, fetched_type, amt))
        conn.commit()
        conn.close()

        messagebox.showinfo("Encounter Saved", enc_name + " successfully saved.")

    def run_encounter(self, controller):
        global encounter
        if not encounter:
            encounter = self.encounter_title.get()
        if database.does_encounter_exist("Terrinoth", encounter):
            database.switch_to_active("Terrinoth", "encounter", encounter)
            controller.show_frame(CombatTracker)
        else:
            messagebox.showwarning("Encounter not saved", "Please save your encounter before running.")
