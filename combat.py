import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from operator import itemgetter
import critical
import database
import random
import sqlite3
import re
import os

global_adversary = ""
global_weapon_name = ""
global_range = ""

campaign = ""

encounter = ""
encounter_adversaries = []

crit_to_apply = ""

mel_def = 0
rng_def = 0

major_pool = 0
minor_pool = 0
pc_aware = ""
npc_aware = ""
combatants = {"PCs":{}, "NPCs":{}}

rolled_adv = 0
rolled_th = 0
rolled_succ = 0
rolled_fail = 0
rolled_tri = 0
rolled_desp = 0

class CombatTracker(tk.Frame):
    def __init__(self, parent, controller):
        # TODO: Add if statement to cut out bottom bar on dice results
        tk.Frame.__init__(self, parent)

        self.combat_frame_full = False

        self.bind("<<ShowFrame>>", lambda x:self.on_show_frame(controller))

    def on_show_frame(self, controller):
        global encounter
        global encounter_adversaries

        if self.combat_frame_full:
            self.clear_combat_frame()

        self.set_initial_values() # values used in building ui such as current encounter
        self.build_header()
        self.build_ui_per_adversary(controller)
        self.build_footer(controller)

        print(self.widget_dict.items())
    def set_initial_values(self):
        global campaign
        global encounter
        campaign = database.fetch_active("Terrinoth", 'campaign')

        # set encounter
        encounter = database.fetch_active("Terrinoth", 'encounter', campaign)
        encounter_adversaries = database.fetch_encounter_data("Terrinoth", database.fetch_active("Terrinoth", 'encounter'))

        self.adversaries = encounter_adversaries # ('1-Reanimate x 3 (Minion)', '2-Boneguard (Rival)', '3-Reanimate x 4 (Minion)')

        # top_margin = (30,10)
        self.row_begin_value = 1
        self.combat_frame_full = True
        self.establish_dictionaries() # use dictionaries to separate adversary A from adversary C
        self.establish_widget_lists() # used for clearing

    def establish_dictionaries(self):
        self.damage_vars = {}
        self.strain_vars = {}
        self.inflicted_wounds_dict = {}
        self.inflicted_strain_dict = {}
        self.wound_values = {}
        self.strain_values = {}
        self.strain_thresh_dict = {}
        self.wound_thresh_dict = {}
        self.widget_dict = {}
        self.amt_dict = {}
        self.const_amt_dict = {}
        self.dice_dict = {}
        self.key_dict = {}
        self.master_stats = {}
        self.weapon_dict = {}
        self.name_dict = {}

    def establish_widget_lists(self):
        # These aren't used until clearing but are really definitions that need to only be established once.
        self.widget_list = ['name', 'cur_wounds', 'cur_strain', 'strain_btn', 'dmg_btn', 'crit_btn', 'soak_label', 'wound_thresh_label', 'strain_thresh_label', 'mel_def_label', 'rng_def_label', 'soak_value', 'wound_thresh_value', 'strain_thresh_value', 'mel_def_value', 'rng_def_value', 'main_action_label']

        self.action_widget_list = ['weapon_name', 'quality_label', 'action_btn']

    def build_header(self):
        global encounter
        self.title_label = tk.Label(self, text=encounter)
        self.title_label.grid(row=0, column=0, columnspan=4)

    def build_ui_per_adversary(self, controller):
        for adversary in self.adversaries:
            self.load_adversary_stats(adversary)
            self.build_name_btn(adversary, controller)
            self.build_wounds_label()
            self.build_strain_label()

            self.build_stat_labels()
            self.build_stat_label_values()
            self.build_main_action_label()
            self.set_initial_action_values() # fetches equipment and sets dice defaults
            for weapon in self.fetched_equipment:
                # Sets weapon row
                self.action_begin_value += 1
                self.build_actions(controller, weapon)

            # These buttons make references to values in build_actions. They break if built in normal order.
            self.build_damage_btn()
            self.build_crit_btn(controller)
            self.build_strain_if_nemesis(controller)

            self.build_divider()

            # Stores each group of weapons to each individual adversary. If a guard has a rifle and a pistol, both those will be asssigned to that single guard.
            self.weapon_dict[self.row_begin_value] = self.row_actions

            # Sets up row for next adversary
            self.row_begin_value = self.action_begin_value + 2

    def load_adversary_stats(self, adversary):
        self.key = adversary[adversary.find("-")+1:adversary.rfind(" x ")]
        self.full_name = adversary[:adversary.find(" x ")] # '2-Reanimate'
        self.amt = adversary[adversary.rfind("x ")+1:adversary.rfind("(")-1] # '2-Reanimate', 'x', '3' --> 3
        self.amt_dict[self.row_begin_value] = self.amt
        self.const_amt_dict[self.row_begin_value] = self.amt
        fetched_stats = database.fetch_adversary_stats("Terrinoth", self.key)[0] # ('Reanimate', 'Undead', 'Minion', 2, 2, 1, 1, 1, 1, 3, 4, 0, 1, 1)
        self.stats = {}
        self.stats['type'] = fetched_stats[2]
        self.stats['brawn'] = fetched_stats[3]
        self.stats['agility'] = fetched_stats[4]
        self.stats['intellect'] = fetched_stats[5]
        self.stats['cunning'] = fetched_stats[6]
        self.stats['willpower'] = fetched_stats[7]
        self.stats['presence'] = fetched_stats[8]
        self.stats['soak'] = fetched_stats[9]
        self.stats['wound_thresh'] = fetched_stats[10]
        self.stats['strain_thresh'] = fetched_stats[11]
        self.stats['mel_def'] = fetched_stats[12]
        self.stats['rng_def'] = fetched_stats[13]
        self.master_stats[self.row_begin_value] = self.stats

    def build_name_btn(self, adversary, controller):
        self.name_dict[self.row_begin_value] = self.full_name
        self.name_btn = ttk.Button(self, text=adversary, command=lambda key=self.key:self.display_adversary(controller, key))
        self.name_btn.grid(row=self.row_begin_value, column=0)
        self.widget_dict['%s_name' % self.row_begin_value] = self.name_btn

    def build_wounds_label(self):
        # This is just saying the adversary is nice and healthy with no wounds on them.
        # This is the current wounds, not the threshold which is established under stats.
        # This part is the backend used for calculations.
        self.inflicted_wounds_dict[self.row_begin_value] = 0

        # This is the frontend for the user.
        self.cur_wounds = tk.Label(self, text=("Wounds: " + str(self.inflicted_wounds_dict[self.row_begin_value])))
        self.cur_wounds.grid(row=self.row_begin_value, column=1)
        self.widget_dict['%s_cur_wounds' % self.row_begin_value] = self.cur_wounds
        self.wound_values[self.row_begin_value] = self.cur_wounds

    def build_strain_label(self):
        if self.stats['type'] == 'Nemesis':
            self.inflicted_strain_dict[self.row_begin_value] = 0

            # This is the frontend for the user.
            self.cur_strain = tk.Label(self, text=("Strain: " + str(self.inflicted_strain_dict[self.row_begin_value])))
            self.cur_strain.grid(row=self.row_begin_value, column=2)
            self.widget_dict['%s_cur_strain' % self.row_begin_value] = self.cur_strain
            self.strain_values[self.row_begin_value] = self.cur_strain

    def build_strain_if_nemesis(self, controller):
        if self.stats['type'] == 'Nemesis':
            self.selected_strain = tk.IntVar(self)

            self.strain_vars[self.row_begin_value] = self.selected_strain

            self.possible_strain = []
            for strain_option in range(1,21):
                self.possible_strain.append(strain_option)
            self.strain_btn = ttk.Menubutton(self, text="Inflict Strain")
            self.strain_menu = tk.Menu(self.strain_btn, tearoff=False)
            self.strain_btn.configure(menu=self.strain_menu)
            for option in self.possible_strain:
                self.strain_menu.add_radiobutton(label=option, variable=self.selected_strain, value=option, command=lambda row_begin_value=self.row_begin_value, adver_type=self.stats['type'], key=self.key, full_name=self.full_name:self.apply_strain(row_begin_value, self.strain_vars[row_begin_value].get(), adver_type, full_name), indicatoron=False)
            self.strain_btn.grid(row=self.row_begin_value, column=3)
            self.widget_dict['%s_strain_btn' % self.row_begin_value] = self.strain_btn

    def build_damage_btn(self):
        self.selected_damage = tk.IntVar(self)

        self.damage_vars[self.row_begin_value] = self.selected_damage

        self.possible_damage = []
        for damage_option in range(1,21):
            self.possible_damage.append(damage_option)
        self.damage_btn = ttk.Menubutton(self, text="Damage Adversary") # , indicatoron=True
        self.damage_menu = tk.Menu(self.damage_btn, tearoff=False)
        self.damage_btn.configure(menu=self.damage_menu)
        for option in self.possible_damage:
            self.damage_menu.add_radiobutton(label=option, variable=self.selected_damage, value=option, command=lambda row_begin_value=self.row_begin_value, action_begin_value=self.action_begin_value, damage=option, soak=self.stats['soak'], adver_type=self.stats['type'], key=self.key, full_name=self.full_name:self.apply_damage(row_begin_value, damage, soak, adver_type, full_name), indicatoron=False)
        self.damage_btn.grid(row=self.row_begin_value, column=4)
        self.widget_dict['%s_dmg_btn' % self.row_begin_value] = self.damage_btn

    def build_crit_btn(self, controller):
        crit_text_input = ""

        if self.stats['type'] == 'Minion':
            crit_text_input = "Apply Critical"
        else:
            crit_text_input = "Manage Criticals"

        minion_kill_value = self.stats['wound_thresh']+1+self.stats['soak']

        self.crit_btn = ttk.Button(self, text=crit_text_input, command=lambda row_begin_value=self.row_begin_value, soak=self.stats['soak'], adver_type=self.stats['type'], key=self.key, full_name=self.full_name:self.crit_adversary(row_begin_value, minion_kill_value, soak, adver_type, controller))
        self.crit_btn.grid(row=self.row_begin_value, column=5)

        # (self, key, inflicted_dmg, soak, adver_type, controller):

        self.widget_dict['%s_crit_btn' % self.row_begin_value] = self.crit_btn

    def build_stat_labels(self):
        self.soak_label = tk.Label(self, text="Soak")
        self.soak_label.grid(row=self.row_begin_value+1, column=0)
        self.widget_dict['%s_soak_label' % self.row_begin_value] = self.soak_label
        self.wound_thresh_label= tk.Label(self, text="W. Thresh")
        self.wound_thresh_label.grid(row=self.row_begin_value+1, column=1)
        self.widget_dict['%s_wound_thresh_label' % self.row_begin_value] = self.wound_thresh_label
        if self.stats['type'] == 'Nemesis':
            self.strain_thresh_label = tk.Label(self, text="S. Thresh")
            self.strain_thresh_label.grid(row=self.row_begin_value+1, column=2)
            self.widget_dict['%s_strain_thresh_label' % self.row_begin_value] = self.strain_thresh_label
        self.mel_def_label = tk.Label(self, text="Mel. Defense")
        self.mel_def_label.grid(row=self.row_begin_value+1, column=3)
        self.widget_dict['%s_mel_def_label' % self.row_begin_value] = self.mel_def_label
        self.rng_def_label = tk.Label(self, text="Rng. Defense")
        self.rng_def_label.grid(row=self.row_begin_value+1, column=4)
        self.widget_dict['%s_rng_def_label' % self.row_begin_value] = self.rng_def_label

    def build_stat_label_values(self):
        self.soak_value = tk.Label(self, text=self.stats['soak'])
        self.soak_value.grid(row=self.row_begin_value+2, column=0)
        self.widget_dict['%s_soak_value' % self.row_begin_value] = self.soak_value
        if self.stats['type'] == "Minion":
            self.wound_thresh_value = tk.Label(self, text=str(self.stats['wound_thresh']) + " (" + str(int(self.stats['wound_thresh']) * int(self.amt)) + ")")
            self.wound_thresh_value.grid(row=self.row_begin_value+2, column=1)
            self.wound_thresh_dict[self.row_begin_value] = self.wound_thresh_value.cget("text")
            self.widget_dict['%s_wound_thresh_value' % self.row_begin_value] = self.wound_thresh_value
        else:
            self.wound_thresh_value = tk.Label(self, text=self.stats['wound_thresh'])
            self.wound_thresh_value.grid(row=self.row_begin_value+2, column=1)
            self.wound_thresh_dict[self.row_begin_value] = self.wound_thresh_value.cget("text")
            self.widget_dict['%s_wound_thresh_value' % self.row_begin_value] = self.wound_thresh_value

        if self.stats['type'] == "Nemesis":
            self.strain_thresh_value = tk.Label(self, text=self.stats['strain_thresh'])
            self.strain_thresh_value.grid(row=self.row_begin_value+2, column=2)
            self.strain_thresh_dict[self.row_begin_value] = self.strain_thresh_value.cget("text")
            self.widget_dict['%s_strain_thresh_value' % self.row_begin_value] = self.strain_thresh_value
        self.mel_def_value = tk.Label(self, text=self.stats['mel_def'])
        self.mel_def_value.grid(row=self.row_begin_value+2, column=3)
        self.widget_dict['%s_mel_def_value' % self.row_begin_value] = self.mel_def_value
        self.rng_def_value = tk.Label(self, text=self.stats['rng_def'])
        self.rng_def_value.grid(row=self.row_begin_value+2, column=4)
        self.widget_dict['%s_rng_def_value' % self.row_begin_value] = self.rng_def_value

    def build_main_action_label(self):
        self.action_begin_value = self.row_begin_value + 3
        self.action_label = tk.Label(self, text="Actions:")
        self.action_label.grid(row=self.action_begin_value, column=0)
        self.widget_dict['%s_main_action_label' % self.row_begin_value] = self.action_label

    def build_actions(self, controller, weapon):
        wpn_stats = (weapon[0],)
        for name, skill, damage, crit, wpn_range in wpn_stats:
            self.build_action_label(name, wpn_range)
            self.set_dice_values(skill)
            self.build_dice_btn(controller, name, wpn_range)
            self.row_actions.append(self.action_begin_value) # helps with clearing when defeating an adversary

    def set_initial_action_values(self):
        self.row_actions = []
        self.fetched_equipment = database.fetch_adversary_equipment("Terrinoth", self.key) # [[('Rusted Blade', 'Melee (Light)', 5, 3, 'Engaged')], [('Worn Bow', 'Ranged', 6, 3, 'Medium')]]
        self.fetched_skills = database.fetch_adversary_skills("Terrinoth", self.key)

        self.ability_dice = 0
        self.prof_dice = 0

    def build_action_label(self, name, wpn_range):
        weapon_label_value = name + " (" + wpn_range + "):"
        self.weapon_name_label = tk.Label(self, text=weapon_label_value)
        self.weapon_name_label.grid(row=self.action_begin_value, column=0)
        self.widget_dict['%s_weapon_name' % self.action_begin_value] = self.weapon_name_label
        fetched_qualities = database.fetch_weapon_qualities('Terrinoth', name)
        quality_input = ", ".join(fetched_qualities)
        self.quality_label = tk.Label(self, text=quality_input)
        self.quality_label.grid(row=self.action_begin_value, column=1, columnspan=4)
        self.widget_dict['%s_quality_label' % self.action_begin_value] = self.quality_label

    def set_dice_values(self, skill):
        global major_pool
        global minor_pool
        if database.fetch_adversary_type('Terrinoth', self.key) == 'Minion':
            if skill in self.fetched_skills:
                skill_value = int(self.amt_dict[self.row_begin_value]) - 1 # amt is 3, so Melee (Light) is 2
            else:
                skill_value = 0
        else:
            if skill in self.fetched_skills.keys():
                skill_value = self.fetched_skills[skill] # ranged of 3
            else:
                skill_value = 0
        print("Evaluating skill: " + str(skill))
        print("Skill value is %s." % skill_value)
        linked_char = database.fetch_linked_char("Terrinoth", skill)[0][1].lower() # brawn

        print("Linked characteristic is %s." % linked_char)
        char_value = self.stats[linked_char] # agility of 2
        print("Value of linked characteristic is %s." % char_value)

        if char_value > skill_value:
            major_pool = char_value
            minor_pool = skill_value
            self.ability_dice = char_value - skill_value # 3 - 1 = 2 dice
            self.prof_dice = char_value - self.ability_dice
            print("Producing %s ability dice and %s proficiency dice" % (self.ability_dice, self.prof_dice))
        elif skill_value > char_value:
            major_pool = skill_value
            minor_pool = char_value
            self.ability_dice = skill_value - char_value # 3 - 1 = 2 dice
            self.prof_dice = skill_value - self.ability_dice
            print("Producing %s ability dice and %s proficiency dice" % (self.ability_dice, self.prof_dice))
        elif char_value == skill_value:
            major_pool = char_value
            minor_pool = char_value
            self.prof_dice = char_value
            self.ability_dice = 0
            print("Producing %s ability dice and %s proficiency dice" % (self.ability_dice, self.prof_dice))

    def build_dice_btn(self, controller, name, wpn_range):
        global major_pool
        global minor_pool
        image_prefix = 'images'
        image_input = ""
        if self.prof_dice:
            for d in range(self.prof_dice):
                image_input += "P"
        if self.ability_dice:
            for d in range(self.ability_dice):
                image_input += "A"

        image_input += ".png"
        image_string = os.path.join(os.getcwd(), image_prefix, image_input)
        print("image string is " + str(image_string))

        self.load_dice = Image.open(image_string)
        self.dice_dict["load_%s_%s" % (self.row_begin_value, self.action_begin_value)] = self.load_dice
        self.render_dice = ImageTk.PhotoImage(self.load_dice)
        self.dice_dict["render_%s_%s" % (self.row_begin_value, self.action_begin_value)] = self.render_dice

        self.attack_btn = ttk.Button(self, image=self.dice_dict["render_%s_%s" % (self.row_begin_value, self.action_begin_value)], command=lambda key=self.key, name=name, wpn_range=wpn_range, major_pool=major_pool, minor_pool=minor_pool:self.create_dice_roller(controller, key, name, wpn_range, major_pool, minor_pool))
        self.attack_btn.grid(row=self.action_begin_value, column=5)
        self.widget_dict['%s_action_btn' % (self.action_begin_value)] = self.attack_btn

    def build_divider(self):
        self.divider = ttk.Separator(self, orient="horizontal")
        self.divider.grid(row=self.action_begin_value+1, columnspan=6, pady=10, sticky="ew")
        self.widget_dict['separator_%s' % self.action_begin_value] = self.divider
        self.key_dict[self.row_begin_value] = self.action_begin_value

    def build_footer(self, controller):
        self.footer_begin_value = self.row_begin_value
        self.initiative_btn = ttk.Button(self, text="Roll Initiave", command=lambda:self.roll_initative(controller))
        self.initiative_btn.grid(row=self.footer_begin_value, column=0)
        self.widget_dict['%s_initiative' % self.footer_begin_value] = self.initiative_btn
        self.back_btn = ttk.Button(self, text="Back", command=lambda:controller.back_to_sessions())
        self.back_btn.grid(row=self.footer_begin_value, column=5)
        self.widget_dict['%s_back' % self.footer_begin_value] = self.back_btn

    def clear_combat_frame(self):
        for widget in self.widget_dict.values():
            widget.grid_forget()

        self.damage_vars.clear()
        self.inflicted_wounds_dict.clear()
        self.wound_values.clear()
        self.strain_thresh_dict.clear()
        self.wound_thresh_dict.clear()
        self.widget_dict.clear()
        self.amt_dict.clear()
        self.const_amt_dict.clear()
        self.dice_dict.clear()
        self.key_dict.clear()
        self.master_stats.clear()
        self.weapon_dict.clear()
        self.name_dict.clear()

        self.row_begin_value = 1

    def roll_initative(self, controller):
        root = InitiativeRoot(controller)

    def create_dice_roller(self, controller, adversary, name, wpn_range, major, minor):
        global global_adversary
        global global_weapon_name
        global global_range
        global major_pool
        global minor_pool

        global_adversary = adversary
        global_weapon_name = name
        global_range = wpn_range
        major_pool = major
        minor_pool = minor

        print("Dice Roller ")

        root = DiceRoot(controller)

    def display_adversary(self, controller, key):
        root = AdversaryExtras(controller, key)


        # row_begin_value, damage, soak, adver_type, key, full_name
    def apply_damage(self, row_begin_value, inflicted_dmg, soak, adver_type, full_name):
        adversary = full_name.split('-')[1]
        print('Adversary is: ' + str(adversary))
        skill_value = 0
        print("Inflicted damage is " + str(inflicted_dmg))
        print("Soak is " + str(soak))
        if (inflicted_dmg - soak) > 0:
            self.pull_wounds_from_label(adver_type, row_begin_value)
            current_damage = self.inflicted_wounds_dict[row_begin_value]
            inflicted_dmg = (inflicted_dmg - soak) + current_damage
            self.kill_minion_if_able(adver_type, inflicted_dmg, row_begin_value, adversary, skill_value, full_name)
            self.damage_or_defeat_adversary(inflicted_dmg, row_begin_value)

    def pull_wounds_from_label(self, adver_type, row_begin_value):
        if adver_type == "Minion":
            self.wound_thresh = self.wound_thresh_dict[row_begin_value].split(" ")[1][1:-1] # 4 (12) --> (12) --> 12
            self.minion_thresh = self.wound_thresh_dict[row_begin_value].split(" ")[0] # 4 (12) --> 4
        else:
            self.wound_thresh = self.wound_thresh_dict[row_begin_value]

    def pull_strain_from_label(self, row_begin_value):
            self.strain_thresh = self.strain_thresh_dict[row_begin_value]

    def kill_minion_if_able(self, adver_type, inflicted_dmg, row_begin_value, adversary, skill_value, full_name):
        if adver_type == "Minion":
            if not inflicted_dmg > int(self.wound_thresh):
                orig_amt = self.const_amt_dict[row_begin_value] # Will be the number of minion ripped from string, so Reanimate x 3, will be '3'
                tmp_amt = 0
                for self.row_begin_value in range(1, int(self.const_amt_dict[row_begin_value]) + 1):
                    if self.row_begin_value == 1:
                        self.amt_dict[row_begin_value] = tmp_amt
                    if int(self.amt_dict[row_begin_value]) + 1 <= int(orig_amt):
                        self.amt_dict[row_begin_value] = int(self.amt_dict[row_begin_value]) + 1
                    threshold = int(self.minion_thresh) * self.row_begin_value # 5
                    if inflicted_dmg > threshold:
                        self.amt_dict[row_begin_value] = int(self.amt_dict[row_begin_value]) - 1

            # Sets proper amount of minions in group, killed or otherwise
            self.widget_dict['%s_name' % row_begin_value].config(text="%s x %s (Minion)" % (full_name, self.amt_dict[row_begin_value]))

            self.fetched_equipment = database.fetch_adversary_equipment("Terrinoth", adversary) # [[('Rusted Blade', 'Melee (Light)', 4, 2, 'Engaged'), 'Viscious']]
            self.fetched_skills = database.fetch_adversary_skills("Terrinoth", adversary)

            print("fetched equipment is: " + str(self.fetched_equipment))

            for weapon in self.fetched_equipment:
                print("weapon is" + str(weapon))

            for weapon in self.fetched_equipment:
                weapon = weapon[0]
                weapon = (weapon,)
                for name, skill, wpn_damage, crit, wpn_range in weapon:
                    if skill in self.fetched_skills:
                        if self.amt_dict[row_begin_value] - 1 > 0: # amt is 3, so Melee (Light) is 2
                            skill_value = self.amt_dict[row_begin_value] - 1
                    else:
                        skill_value = 0

                    linked_char = database.fetch_linked_char("Terrinoth", skill)[0][1].lower() # brawn

                    char_value = self.master_stats[row_begin_value][linked_char] # brawn of 2

                    ability_dice = 0
                    prof_dice = 0

                    if char_value > skill_value:
                        major_pool = char_value
                        minor_pool = skill_value
                    elif skill_value > char_value:
                        major_pool = skill_value
                        minor_pool = char_value
                    elif char_value == skill_value:
                        major_pool = char_value
                        minor_pool = char_value

                    ability_dice = major_pool - minor_pool  # Brawn 3, Melee (Light) 2 = 2 Proficiency, 1 Ability
                    prof_dice = major_pool - ability_dice

                    # print("Ability Dice: " + str(global_ability_dice))
                    # print("Proficiency Dice: " + str(global_prof_dice))

                    image_string = "images/"
                    if prof_dice:
                        for d in range(prof_dice):
                            image_string += "P"
                    if ability_dice:
                        for d in range(ability_dice):
                            image_string += "A"
                    image_string += ".png"
                    print(image_string)
            print(self.widget_dict)
            for action_key in self.weapon_dict[row_begin_value]:
                load_dice = Image.open(image_string)
                render_dice = ImageTk.PhotoImage(load_dice)

                self.widget_dict['%s_action_btn' % (action_key)].configure(image=render_dice)
                self.widget_dict['%s_action_btn' % (action_key)].dice_ref = render_dice

    def damage_or_defeat_adversary(self, inflicted_dmg, row_begin_value):
        if inflicted_dmg > int(self.wound_thresh):
            for widget_key in self.widget_dict.keys(): # row_type
                widget_regex = re.compile('^%s_' % row_begin_value)
                if widget_regex.search(widget_key):
                    for widget in self.widget_list:
                        if widget in widget_key:
                            self.widget_dict['%s_%s' % (row_begin_value, widget)].config(state="disabled")
                for action in self.weapon_dict[row_begin_value]:
                    for widget in self.action_widget_list:
                        if widget in widget_key:
                            self.widget_dict['%s_%s' % (action, widget)].config(state="disabled")
        else:
            self.inflicted_wounds_dict[row_begin_value] = inflicted_dmg
            self.wound_values[row_begin_value].config(text= "Wounds: " + str(self.inflicted_wounds_dict[row_begin_value]))

    # row_begin_value, self.strain_vars[row_begin_value].get(), adver_type, key, full_name

    def apply_strain(self, row_begin_value, inflicted_dmg, adver_type, full_name):
        # print(self.strain_values)
        # print(self.strain_values[1])
        adversary = full_name.split('-')[1]
        print('Adversary is: ' + str(adversary))
        skill_value = 0
        print("Inflicted damage is " + str(inflicted_dmg))
        self.pull_strain_from_label(row_begin_value)
        current_damage = self.inflicted_strain_dict[row_begin_value]
        inflicted_dmg = inflicted_dmg + current_damage
        self.strain_or_defeat_nemesis(inflicted_dmg, row_begin_value)

    def strain_or_defeat_nemesis(self, inflicted_dmg, row_begin_value):
        if inflicted_dmg > int(self.strain_thresh):
            for widget_key in self.widget_dict.keys(): # row_type
                widget_regex = re.compile('^%s_' % row_begin_value)
                if widget_regex.search(widget_key):
                    for widget in self.widget_list:
                        if widget in widget_key:
                            self.widget_dict['%s_%s' % (row_begin_value, widget)].config(state="disabled")
                for action in self.weapon_dict[row_begin_value]:
                    for widget in self.action_widget_list:
                        if widget in widget_key:
                            self.widget_dict['%s_%s' % (action, widget)].config(state="disabled")
        else:
            self.inflicted_strain_dict[row_begin_value] = inflicted_dmg
            self.strain_values[row_begin_value].config(text= "Strain: " + str(self.inflicted_strain_dict[row_begin_value]))

    def crit_adversary(self, key, inflicted_dmg, soak, adver_type, controller):
        full_name = self.name_dict[key]
        adversary = full_name.split('-')[1]
        if adver_type == 'Minion':
            self.apply_damage(key, inflicted_dmg, soak, adver_type, full_name)
        else:
            root = CritMenu(controller, full_name, adversary)

class CritMenu(tk.Toplevel):
    def __init__(self, parent, key, adversary):
        tk.Toplevel.__init__(self)

        self.build_main_window(key)
        self.populate_prev_injuries(key)

    def build_main_window(self, key):
        self.name_label = tk.Label(self, text=key)
        self.name_label.grid(row=0, column=0)
        self.crit_listbox = tk.Listbox(self, width=50)
        self.crit_listbox.grid(row=1, column=0)
        self.vert_crit_sb = tk.Scrollbar(self, orient="vertical")
        self.vert_crit_sb.grid(row=1, column=1, sticky="ns")
        self.crit_listbox.configure(yscrollcommand=self.vert_crit_sb)
        self.vert_crit_sb.configure(command=self.crit_listbox.yview)
        self.hor_crit_sb = tk.Scrollbar(self, orient="horizontal")
        self.hor_crit_sb.grid(row=2, column=0, sticky="ew")
        self.crit_listbox.configure(xscrollcommand=self.hor_crit_sb)
        self.hor_crit_sb.configure(command=self.crit_listbox.xview)
        self.add_btn = ttk.Button(self, text="Add", command=lambda:self.add_critical(key)).grid(row=3, column=0)
        self.remove_btn = ttk.Button(self, text="Remove", command=lambda:self.remove_crit(key)).grid(row=4, column=0)

    def add_critical(self, key):
        self.load_CritOptions(key)
        self.update_crit_listbox()

    def load_CritOptions(self, key):
        self.crit_options = CritOptions(self, key)

    def update_crit_listbox(self):
        global crit_to_apply
        self.wait_window(self.crit_options)
        self.crit_listbox.insert(tk.END, crit_to_apply)

    def remove_crit(self, key):
        print("Running remove, key is " + str(key))
        self.remove_crit_from_db(key)
        self.delete_crit_from_listbox()

    def delete_crit_from_listbox(self):
        index = self.crit_listbox.curselection()
        self.crit_listbox.delete(index)

    def remove_crit_from_db(self, key):
        global encounter

        id = key.split('-')[0]
        index = self.crit_listbox.curselection()
        injury = self.crit_listbox.get(index)

        print("Encounter is " + encounter)
        print("id is " + str(id))
        print("injury is " + str(injury))

        conn = sqlite3.connect('Terrinoth')
        cur = conn.cursor()
        cur.execute("DELETE FROM encounter_injuries WHERE encounter = (?) AND id = (?) AND injury = (?)", (encounter, id, injury))
        conn.commit()
        conn.close()

    def populate_prev_injuries(self, key):
        global encounter
        id = key.split('-')[0]
        fetched_injuries = database.fetch_prev_injuries('Terrinoth', encounter, id)
        for injury in fetched_injuries:
            self.crit_listbox.insert(tk.END, injury)

class CritOptions(tk.Toplevel):
    def __init__(self, parent, key):
        tk.Toplevel.__init__(self)

        self.build_crit_window(key)
        self.populate_crit_listbox()

    def build_crit_window(self, key): # 1-Sergeant
        id = key.split('-')[0]
        name = key.split('-')[1]
        self.avail_crit_listbox = tk.Listbox(self, width=100)
        self.avail_crit_listbox.grid(row=0, column=0)
        self.vert_avail_crit_sb = tk.Scrollbar(self, orient="vertical")
        self.vert_avail_crit_sb.grid(row=0, column=1, sticky="ns")
        self.avail_crit_listbox.configure(yscrollcommand=self.vert_avail_crit_sb)
        self.vert_avail_crit_sb.configure(command=self.avail_crit_listbox.yview)
        self.hor_avail_crit_sb = tk.Scrollbar(self, orient="horizontal")
        self.hor_avail_crit_sb.grid(row=1, column=0, sticky="ew")
        self.avail_crit_listbox.configure(xscrollcommand=self.hor_avail_crit_sb)
        self.hor_avail_crit_sb.configure(command=self.avail_crit_listbox.yview)
        self.add_crit_btn = ttk.Button(self, text="Add Critical", command=lambda:self.apply_crit(id, name))
        self.add_crit_btn.grid(row=2, column=0)

    def apply_crit(self, id, name):
        self.add_crit_to_listbox()
        self.save_crit_to_database(id, name)

    def add_crit_to_listbox(self):
        global crit_to_apply
        index = self.avail_crit_listbox.curselection()
        crit_to_apply = self.avail_crit_listbox.get(index)

    def save_crit_to_database(self, id, name):
        global encounter
        global crit_to_apply

        print("encounter is " + str(encounter))
        print("id is " + str(id))
        print("name is " + str(name))
        print("crit_to_apply is " + str(crit_to_apply))

        conn = sqlite3.connect('Terrinoth')
        cur = conn.cursor()
        cur.execute("INSERT INTO encounter_injuries VALUES (?, ?, ?, ?)", (encounter, id, name, crit_to_apply))
        conn.commit()
        conn.close()

        self.destroy()

    def populate_crit_listbox(self):
        crit_list = {}

        crit_list['Minor Nick'] = (1, "The target suffers 1 strain")
        crit_list['Slowed Down'] = (1, "The target can only act during the last allied Initiative slot on their next turn.")
        crit_list['Sudden Jolt'] = (1, "The target drops whatever is in hand.")
        crit_list['Distracted'] = (1, "The target cannot perfrom a free maneuver during their next turn.")
        crit_list['Off-Balance'] = (1, "Add a Setback to the target's next skill check.")
        crit_list['Discouraging Wound'] = (1, "Move one player pool Story Point to the Game Master pool (reverse if NPC).")
        crit_list['Stunned'] = (1, "The target is staggered until the end of their next turn.")
        crit_list['Stinger'] = (1, "Increase the difficulty of the target's next check by one.")
        crit_list['Bowled Over'] = (2, "The target is knocked prone and suffers 1 strain.")
        crit_list['Head Ringer'] = (2, "The target increases the difficulty of all Intellect and Cunning checks by one until this Critical Injury is healed.")
        crit_list['Fearsome Wound'] = (2, "The target increases the difficulty of all Presence and Willpower checks by one until this Crtical Injury is healed.")
        crit_list['Agonizing Wound'] = (2, "The target increases the difficulty of all Brawn and Agility checks by one until this Critical Injury is healed.")
        crit_list['Slightly Dazed'] = (2, "The target is disoriented until this Critical Injury is healed.")
        crit_list['Scattered Senses'] = (2, "Scattered Senses: The target removes all Boosts from skill checks until this Critical Injury is healed.")
        crit_list['Hamstrung'] = (2, "The target loses their free maneuver until this Critical Injury is healed.")
        crit_list['Overpowered'] = (2, "The target leaves themselves open, and the attacker may immediately attempt another attack against them as an incidental, using the exact same pool as the original attack")
        crit_list['Winded'] = (2, "The target cannot voluntarily suffer strain to activate any abilities or gain additional maneuvers until this Critical Injury is healed.")
        crit_list['Compromised'] = (2, "Increase the difficulty of all skill checks by one until this Critical Injury is healed.")
        crit_list['At the Brink'] = (3, "The target suffers 2 strain each time they perform an action until this Critical Injuury is healed.")
        crit_list['Crippled'] = (3, "One of the target's limbs (selected by the GM) is impaired until this Critical Injury is healed. Increase the difficulty of all checks that require use of that limb by one.")
        crit_list['Maimed'] = (3, "One of the target's limbs (selected by the GM) is permanently lost. Unless the target has a cybernetic or prosthetic replacement, the target cannot perform actions that would require the use of that limb. All other actions gain a Setback until this Critical Injury is healed.")
        crit_list['Horrific Injury'] = (3, "Roll 1d10 to determine which of the target's characteristics is affected: 1-3 for Brawn, 4-6 for Agility, 7 for Intellect, 8 for Cunning, 9 for Presence, 10 for Willpower. Until this Critical Injury is healed, treat that characteristic as one point lower.")
        crit_list['Temporarily Disabled'] = (3, "The target is immobilized until this Critical Injury is healed.")
        crit_list['Blinded'] = (3, "The target can no longer see. Upgrade the difficulty of all checks twice, and upgrade the difficulty of Perception and Vigilance checks three times, until this Critical Injury is healed.")
        crit_list['Knocked Senseless'] = (3, "The target is staggered until this Critical Injury is healed")
        crit_list['Gruesome Injury'] = (4, "Roll 1d10 to determine which of the target's characteristics is affected: 1-3 for Brawn, 4-6 for Agility, 7 for Intellect, 8 for Cunning, 9 for Presence, 10 for Willpower. That characteristic is permanently reduced by one to a minimum of 1.")
        crit_list['Bleeding out'] = (4, "Until this Critical Injury is healed, every round, the target suffers 1 wound and 1 strain at the beginning of their turn. For every 5 wounds they suffer beyond their wound threshold, they suffer one additional Critical Injury. Roll on the chart, suffering the injury (if they suffer this result a second time due to this, roll again).")
        crit_list['The End is Nigh'] = (4, "The target dies after the last Initiative slot during the next round unless this Critical Injury is healed.")

        diff_options = ["Easy", "Average", "Hard", "Daunting"]

        for critical in crit_list.keys():
            crit_difficulty = diff_options[crit_list[critical][0]-1]
            crit_description = crit_list[critical][1]
            critical_input = "(%s) " % crit_difficulty + critical + ": " + crit_description
            self.avail_crit_listbox.insert(tk.END, critical_input)

class AdversaryExtras(tk.Toplevel):
    def __init__(self, parent, key):
        tk.Toplevel.__init__(self)

        tk.Label(self, text=key).pack()
        for talent in database.fetch_adversary_talents('Terrinoth', key): # Swift OR Adversary 2
            input = talent[0] + " (%s) " % talent[1][0] + ": " + talent[1][1]
            tk.Message(self, text=input, width=500).pack(anchor="w")
        for ability in database.fetch_adversary_abilities('Terrinoth', key):
            tk.Message(self, text=ability[:-2], width=500).pack(anchor="w")

class DiceRoot(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        container = tk.Frame(self)
        container.pack()

        self.frames = {}

        for F in (PlayerSelect, DiceRoller, DiceResults):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PlayerSelect)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

class PlayerSelect(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        global campaign

        # Is this redundant? Did self.row_begin_value add this to fix some bug? This is also set globally.
        campaign = database.fetch_active("Terrinoth", "campaign")
        fetched_players = database.fetch_players("Terrinoth", campaign)
        self.stats = database.fetch_player_stats("Terrinoth", campaign)
        attending_players = []

        for player in fetched_players.keys():
            if fetched_players[player] == 1:
                attending_players.append(player)

        tk.Label(self, text="Select a target").pack()

        for player in attending_players:
            ttk.Button(self, text=player, command=lambda player=player:self.select_target(player, controller)).pack()

    def select_target(self, target, controller):
        global mel_def
        global rng_def
        global campaign

        self.stats = database.fetch_player_stats("Terrinoth", campaign)
        mel_def = self.stats[target][0]
        rng_def = self.stats[target][1]

        print("Melee defense is: " + str(mel_def))
        print("Ranged defense is: " + str(rng_def))
        controller.show_frame(DiceRoller)

class DiceRoller(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        global global_adversary
        global global_weapon_name
        global global_range
        global major_pool
        global minor_pool

        # Initial labels
        self.weapon_label = tk.Label(self, text=global_weapon_name).grid(row=0, column=0, columnspan=5)
        self.range_label = tk.Label(self, text="Range").grid(row=1, column=0, columnspan=2)
        self.boost_label = tk.Label(self, text="Boost").grid(row=1, column=3)
        self.setback_label = tk.Label(self, text="Setback").grid(row=1, column=4)
        self.selected_range = tk.StringVar(self)
        self.all_ranges = ["Select a range", "Engaged", "Short", "Medium", "Long", "Extreme", "Strategic"]
        self.avail_ranges = self.all_ranges[:self.all_ranges.index(global_range)+1]
        if len(self.avail_ranges) > 2:
            self.range_menu = ttk.OptionMenu(self, self.selected_range, *self.avail_ranges)
            self.range_menu.grid(row=2, column=0, columnspan=2)
        else:
            self.engaged_range_label = tk.Label(self, text="Engaged").grid(row=2, column=0, columnspan=2)

        # Boost and setback options
        self.selected_boost = tk.IntVar(self)
        self.boost_values = (0, 0, 1, 2, 3, 4, 5, 6)
        self.boost_menu = ttk.OptionMenu(self, self.selected_boost, *self.boost_values)
        self.boost_menu.grid(row=2, column=3)
        self.selected_setback = tk.IntVar(self)

        self.setback_values = (0, 0, 1, 2, 3, 4, 5, 6)
        self.setback_menu = ttk.OptionMenu(self, self.selected_setback, *self.setback_values)
        self.setback_menu.grid(row=2, column=4)

        # Ability labels
        self.ability_label = tk.Label(self, text="Ability Adjust").grid(row=4, column=0, columnspan=2)
        self.abil_upgrade = tk.Label(self, text="Upgrade").grid(row=5, column=0)
        self.abil_downgrade = tk.Label(self, text="Downgrade").grid(row=5, column=1)
        self.abil_increase = tk.Label(self, text="Increase").grid(row=7, column=0)
        self.abil_decrease = tk.Label(self, text="Decrease").grid(row=7, column=1)

        # Ability options
        self.selected_abil_up = tk.IntVar(self)
        self.abil_upgrade_values = (0, 0, 1, 2, 3, 4, 5)
        self.abil_upgrade_menu = ttk.OptionMenu(self, self.selected_abil_up, *self.abil_upgrade_values)
        self.abil_upgrade_menu.grid(row=6, column=0)

        self.selected_abil_down = tk.IntVar(self)
        self.abil_downgrade_values = (0, 0, 1, 2, 3, 4, 5)
        self.abil_downgrade_menu = ttk.OptionMenu(self, self.selected_abil_down, *self.abil_downgrade_values)
        self.abil_downgrade_menu.grid(row=6, column=1)

        self.selected_abil_inc = tk.IntVar(self)
        self.abil_increase_values = (0, 0, 1, 2, 3, 4, 5)
        self.abil_increase_menu = ttk.OptionMenu(self, self.selected_abil_inc, *self.abil_increase_values)
        self.abil_increase_menu.grid(row=8, column=0)

        self.selected_abil_dec = tk.IntVar(self)
        self.abil_decrease_values = (0, 0, 1, 2, 3, 4, 5)
        self.abil_decrease_menu = ttk.OptionMenu(self, self.selected_abil_dec, *self.abil_decrease_values)
        self.abil_decrease_menu.grid(row=8, column=1)

        # Difficulty labels
        self.difficulty_label = tk.Label(self, text="Difficulty Adjust").grid(row=4, column=3, columnspan=2)
        self.diff_upgrade = tk.Label(self, text="Upgrade").grid(row=5, column=3)
        self.diff_downgrade = tk.Label(self, text="Downgrade").grid(row=5, column=4)
        self.diff_increase = tk.Label(self, text="Increase").grid(row=7, column=3)
        self.diff_decrease = tk.Label(self, text="Decrease").grid(row=7, column=4)

        # Difficulty options
        self.selected_diff_up = tk.IntVar(self)
        self.diff_upgrade_values = (0, 0, 1, 2, 3, 4, 5)
        self.diff_upgrade_menu = ttk.OptionMenu(self, self.selected_diff_up, *self.diff_upgrade_values)
        self.diff_upgrade_menu.grid(row=6, column=3)

        self.selected_diff_down = tk.IntVar(self)
        self.diff_downgrade_values = (0, 0, 1, 2, 3, 4, 5)
        self.diff_downgrade_menu = ttk.OptionMenu(self, self.selected_diff_down, *self.diff_downgrade_values)
        self.diff_downgrade_menu.grid(row=6, column=4)

        self.selected_diff_inc = tk.IntVar(self)
        self.diff_increase_values = (0, 0, 1, 2, 3, 4, 5)
        self.diff_increase_menu = ttk.OptionMenu(self, self.selected_diff_inc, *self.diff_increase_values)
        self.diff_increase_menu.grid(row=8, column=3)

        self.selected_diff_dec = tk.IntVar(self)
        self.diff_decrease_values = (0, 0, 1, 2, 3, 4, 5)
        self.diff_decrease_menu = ttk.OptionMenu(self, self.selected_diff_dec, *self.diff_decrease_values)
        self.diff_decrease_menu.grid(row=8, column=4)

        # Dividers
        self.first_divide = ttk.Separator(self, orient="horizontal").grid(row=3, columnspan=5, sticky="ew")
        self.second_divide = ttk.Separator(self, orient="horizontal").grid(row=9, columnspan=5, sticky="ew")
        self.vert_divide = ttk.Separator(self, orient="vertical").grid(row=3, column=2, rowspan=7, sticky ="ns")

        # Magic labels
        self.magic_label = tk.Label(self, text="Magic").grid(row=10, column=1, columnspan=3)
        self.augment_label = tk.Label(self, text="Augment").grid(row=11, column=1)
        self.curse_label = tk.Label(self, text="Curse").grid(row=11, column=3)

        # Magic options
        self.selected_aug_value = tk.IntVar(self)
        self.avail_aug_values = (0, 0, 1, 2, 3, 4, 5)
        self.aug_menu = ttk.OptionMenu(self, self.selected_aug_value, *self.avail_aug_values)
        self.aug_menu.grid(row=12, column=1)

        self.selected_curse_value = tk.IntVar(self)
        self.avail_curse_values = (0, 0, 1, 2, 3, 4, 5)
        self.curse_menu = ttk.OptionMenu(self, self.selected_curse_value, *self.avail_curse_values)
        self.curse_menu.grid(row=12, column=3)

        self.roll_btn = ttk.Button(self, text="Roll", command=lambda:self.roll_dice(parent, controller, global_weapon_name, major_pool, minor_pool)).grid(row=13,column=0, columnspan=5)

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        global mel_def
        global rng_def

        if len(self.avail_ranges) > 2:
            self.selected_setback.set(rng_def)
        else:
            self.selected_setback.set(mel_def)

    def roll_dice(self, parent, controller, weapon, major_pool, minor_pool):
        boost_dice = self.selected_boost.get()
        setback_dice = self.selected_setback.get()

        # Magic logic
        for curse in range(self.selected_curse_value.get()):
            if major_pool >= minor_pool:
                if major_pool > 0:
                    major_pool -= 1
            else:
                minor_pool -= 1

        for augment in range(self.selected_aug_value.get()):
            if major_pool >= minor_pool:
                if major_pool < 5:
                    major_pool += 1
            else:
                if minor_pool < 5:
                    minor_pool += 1

        if major_pool > minor_pool: # Brawn 3, Melee (Light) 2: 2 Proficiency, 1 Ability
            ability_dice = major_pool - minor_pool
            prof_dice = major_pool - ability_dice
        elif minor_pool > major_pool:
            ability_dice = minor_pool - major_pool
            prof_dice = minor_pool - ability_dice
        elif major_pool == minor_pool:
            ability_dice = 0
            prof_dice = major_pool

        # TODO: Hardcoded at the moment, ranged weapons need a size to determine engaged difficulty. One handed = 2, Two handed = 3, Gunnery style heavy weapons are not able to attack while engaged.
        if len(self.avail_ranges) > 2:
            weapon_range = self.selected_range.get()
            range_dict = {"Engaged":3, "Short":1, "Medium":2, "Long":3, "Extreme":4, "Strategic":5}
            difficulty_dice = range_dict[weapon_range]
        else:
            difficulty_dice = 2

        challenge_dice = 0

        # Difficulty adjust logic
        for downgrade in range(self.selected_diff_down.get()):
            if challenge_dice > 0:
                challenge_dice -= 1
                difficulty_dice += 1

        for upgrade in range(self.selected_diff_up.get()):
            if difficulty_dice > 0:
                difficulty_dice -= 1
                challenge_dice += 1
            else:
                difficulty_dice += 1

        for increase in range(self.selected_diff_inc.get()):
            if difficulty_dice < 5:
                difficulty_dice += 1

        for decrease in range(self.selected_diff_dec.get()):
            if difficulty_dice > 0:
                difficulty_dice -= 1

        # Ability adjust logic
        for downgrade in range(self.selected_abil_down.get()):
            if prof_dice > 0:
                prof_dice -= 1
                ability_dice += 1

        for upgrade in range(self.selected_abil_up.get()):
            if ability_dice > 0:
                ability_dice -= 1
                prof_dice += 1
            else:
                ability_dice += 1

        for increase in range(self.selected_abil_inc.get()):
            if ability_dice < 5:
                ability_dice += 1

        for decrease in range(self.selected_abil_dec.get()):
            if ability_dice > 0:
                ability_dice -= 1

        print("Boost dice: " + str(boost_dice))
        print("Ability dice: " + str(ability_dice))
        print("Proficiency dice: " + str(prof_dice))
        print("Setback dice: " + str(setback_dice))
        print("Difficulty dice: " + str(difficulty_dice))
        print("Challenge dice: " + str(challenge_dice) + "\n")

        dice_values = {}
        dice_values["boost_dice"] = (None, None, "Success", ["Success", "Advantage"], ["Advantage", "Advantage"], "Advantage")
        dice_values["setback_dice"] = (None, None, "Failure", "Failure", "Threat", "Threat")
        dice_values["ability_dice"] = (None, "Success", "Success", ["Success", "Success"], "Advantage", "Advantage", ["Success", "Advantage"], ["Advantage", "Advantage"])
        dice_values["difficulty_dice"] = (None, "Failure", ["Failure", "Failure"], "Threat", "Threat", "Threat", ["Threat", "Threat"], ["Failure", "Threat"])
        dice_values["prof_dice"] = (None, "Success", "Success", ["Success", "Success"], ["Success", "Success"], "Advantage", ["Success", "Advantage"], ["Success", "Advantage"], ["Success", "Advantage"], ["Advantage", "Advantage"], ["Advantage", "Advantage"], ["Triumph", "Success"])
        dice_values["challenge_dice"] = (None, "Failure", "Failure", ["Failure", "Failure"], ["Failure", "Failure"], "Threat", "Threat", ["Failure", "Threat"], ["Failure", "Threat"], ["Threat", "Threat"], ["Threat", "Threat"], ["Despair", "Failure"])

        roll_results = []

        for dice in range(boost_dice):
            roll = dice_values["boost_dice"][random.randint(0, len(dice_values["boost_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(setback_dice):
            roll = dice_values["setback_dice"][random.randint(0, len(dice_values["setback_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(ability_dice):
            roll = dice_values["ability_dice"][random.randint(0, len(dice_values["ability_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(difficulty_dice):
            roll = dice_values["difficulty_dice"][random.randint(0, len(dice_values["difficulty_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(prof_dice):
            roll = dice_values["prof_dice"][random.randint(0, len(dice_values["prof_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(challenge_dice):
            roll = dice_values["challenge_dice"][random.randint(0, len(dice_values["challenge_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        global rolled_adv
        global rolled_th
        global rolled_succ
        global rolled_fail
        global rolled_tri
        global rolled_desp

        # Value reset
        rolled_adv = 0
        rolled_th = 0
        rolled_succ = 0
        rolled_fail = 0
        rolled_tri = 0
        rolled_desp = 0

        advantages = roll_results.count("Advantage")
        successes = roll_results.count("Success")
        rolled_tri = roll_results.count("Triumph")
        threat = roll_results.count("Threat")
        failures = roll_results.count("Failure")
        rolled_desp = roll_results.count("Despair")



        print("Advantages: " +str(advantages))
        print("Success: " + str(successes))
        print("Triumph: " + str(rolled_tri))
        print("Threat: " +str(threat))
        print("Failures: " + str(failures))
        print("Despair: " +str(rolled_desp))

        if advantages > threat:
            rolled_adv = advantages - threat
            adv_threat_key = "Advantage"
        elif threat > advantages:
            rolled_th = threat - advantages
            adv_threat_key = "Threat"
        elif advantages == threat:
            total_adv_threat = 0
            adv_threat_key = ""

        if successes > failures:
            rolled_succ = successes - failures
            succ_fail_key = "Success"
        elif failures > successes:
            rolled_fail = failures - successes
            succ_fail_key = "Fail"
        elif successes == failures:
            total_succ_fail = 0
            succ_fail_key = ""

        roll_result_string = ""

        if adv_threat_key:
            if adv_threat_key == "Advantage":
                roll_result_string += str(rolled_adv) + " advantage"
            else:
                roll_result_string += str(rolled_th) + " threat"

            if rolled_tri or rolled_desp or succ_fail_key:
                roll_result_string += ", "

        if succ_fail_key:
            if succ_fail_key == "Success":
                roll_result_string += str(rolled_succ) + " successes"
            else:
                roll_result_string += str(rolled_fail) + " failures"

            if rolled_tri or rolled_desp:
                roll_result_string += ", "

        if rolled_tri:
            roll_result_string += str(rolled_tri) + " triumph"

            if rolled_desp:
                roll_result_string += ", "

        if rolled_desp:
            roll_result_string += str(rolled_desp) + " despair"

        if roll_result_string:
            roll_result_string = "Rolled: " + roll_result_string
        else:
            roll_result_string = "Rolled: No remaining symbols"

        print(roll_result_string)

        controller.show_frame(DiceResults)

class DiceResults(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # TODO: Some talents or effects, such as berserk, automatically add symbols to a dice check. Account for that.
        # Frames
        self.roll_frame = tk.Frame(self)
        self.roll_frame.pack()

        self.results_frame = tk.Frame(self)
        self.results_frame.pack()

        self.spend_frame = tk.Frame(self)
        self.spend_frame.pack()

        # Result symbols
        # Success symbol
        self.load_fade_succ = Image.open('images/grayed_Success.png')
        self.render_fade_succ = ImageTk.PhotoImage(self.load_fade_succ)
        self.load_succ = Image.open('images/Success.png')
        self.render_succ = ImageTk.PhotoImage(self.load_succ)
        self.succ_symbol = tk.Label(self.roll_frame, image=self.render_succ)
        self.succ_symbol.grid(row=0, column=0)
        self.succ_data = tk.Label(self.roll_frame)
        self.succ_data.grid(row=0, column=1)

        # Advantage symbol
        self.load_fade_adv = Image.open('images/grayed_Advantage.png')
        self.render_fade_adv = ImageTk.PhotoImage(self.load_fade_adv)
        self.load_adv = Image.open('images/Advantage.png')
        self.render_adv = ImageTk.PhotoImage(self.load_adv)
        self.adv_symbol = tk.Label(self.roll_frame, image=self.render_adv)
        self.adv_symbol.grid(row=0, column=2)
        self.adv_data = tk.Label(self.roll_frame)
        self.adv_data.grid(row=0, column=3)

        # Triumph symbol
        self.load_fade_tri = Image.open('images/grayed_Triumph.png')
        self.render_fade_tri = ImageTk.PhotoImage(self.load_fade_tri)
        self.load_tri = Image.open('images/Triumph.png')
        self.render_tri = ImageTk.PhotoImage(self.load_tri)
        self.tri_symbol = tk.Label(self.roll_frame, image=self.render_tri)
        self.tri_symbol.grid(row=0, column=4)
        self.tri_data = tk.Label(self.roll_frame)
        self.tri_data.grid(row=0, column=5)

        # Fail symbol
        self.load_fade_fail = Image.open('images/grayed_Failure.png')
        self.render_fade_fail = ImageTk.PhotoImage(self.load_fade_fail)
        self.load_fail = Image.open('images/Failure.png')
        self.render_fail = ImageTk.PhotoImage(self.load_fail)
        self.fail_symbol = tk.Label(self.roll_frame, image=self.render_fail)
        self.fail_symbol.grid(row=1, column=0)
        self.fail_data = tk.Label(self.roll_frame)
        self.fail_data.grid(row=1, column=1)

        # Threat symbol
        self.load_fade_threat = Image.open('images/grayed_Threat.png')
        self.render_fade_threat = ImageTk.PhotoImage(self.load_fade_threat)
        self.load_threat = Image.open('images/Threat.png')
        self.render_threat = ImageTk.PhotoImage(self.load_threat)
        self.threat_symbol = tk.Label(self.roll_frame, image=self.render_threat)
        self.threat_symbol.grid(row=1, column=2)
        self.threat_data = tk.Label(self.roll_frame)
        self.threat_data.grid(row=1, column=3)

        # Despair symbol
        self.load_fade_desp = Image.open('images/grayed_Despair.png')
        self.render_fade_desp = ImageTk.PhotoImage(self.load_fade_desp)
        self.load_desp = Image.open('images/Despair.png')
        self.render_desp = ImageTk.PhotoImage(self.load_desp)
        self.desp_symbol = tk.Label(self.roll_frame, image=self.render_desp)
        self.desp_symbol.grid(row=1, column=4)
        self.desp_data = tk.Label(self.roll_frame)
        self.desp_data.grid(row=1, column=5)

        # Label that reads in either damage or "Failure"
        self.succ_fail_label = tk.Label(self.roll_frame, font=("TkDefaultFont", 20, "bold"))
        self.succ_fail_label.grid(row=2, column=0, columnspan=6)

        # Label that shows reamining threat or advantage to spend
        self.adv_th_remain_label = tk.Label(self.results_frame)
        self.adv_th_remain_label.grid(row=0, column=0)
        self.adv_th_remain_symbols = tk.Label(self.results_frame)
        self.adv_th_remain_symbols.grid(row=0, column=1)

        # Label that shows remaining triumph
        self.tri_remain_label = tk.Label(self.results_frame)
        self.tri_remain_label.grid(row=0, column=2)
        self.tri_remain_symbols = tk.Label(self.results_frame)
        self.tri_remain_symbols.grid(row=0, column=3)

        # Label that shows remaining despair
        self.desp_remain_label = tk.Label(self.results_frame)
        self.desp_remain_label.grid(row=0, column=4)
        self.desp_remain_symbols = tk.Label(self.results_frame)
        self.desp_remain_symbols.grid(row=0, column=5)

        # Images loaded in under on_show_frame
        # Advantage images
        self.load_adv1_display = Image.open('images/Advantage.png')
        self.render_adv1_display = ImageTk.PhotoImage(self.load_adv1_display)
        self.load_adv2_display = Image.open('images/AdvantageAdvantage.png')
        self.render_adv2_display = ImageTk.PhotoImage(self.load_adv2_display)
        self.load_adv3_display = Image.open('images/AdvantageAdvantageAdvantage.png')
        self.render_adv3_display = ImageTk.PhotoImage(self.load_adv3_display)
        self.load_adv4_display = Image.open('images/AdvantageAdvantageAdvantageAdvantage.png')
        self.render_adv4_display = ImageTk.PhotoImage(self.load_adv4_display)
        self.load_adv5_display = Image.open('images/AdvantageAdvantageAdvantageAdvantageAdvantage.png')
        self.render_adv5_display = ImageTk.PhotoImage(self.load_adv5_display)

        # Threat images
        self.load_th1_display = Image.open('images/Threat.png')
        self.render_th1_display = ImageTk.PhotoImage(self.load_th1_display)
        self.load_th2_display = Image.open('images/ThreatThreat.png')
        self.render_th2_display = ImageTk.PhotoImage(self.load_th2_display)
        self.load_th3_display = Image.open('images/ThreatThreatThreat.png')
        self.render_th3_display = ImageTk.PhotoImage(self.load_th3_display)
        self.load_th4_display = Image.open('images/ThreatThreatThreatThreat.png')
        self.render_th4_display = ImageTk.PhotoImage(self.load_th4_display)
        self.load_th5_display = Image.open('images/ThreatThreatThreatThreatThreat.png')
        self.render_th5_display = ImageTk.PhotoImage(self.load_th5_display)

        # Triumph images
        self.load_tri1_display = Image.open('images/Triumph.png')
        self.render_tri1_display = ImageTk.PhotoImage(self.load_tri1_display)
        self.load_tri2_display = Image.open('images/TriumphTriumph.png')
        self.render_tri2_display = ImageTk.PhotoImage(self.load_tri2_display)

        # Triumph images
        self.load_desp1_display = Image.open('images/Despair.png')
        self.render_desp1_display = ImageTk.PhotoImage(self.load_desp1_display)
        self.load_desp2_display = Image.open('images/DespairDespair.png')
        self.render_desp2_display = ImageTk.PhotoImage(self.load_desp2_display)

        self.bind("<<ShowFrame>>", lambda x:self.on_show_frame(controller))

    def on_show_frame(self, controller):
        global global_weapon_name
        global rolled_adv
        global rolled_succ
        global rolled_tri
        global rolled_fail
        global rolled_th
        global rolled_desp

        # Manually set roll for testing purposes
        # rolled_succ = 0
        # rolled_adv = 0
        # rolled_tri = 1
        # rolled_fail = 1
        # rolled_th = 3
        # rolled_desp = 0

        print("Running show_frame")
        print("Rolled succ: " + str(rolled_succ))
        print("Rolled adv: " + str(rolled_adv))
        print("Rolled tri: " + str(rolled_tri))
        print("Rolled fail: " + str(rolled_fail))
        print("Rolled threat: " + str(rolled_th))
        print("Rolled despair: " + str(rolled_desp))

        if rolled_adv:
            # Set label to remaining advantage (as opposed to blank or remaning threat)
            self.adv_data.config(text=str(rolled_adv))
            self.adv_th_remain_label.config(text="Remaining Advantage:")
            self.adjust_adv(controller)
        else:
            self.adv_symbol.config(image=self.render_fade_adv)


        if rolled_th:
            self.threat_data.config(text=str(rolled_th))
            self.adv_th_remain_label.config(text="Remaining Threat:")
            self.adjust_th(controller)
        else:
            self.threat_symbol.config(image=self.render_fade_threat)


        if rolled_succ:
            self.succ_data.config(text=str(rolled_succ))
            fetched_damage = database.fetch_weapon_damage("Terrinoth", global_weapon_name)
            self.succ_fail_label.config(text=(str(rolled_succ + fetched_damage) + " Damage"))
        else:
            self.succ_symbol.config(image=self.render_fade_succ)
            self.succ_fail_label.config(text="Failure")


        if rolled_fail:
            self.fail_data.config(text=str(rolled_fail))
        else:
            self.fail_symbol.config(image=self.render_fade_fail)


        if rolled_tri:
            self.tri_data.config(text=str(rolled_tri))
            self.tri_remain_label.config(text="Remaining Triumph:")
            self.adjust_tri(controller)
        else:
            self.tri_symbol.config(image=self.render_fade_tri)


        if rolled_desp:
            self.desp_data.config(text=str(rolled_desp))
            self.desp_remain_label.config(text="Remaining Despair:")
            self.adjust_desp(controller)
        else:
            self.desp_symbol.config(image=self.render_fade_desp)

        if rolled_adv or rolled_th or rolled_tri or rolled_desp:
            self.cost_label = tk.Label(self.spend_frame, text="Cost").grid(row=0, column=0, columnspan=3)
            self.results_op_label = tk.Label(self.spend_frame, text="Result Options").grid(row=0, column=3)

        if (rolled_adv and rolled_desp) or (rolled_th and rolled_tri):
            self.establish_combined_table(controller)

        elif (rolled_adv > 0 and rolled_desp == 0) or (rolled_tri > 0 and rolled_th == 0):
            self.establish_advantage_table(controller)

        elif (rolled_th > 0 and rolled_tri == 0) or (rolled_desp > 0 and rolled_adv == 0):
            self.establish_threat_table(controller)

    def establish_combined_table(self, controller):
        print("Running establish_advantage_table")
        global global_weapon_name
        fetched_critical = database.fetch_weapon_crit("Terrinoth", global_weapon_name)

        # Adjustable padding and wrap length
        op_pad = (10, 10)
        wrapper = 500

        # Tier 1
        adv_t1_ops = ["Add a Boost to the next allied character's check.", "Notice a single important point in the ongoing conflict, such as the location of a door's control panel or a weak point on an armored car."]

        # TODO: if Nemesis, append recover strain    text="Recover 1 strain."
        # TODO: if knockdown quality, append knockdown
        if fetched_critical == 1:
            adv_t1_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
            adv_t1_ops.append("Used to boost Critical Injury roll by +10.")

        # Establish symbols for loop
        self.load_tier_one_adv = Image.open('images/Advantage.png')
        self.render_tier_one_adv = ImageTk.PhotoImage(self.load_tier_one_adv)
        self.load_tier_one_tri = Image.open('images/Triumph.png')
        self.render_tier_one_tri = ImageTk.PhotoImage(self.load_tier_one_tri)

        self.row_begin_value = 1

        for option in adv_t1_ops:
            if option == adv_t1_ops[-1]:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_adv, command=lambda option=option:self.decrease_adv(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                # Separator
                ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                self.row_begin_value += 2
            else:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_adv, command=lambda option=option:self.decrease_adv(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

        if rolled_adv >= 2:
            # Tier 2
            adv_t2_ops = ["Perform an immediate free maneuver that does not exceed the limit of two maneurvers per turn.", "Add a Setback to the targeted character's next check.", "Add a Boost to any allied character's next check, including that of the active character."]

            if fetched_critical == 2:
                adv_t2_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
                adv_t2_ops.append("Used to boost Critical Injury roll by +10.")

            # TODO: if active quality present, append active quality

            # Establish symbols for loop
            self.load_tier_two_adv = Image.open('images/AdvantageAdvantage.png')
            self.render_tier_two_adv = ImageTk.PhotoImage(self.load_tier_two_adv)

            for option in adv_t2_ops:
                if option == adv_t2_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_adv, command=lambda option=option:self.decrease_adv(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_adv, command=lambda option=option:self.decrease_adv(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    self.tier_one_adv_op = tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_adv >= 3:
            # Tier 3
            adv_t3_ops = ["Negate the targeted enemy's defense (such as the defense gained from cover, equipment, or performing the guarded stance maneuver) until the end of the currend round.", "Ignore penalizing environmental effects such as inclement weather, zero gravity, or similar circumstances until the end of the active character's next turn.", "When dealing damage to a target, have the attack disable the opponent or one piece of gear rather than dealing wounds or strain. This could include hobbling them temporarily with a shot to the leg, or disabling their radio. This should be agreed upon by the player and the GM, and the effects are up to the GM. The effects should be temporary and not too excessive.", "Gain +1 melee or ranged defense until the end of the active character's next turn.", "Force the target to drop a melee or ranged weapon they are wielding."]

            if fetched_critical == 3:
                adv_t3_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
                adv_t3_ops.append("Used to boost Critical Injury roll by +10.")

            # Establish symbols for loop
            self.load_tier_three_adv = Image.open('images/AdvantageAdvantageAdvantage.png')
            self.render_tier_three_adv = ImageTk.PhotoImage(self.load_tier_three_adv)

            for option in adv_t3_ops:
                if option == adv_t3_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_adv, command=lambda option=option:self.decrease_adv(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_adv, command=lambda option=option:self.decrease_adv(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_tri >= 1:
            # Tier 4
            adv_t4_ops = ["Upgrade the difficulty of the targeted character's next check.", "Upgrade the ability of any allied character's next check, including that of the current active character.", "Do something vital, such as shooting the conrols to the nearby blast doors to seal them shut.", "Inflict a Critical Injury with a successful attack that deals damage past soak.", "Used to boost Critical Injury roll by +10."]

            # TODO: append options for abilities like Ogre's swing if present

            for option in adv_t4_ops:
                if option == adv_t4_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_tri >= 2:
            # Tier 5 Options
            self.load_tier_two_tri = Image.open('images/TriumphTriumph.png')
            self.render_tier_two_tri = ImageTk.PhotoImage(self.load_tier_two_tri)

            # Symbol buttons
            ttk.Button(self.spend_frame, image=self.render_tier_two_tri, command=lambda option=option:self.decrease_tri(controller, 2, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

            # Description
            tk.Label(self.spend_frame, text="When dealing damage to a target, have the attack destroy a piece of equipment the target is using, such as blowing up their assault rifle or slicing their sword in half.", wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

            self.row_begin_value += 1

        print("Running establish_threat_table")
        global global_adversary
        fetched_type = database.fetch_adversary_type("Terrinoth", global_adversary)

        # TODO: Add a place for damaged weapons? Maybe just make it a string and have it added as an ongoing effect

        # Adjustable padding and wrap length
        op_pad = (10, 10)
        wrapper = 500

        # Tier 1
        th_t1_ops = []

        if fetched_type == "Minion":
            th_t1_ops.append("The active minion group suffers 1 wound")
        elif fetched_type == "Rival":
            th_t1_ops.append("The active character suffers 1 wound")
        elif fetched_type == "Nemesis":
            th_t1_ops.append("The active character suffers 1 strain")

        if fetched_type == "Minion":
            th_t1_ops.append("The active minion group loses the benefit of a prior maneuver (such as taking cover or assuming a guarded stance) until they perform the maneuver again.")
        elif fetched_type == "Rival" or "Nemesis":
            th_t1_ops.append("The active character loses the benefit of a prior maneuver (such as taking cover or assuming a guarded stance) until they perform the maneuver again.")

        # Establish symbols for loop
        self.load_tier_one_th = Image.open('images/Threat.png')
        self.render_tier_one_th = ImageTk.PhotoImage(self.load_tier_one_th)
        self.load_tier_one_desp = Image.open('images/Despair.png')
        self.render_tier_one_desp = ImageTk.PhotoImage(self.load_tier_one_desp)

        # self.row_begin_value = 1

        for option in th_t1_ops:
            if option == th_t1_ops[-1]:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_th, command=lambda option=option:self.decrease_th(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                # Separator
                ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                self.row_begin_value += 2
            else:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_th, command=lambda option=option:self.decrease_th(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

        if rolled_th >= 2:
            # Tier 2
            th_t2_ops = ["An opponent may immediately perform one free maneuver as an incidental in response to the active character's check.", "Add a Boost to the targeted character's next check.", "The active character or an allied character suffers a Setback on their next action."]

            # Establish symbols for loop
            self.load_tier_two_th = Image.open('images/ThreatThreat.png')
            self.render_tier_two_th = ImageTk.PhotoImage(self.load_tier_two_th)

            for option in th_t2_ops:
                if option == th_t2_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    self.tier_one_th_op = tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1
        if rolled_th >= 3:
            # Tier 3
            th_t3_ops = ["The active character falls prone.", "The active character grants the enemy a significant advantage in the ongoing encounter, such as accidentally blasting the controls to a bridge the active character was planning to use for their escape."]

            # Establish symbols for loop
            self.load_tier_three_th = Image.open('images/ThreatThreatThreat.png')
            self.render_tier_three_th = ImageTk.PhotoImage(self.load_tier_three_th)

            for option in th_t3_ops:
                if option == th_t3_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_th, command=lambda option=option:self.decrease_th(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_desp >= 1:
            # Tier 4
            th_t4_ops = ["The character's weapon immediately runs of of ammuniation and may not be used for the remainder of the encounter.", "Upgrade the difficulty of an allied character's next check or the next check of the current active character.", "The tool, Brawl, or Melee weapon the active character is using becomes damaged."]

            for option in th_t4_ops:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

    def establish_advantage_table(self, controller):
        print("Running establish_advantage_table")
        global global_weapon_name
        fetched_critical = database.fetch_weapon_crit("Terrinoth", global_weapon_name)

        # Adjustable padding and wrap length
        op_pad = (10, 10)
        wrapper = 500

        # Tier 1
        adv_t1_ops = ["Add a Boost to the next allied character's check.", "Notice a single important point in the ongoing conflict, such as the location of a door's control panel or a weak point on an armored car."]

        # TODO: if Nemesis, append recover strain    text="Recover 1 strain."
        # TODO: if knockdown quality, append knockdown
        if fetched_critical == 1:
            adv_t1_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
            adv_t1_ops.append("Used to boost Critical Injury roll by +10.")

        # Establish symbols for loop
        self.load_tier_one_adv = Image.open('images/Advantage.png')
        self.render_tier_one_adv = ImageTk.PhotoImage(self.load_tier_one_adv)
        self.load_tier_one_tri = Image.open('images/Triumph.png')
        self.render_tier_one_tri = ImageTk.PhotoImage(self.load_tier_one_tri)

        self.row_begin_value = 1

        for option in adv_t1_ops:
            if option == adv_t1_ops[-1]:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_adv, command=lambda option=option:self.decrease_adv(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                # Separator
                ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                self.row_begin_value += 2
            else:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_adv, command=lambda option=option:self.decrease_adv(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

        if rolled_adv >= 2:
            # Tier 2
            adv_t2_ops = ["Perform an immediate free maneuver that does not exceed the limit of two maneurvers per turn.", "Add a Setback to the targeted character's next check.", "Add a Boost to any allied character's next check, including that of the active character."]

            if fetched_critical == 2:
                adv_t2_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
                adv_t2_ops.append("Used to boost Critical Injury roll by +10.")

            # TODO: if active quality present, append active quality

            # Establish symbols for loop
            self.load_tier_two_adv = Image.open('images/AdvantageAdvantage.png')
            self.render_tier_two_adv = ImageTk.PhotoImage(self.load_tier_two_adv)

            for option in adv_t2_ops:
                if option == adv_t2_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_adv, command=lambda option=option:self.decrease_adv(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_adv, command=lambda option=option:self.decrease_adv(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    self.tier_one_adv_op = tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_adv >= 3:
            # Tier 3
            adv_t3_ops = ["Negate the targeted enemy's defense (such as the defense gained from cover, equipment, or performing the guarded stance maneuver) until the end of the currend round.", "Ignore penalizing environmental effects such as inclement weather, zero gravity, or similar circumstances until the end of the active character's next turn.", "When dealing damage to a target, have the attack disable the opponent or one piece of gear rather than dealing wounds or strain. This could include hobbling them temporarily with a shot to the leg, or disabling their radio. This should be agreed upon by the player and the GM, and the effects are up to the GM. The effects should be temporary and not too excessive.", "Gain +1 melee or ranged defense until the end of the active character's next turn.", "Force the target to drop a melee or ranged weapon they are wielding."]

            if fetched_critical == 3:
                adv_t3_ops.append("Inflict a Critical Injury with a successful attack that deals damage past soak.")
                adv_t3_ops.append("Used to boost Critical Injury roll by +10.")

            # Establish symbols for loop
            self.load_tier_three_adv = Image.open('images/AdvantageAdvantageAdvantage.png')
            self.render_tier_three_adv = ImageTk.PhotoImage(self.load_tier_three_adv)

            for option in adv_t3_ops:
                if option == adv_t3_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_adv, command=lambda option=option:self.decrease_adv(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_adv, command=lambda option=option:self.decrease_adv(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_tri >= 1:
            # Tier 4
            adv_t4_ops = ["Upgrade the difficulty of the targeted character's next check.", "Upgrade the ability of any allied character's next check, including that of the current active character.", "Do something vital, such as shooting the conrols to the nearby blast doors to seal them shut.", "Used to boost Critical Injury roll by +10.", "Inflict a Critical Injury with a successful attack that deals damage past soak."]

            # TODO: append options for abilities like Ogre's swing if present

            for option in adv_t4_ops:
                if option == adv_t4_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda option=option:self.decrease_tri(controller, 1, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_one_tri, command=lambda:self.decrease_tri(controller, 1, self.row_begin_value)).grid(row=self.row_begin_value, column=0, columnspan=3)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_tri >= 2:
            # Tier 5 Options
            self.load_tier_two_tri = Image.open('images/TriumphTriumph.png')
            self.render_tier_two_tri = ImageTk.PhotoImage(self.load_tier_two_tri)

            # Symbol buttons
            ttk.Button(self.spend_frame, image=self.render_tier_two_tri, command=lambda option=option:self.decrease_tri(controller, 2, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

            # Description
            tk.Label(self.spend_frame, text="When dealing damage to a target, have the attack destroy a piece of equipment the target is using, such as blowing up their assault rifle or slicing their sword in half.", wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

    def establish_threat_table(self, controller):
        print("Running establish_threat_table")
        global global_adversary
        fetched_type = database.fetch_adversary_type("Terrinoth", global_adversary)

        # TODO: Add a place for damaged weapons? Maybe just make it a string and have it added as an ongoing effect

        # Adjustable padding and wrap length
        op_pad = (10, 10)
        wrapper = 500

        # Tier 1
        th_t1_ops = []

        if fetched_type == "Minion":
            th_t1_ops.append("The active minion group suffers 1 wound")
        elif fetched_type == "Rival":
            th_t1_ops.append("The active character suffers 1 wound")
        elif fetched_type == "Nemesis":
            th_t1_ops.append("The active character suffers 1 strain")

        if fetched_type == "Minion":
            th_t1_ops.append("The active minion group loses the benefit of a prior maneuver (such as taking cover or assuming a guarded stance) until they perform the maneuver again.")
        elif fetched_type == "Rival" or "Nemesis":
            th_t1_ops.append("The active character loses the benefit of a prior maneuver (such as taking cover or assuming a guarded stance) until they perform the maneuver again.")

        # Establish symbols for loop
        self.load_tier_one_th = Image.open('images/Threat.png')
        self.render_tier_one_th = ImageTk.PhotoImage(self.load_tier_one_th)
        self.load_tier_one_desp = Image.open('images/Despair.png')
        self.render_tier_one_desp = ImageTk.PhotoImage(self.load_tier_one_desp)

        self.row_begin_value = 1

        for option in th_t1_ops:
            if option == th_t1_ops[-1]:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_th, command=lambda option=option:self.decrease_th(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                # Separator
                ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                self.row_begin_value += 2
            else:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_th, command=lambda option=option:self.decrease_th(controller, 1, option)).grid(row=self.row_begin_value, column=0)
                tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

        if rolled_th >= 2:
            # Tier 2
            th_t2_ops = ["An opponent may immediately perform one free maneuver as an incidental in response to the active character's check.", "Add a Boost to the targeted character's next check.", "The active character or an allied character suffers a Setback on their next action."]

            # Establish symbols for loop
            self.load_tier_two_th = Image.open('images/ThreatThreat.png')
            self.render_tier_two_th = ImageTk.PhotoImage(self.load_tier_two_th)

            for option in th_t2_ops:
                if option == th_t2_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_two_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    self.tier_one_th_op = tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1
        if rolled_th >= 3:
            # Tier 3
            th_t3_ops = ["The active character falls prone.", "The active character grants the enemy a significant advantage in the ongoing encounter, such as accidentally blasting the controls to a bridge the active character was planning to use for their escape."]

            # Establish symbols for loop
            self.load_tier_three_th = Image.open('images/ThreatThreatThreat.png')
            self.render_tier_three_th = ImageTk.PhotoImage(self.load_tier_three_th)

            for option in th_t3_ops:
                if option == th_t3_ops[-1]:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_th, command=lambda option=option:self.decrease_th(controller, 3, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")

                    # Separator
                    ttk.Separator(self.spend_frame, orient="horizontal").grid(row=self.row_begin_value+1, columnspan=4, pady=10, sticky="ew")
                    self.row_begin_value += 2
                else:
                    # Symbol buttons
                    ttk.Button(self.spend_frame, image=self.render_tier_three_th, command=lambda option=option:self.decrease_th(controller, 2, option)).grid(row=self.row_begin_value, column=0)
                    tk.Label(self.spend_frame, text="or").grid(row=self.row_begin_value, column=1)
                    ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=2)

                    # Description
                    tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                    self.row_begin_value += 1

        if rolled_desp >= 1:
            # Tier 4
            th_t4_ops = ["The character's weapon immediately runs of of ammuniation and may not be used for the remainder of the encounter.", "Upgrade the difficulty of an allied character's next check or the next check of the current active character.", "The tool, Brawl, or Melee weapon the active character is using becomes damaged."]

            for option in th_t4_ops:
                # Symbol buttons
                ttk.Button(self.spend_frame, image=self.render_tier_one_desp, command=lambda option=option:self.decrease_desp(controller, 1, option)).grid(row=self.row_begin_value, column=0, columnspan=3)

                # Description
                tk.Label(self.spend_frame, text=option, wraplength=wrapper, justify="left").grid(row=self.row_begin_value, column=3, padx=op_pad, sticky="w")
                self.row_begin_value += 1

    def adjust_adv(self, controller):
        global rolled_adv
        if rolled_adv == 0 and rolled_tri == 0 and rolled_desp == 0:
            controller.destroy()
        elif rolled_adv == 0:
            if self.adv_th_remain_symbols.cget("image") == '':
                pass
            else:
                self.adv_th_remain_symbols.config(image='', text=None)
        elif rolled_adv == 1:
            if self.adv_th_remain_symbols.cget("image") == self.render_adv1_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_adv1_display, text=None)
        elif rolled_adv == 2:
            if self.adv_th_remain_symbols.cget("image") == self.render_adv2_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_adv2_display, text=None)
        elif rolled_adv == 3:
            if self.adv_th_remain_symbols.cget("image") == self.render_adv3_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_adv3_display, text=None)
        elif rolled_adv == 4:
            if self.adv_th_remain_symbols.cget("image") == self.render_adv4_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_adv4_display, text=None)
        elif rolled_adv == 5:
            if self.adv_th_remain_symbols.cget("image") == self.render_adv5_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_adv5_display, text=None)
        elif rolled_adv > 5:
            self.adv_th_remain_symbols.config(text=str(rolled_adv), image=None)

    def adjust_tri(self, controller):
        global rolled_tri
        if rolled_tri == 0 and rolled_adv == 0 and rolled_th == 0 and rolled_desp == 0:
            controller.destroy()
        elif rolled_tri == 0:
            if self.tri_remain_symbols.cget("image") == '':
                pass
            else:
                self.tri_remain_symbols.config(image='', text=None)
        elif rolled_tri == 1:
            if self.tri_remain_symbols.cget("image") == self.render_tri1_display:
                pass
            else:
                self.tri_remain_symbols.config(image=self.render_tri1_display, text=None)
        elif rolled_tri == 2:
            if self.tri_remain_symbols.cget("image") == self.render_tri2_display:
                pass
            else:
                self.tri_remain_symbols.config(image=self.render_tri2_display, text=None)
        elif rolled_tri > 2:
            if self.tri_remain_symbols.cget("text") == str(rolled_tri):
                pass
            else:
                self.tri_remain_symbols.config(text=str(rolled_tri))

    def adjust_th(self, controller):
        global rolled_th
        if rolled_th == 0 and rolled_desp == 0 and rolled_tri == 0:
            controller.destroy()
        elif rolled_th == 0:
            if self.adv_th_remain_symbols.cget("image") == '':
                pass
            else:
                self.adv_th_remain_symbols.config(image='', text=None)
        elif rolled_th == 1:
            if self.adv_th_remain_symbols.cget("image") == self.render_th1_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_th1_display, text=None)
        elif rolled_th == 2:
            if self.adv_th_remain_symbols.cget("image") == self.render_th2_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_th2_display, text=None)
        elif rolled_th == 3:
            if self.adv_th_remain_symbols.cget("image") == self.render_th3_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_th3_display, text=None)
        elif rolled_th == 4:
            if self.adv_th_remain_symbols.cget("image") == self.render_th4_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_th4_display, text=None)
        elif rolled_th == 5:
            if self.adv_th_remain_symbols.cget("image") == self.render_th5_display:
                pass
            else:
                self.adv_th_remain_symbols.config(image=self.render_th5_display, text=None)
        elif rolled_th > 5:
            self.adv_th_remain_symbols.config(text=str(rolled_th), image=None)

    def adjust_desp(self, controller):
        global rolled_desp
        if rolled_desp == 0 and rolled_th == 0 and rolled_adv == 0 and rolled_tri == 0:
            controller.destroy()
        elif rolled_desp == 0:
            if self.desp_remain_symbols.cget("image") == '':
                pass
            else:
                self.desp_remain_symbols.config(image='', text=None)
        elif rolled_desp == 1:
            if self.desp_remain_symbols.cget("image") == self.render_desp1_display:
                pass
            else:
                self.desp_remain_symbols.config(image=self.render_desp1_display, text=None)
        elif rolled_desp == 2:
            if self.desp_remain_symbols.cget("image") == self.render_desp2_display:
                pass
            else:
                self.desp_remain_symbols.config(image=self.render_desp2_display, text=None)
        elif rolled_desp > 2:
            if self.desp_remain_symbols.cget("text") == str(rolled_desp):
                pass
            else:
                self.desp_remain_symbols.config(text=str(rolled_desp))



    def decrease_adv(self, controller, amt, option):
        global rolled_adv
        # print("Current available advantage is: " + str(rolled_adv))
        # print("The amount on the option you selected is: " + str(amt))
        if amt <= rolled_adv:
            if option == "Inflict a Critical Injury with a successful attack that deals damage past soak.":
                if rolled_succ > 0:
                    critical.CritRoller(self)
                    rolled_adv -= amt
                    self.adjust_adv(controller)
                    self.lift()
                    self.focus_force()
                    self.grab_set()
                    self.grab_release()
                else:
                    messagebox.showwarning("Attack not successful", "Your attack must be successful in order to inflict a critical hit.")
                    self.lift()
                    self.focus_force()
                    self.grab_set()
                    self.grab_release()
            else:
                print("String didn't match critical input")
                rolled_adv -= amt
                self.adjust_adv(controller)
        else:
            # TODO: Should not need a messagebox. If there is not enough advantage. Options should be either hidden or grayed out. Probably just set state to disabled would be the easiest.
            messagebox.showwarning("Not enough advantage", "You do not have enough advantage for that action.")
            self.lift()
            self.focus_force()
            self.grab_set()
            self.grab_release()

    def decrease_tri(self, controller, amt, option):
        global rolled_tri
        # print("Current available Threat is: " + str(rolled_th))
        # print("Current amount on the option you selected is: " + str(amt))
        if amt <= rolled_tri:
            rolled_tri -= amt
            self.adjust_tri(controller)
            if option == "Inflict a Critical Injury with a successful attack that deals damage past soak.":
                critical.CritRoller(self)
            else:
                print("String didn't match critical input")
        else:
            # TODO: Should not need a messagebox. If there is not enough advantage. Options should be either hidden or grayed out. Probably just set state to disabled would be the easiest.
            messagebox.showwarning("Not enough triumph", "You do not have enough triumph for that.")
            self.lift()
            self.focus_force()
            self.grab_set()
            self.grab_release()

    def decrease_th(self, controller, amt, option):
        global rolled_th
        print("Current available Threat is: " + str(rolled_th))
        print("Current amount on the option you selected is: " + str(amt))
        if amt <= rolled_th:
            rolled_th -= amt
            self.adjust_th(controller)
        else:
            # TODO: Should not need a messagebox. If there is not enough advantage. Options should be either hidden or grayed out. Probably just set state to disabled would be the easiest.
            messagebox.showwarning("Not enough threat", "You, thankfully, do not have enough threat for that.")
            self.lift()
            self.focus_force()
            self.grab_set()
            self.grab_release()

    def decrease_desp(self, controller, amt, option):
        global rolled_desp
        # print("Current available Threat is: " + str(rolled_th))
        # print("Current amount on the option you selected is: " + str(amt))
        if amt <= rolled_desp:
            rolled_desp -= amt
            self.adjust_desp(controller)
        else:
            # TODO: Should not need a messagebox. If there is not enough advantage. Options should be either hidden or grayed out. Probably just set state to disabled would be the easiest.
            messagebox.showwarning("Not enough despair", "You're de-spared from having to spend that despair. You don't have enough.")
            self.lift()
            self.focus_force()
            self.grab_set()
            self.grab_release()


class InitiativeRoot(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        self.geometry('300x200+100+100')
        container = tk.Frame(self)
        container.pack()

        self.frames = {}

        for F in (Awareness, SplitAwareSelector, InitiativeRoller):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Awareness)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

class Awareness(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.pc_aware_label = ttk.Label(self, text="Party Aware?").pack()
        self.selected_pc_awareness = tk.StringVar(self)
        self.possible_pc_awareness = ("Select an option", "Yes", "No", "Split")
        self.pc_awareness_menu = ttk.OptionMenu(self, self.selected_pc_awareness, *self.possible_pc_awareness)
        self.pc_awareness_menu.pack()

        self.npc_aware_label = ttk.Label(self, text="Adversaries Aware?").pack()
        self.selected_npc_awareness = tk.StringVar(self)
        self.possible_npc_awareness = ("Select an option", "Yes", "No", "Split")
        self.npc_awareness_menu = ttk.OptionMenu(self, self.selected_npc_awareness, *self.possible_npc_awareness)
        self.npc_awareness_menu.pack()

        self.next_btn = ttk.Button(self, text="Next", command=lambda:self.advance(controller)).pack()

    def advance(self, controller):
        global pc_aware
        global npc_aware
        global encounter
        global encounter_adversaries

        encounter_adversaries = database.fetch_encounter_data('Terrinoth', encounter)

        campaign = database.fetch_active("Terrinoth",'campaign')
        print("campaign is: " + str(campaign))

        pc_aware = self.selected_pc_awareness.get()
        npc_aware = self.selected_npc_awareness.get()

        fetched_players = database.fetch_player_stats("Terrinoth", campaign)
        print("Fetched players are: " + str(fetched_players))
        for player in fetched_players.keys():
            if pc_aware == "Yes":
                combatants["PCs"][player] = "Cool"
            elif pc_aware == "No":
                combatants["PCs"][player] = "Vigilance"
        for adversary in encounter_adversaries:
            if npc_aware == "Yes":
                combatants["NPCs"][adversary] = "Cool"
            elif npc_aware == "No":
                combatants["NPCs"][adversary] = "Vigilance"

        if pc_aware == "Split" or npc_aware =="Split":
            controller.show_frame(SplitAwareSelector)
        else:
            controller.show_frame(InitiativeRoller)

class SplitAwareSelector(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # test = tk.Label(self, text="self.row_begin_value'm the split aware selector.").grid(row=0, column=0)

        self.bind("<<ShowFrame>>", lambda x:self.on_show_frame(controller))

    def on_show_frame(self, controller):
        print("Split Aware Selector activated")
        global pc_aware
        global npc_aware
        global encounter_adversaries

        campaign = database.fetch_active("Terrinoth", 'campaign')

        self.fetched_players = database.fetch_player_stats("Terrinoth", campaign)
        skill_options = ("Select a skill","Cool", "Vigilance")
        self.widget_dict = {}

        self.row_begin_value = 0

        if pc_aware == "Split":
            self.pc_label = tk.Label(self, text="Player").grid(row=self.row_begin_value, column=0)
            self.pc_skill_label = tk.Label(self, text="Skill").grid(row=self.row_begin_value, column=1)
            self.row_begin_value += 1
            self.pc_divider = ttk.Separator(self, orient="horizontal").grid(row=self.row_begin_value, column=0, columnspan=2, sticky="ew")
            for player in self.fetched_players.keys():
                self.row_begin_value += 1
                self.player_label = tk.Label(self, text=player).grid(row=self.row_begin_value, column=0)
                self.selected_skill = tk.StringVar(self)
                self.widget_dict[self.row_begin_value] = self.selected_skill
                self.pc_skill_menu = ttk.OptionMenu(self, self.selected_skill, *skill_options)
                self.pc_skill_menu.grid(row=self.row_begin_value, column=1)

        if npc_aware == "Split":
            self.row_begin_value += 1
            self.npc_label = tk.Label(self, text="Adversary").grid(row=self.row_begin_value, column=0)
            self.npc_skill_label = tk.Label(self, text="Skill").grid(row=self.row_begin_value, column=1)
            self.row_begin_value += 1
            self.npc_divider = ttk.Separator(self, orient="horizontal").grid(row=self.row_begin_value, column=0, columnspan=2, sticky="ew")
            for adversary in encounter_adversaries:
                self.row_begin_value += 1
                self.adversary_label = tk.Label(self, text=adversary).grid(row=self.row_begin_value, column=0)
                self.selected_skill = tk.StringVar(self)
                self.widget_dict[self.row_begin_value] = self.selected_skill
                self.npc_skill_menu = ttk.OptionMenu(self, self.selected_skill, *skill_options)
                self.npc_skill_menu.grid(row=self.row_begin_value, column=1)

        self.row_begin_value += 1
        self.advance_btn = ttk.Button(self, text="Next", command=lambda:self.advance(controller)).grid(row=self.row_begin_value, column=1)

    def advance(self, controller):
        self.row_begin_value = 2
        global combatants
        global encounter_adversaries
        if pc_aware == "Split":
            for player in self.fetched_players.keys():
                combatants["PCs"][player] = self.widget_dict[self.row_begin_value].get()
                self.row_begin_value += 1
            self.row_begin_value += 2
            if npc_aware == "Split":
                for adversary in encounter_adversaries:
                    combatants["NPCs"][adversary] = self.widget_dict[self.row_begin_value].get()
                    self.row_begin_value += 1

        controller.show_frame(InitiativeRoller)

class InitiativeRoller(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.dice_results = {}

        self.bind("<<ShowFrame>>", lambda x:self.on_show_frame(controller))

    def on_show_frame(self, event):
        global combatants
        party = combatants["PCs"]
        adversaries = combatants["NPCs"]
        id = 0
        for player in party.keys():
            id += 1
            self.roll_initative(id, player, party[player], "PC")
        for adversary in adversaries.keys():
            id += 1
            self.roll_initative(id, adversary, adversaries[adversary], "NPC")

        ordered_results = []
        initiative_order = []
        print("Dice results are: " + str(self.dice_results))
        for character in self.dice_results:
            successes = self.dice_results[character][1]["Successes"]
            advantages = self.dice_results[character][1]["Advantages"]
            if self.dice_results[character][0] == "PC":
                pc = 1
            else:
                pc = 0
            ordered_results.append((character, successes, advantages, pc))

        initial_list = sorted(ordered_results, key=itemgetter(1, 2, 3), reverse=True)
        print(initial_list)

        print("Creating initiative order")
        for character in initial_list:
            name = character[0]
            slot_value = self.dice_results[name][0]
            initiative_order.append(slot_value)
        tk.Label(self, text="Initiative Order").pack()

        for slot in initiative_order:
            tk.Label(self, text=slot).pack()

    def roll_initative(self, id, name, skill, side):
        print("Running roll initiative")
        campaign = database.fetch_active("Terrinoth", 'campaign')
        dice_values = {}
        dice_values["ability_dice"] = (None, "Success", "Success", ["Success", "Success"], "Advantage", "Advantage", ["Success", "Advantage"], ["Advantage", "Advantage"])
        dice_values["prof_dice"] = (None, "Success", "Success", ["Success", "Success"], ["Success", "Success"], "Advantage", ["Success", "Advantage"], ["Success", "Advantage"], ["Success", "Advantage"], ["Advantage", "Advantage"], ["Advantage", "Advantage"], ["Triumph", "Success"])

        characteristic = database.fetch_linked_char("Terrinoth", skill)[0][1]
        print(characteristic)
        # mel_def, rng_def, presence, willpower, cool, vigilance
        if side == "PC":
            fetched_players = database.fetch_player_stats("Terrinoth", campaign)
            presence = fetched_players[name][2]
            willpower = fetched_players[name][3]
            cool = fetched_players[name][4]
            vigilance = fetched_players[name][5]
        elif side == "NPC":
            key = name[name.find("-")+1:name.rfind(" x ")] # 2-Greyhaven Wizard x 1
            print("key is: " + key)
            amt = int(name[name.find(" x ")+3:name.rfind("(")-1])
            adver_stats = database.fetch_adversary_stats("Terrinoth", key)[0] # ('Reanimate', 'Undead', 'Minion', 2, 2, 1, 1, 1, 1, 3, 4, 0, 1, 1)
            willpower = adver_stats[7]
            presence = adver_stats[8]
            skill_list = database.fetch_adversary_skills("Terrinoth", key)
            if database.fetch_adversary_type('Terrinoth', key) == 'Minion':
                if "Cool" in skill_list:
                    cool = amt - 1
                else:
                    cool = 0
                if "Vigilance" in skill_list:
                    vigilance = amt - 1
                else:
                    vigilance = 0
            else:
                skill_dict = database.fetch_adversary_skills('Terrinoth', key)
                if "Cool" in skill_dict.keys():
                    cool = skill_dict["Cool"]
                else:
                    cool = 0
                if "Vigilance" in skill_dict.keys():
                    vigilance = skill_dict["Vigilance"]
                else:
                    vigilance = 0

        print("Characteristic is " + characteristic)
        print("Skill is " + skill)

        if characteristic == "Presence":
            used_char = presence
        elif characteristic == "Willpower":
            used_char = willpower
        else:
            print("You shouldn't see me, something went wrong with your code.")

        if skill == "Cool":
            used_skill = cool
        elif skill == "Vigilance":
            used_skill = vigilance
        else:
            print("You shouldn't see me, something went wrong with your code.")

        if used_char > used_skill: # Presence 3, Cool 2 = 1 ability dice 2 proficiency dice
            ability_dice = used_char - used_skill
            prof_dice = used_char - ability_dice
        elif used_skill > used_char:
            ability_dice = used_skill - used_char
            prof_dice = used_skill - ability_dice
        elif used_char == used_skill:
            ability_dice = 0
            prof_dice = used_char

        roll_results = []

        for dice in range(ability_dice):
            roll = dice_values["ability_dice"][random.randint(0, len(dice_values["ability_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        for dice in range(prof_dice):
            roll = dice_values["prof_dice"][random.randint(0, len(dice_values["prof_dice"])-1)]
            print(roll)
            if type(roll) == list:
                symbol_one = roll[0]
                symbol_two = roll[1]
                roll_results.append(symbol_one)
                roll_results.append(symbol_two)
            else:
                roll_results.append(roll)

        advantages = roll_results.count("Advantage")
        successes = roll_results.count("Success")
        triumph = roll_results.count("Triumph")

        dice_dict_insert = (side, {"Advantages": advantages, "Successes": successes, "Triumph": triumph})
        if side == "NPC":
            name = str(id) + "_" + name
        self.dice_results[name] = dice_dict_insert
        print(self.dice_results.items())
