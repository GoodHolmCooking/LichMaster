import random
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

class CritRoller(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self)

        self.generate_crit_table()
        self.build_dice_mod_window()

    def generate_crit_table(self):
        self.critical_table = {}

        for i in range(1, 6):
            self.critical_table[i] = (1, "Minor Nick: The target suffers 1 strain")
        for i in range(6, 11):
            self.critical_table[i] = (1, "Slowed Down: The target can only act during the last allied Initiative slot on their next turn.")
        for i in range(11, 16):
            self.critical_table[i] = (1, "Sudden Jolt: The target drops whatever is in hand.")
        for i in range(16, 21):
            self.critical_table[i] = (1, "Distracted: The target cannot perfrom a free maneuver during their next turn.")
        for i in range(21, 26):
            self.critical_table[i] = (1, "Off-Balance: Add a Setback to the target's next skill check.")
        for i in range(26, 31):
            self.critical_table[i] = (1, "Discouraging Wound: Move one player pool Story Point to the Game Master pool (reverse if NPC).")
        for i in range(31, 36):
            self.critical_table[i] = (1, "Stunned: The target is staggered until the end of their next turn.")
        for i in range(36, 41):
            self.critical_table[i] = (1, "Stinger: Increase the difficulty of the target's next check by one.")
        for i in range(41, 46):
            self.critical_table[i] = (2, "Bowled Over: The target is knocked prone and suffers 1 strain.")
        for i in range(46, 51):
            self.critical_table[i] = (2, "Head Ringer: The target increases the difficulty of all Intellect and Cunning checks by one until this Critical Injury is healed.")
        for i in range(51, 56):
            self.critical_table[i] = (2, "Fearsome Wound: The target increases the difficulty of all Presence and Willpower checks by one until this Crtical Injury is healed.")
        for i in range(56, 61):
            self.critical_table[i] = (2, "Agonizing Wound: The target increases the difficulty of all Brawn and Agility checks by one until this Critical Injury is healed.")
        for i in range(61, 66):
            self.critical_table[i] = (2, "Slightly Dazed: The target is disoriented until this Critical Injury is healed.")
        for i in range(66, 71):
            self.critical_table[i] = (2, "Scattered Senses: The target removes all Boosts from skill checks until this Critical Injury is healed.")
        for i in range(71, 76):
            self.critical_table[i] = (2, "Hamstrung: The target loses their free maneuver until this Critical Injury is healed.")
        for i in range(76, 81):
            self.critical_table[i] = (2, "Overpowered: The target leaves themselves open, and the attacker may immediately attempt another attack against them as an incidental, using the exact same pool as the original attack")
        for i in range(81, 86):
            self.critical_table[i] = (2, "Winded: The target cannot voluntarily suffer strain to activate any abilities or gain additional maneuvers until this Critical Injury is healed.")
        for i in range(86, 91):
            self.critical_table[i] = (2, "Compromised: Increase the difficulty of all skill checks by one until this Critical Injury is healed.")
        for i in range(91, 96):
            self.critical_table[i] = (3, "At the Brink: The target suffers 2 strain each time they perform an action until this Critical Injuury is healed.")
        for i in range(96, 101):
            self.critical_table[i] = (3, "Crippled: One of the target's limbs (selected by the GM) is impaired until this Critical Injury is healed. Increase the difficulty of all checks that require use of that limb by one.")
        for i in range(101, 106):
            self.critical_table[i] = (3, "Maimed: One of the target's limbs (selected by the GM) is permanently lost. Unless the target has a cybernetic or prosthetic replacement, the target cannot perform actions that would require the use of that limb. All other actions gain a Setback until this Critical Injury is healed.")
        for i in range(106, 111):
            self.critical_table[i] = (3, "Horrific Injury: Roll 1d10 to determine which of the target's characteristics is affected: 1-3 for Brawn, 4-6 for Agility, 7 for Intellect, 8 for Cunning, 9 for Presence, 10 for Willpower. Until this Critical Injury is healed, treat that characteristic as one point lower.")
        for i in range(111, 116):
            self.critical_table[i] = (3, "Temporarily Disabled: The target is immobilized until this Critical Injury is healed.")
        for i in range(116, 121):
            self.critical_table[i] = (3, "Blinded: The target can no longer see. Upgrade the difficulty of all checks twice, and upgrade the difficulty of Perception and Vigilance checks three times, until this Critical Injury is healed.")
        for i in range(121, 126):
            self.critical_table[i] = (3, "Knocked Senseless: The target is staggered until this Critical Injury is healed")
        for i in range(126, 131):
            self.critical_table[i] = (4, "Gruesome Injury: Roll 1d10 to determine which of the target's characteristics is affected: 1-3 for Brawn, 4-6 for Agility, 7 for Intellect, 8 for Cunning, 9 for Presence, 10 for Willpower. That characteristic is permanently reduced by one to a minimum of 1.")
        for i in range(131, 141):
            self.critical_table[i] = (4, "Bleeding out: Until this Critical Injury is healed, every round, the target suffers 1 wound and 1 strain at the beginning of their turn. For every 5 wounds they suffer beyond their wound threshold, they suffer one additional Critical Injury. Roll on the chart, suffering the injury (if they suffer this result a second time due to this, roll again).")
        for i in range(141, 151):
            self.critical_table[i] = (4, "The End is Nigh: The target dies after the last Initiative slot during the next round unless this Critical Injury is healed.")
        self.critical_table[151] = (None, "Dead: Complete, obliterated death.")

    def build_dice_mod_window(self):
        self.label = tk.Label(self, text="Select a modifier").pack()
        self.selected_option = tk.StringVar(self)
        self.options = ['+0', '+0', '+10', '+20', '+30', '+40', '+50', '+60', '+70', '+80', '+90', '+100']
        self.mod_menu = ttk.OptionMenu(self, self.selected_option, *self.options)
        self.mod_menu.pack()
        self.confirm_btn = ttk.Button(self, text='Apply & Roll', command=self.roll_crit).pack()

    def roll_crit(self):
        mod = self.apply_dice_mod()
        self.produce_crit_result(mod)

    def apply_dice_mod(self):
        fetched_modifier = self.selected_option.get()
        self.destroy()
        converted_int = int(fetched_modifier[1:])
        return converted_int

    def produce_crit_result(self, mod):
        crit_result = self.critical_table[random.randint(1, 101) + mod]
        diff_index = crit_result[0]-1
        crit_description = crit_result[1]
        diff_options = ["Easy", "Average", "Hard", "Daunting"]
        crit_difficulty = diff_options[diff_index]
        messagebox.showinfo("Critical", "(%s) " % crit_difficulty + crit_description)
