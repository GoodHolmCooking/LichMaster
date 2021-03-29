import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import database

current_talents = []
current_abilities = []
item_to_add = ""
adversary_import = ""

class AdversaryEditor(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Import
        import_button = ttk.Button(self, text="Manage Adversaries", command=lambda:self.import_adversary(controller))
        import_button.grid(row=2, column=7)

        # Group
        # grp_label = tk.Label(self, text="Group:").grid(row=0, column=0)
        fetched_groups = sorted(database.fetch_groups('Terrinoth'))
        avail_groups = []
        avail_groups.append("Select a group")
        for group in fetched_groups:
            avail_groups.append(group[0])
        self.grp_data = tk.StringVar(self)
        adversary_grp_menu = ttk.OptionMenu(self, self.grp_data, *avail_groups)
        # adversary_grp_menu.grid(row=0, column=1, columnspan=2)
        # TODO: Figure out where to establish groups. Probably in your campaign settings.

        # Name
        name_label = tk.Label(self, text="Name:")
        name_label.grid(row=2, column=0)
        self.name_text = tk.Entry(self)
        self.name_text.grid(row=2, column=1, columnspan=2)

        # Type
        type_label = tk.Label(self, text="Type:")
        type_label.grid(row=2, column=3, padx=(50,0))
        adversary_types = ["Select a type", "Minion", "Rival", "Nemesis"]
        self.selected_type = tk.StringVar()
        self.selected_type.set(adversary_types[0])
        adversary_type_menu = ttk.OptionMenu(self, self.selected_type, *adversary_types, command=self.type_change)
        adversary_type_menu.grid(row=2, column=4, columnspan=2, pady=10)

        # Divider
        characterstic_divide = ttk.Separator(self, orient="horizontal").grid(row=3, columnspan=8, pady=10, sticky="ew")

        # Characteristic Values
        self.brawn_value = tk.Entry(self, width=2)
        self.brawn_value.grid(row=4, column=0)
        self.agility_value = tk.Entry(self, width=2)
        self.agility_value.grid(row=4, column=1)
        self.intellect_value = tk.Entry(self, width=2)
        self.intellect_value.grid(row=4, column=2)
        self.cunning_value = tk.Entry(self, width=2)
        self.cunning_value.grid(row=4, column=3)
        self.willpower_value = tk.Entry(self, width=2)
        self.willpower_value.grid(row=4, column=4)
        self.presence_value = tk.Entry(self, width=2)
        self.presence_value.grid(row=4, column=5)

        # Characteristic Labels
        brawn_label = tk.Label(self, text="Brawn")
        brawn_label.grid(row=5, column=0)
        agility_label = tk.Label(self, text="Agility")
        agility_label.grid(row=5, column=1)
        intellect_label = tk.Label(self, text="Intellect")
        intellect_label.grid(row=5, column=2)
        cunning_label = tk.Label(self, text="Cunning")
        cunning_label.grid(row=5, column=3)
        willpower_label = tk.Label(self, text="Willpower")
        willpower_label.grid(row=5, column=4)
        presence_label = tk.Label(self, text="Presence")
        presence_label.grid(row=5, column=5)

        # Divider
        derived_divide = ttk.Separator(self, orient="horizontal")
        derived_divide.grid(row=6, columnspan=8, pady=10, sticky="ew")

        # Derived Characterstic Labels
        soak_label = tk.Label(self, text="Soak Value")
        soak_label.grid(row=7, column=0, columnspan=2)
        self.wound_thresh_label = tk.Label(self, text="W. Threshold")
        self.wound_thresh_label.grid(row=7, column=2)
        self.strain_thresh_label = tk.Label(self, text="S. Threshold")
        self.strain_thresh_label.grid(row=7, column=3)
        mel_def_label = tk.Label(self, text="Mel. Defense")
        mel_def_label.grid(row=7, column=4)
        rng_def_label = tk.Label(self, text="Rng. Defense")
        rng_def_label.grid(row=7, column=5)

        # Derived Characteristic Values
        self.soak_value = tk.Entry(self, width=2)
        self.soak_value.grid(row=8, column=0, columnspan=2)
        self.wound_thresh_value = tk.Entry(self, width=2)
        self.wound_thresh_value.grid(row=8, column=2)
        self.strain_thresh_value = tk.Entry(self, width=2)
        self.strain_thresh_value.grid(row=8, column=3)
        self.mel_def_value = tk.Entry(self, width=2)
        self.mel_def_value.grid(row=8, column=4)
        self.rng_def_value = tk.Entry(self, width=2)
        self.rng_def_value.grid(row=8, column=5)

        # Divider
        skills_divide = ttk.Separator(self, orient="horizontal")
        skills_divide.grid(row=9, columnspan=8, pady=10, sticky="ew")

        box_width = 55
        box_height = 4

        # Adversary Skills
        self.skills_label = tk.Label(self, text="Skills")
        self.skills_label.grid(row=10, column=0)
        self.adver_skills = tk.Listbox(self, width=box_width, height=box_height)
        self.adver_skills.grid(row=10, column=1, rowspan=3, columnspan=5)
        skills_sby = tk.Scrollbar(self)
        skills_sby.grid(row=10, column=6, rowspan=3, sticky="ns")
        self.adver_skills.configure(yscrollcommand=skills_sby.set)
        skills_sby.configure(command=self.adver_skills.yview)

        # Add/Remove Skills
        selected_skill = tk.StringVar(self)
        skills = sorted(database.fetch_skills())
        add_skill = tk.Menubutton(self, text="Add skill", indicatoron=True)
        skill_menu = tk.Menu(add_skill, tearoff=False)
        add_skill.configure(menu=skill_menu)
        for skill in skills:
            skill_menu.add_radiobutton(label=skill, variable=selected_skill, value=skill, command=lambda:self.skill_changed(selected_skill.get(), self.adver_skills, list(self.adver_skills.get(0, tk.END))), indicatoron=False)
        add_skill.grid(row=10, column=7)

        remove_skill = ttk.Button(self, text="Remove", command=lambda:self.remove_skill_func(self.adver_skills))
        remove_skill.grid(row=11, column=7)

        # Divider
        talents_divide = ttk.Separator(self, orient="horizontal")
        talents_divide.grid(row=13, columnspan=8, pady=10, sticky="ew")

        # Adversary Talents
        talents_label = tk.Label(self, text="Talents")
        talents_label.grid(row=14, column=0)
        self.adver_talents = tk.Listbox(self, width=box_width, height=box_height)
        self.adver_talents.grid(row=14, column=1, rowspan=3, columnspan=5)
        talents_sby = tk.Scrollbar(self)
        talents_sby.grid(row=14, column=6, rowspan=3, sticky="ns")
        self.adver_talents.configure(yscrollcommand=talents_sby.set)
        talents_sby.configure(command=self.adver_talents.yview)

        # Add/Remove Talents
        add_talent = ttk.Button(self, text="Add", command=lambda:self.add_talent_func(controller))
        add_talent.grid(row=14, column=7)
        remove_talent = ttk.Button(self, text="Remove", command=self.remove_talent_func)
        remove_talent.grid(row=15, column=7)

        # Horizontal Talents Scroll
        talents_sbx = tk.Scrollbar(self, orient="horizontal")
        talents_sbx.grid(row=17, column=1, columnspan=5, sticky="ew")
        self.adver_talents.configure(xscrollcommand=talents_sbx.set)
        talents_sbx.configure(command=self.adver_talents.xview)

        # Divider
        abilities_divide = ttk.Separator(self, orient="horizontal")
        abilities_divide.grid(row=18, columnspan=8, pady=10, sticky="ew")

        # Adversary Abilities
        abilities_label = tk.Label(self, text="Abilities")
        abilities_label.grid(row=19, column=0)
        self.adver_abilities = tk.Listbox(self, width=box_width, height=box_height)
        self.adver_abilities.grid(row=19, column=1, rowspan=3, columnspan=5)
        abilities_sby = tk.Scrollbar(self)
        abilities_sby.grid(row=19, column=6, rowspan=3)
        self.adver_abilities.configure(yscrollcommand=abilities_sby.set)
        abilities_sby.configure(command=self.adver_abilities.yview)

        # Add/Remove Abilities
        add_ability = ttk.Button(self, text="Add", command=lambda:self.add_ability_func(controller))
        add_ability.grid(row=19, column=7)
        remove_ability = ttk.Button(self, text="Remove", command=self.remove_ability_func)
        remove_ability.grid(row=20, column=7)

        # self.adver_abilities.bind('<Double-Button-1>', lambda x:self.edit_ability())

        # Horizontal Ability Scroll
        abilities_sbx = tk.Scrollbar(self, orient="horizontal")
        abilities_sbx.grid(row=22, column=1, columnspan=5, sticky="ew")
        self.adver_abilities.configure(xscrollcommand=abilities_sbx.set)
        abilities_sbx.configure(command=self.adver_abilities.xview)

        # Divider
        equipment_divide = ttk.Separator(self, orient="horizontal")
        equipment_divide.grid(row=23, columnspan=8, pady=10, sticky="ew")

        # Adversary Equipment
        equipment_label = tk.Label(self, text="Equipment")
        equipment_label.grid(row=24, column=0)
        self.adver_equipment = tk.Listbox(self, width=box_width, height=box_height)
        self.adver_equipment.grid(row=24, column=1, rowspan=3, columnspan=5)
        equipment_sby = tk.Scrollbar(self)
        equipment_sby.grid(row=24, column=6, rowspan=3, sticky="ns")
        self.adver_equipment.configure(yscrollcommand=equipment_sby.set)
        equipment_sby.configure(command=self.adver_equipment.yview)

        # Add/Remove Equipment
        add_equipment = ttk.Button(self, text="Add", command=lambda:self.add_equip_func(controller))
        add_equipment.grid(row=24, column=7)
        remove_equipment = ttk.Button(self, text="Remove", command=self.remove_equip_func)
        remove_equipment.grid(row=25, column=7)

        # self.adver_equipment.bind('<Double-Button-1>', lambda x:self.edit_equipment())

        # Horizontal Equipment Scroll
        equipment_sbx = tk.Scrollbar(self, orient="horizontal")
        equipment_sbx.grid(row=27, column=1, columnspan=5, sticky="ew")
        self.adver_equipment.configure(xscrollcommand=equipment_sbx.set)
        equipment_sbx.configure(command=self.adver_equipment.xview)

        save_button = ttk.Button(self, text="Save Changes", command=self.save_adversary)
        save_button.grid(row=29, column=0, columnspan=8)

        self.equipment_list = []
        self.weapon_list = []
        self.gear_list = []

    def type_change(self, event):
        if self.selected_type.get() == 'Minion':
            self.skills_label.config(text='Skills (Group)')
            self.wound_thresh_label.grid(row=7, column=2, columnspan=2)
            self.strain_thresh_label.grid_forget()
            self.wound_thresh_value.grid(row=8, column=2, columnspan=2)
            self.strain_thresh_value.grid_forget()

        elif self.selected_type.get() == 'Rival':
            self.skills_label.config(text='Skills')
            self.wound_thresh_label.grid(row=7, column=2, columnspan=2)
            self.strain_thresh_label.grid_forget()
            self.wound_thresh_value.grid(row=8, column=2, columnspan=2)
            self.strain_thresh_value.grid_forget()

        elif self.selected_type.get() == 'Nemesis':
            self.skills_label.config(text='Skills')
            self.wound_thresh_label.grid_forget()
            self.wound_thresh_label.grid(row=7, column=2)
            self.strain_thresh_label.grid_forget()
            self.strain_thresh_label.grid(row=7, column=3)
            self.wound_thresh_value.grid_forget()
            self.wound_thresh_value.grid(row=8, column=2)
            self.strain_thresh_value.grid_forget()
            self.strain_thresh_value.grid(row=8, column=3)

    def import_adversary(self, controller):
        root = AdversaryImporter(controller)
        self.wait_window(root)
        global adversary_import
        if adversary_import:
            fetched_adver_stats = database.fetch_adversary_stats("Terrinoth", adversary_import)[0]

            fetched_name = fetched_adver_stats[0]
            self.name_text.insert(tk.END, fetched_name)
            fetched_grp = fetched_adver_stats[1]
            self.grp_data.set(fetched_grp)
            fetched_type = fetched_adver_stats[2]
            self.selected_type.set(fetched_type)
            brawn = fetched_adver_stats[3]
            self.brawn_value.insert(tk.END, brawn)
            agility = fetched_adver_stats[4]
            self.agility_value.insert(tk.END, agility)
            intellect = fetched_adver_stats[5]
            self.intellect_value.insert(tk.END, intellect)
            cunning = fetched_adver_stats[6]
            self.cunning_value.insert(tk.END, cunning)
            willpower = fetched_adver_stats[7]
            self.willpower_value.insert(tk.END, willpower)
            presence = fetched_adver_stats[8]
            self.presence_value.insert(tk.END, presence)
            soak = fetched_adver_stats[9]
            self.soak_value.insert(tk.END, soak)
            wound_thresh = fetched_adver_stats[10]
            self.wound_thresh_value.insert(tk.END, wound_thresh)
            strain_thresh = fetched_adver_stats[11]
            self.strain_thresh_value.insert(tk.END, strain_thresh)
            mel_def = fetched_adver_stats[12]
            self.mel_def_value.insert(tk.END, mel_def)
            rng_def = fetched_adver_stats[13]
            self.rng_def_value.insert(tk.END, rng_def)

            fetched_adver_skills = database.fetch_adversary_skills("Terrinoth", adversary_import)
            if database.fetch_adversary_type("Terrinoth", adversary_import) == "Minion":
                for skill in fetched_adver_skills:
                    self.adver_skills.insert(tk.END, skill)
            else:
                for skill in fetched_adver_skills.keys():
                    skill_input = skill + " " + str(fetched_adver_skills[skill])
                    self.adver_skills.insert(tk.END, skill_input)

            fetched_adver_abilities = database.fetch_adversary_abilities("Terrinoth", adversary_import)

            if fetched_adver_abilities:
                for ability in fetched_adver_abilities:
                    ability = ability[:-2]
                    self.adver_abilities.insert(tk.END, ability)

            fetched_adver_equipment = database.fetch_adversary_equipment("Terrinoth", adversary_import)

            # [[('Rusted Blade', 'Melee (Light)', 5, 3, 'Engaged')], [('Worn Bow', 'Ranged', 6, 3,'Medium')]]

            items_to_import = []
            for item in fetched_adver_equipment:
                weapon_name = item[0][0]
                weapon_skill = item[0][1]
                weapon_damage = str(item[0][2])
                weapon_critical = str(item[0][3])
                weapon_rng = item[0][4]
                if len(item[0]) > 5:
                    weapon_qualities = item[0][5]
                    weapon_output = weapon_name + " (" + weapon_skill + "; Damage " + weapon_damage + "; Critical " + weapon_critical + "; Range [" + weapon_rng + "]; " + weapon_qualities
                else:
                    weapon_output = weapon_name + " (" + weapon_skill + "; Damage " + weapon_damage + "; Critical " + weapon_critical + "; Range [" + weapon_rng + "])"
                items_to_import.append(weapon_output)

            for item in items_to_import:
                self.adver_equipment.insert(tk.END, item)

            adversary_import = ""

    def skill_changed(self, s, s_listbox, cur_list):
        def rank_changed(event):
            rank = selected_rank.get()
            input = s + ": " + str(rank)
            root.destroy()

            if s in str(s_listbox.get(0, tk.END)):
                i = 0
                for skill in s_listbox.get(0, tk.END):
                    if s in str(skill):
                        s_listbox.delete(i)
                    i += 1
                s_listbox.insert(tk.END, input)
            else:
                cur_list.append(input)
                sorted_list = sorted(cur_list)
                s_listbox.delete(0, tk.END)
                for skill in sorted_list:
                    s_listbox.insert(tk.END, skill)

        if not self.selected_type.get() == 'Minion':
            root = tk.Toplevel(self)
            tk.Label(root, text='Rank').pack(anchor="w")
            selected_rank = tk.StringVar(root)
            avail_ranks = ('Select a rank', 1, 2, 3, 4, 5)
            rank_options = ttk.OptionMenu(root, selected_rank, *avail_ranks, command=rank_changed)
            rank_options.pack(anchor="e")
        else:
            if s in s_listbox.get(0, tk.END):
                pass
            else:
                cur_list.append(s)
                sorted_list = sorted(cur_list)
                s_listbox.delete(0, tk.END)
                for skill in sorted_list:
                    s_listbox.insert(tk.END, skill)

    def remove_skill_func(self, s_list):
        # TODO: Maybe add exception for if nothing is selected
        index = s_list.curselection()[0]
        s_list.delete(index)

    def add_ability_func(self, controller):
        root = AbilityCreator(controller)
        self.wait_window(root)
        global current_abilities
        self.adver_abilities.delete(0, tk.END)
        for ability in current_abilities:
            self.adver_abilities.insert(tk.END, ability)

    def remove_ability_func(self):
        index = self.adver_abilities.curselection()
        ability = self.adver_abilities.get(index)
        global current_abilities
        current_abilities.remove(ability)
        self.adver_abilities.delete(index)


    def add_equip_func(self, controller):
        root = EquipmentEditor(controller)
        self.wait_window(root)
        global item_to_add
        self.adver_equipment.insert(tk.END, item_to_add[0])

    def remove_equip_func(self):
        global item_to_add
        item_to_add = ""
        index = self.adver_equipment.curselection()[0]
        self.adver_equipment.delete(index)

    def add_talent_func(self, controller):
        root = TalentImporter(controller)
        self.wait_window(root)
        global current_talents
        self.adver_talents.delete(0, tk.END)
        for talent in current_talents:
            self.adver_talents.insert(tk.END, talent)

    def remove_talent_func(self):
        global current_talents
        index = self.adver_talents.curselection()[0]
        talent = self.adver_talents.get(index)
        self.adver_talents.delete(index)
        current_talents.remove(talent)

    def save_adversary(self):
        # TABLE adversary_stats
        adver_name = self.name_text.get().title()
        if adver_name == "":
            messagebox.showwarning("No name entered", "Please enter a name.")

        else:
            # adver_grp = self.grp_data.get()
            adver_grp = 'Uncategorized'
            adver_type = self.selected_type.get()
            if adver_type == 'Select a type':
                messagebox.showwarning("No type selected", "Please select an adversary type.")
            else:
                brawn = self.brawn_value.get()
                agility = self.agility_value.get()
                intellect = self.intellect_value.get()
                cunning = self.cunning_value.get()
                willpower = self.willpower_value.get()
                presence = self.presence_value.get()
                soak = self.soak_value.get()
                wound_thresh = self.wound_thresh_value.get()
                strain_thresh = self.strain_thresh_value.get()
                if strain_thresh == "":
                    strain_thresh = '0'
                mel_def = self.mel_def_value.get()
                rng_def = self.rng_def_value.get()

                adver_stats_input = [adver_name, adver_grp, adver_type, brawn, agility, intellect, cunning, willpower, presence, soak, wound_thresh, strain_thresh, mel_def, rng_def]
                adver_stats_input = str(adver_stats_input)[1:-1]

                conn = sqlite3.connect("Terrinoth")
                cur = conn.cursor()
                cur.execute("INSERT INTO adversary_stats (adver_name, adver_grp, adver_type, brawn, agility, intellect, cunning, willpower, presence, soak, wound_thresh, strain_thresh, mel_def, rng_def) VALUES (" + adver_stats_input + ")")
                conn.commit()
                conn.close()

                if self.selected_type.get() == 'Minion':
                    # TABLE minion_skills
                    skill_list = list(self.adver_skills.get(0, tk.END))
                    for skill in skill_list:
                        skill_input = str([adver_name, skill])[1:-1]

                        conn = sqlite3.connect("Terrinoth")
                        cur = conn.cursor()
                        cur.execute("INSERT INTO minion_skills (adver_name, skill) VALUES (" + skill_input + ")")
                        conn.commit()
                        conn.close()
                else:
                    # TABLE non_minion_skills
                    skill_list = list(self.adver_skills.get(0, tk.END))
                    for skill in skill_list: # ('Brawl: 3', 'Charm: 2')
                        skill_name = skill.split(":")[0]
                        skill_rank = skill.split(":")[1][1:]
                        skill_input = str([adver_name, skill_name, skill_rank])[1:-1]

                        conn = sqlite3.connect("Terrinoth")
                        cur = conn.cursor()
                        cur.execute("INSERT INTO non_minion_skills (adver_name, skill, skill_rank) VALUES (" + skill_input + ")")
                        conn.commit()
                        conn.close()

                # Save talents
                talent_list = self.adver_talents.get(0, tk.END)

                for talent in talent_list: # Precise Archery OR Body Guard 2
                    if talent.split()[-1].isdigit():
                        talent_key = ' '.join(talent.split()[:-1]) #(Body, Guard) --> 'Body Guard'
                        talent_rank = talent.split()[-1]
                    else:
                        talent_key = talent
                        talent_rank = 1
                    conn = sqlite3.connect("Terrinoth")
                    cur = conn.cursor()
                    cur.execute("INSERT INTO adversary_talents VALUES (?,?,?)", (adver_name, talent_key, talent_rank))
                    conn.commit()
                    conn.close()

                # Save abilities
                adver_ability_list = list(self.adver_abilities.get(0, tk.END))
                # ("Muffin Maker: Makes muffins", "Bro: Good at lifting")

                for ability in adver_ability_list:
                    ability_name = ability.split(":")[0] # ['Muffin Maker', ' Makes muffins'] --> 'Muffin Maker'
                    ability_effect = ability.split(":")[1][1:] # ['Muffin Maker', ' Makes muffins'] --> ' Make muffins' --> 'Make muffins'

                    ability_input = str([adver_name, ability_name, ability_effect])[1:-1]

                    conn = sqlite3.connect("Terrinoth")
                    cur = conn.cursor()
                    cur.execute("INSERT INTO adversary_abilities (adver_name, ability_name, ability_descr) VALUES (" + ability_input + ")")
                    conn.commit()
                    conn.close()

                # Sample Equipment List
                # ['Sword (Melee (Light); Damage 5; Critical 2; Range [Engaged]; Defensive) (Weapon)', 'Bow (Ranged; Damage 7; Critical 3; Range [Medium]) (Weapon)', 'Elf Spear (Melee (Heavy); Damage 7; Critcal 3; Range [Engaged]; Accurate, Defensive)']

                # 'Accurate 1) (Weapon'

                # TODO: Can't save gear at the moment, add functionality later.

                # Save items
                for item in self.adver_equipment.get(0, tk.END):
                    if item[item.rfind("(")+1:item.rfind(")")] == 'Weapon':
                        item_data = item.split(";")
                        # item_data is: ['Sword (Melee (Light)', ' Damage 6', ' Critical 2', ' Range [Engaged]', ' Defensive 2, Pierce 2) (Weapon)']

                        print("item_data is: " + str(item_data))
                        item_end = item_data[-1] # ' Defensive 2, Pierce 2) (Weapon)'
                        item_tag = item_end.split()[-1] # ['Defensive', '2,', 'Pierce', '2)', '(Weapon)'
                        if item_tag == '(Weapon)':
                            is_weapon = 1
                        elif item_tag == '(Gear)':
                            is_weapon = 0
                        weapon_name_skill = item_data[0].split("(") # ['Sword ','Melee', 'Light)'] OR ['Haste Bow ', 'Ranged']
                        equip_name = weapon_name_skill[0].rstrip() # 'Sword' Chops space off end
                        if len(weapon_name_skill) > 2:
                            weapon_skill = weapon_name_skill[1] + "(" + weapon_name_skill[2] # Melee (Light)
                        else:
                            weapon_skill = weapon_name_skill[1] # Ranged for example
                        weapon_damage = item_data[1].split(" ")[2] # Damage 6 --> 6
                        weapon_critical = item_data[2].split(" ")[2] # Critical 2 --> 2
                        weapon_range_brackets = item_data[3].split(" ")[2] # 'Range [Engaged]' --> '[Engaged]'
                        weapon_range = ""
                        weapon_qualities = []
                        q_rank = {}
                        if len(item_data) > 4: # Qualities are present
                        # ' Defensive 2, Pierce 2) (Weapon)']
                            weapon_range = weapon_range_brackets[1:-1] # '[Engaged]' --> 'Engaged'
                            if "," in item_data[4]: # There are multiple qualities
                                weapon_qualities_rough = item_data[4].split(",") # [' Defensive 2', ' Pierce 2) (Weapon)']
                                for quality in weapon_qualities_rough[:-1]: # Not last quality, ending with a character vs. ending with )
                                    quality = quality.lstrip() # ' Accurate 2' --> 'Accurate 2' chops off empty space
                                    if len(quality.split()) > 1: # 'Accurate, 2' vs 'Auto-Fire', determines if ranks exist
                                        if len(quality.split()) == 3: # ['Limited', 'Ammo', '3']
                                            q_name = quality.split[:2]
                                            weapon_qualities.append(q_name)
                                            q_rank[q_name] = quality.split()[2]
                                        elif len(quality.split()) == 2: # ['Accurate', '2'] OR ['Stun', 'Damage']
                                            if quality.split()[1].isdigit():
                                                q_name = quality.split()[0]
                                                weapon_qualities.append(q_name)
                                                q_rank[q_name] = quality.split()[1]
                                            else:
                                                q_rank[quality] = '0'
                                                weapon_qualities.append(quality)
                                    else: # this quality has no ranks. Such as Auto-Fire or Superior
                                        weapon_qualities.append(quality)
                                        q_rank[quality] = '0'
                                else: # targets last item quality
                                    last_q = weapon_qualities_rough[-1].split() # ' Defensive 1) (Weapon)' --> [' Defensive', '1)', '(Weapon)'] Or ' Sunder (Weapon)' --> [' Sunder', '(Weapon)']
                                    last_q = last_q[:-1] # [' Defensive', '1)', '(Weapon)'] -- > [' Defensive', '1)'] OR 'Sunder'
                                    last_q = " ".join(last_q) # [' Defensive', '1)'] -- > ' Defensive 1)'
                                    last_q = last_q[:-1].lstrip() # ' Defensive 1)' --> ' Defensive 1' --> 'Defensive 1'
                                    # weapon_qualities.append(last_q.split()[0]) # separates quality and rank
                                    if len(last_q.split()) > 1: # Determines if there is a rank
                                        if len(last_q.split()) == 3:
                                            q_name = last_q.split[:2]
                                            weapon_qualities.append(q_name)
                                            q_rank[q_name] = last_q.split()[2]
                                        elif len(last_q.split()) == 2:
                                            if last_q.split()[1].isdigit(): # ['Accurate', 1] vs ['Stun', 'Damage']
                                                q_name = last_q.split()[0]
                                                weapon_qualities.append(q_name)
                                                q_rank[q_name] = last_q.split()[1]
                                            else:
                                                q_rank[last_q] = '0'
                                                weapon_qualities.append(last_q)
                                    else:
                                        weapon_qualities.append(last_q)
                                        q_rank[last_q] = '0'
                            else:
                                single_q = item_data[4] # 'Defensive 1) (Weapon)'
                                single_q = single_q.split() # ['Defensive', '1)', '(Weapon)']
                                single_q = single_q[:-1] # ['Defensive', '1)']
                                single_q = " ".join(single_q) # Defensive 1)
                                single_q = single_q[:-1] # Defensive 1

                                if len(single_q.split()) > 1: # Determines if there is a rank
                                    if len(single_q.split()) == 3:
                                        q_name = single_q.split[:2]
                                        weapon_qualities.append(q_name)
                                        q_rank[q_name] = single_q.split()[2]
                                    elif len(single_q.split()) == 2:
                                        if single_q.split()[1].isdigit(): # ['Accurate', 1] vs ['Stun', 'Damage']
                                            q_name = single_q.split()[0]
                                            weapon_qualities.append(q_name)
                                            q_rank[q_name] = single_q.split()[1]
                                        else:
                                            q_rank[single_q] = '0'
                                            weapon_qualities.append(single_q)

                            print("Here's the quality dictionary: " + str(q_rank.items()))

                            for quality in weapon_qualities:
                                weapon_quality_input = str([equip_name, quality, q_rank[quality]])[1:-1]

                                print("Here's what you're tossing into the database: " + str(weapon_quality_input))

                                conn = sqlite3.connect("Terrinoth")
                                cur = conn.cursor()
                                cur.execute("INSERT INTO weapon_qualities (equip_name, item_quality, q_rank) VALUES (" + weapon_quality_input + ")")
                                conn.commit()
                                conn.close()

                        else: # Qualites are NOT present
                            weapon_range = weapon_range_brackets[1:-2] # Engaged

                        weapon_list_input = str([adver_name, equip_name, is_weapon])[1:-1]
                        weapon_stat_input = str([equip_name, weapon_skill, weapon_damage, weapon_critical, weapon_range])[1:-1]

                        print("weapon list is: " + str(weapon_list_input))
                        print("weapon stat list is: " + str(weapon_stat_input))

                        conn = sqlite3.connect("Terrinoth")
                        cur = conn.cursor()
                        cur.execute("INSERT INTO adversary_equipment (adver_name, equip_name, is_weapon) VALUES (" + weapon_list_input + ")")
                        cur.execute("INSERT INTO weapon_stats (equip_name, skill, damage, critical, weapon_rng) VALUES (" + weapon_stat_input + ")")
                        conn.commit()
                        conn.close()

                    elif item[item.rfind("("):item.rfind(")")] == 'Gear':
                        equip_name = item.split("(")[0]
                        gear_descr = item.split("(")[1][:-1]

                        conn = sqlite3.connect('Terrinoth')
                        cur = conn.cursor()
                        cur.execute("INSERT INTO adversary_equipment (adver_name, equip_name, is_weapon) VALUES (?, ?, 0)", (adver_name, equip_name))
                        cur.execute("INSERT INTO gear_descriptions VALUES (?, ?)", (equip_name, gear_descr))
                        conn.commit()
                        conn.close()
                # Clear table
                # Clear group
                self.grp_data.set("Select a group")

                # Clear name
                self.name_text.delete(0, tk.END)

                # Clear type
                self.selected_type.set("Select a type")

                # Clear characteristics
                self.brawn_value.delete(0, tk.END)
                self.agility_value.delete(0, tk.END)
                self.intellect_value.delete(0, tk.END)
                self.cunning_value.delete(0, tk.END)
                self.willpower_value.delete(0, tk.END)
                self.presence_value.delete(0, tk.END)

                # Clear derived characteristics
                self.soak_value.delete(0, tk.END)
                self.wound_thresh_value.delete(0, tk.END)
                self.strain_thresh_value.delete(0, tk.END)
                self.mel_def_value.delete(0, tk.END)
                self.rng_def_value.delete(0, tk.END)

                # Clear skills
                self.adver_skills.delete(0, tk.END)

                # Clear talents
                self.adver_talents.delete(0, tk.END)

                # Clear abilities
                self.adver_abilities.delete(0, tk.END)

                # Clear Equipment
                self.adver_equipment.delete(0, tk.END)

                # Clear globals
                current_talents = []
                current_abilities = []
                item_to_add = ""
                adversary_import = ""

                messagebox.showinfo("Adversary Saved", adver_name + " successfully saved.")

class AdversaryImporter(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        # Build window
        title_label = tk.Label(self, text="Adversary List").grid(row=0, column=0, columnspan=2)
        grp_label = tk.Label(self, text="Group").grid(row=1, column=0)
        selected_grp = tk.StringVar(self)
        # TODO: limit display on select. Doesn't do anything at the moment.
        fetched_groups = sorted(database.fetch_groups('Terrinoth'))
        grp_list = ["Select a group", "All"]
        for group in fetched_groups:
            grp_list.append(group[0])
        grp_menu = ttk.OptionMenu(self, selected_grp, *grp_list)
        # grp_menu.grid(row=1, column=1)

        self.listbox = tk.Listbox(self, height=25, width=75)
        self.listbox.grid(row=2, column=0, columnspan=3)
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=2, column=3, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.listbox.yview)
        load_button = ttk.Button(self, text="Load Adversary", command=self.load_adversary).grid(row=3, column=1)
        delete_button = ttk.Button(self, text="Delete Adversary", command=self.delete_adversary).grid(row=4, column=1)


        # Populate available adversaries
        try:
            avail_adversaries = database.fetch_adversaries()

            if type(avail_adversaries) is list:
                avail_adversaries.sort()
                for adversary in avail_adversaries:
                    self.listbox.insert(tk.END, adversary)
            else:
                self.listbox.insert(tk.END, avail_adversaries)
        except IndexError:
            pass

    def load_adversary(self):
        index = self.listbox.curselection()[0]
        selected_adver = self.listbox.get(index) # Reanimate (Minion): Undead
        global adversary_import
        adversary_import = selected_adver.split("(")[0].rstrip() # ['Reanimate ', 'Minion): Undead'] --> 'Reanimate ' --> 'Reanimate'
        self.destroy()

    def delete_adversary(self):
        index = self.listbox.curselection()[0]
        adver_full = self.listbox.get(index)
        self.listbox.delete(index)
        adver = adver_full.split("(")[0][:-1]
        selected_type = adver_full[adver_full.rfind("(")+1:adver_full.rfind(")")]

        print("adver_full is: " + str(adver_full))
        print("adver is: " + str(adver))
        print("selected_type is: " + str(selected_type))

        # adver_full is: Zombie (Minion): Undead
        # adver is: Zombie
        # selected_type is: Zombi

        conn = sqlite3.connect('Terrinoth')
        cur = conn.cursor()

        # encounter data
        cur.execute("DELETE FROM encounter_data WHERE adver_name = ?", (adver,))
        # encounter injuries
        cur.execute("DELETE FROM encounter_injuries WHERE adver_name = ?", (adver,))
        # adversary stats
        cur.execute("DELETE FROM adversary_stats WHERE adver_name = ?", (adver,))
        if selected_type == 'Minion':
            # clear minion_skills
            cur.execute("DELETE FROM minion_skills WHERE adver_name = ?", (adver,))
            # conn.commit()
        else:
            cur.execute("DELETE FROM non_minion_skills WHERE adver_name = ?", (adver,))
            # conn.commit()
        # adversary_talents
        cur.execute("DELETE FROM adversary_talents WHERE adver_name = ?", (adver,))
        # conn.commit()
        # adversary_abilities
        cur.execute("DELETE FROM adversary_abilities WHERE adver_name = ?", (adver,))
        # conn.commit()
        cur.execute("SELECT equip_name FROM adversary_equipment WHERE adver_name = ?", (adver,))
        equipment = cur.fetchall()

        for i in equipment:
            item = i[0]
            print("item is: " + str(item))
            # weapon_stats
            cur.execute("DELETE FROM weapon_stats WHERE equip_name = ?", (item,))
            # weapon_qualities
            cur.execute("DELETE FROM weapon_qualities WHERE equip_name = ?", (item,))
            # gear_descriptions
            # adversary_equipment
            cur.execute("DELETE FROM adversary_equipment WHERE adver_name = ?", (adver,))
        conn.commit()
        conn.close()
        # print("Delete has run")
        # print(database.view_table("Terrinoth", "adversary_equipment"))

class TalentImporter(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        # Build window
        self.list_label = tk.Label(self, text="Talent List").grid(row=0, column=0, columnspan=2)
        self.talent_listbox = tk.Listbox(self, height=25, width=150)
        self.talent_listbox.grid(row=1, column=0)
        self.v_scrollbar = tk.Scrollbar(self)
        self.v_scrollbar.grid(row=1, column=1, sticky="ns")
        self.talent_listbox.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.configure(command=self.talent_listbox.yview)
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal")
        self.h_scrollbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.talent_listbox.configure(xscrollcommand=self.h_scrollbar.set)
        self.h_scrollbar.configure(command=self.talent_listbox.xview)
        self.add_button = ttk.Button(self, text="Add talent", command=self.commit_talent).grid(row=3, column=0)


        # Populate talent data
        avail_talents = database.fetch_talents('Terrinoth').items()
        avail_talents = sorted(avail_talents)
        for talent in avail_talents:
            input = talent[0] + ": " + talent[1]
            self.talent_listbox.insert(tk.END, input)

    def commit_talent(self):
        global current_talents
        index = self.talent_listbox.curselection()[0]
        talent = self.talent_listbox.get(index).split(":")[0]
        if database.is_talent_ranked('Terrinoth', talent):
            root = tk.Toplevel(self)
            tk.Label(root, text="Rank").grid(row=0, column=0)
            selected_rank = tk.IntVar(root)
            avail_ranks = ("Select a rank", 1, 2, 3, 4, 5, 6)
            rank_options = ttk.OptionMenu(root, selected_rank, *avail_ranks, command=lambda rank=selected_rank:self.rank_selected(talent, rank))
            rank_options.grid(row=0, column=1)
        else:
            if not talent in current_talents:
                current_talents.append(talent)
                current_talents = sorted(current_talents)
            self.destroy()

    def rank_selected(self,talent, rank):
        global current_talents
        output = talent.split(":")[0] + " " + str(rank)
        current_talents.append(output)
        current_talents = sorted(current_talents)
        self.destroy()



class AbilityCreator(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        self.new_label = tk.Label(self, text="New Ability").grid(row=0, column=0, columnspan=2)
        self.ability_name_label = tk.Label(self, text="Name:").grid(row=1, column=0)
        self.ability_name_data = tk.Entry(self)
        self.ability_name_data.grid(row=1, column=1, sticky="ew")
        self.effect_label = tk.Label(self, text="Effect:").grid(row=2, column=0)
        self.effect_data = tk.Text(self, height=3, width=50)
        self.effect_data.grid(row=2, column=1)
        save_ability = tk.Button(self, text="Apply", command=self.save_ability_func).grid(row=3, column=1)


    def save_ability_func(self):
        ability_name = self.ability_name_data.get().title()
        ability_effect = self.effect_data.get("1.0", tk.END)
        output = ability_name + ": " + ability_effect

        global current_abilities
        # current_abilities = list(self.adver_abilities.get(0, tk.END))
        current_abilities.append(output)
        current_abilities.sort()

        self.destroy()


    # def edit_ability(self):
    #     index = self.adver_abilities.curselection()[0]
    #     def save_ability_func():
    #         ability_name = ability_name_data.get().title()
    #         ability_effect = effect_data.get("1.0", tk.END)
    #         output = ability_name + ": " + ability_effect
    #
    #         self.adver_abilities.delete(index)
    #
    #         current_abilities = list(self.adver_abilities.get(0, tk.END))
    #         current_abilities.append(output)
    #         current_abilities.sort()
    #         self.adver_abilities.delete(0, tk.END)
    #         for ability in current_abilities:
    #             self.adver_abilities.insert(tk.END, ability)
    #         root.destroy()
    #
    #     #Build window
    #     root = tk.Tk()
    #     new_label = tk.Label(root, text="New Ability").grid(row=0, column=0, columnspan=2)
    #     ability_name_label = tk.Label(root, text="Name:").grid(row=1, column=0)
    #     ability_name_data = tk.Entry(root)
    #     ability_name_data.grid(row=1, column=1, sticky="ew")
    #     effect_label = tk.Label(root, text="Effect:").grid(row=2, column=0)
    #     effect_data = tk.Text(root, height=3, width=50)
    #     effect_data.grid(row=2, column=1)
    #     save_ability = tk.Button(root, text="Save Changes", command=save_ability_func).grid(row=3, column=1)
    #
    #     #Populate data
    #     ability_data = self.adver_abilities.get(index) # Muffin Man: Makes all the muffins.
    #     ability_name_input = ability_data.split(":")[0]
    #     ability_effect_input = ability_data.split(":")[1][1:]
    #     ability_name_data.insert(tk.END, ability_name_input)
    #     effect_data.insert(tk.END, ability_effect_input)

class EquipmentEditor(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        self.type_label = tk.Label(self, text= "Type:")
        self.type_label.grid(row=0, column=0)

        equipment_types = ["Weapon", "Weapon"]
        selected_equip_type = tk.StringVar(self)
        self.equip_type_menu = ttk.OptionMenu(self, selected_equip_type, *equipment_types, command=lambda x:self.type_change(selected_equip_type.get()))
        self.equip_type_menu.grid(row=0, column=1, sticky="w")

        # Item Name
        self.item_name_label = tk.Label(self, text="Name:")
        self.item_name_label.grid(row=1, column=0)
        self.item_name_text = tk.Entry(self)
        self.item_name_text.grid(row=1, column=1, sticky="ew")

        # Gear options
        self.gear_label = tk.Label(self, text="Effect:")
        self.gear_description = tk.Text(self, height=6, width=50)

        # Weapon Skill
        self.weapon_skill_label = tk.Label(self, text="Skill:")
        self.weapon_skill_label.grid(row=1, column=3)
        selected_skill = tk.StringVar(self)
        fetched_skills = database.fetch_skills()
        fetched_skills = sorted(fetched_skills)
        skills = []
        skills.append("Select a skill")
        for skill in fetched_skills:
            skills.append(skill)
        self.skill_menu = ttk.OptionMenu(self, selected_skill, *skills)
        self.skill_menu.grid(row=1, column=4)

        # Damage
        self.dam_warn_label = tk.Label(self, text="*Remember, damage should be the final value. If a sword adds +3 and the adversary has 2 brawn, the damage is 5 not 3.", wraplength=500, justify="left")
        self.dam_warn_label.grid(row=2, column=0, columnspan=5)
        self.damage_label = tk.Label(self, text="Damage:")
        self.damage_label.grid(row=3, column=0)
        self.damage_data = tk.Entry(self, width=2)
        self.damage_data.grid(row=3, column=1)

        # Critical
        self.critical_label = tk.Label(self, text="Critical:")
        self.critical_label.grid(row=4, column=0)
        self.critical_data = tk.Entry(self, width=2)
        self.critical_data.grid(row=4, column=1)

        # Range
        self.range_label = tk.Label(self, text="Range:")
        self.range_label.grid(row=5, column=0)
        self.selected_range = tk.StringVar(self)
        range_bands = ["Select a range", "Engaged", "Short", "Medium", "Long", "Extreme", "Strategic"]
        self.range_data = ttk.OptionMenu(self, self.selected_range, *range_bands)
        self.range_data.grid(row=5, column=1)

        # Qualities
        self.qualities_label = tk.Label(self, text="Qualities:")
        self.qualities_label.grid(row=6, column=0)
        self.qualities_list = tk.Listbox(self, width=50, height=6)
        self.qualities_list.grid(row=6, column=1, rowspan=3, columnspan=2)
        self.qualities_sby = tk.Scrollbar(self)
        self.qualities_sby.grid(row=6, column=3, rowspan=3, sticky="ns")
        self.qualities_list.configure(yscrollcommand=self.qualities_sby.set)
        self.qualities_sby.configure(command=self.qualities_list.yview)

        self.selected_quality = tk.StringVar(self)
        qualities = []
        full_fetched_qualities = database.fetch_item_qualities()
        for ffq_name, ffq_active, ffq_descr, ffq_ranked in full_fetched_qualities:
            qualities.append(ffq_name)
        self.add_quality = tk.Menubutton(self, text="Add quality", indicatoron=True)
        self.quality_menu = tk.Menu(self.add_quality, tearoff=False)
        self.add_quality.configure(menu=self.quality_menu)
        for quality in qualities:
            self.quality_menu.add_radiobutton(label=quality, variable=self.selected_quality, value=quality, command=lambda:self.quality_changed(self.selected_quality.get(), self.qualities_list, list(self.qualities_list.get(0, tk.END))), indicatoron=False)
        self.add_quality.grid(row=6, column=4)

        self.remove_quality = ttk.Button(self, text="Remove", command=lambda:self.remove_quality_func(self.qualities_list))
        self.remove_quality.grid(row=7, column=4)

        self.add_weapon = ttk.Button(self, text="Apply", command=lambda:self.save_weapon(self.item_name_text.get().title(), selected_skill.get(), self.damage_data.get(), self.critical_data.get(), self.selected_range.get(), list(self.qualities_list.get(0, tk.END))))
        self.add_gear = ttk.Button(self, text="Apply", command=lambda:self.save_gear(self.item_name_text.get().title(), self.gear_description.get("1.0", tk.END)))
        self.add_weapon.grid(row=9, column=1)

    def type_change(self, type):
        if type == 'Weapon':
            self.gear_label.grid_forget()
            self.gear_description.grid_forget()
            self.add_gear.grid_forget()

            # Weapon Skill
            self.weapon_skill_label.grid(row=1, column=3)
            self.skill_menu.grid(row=1, column=4)

            # Damage
            self.dam_warn_label.grid(row=2, column=0, columnspan=5)
            self.damage_label.grid(row=3, column=0)
            self.damage_data.grid(row=3, column=1)

            # Critical
            self.critical_label.grid(row=4, column=0)
            self.critical_data.grid(row=4, column=1)

            # Range
            self.range_label.grid(row=5, column=0)
            self.range_data.grid(row=5, column=1)

            # Qualities
            self.qualities_label.grid(row=6, column=0)
            self.qualities_list.grid(row=6, column=1, rowspan=3, columnspan=2)
            self.qualities_sby.grid(row=6, column=3, rowspan=3, sticky="ns")
            self.add_quality.grid(row=6, column=4)
            self.remove_quality.grid(row=7, column=4)
        elif type == 'Gear':

            # clear weapon options
            self.weapon_skill_label.grid_forget()
            self.skill_menu.grid_forget()
            self.dam_warn_label.grid_forget()
            self.damage_label.grid_forget()
            self.damage_data.grid_forget()
            self.critical_label.grid_forget()
            self.critical_data.grid_forget()
            self.range_label.grid_forget()
            self.range_data.grid_forget()
            self.qualities_label.grid_forget()
            self.qualities_list.grid_forget()
            self.qualities_sby.grid_forget()
            self.add_quality.grid_forget()
            self.remove_quality.grid_forget()
            self.add_weapon.grid_forget()

            # establish gear grid
            self.gear_label.grid(row=2, column=0)
            self.gear_description.grid(row=2, column=1)
            self.add_gear.grid(row=3, column=1)

    def save_weapon(self, name, skill, damage, crit, rng, q_list):
        name_present = 0
        skill_present = 0
        rng_present = 0
        if not name:
            messagebox.showwarning("No name entered","A name has not been entered. Enter a name before continuing.")
        else:
            name_present = 1

        if skill == "Select a skill":
            messagebox.showwarning("No skill selected","A skill has not been selected. Select a skill before continuing.")
        else:
            skill_present = 1

        if not damage:
            damage = "0"

        if not crit:
            crit = "0"

        if rng == "Select a range":
            messagebox.showwarning("No range selected","A range has not been selected. Select a range before continuing.")
        else:
            rng_present = 1

        if name_present and skill_present and rng_present:
            # clear values
            name_present = 0
            skill_present = 0
            rng_present = 0

            if q_list:
                output = name + " (" + skill + "; Damage " + damage + "; Critical " + crit + "; Range [" + rng + "]; "
                if len(q_list) > 1:
                    for quality in q_list[:-1]:
                        output = output + quality + ", "
                    else:
                        output = output + q_list[-1] + ")"
                else:
                    output = output + q_list[-1] + ")"
            else:
                output = name + " (" + skill + "; Damage " + damage + "; Critical " + crit + "; Range [" + rng + "])"

            output += " (Weapon)"
            global item_to_add
            item_to_add = (output, 'Weapon')
            self.destroy()

    def save_gear(self, name, effect):
        global item_to_add
        output = name + " (%s)" % effect + " (Gear)"
        item_to_add = (output, 'Gear')
        self.destroy()

    def quality_changed(self, q, q_list, cur_list):
        def rank_selected(event):
            q_rank = selected_rank.get()
            root.destroy()

            full_quality = q + " " + str(q_rank)

            cur_list.append(full_quality)
            sorted_list = sorted(cur_list)
            q_list.delete(0, tk.END)
            for quality in sorted_list:
                q_list.insert(tk.END, quality)

        if q in str(q_list.get(0, tk.END)):
            pass
        else:
            if not database.is_quality_ranked(q):
                cur_list.append(q)
                sorted_list = sorted(cur_list)
                q_list.delete(0, tk.END)
                for quality in sorted_list:
                    q_list.insert(tk.END, quality)
            else:
                root = tk.Toplevel(self)
                tk.Label(root, text='Rank').grid(row=0, column=0)
                selected_rank = tk.IntVar(root)
                avail_ranks = ('Select a rank', 1, 2, 3, 4, 5)
                rank_options = ttk.OptionMenu(root, selected_rank, *avail_ranks, command=rank_selected)
                rank_options.grid(row=0, column=1)

    def remove_quality_func(self, q_list):
        # TODO: Maybe add exception for if nothing is selected
        index = q_list.curselection()[0]
        q_list.delete(index)

    # def edit_equipment(self):
    #     item_index = self.adver_equipment.curselection()[0]
    #     def test_print():
    #         print("Yup, that's a button.")
    #
    #     def type_change(type):
    #         print("You've selected: " + type)
    #
    #     def test_equipment(q_list):
    #         print(q_list[:-1])
    #
    #     def save_equipment(name, skill, damage, crit, rng, q_list):
    #         # TODO: Force data types
    #         # TODO: Warning if missing required data
    #         print("Current equipment list is: " + str(self.equipment_list))
    #
    #         if q_list:
    #             output = name + " (" + skill + "; Damage " + damage + "; Critical " + crit + "; Range [" + rng + "]; "
    #             if len(q_list) > 1:
    #                 for quality in q_list[:-1]:
    #                     output = output + quality + ", "
    #                 else:
    #                     output = output + q_list[-1] + ")"
    #             else:
    #                 output = output + q_list[-1] + ")"
    #         else:
    #             output = name + " (" + skill + "; Damage " + damage + "; Critical " + crit + "; Range [" + rng + "])"
    #
    #         # Sort and add equipment
    #         del self.equipment_list[item_index]
    #
    #         print("Current equipment list, after deleting index is: " + str(self.equipment_list))
    #         self.equipment_list.append(output)
    #         self.equipment_list.sort()
    #         print("Current equipment list, after sorting is: " + str(self.equipment_list))
    #         self.adver_equipment.delete(0, tk.END)
    #         for item in self.equipment_list:
    #             self.adver_equipment.insert(tk.END, item)
    #
    #         root.destroy()
    #
    #
    #     def quality_changed(q, q_list, cur_list):
    #         if q in q_list.get(0, tk.END):
    #             pass
    #         else:
    #             cur_list.append(q)
    #             sorted_list = sorted(cur_list)
    #             q_list.delete(0, tk.END)
    #             for quality in sorted_list:
    #                 q_list.insert(tk.END, quality)
    #
    #     def remove_quality_func(q_list):
    #         # TODO: Maybe add exception for if nothing is selected
    #         index = q_list.curselection()[0]
    #         q_list.delete(index)
    #
    #     # TODO: Check for other item types and pull data for those
    #     # Pull weapon data
    #     # Seeker Sword (Melee(Light); Damage 6; Critcial 2; Range [Engaged]; Defensive, Accurate)
    #
    #     item_data = self.adver_equipment.get(item_index).split(";") # ['Seeker Sword (Melee(Light)', 'Damage 6', 'Critical 2', 'Range [Engaged]', 'Defensive, Accurate)']
    #     weapon_name_skill = item_data[0].split("(") # ['Seeker Sword ','Melee', 'Light)']
    #     weapon_name = weapon_name_skill[0][:-1] # 'Seeker Sword'
    #     if len(weapon_name_skill) > 2:
    #         weapon_skill = weapon_name_skill[1] + "(" + weapon_name_skill[2] # Melee(Light)
    #     else:
    #         weapon_skill = weapon_name_skill[1] # Ranged for example
    #     weapon_damage = item_data[1].split(" ")[2] # Damage 6 --> 6
    #     weapon_critical = item_data[2].split(" ")[2] # Critical 2 --> 2
    #     weapon_range_brackets = item_data[3].split(" ")[2] # Range [Engaged] --> [Engaged]
    #     weapon_range = ""
    #     weapon_qualities = []
    #     if len(item_data) > 4:
    #         weapon_range = weapon_range_brackets[1:-1] # Engaged
    #         if "," in item_data[4]:
    #             weapon_qualities_rough = item_data[4].split(",") # [' Accurate', ' Defensive)']
    #             if len(weapon_qualities_rough) > 1:
    #                 for item in weapon_qualities_rough[:-1]:
    #                     weapon_qualities.append(item[1:])
    #                 else:
    #                     weapon_qualities.append(weapon_qualities_rough[-1][1:-1])
    #         else:
    #             weapon_range = weapon_range_brackets[1:-2] # Engaged
    #             weapon_qualities.append(item_data[4][1:-1])
    #             weapon_qualities = weapon_qualities[0]
    #
    #     print(item_data)
    #     print(weapon_name_skill)
    #     print("Weapon name: " + weapon_name)
    #     print("Weapon skill: " + weapon_skill)
    #     print("Weapon damage: " + weapon_damage)
    #     print("Weapon critical: " + weapon_critical)
    #     print("Weapon range: " + weapon_range)
    #     if weapon_qualities:
    #         print("Weapon Qualities: " + str(weapon_qualities))
    #
    #     # Build window
    #     root = tk.Tk()
    #
    #     type_label = tk.Label(root, text= "Type:")
    #     type_label.grid(row=0, column=0)
    #
    #     # TODO change layout and options on type selection
    #     equipment_types = ["Armor", "Gear", "Weapon"]
    #     selected_equip_type = tk.StringVar(root)
    #     selected_equip_type.set("Weapon") # TODO: Weapon is bruteforced, need to pull procedurally
    #     equip_type_menu = tk.OptionMenu(root, selected_equip_type, *equipment_types, command=lambda x:type_change(selected_equip_type.get()))
    #     equip_type_menu.grid(row=0, column=1)
    #
    #     # Weapon Name
    #     weapon_name_label = tk.Label(root, text="Name:")
    #     weapon_name_label.grid(row=1, column=0)
    #     weapon_name_text = tk.Entry(root)
    #     weapon_name_text.grid(row=1, column=1)
    #
    #     # Weapon Skill
    #     weapon_skill_label = tk.Label(root, text="Skill:")
    #     weapon_skill_label.grid(row=1, column=3)
    #     selected_skill = tk.StringVar(root)
    #     selected_skill.set(weapon_skill)
    #     skills = database.fetch_skills()
    #     skills = sorted(skills)
    #     skill_menu = tk.OptionMenu(root, selected_skill, *skills)
    #     skill_menu.grid(row=1, column=4)
    #
    #     # Damage
    #     dam_warn_label = tk.Label(root, text="*Remember, damage should be the final value. If a sword adds +3 and the adversary has 2 brawn, the damage is 5 not 3.", wraplength=500, justify="left")
    #     dam_warn_label.grid(row=2, column=0, columnspan=5)
    #     damage_label = tk.Label(root, text="Damage:")
    #     damage_label.grid(row=3, column=0)
    #     damage_data = tk.Entry(root, width=2)
    #     damage_data.grid(row=3, column=1)
    #
    #     # Critical
    #     critical_label = tk.Label(root, text="Critical:")
    #     critical_label.grid(row=4, column=0)
    #     critical_data = tk.Entry(root, width=2)
    #     critical_data.grid(row=4, column=1)
    #
    #     # Range
    #     range_label = tk.Label(root, text="Range:")
    #     range_label.grid(row=5, column=0)
    #     selected_range = tk.StringVar(root)
    #     selected_range.set(weapon_range)
    #     range_bands = ["Engaged", "Short", "Medium", "Long", "Extreme", "Strategic"]
    #     range_data = tk.OptionMenu(root, selected_range, *range_bands)
    #     range_data.grid(row=5, column=1)
    #
    #     # Qualities
    #     qualities_label = tk.Label(root, text="Qualities:")
    #     qualities_label.grid(row=6, column=0)
    #     qualities_list = tk.Listbox(root, width=30, height=3)
    #     qualities_list.grid(row=6, column=1, rowspan=3, columnspan=2)
    #     qualities_sby = tk.Scrollbar(root)
    #     qualities_sby.grid(row=6, column=3, rowspan=3, sticky="ns")
    #     qualities_list.configure(yscrollcommand=qualities_sby.set)
    #     qualities_sby.configure(command=qualities_list.yview)
    #
    #     selected_quality = tk.StringVar(root)
    #     # TODO: Qualities are bruteforced, they should pull from a DB
    #     qualities = ['Accurate', 'Defensive']
    #     add_quality = tk.Menubutton(root, text="Add quality", indicatoron=True)
    #     quality_menu = tk.Menu(add_quality, tearoff=False)
    #     add_quality.configure(menu=quality_menu)
    #     for quality in qualities:
    #         quality_menu.add_radiobutton(label=quality, variable=selected_quality, value=quality, command=lambda:quality_changed(selected_quality.get(), qualities_list, list(qualities_list.get(0, tk.END))), indicatoron=False)
    #     add_quality.grid(row=6, column=4)
    #
    #     remove_quality = tk.Button(root, text="Remove", command=lambda:remove_quality_func(qualities_list))
    #     remove_quality.grid(row=7, column=4)
    #
    #     add_item = tk.Button(root, text="Save Changes", command=lambda:save_equipment(weapon_name_text.get().title(), selected_skill.get(), damage_data.get(), critical_data.get(), selected_range.get(), list(qualities_list.get(0, tk.END))))
    #     add_item.grid(row=9, column=1)
    #
    #     # Populate remaining data
    #     weapon_name_text.insert(tk.END, weapon_name)
    #
    #     damage_data.insert(tk.END, weapon_damage)
    #     critical_data.insert(tk.END, weapon_critical)
    #     if weapon_qualities:
    #         if type(weapon_qualities) is list:
    #             for quality in weapon_qualities:
    #                 qualities_list.insert(tk.END, quality)
    #         else:
    #             qualities_list.insert(tk.END, weapon_qualities)
    #
    #
    #     root.mainloop()
