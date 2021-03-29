import sqlite3
import os.path
from tkinter import messagebox

def establish_master():
    master_exist = os.path.isfile('Master')
    if not master_exist:
        conn = sqlite3.connect('master')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS settings (setting varchar(30) PRIMARY KEY)")
        # Establish standard
        cur.execute("INSERT INTO settings VALUES ('Terrinoth')")

        #Quality Descriptions
        cur.execute("CREATE TABLE IF NOT EXISTS quality_descriptions (item_quality varchar(20) PRIMARY KEY, active boolean, quality_descr text, ranked boolean)")
        cur.execute("INSERT INTO quality_descriptions (item_quality, active, quality_descr, ranked) VALUES ('Accurate', 0, 'For each level of this quality, the attacker adds BOOST to their combat checks while using this weapon.', 1), ('Auto-Fire', 1, 'Increase difficulty of combat check by 1. If attack hits, spend 2 Advantage to trigger. Can be triggered multiple times. If targeting multiple targets, use the difficulty of the hardest adversary.', 0), ('Blast', 1, 'If successful, each character engaged with the target suffers normal damage. (If the hit misses, spend 3 Advantage to deal Blast rating damage only to all characters engaged with the target, including the original target).', 1), ('Breach', 0, 'Ignore 1 point of vehicle/structure armor per breach rating (ignores 10 soak).', 1), ('Burn', 1, 'When triggered, target receives weapon''s base damage each round equal to the Burn rating. Average Coordination check to stop burn.', 1), ('Concussive', 1, 'Target is Staggered for a number of rounds equal to the Concussive rating', 1), ('Cumbersome', 0, 'Requires Brawn rating greater than or equal to Cumbersome rating. +1 Difficulty to attacks for each point you are deficient.', 1), ('Defensive', 0, 'Increase wielder''s melee defense by Defensive rating.', 1), ('Deflective', 0, 'Increase the wielder''s ranged defense by Deflective rating.', 1), ('Disorient', 1, 'Target is disoriented for rounds equal to Disorient rating. Disoriented targets add a setback to all checks.', 1), ('Ensnare', 1, 'Target is immobilized for rounds equal to rating. Immobilized targets cannot take maneuvers. Hard Athletics check to break free.', 1), ('Guided', 1, 'Can only trigger if the attack misses; make an incidental Average combat check at the end of the round which you missed. Ability dice pool equal Guided rating', 1), ('Inaccurate', 0, 'Add Setback to attacks equal to Inaccurate rating', 1), ('Inferior', 0, 'Add Threat to all checks using this item.', 0), ('Knockdown', 1, 'Only requires a single Advantage to activate plus one advantage per silhouette over 1. Target is knocked prone.', 0), ('Limited Ammo', 0, 'May make a number of attacks equal to Limited Ammo Rating before requiring a maneuver to reload.', 1), ('Linked', 1, 'Spend to gain an additional hit. May trigger a number of times equal to Linked rating. Damage is equal to base damage + successes.', 1), ('Pierce', 0, 'On hit, ignore soak equal to Pierce rating.', 1), ('Prepare', 0, 'Spend a number of prepare maneuvers equal to the Prepare rating before using weapon.', 1), ('Reinforced', 0, 'Weapon is immune to Sunder. Armor is immune to both Pierce and Breach qualities.', 0), ('Slow-Firing', 0, 'Rating determines number of rounds between uses.', 1), ('Stun', 1, 'Inflicts strain eqaul to Stun rating (ignores Soak).', 1), ('Stun Damage', 0, 'Only deals Strain damage (Soak applies).', 1), ('Sunder', 1, 'Damages item 1 step per Advantage spent. Needs minimum 1 Advantage to activate.', 0), ('Superior', 0, 'Generates an Advantage on all checks related to use.', 0), ('Tractor', 0, 'On a successful attack with a tractor beam, target cannot move unless the pilot makes a Pilot check with difficulty equal to Tractor rating.', 1), ('Unwieldy', 0, 'Requires Agility greater than or equal to Unwieldy rating. +1 Difficulty to attacks for each point you are deficient.', 1), ('Vicious', 0, '+10 to Critical Injury rolls per rank in Vicious.', 1)")

        # Universal Skills
        cur.execute("CREATE TABLE IF NOT EXISTS skill_list (skill varchar(20) PRIMARY KEY, characteristic varchar(15), skill_type varchar(15))")
        cur.execute("INSERT INTO skill_list (skill, characteristic, skill_type) VALUES ('Athletics', 'Brawn', 'General'), ('Brawl', 'Brawn', 'Combat'), ('Charm', 'Presence', 'Social'), ('Coercion', 'Willpower', 'Social'), ('Cool', 'Presence', 'General'), ('Coordination', 'Agility', 'General'), ('Deception', 'Cunning', 'Willpower'), ('Discipline', 'Willpower', 'General'), ('Leadership', 'Presence', 'Social'), ('Mechanics', 'Intellect', 'General'), ('Medicine', 'Intellect', 'General'), ('Negotiation', 'Presence', 'Social'), ('Operating', 'Intellect', 'General'), ('Perception', 'Cunning', 'General'), ('Resilience', 'Brawn', 'General'), ('Skulduggery', 'Cunning', 'General'), ('Stealth', 'Agility', 'General'), ('Streetwise', 'Cunning', 'General'), ('Survival', 'Cunning', 'General'), ('Vigilance', 'Willpower', 'General')")

        # Universal Talent Descriptions
        cur.execute("CREATE TABLE IF NOT EXISTS talent_descriptions (talent_name varchar(30) PRIMARY KEY, ranked boolean, activation varchar(20), talent_descr text)")
        cur.execute("INSERT INTO talent_descriptions VALUES ('Apothecary', 0, 'Passive', 'When a patient under this character''s care heals wounds from natural rest, they heal additional wounds eequal to twice this character''s ranks in Apothecary.')")

        conn.commit()
        conn.close()

def fetch_settings():
    conn = sqlite3.connect('master')
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_univ_skills():
    conn = sqlite3.connect('master')
    cur = conn.cursor()
    cur.execute("SELECT * FROM skill_list")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_item_qualities():
    conn = sqlite3.connect('master')
    cur = conn.cursor()
    cur.execute("SELECT * FROM quality_descriptions")
    rows = cur.fetchall()
    conn.close()
    return rows

def establish_initial():
    # Terrinoth
    terrinoth_exist = os.path.isfile('Terrinoth')
    if not terrinoth_exist:

        conn = sqlite3.connect('Terrinoth')
        cur = conn.cursor()

        # Groups
        cur.execute("CREATE TABLE IF NOT EXISTS setting_groups (adver_grp varchar(30) PRIMARY KEY)")
        cur.execute("INSERT INTO setting_groups VALUES ('Uncategorized')")

        # Adversary Stats
        cur.execute("CREATE TABLE IF NOT EXISTS adversary_stats (adver_name varchar(30) PRIMARY KEY, adver_grp varchar(30), adver_type varchar(10), brawn smallint, agility smallint, intellect smallint, cunning smallint, willpower smallint, presence smallint, soak smallint, wound_thresh smallint, strain_thresh smallint, mel_def smallint, rng_def smallint)")

        # Minion skills
        cur.execute("CREATE TABLE IF NOT EXISTS minion_skills (adver_name varchar(30), skill varchar(20))")

        # Rival & Nemesis skills
        cur.execute("CREATE TABLE IF NOT EXISTS non_minion_skills (adver_name varchar(30), skill varchar(20), skill_rank smallint)")

        # Skills
        cur.execute("CREATE TABLE IF NOT EXISTS skill_list (skill varchar(20) PRIMARY KEY, characteristic varchar(15), skill_type varchar(15))")
        cur.execute("INSERT INTO skill_list (skill, characteristic, skill_type) VALUES ('Alchemy', 'Intellect', 'General'), ('Athletics', 'Brawn', 'General'), ('Cool', 'Presence', 'General'), ('Coordination', 'Presence', 'General'), ('Discipline', 'Willpower', 'General'), ('Mechanics', 'Intellect', 'General'), ('Medicine', 'Intellect', 'General'), ('Perception', 'Cunning', 'General'), ('Resilience', 'Brawn', 'General'), ('Riding', 'Agility', 'General'), ('Skulduggery', 'Cunning', 'General'), ('Stealth', 'Agility', 'General'), ('Streetwise', 'Cunning', 'General'), ('Survival', 'Cunning', 'General'), ('Vigilance', 'Willpower', 'General'), ('Arcana', 'Intellect', 'Magic'), ('Divine', 'Willpower', 'Magic'), ('Primal', 'Cunning', 'Magic'), ('Runes', 'Intellect', 'Magic'), ('Verse', 'Presence', 'Magic'), ('Brawl', 'Brawn', 'Combat'), ('Melee (Heavy)', 'Brawn', 'Combat'), ('Melee (Light)', 'Brawn', 'Combat'), ('Ranged', 'Agility', 'Combat'), ('Charm', 'Presence', 'Social'), ('Coercion', 'Willpower', 'Social'), ('Deception', 'Willpower', 'Social'), ('Leadership', 'Presence', 'Social'), ('Negotiation', 'Presence', 'Social'), ('Adventuring', 'Intellect', 'Knowledge'), ('Forbidden', 'Intellect', 'Knowledge'), ('Lore', 'Intellect', 'Knowledge'), ('Geography', 'Intellect', 'Knowledge')")

        #Adversary Talents
        cur.execute("CREATE TABLE IF NOT EXISTS adversary_talents (adver_name varchar(30), talent_name varchar(30), talent_rank smallint)")

        #Talent Descriptions
        cur.execute("CREATE TABLE IF NOT EXISTS talent_descriptions (talent_name varchar(30) PRIMARY KEY, ranked boolean, activation varchar(20), talent_descr text)")
        cur.execute("INSERT INTO talent_descriptions VALUES ('Apothecary', 0, 'Passive', 'When a patient under this character''s care heals wounds from natural rest, they heal additional wounds eequal to twice this character''s ranks in Apothecary.'), ('Bullrush', 0, 'Active (Incidental)', 'When this character makes a Brawl, Melee (Light), or Melee (Heavy) combat check after using a maneuver to engage a target, you may spend 3 Advantage or 1 Triumph to use this talent to knock the target prone and move them up to one range band away from your character.'), ('Challenge!', 1, 'Active (Maneuver)', 'Once per encounter, this character may use this talent to choose a number of characters within short range no greater than this character''s ranks in Challenge! Until the encounter ends or this character is incapacitated, these adversaries add a Boost to combat checks targeting this character and 2 Setback to combat checks targeting other characters.'), ('Clever Retort', 0, 'Active (Incidental, Out of Turn)', 'Once per encounter, this character may use this talent to add an automatic 2 Threat to another character''s social skill check.'), ('Swift', 0, 'Passive', 'This character does not suffer the penalties for moving throught difficulty terrain (they move throught difficult terrain at normal speed without spending additional maneuvers).'), ('Adversary', 1, 'Passive', 'Upgrade the difficulty of any combat check targeting this adversary by ranks in Adversary')")
        # ('Dark Insight', 0, 'When a spell adds a quality to this character''s spell with a rating determined by this character''s ranks in Knowledge (Lore), this character may use their ranks in Kowledge (Forbidden) instead.'),
        # ('Desperate Recovery', 0, 'Before this character heals strain at the end of an encounter, if their strain is more than half of their strain threshold, they heal two additional strain'),
        # ('Duelist', 1, 'This character adds a Boost to their melee combat checks while engaged with a single opponent. This character adds a Setback to their melee combat checks while engaged with three or more opponents.'),
        # ('Dungeoneer', 1, 'After this character makes a Perception, Vigilance, or Knowledge (Adventuring) check to notice, identify, or avoid a threat in a cavern, subterranean ruin, or similar location, this character cancels a number of uncanceled Threat no greater than this character''s ranks in Dungeoneer.'),
        # ('Durable', 1, 'This character reduces any Critical Injury result they suffer by 10 per rank of Durable, to a minimum of 01.'),
        # ('Finesse', 0, 'When making a Brawl or Melee (Light) check, your character may use Agility instead of Brawn.'),
        # ('Forager', 0, 'This character removes up to 2 Setback from any skill checks they make to find food, water, or shelter. Checks to forage or search the area that your character makes take half the time they would normally.'),
        # ('Grit', 1, 'Each rank of Grit increases your character''s strain threshold by one.'),
        # ('Hamstring Shot', 0, 'Once per round, this character may use this talent to perform a ranged combat check against one non-vehicle target within range of the weapon used. If the check is successful, halve the damage inflicted by the attack (before reducing damage by the target''s soak). The target is immobilized until the end of its next turn.'),
        # ('Jump Up', 0, 'Once per round during this character''s turn, this character may use this talent to stand from a prone or seated position as an incidental.'),
        # ('Knack For It', 1, 'Select one skill, this character removes 2 Setback from any checks they make using this skill. For each additional rank purchased in this talent, select two additional skills. This character also removes 2 Setback from any checks the make using these skills. Knack For It cannot be applied to Magic or Combat skills.'),
        # ('Know Somebody', 1, 'Once per session, when attempting to purchase a legally available item, this character may use this talent to reduce its rarity by one per rank of Know Somebody.'),
        # ('Let''s Ride', 0, 'Once per round during this character''s turn, this character can use this talent to mount or dismount from a vehicle or animal, or move from one posiiton in a vehicle to another (such as from the cokcpit to a gun turret) as an incidental). In addition, if your character suffers a short range fall from a vehicle or animal, they suffer no damage and land on their feet.'),
        # ('One with Nature', 0, 'When in the wilderness, this character may make a Simple Survival check, instead of Discipline or Cool, to recover strain at the end of an encounter.'),
        # ('Painful Blow', 0, 'When this character makes a combat check, you may voluntarily increase the difficulty by one to use this talent. If the target suffers one or more wounds from the combat check, the target suffers 2 strain each time they perform a maneuver until the end of the encounter.'),
        # ('Parry', 1, 'When this character suffers a hit from a melee combat check, after damage is calculated but before soak is applied, this character may suffer 3 strain to use this talent to reduce the damage of the hit by two plus their ranks in Parry. This talent can only be used once per hit, and this character needs to be wielding a Melee weapon.'),
        # ('Precision', 0, 'When making a Brawl or Ranged check, this character may use Cunning instead of Brawn or Agility.'),
        # ('Proper Upbringing', 1, 'When this character makes a social skill check in polite company, they may suffer a number of strain to use this talent to add an equal number of Advantage to the check. That number may not exceed this character''s ranks in Proper Upbringing.'),
        # ('Quick Draw', 0, 'Once per round on this character''s turn they may use this talent to draw or holster an easily accessbile weapon or item as an incidental. Quick Draw also reduces a weapon''s Prepare rating by one, to a minimum of one.'),
        # ('Quick Strike', 1, 'This character adds a Boost for each rank of Quick Strike to any combat checks they make against any targets that have not yet taken their turn in the current encounter.'),
        # ('Shapeshifter', 0, 'When this character is incapacitated due to having exceeded their strain threshold while in their normal form, they undergo the following changes as an out-of-turn incidental: they aheal all strain, increase their Brawn and Agility by one to a maximum of 5 and reduce their Intellect and Willpower by one to a minimum of 1. They deal +1 damage when making unarmed attacks and their unarmed attacks have a Critical rating of 3, but they cannot use magic skills or make ranged attacks. This character reverts to thier normal form after 8 hours or if they become incapacitated.'),
        # ('Shield Slam', 0, 'When this character uses a shield to attack a player, minion, or rival, you may spend 4 Advantage or a Triumph to stagger the target until the end of the target''s next turn.'),
        # ('Tavern Brawler', 0, 'This character adds an Advantage to Brawl checks and combat checks using improvised weapons.'),
        # ('Templar', 0, 'Divine is now a career skill for this character. They can only cast one spell using this skill per encounter.'),
        # ('Tumble', 0, 'Once per round on this character''s turn, they may suffer 2 strain to disengage from all engaged adversaries.'),
        # ('Rapid Reaction', 1, 'Your character may suffer a number of strain to use this talent to add an equal number of Successes to a Vigilance or Cool check they make to determine Initiative order. The number may not exceed this character''s ranks in Rapid Reaction.'),
        # ('Second Wind', 1, 'Once per encounter, this character may use this talent to heal an amount of strain equal to their ranks in Second Wind.'),
        # ('Surgeon', 1, 'When this character makes a Medicine check to heal wounds, the target heals one additional wound per rank of Surgeon.'),
        # ('Swift', 0, 'This character does not suffer the penalties for moving throught difficulty terrain (they move throught difficult terrain at normal speed without spending additional maneuvers).'),
        # ('Toughened', 1, 'Each rank of Toughened increases your character''s wound threshold by two.'),
        # ('Unremarkable', 0, 'Other characters add a Failure to any checks they make to find or identify your character in a crowd.'),
        # ('Berserk', 0, 'Once per encounter, this character may use this talent. Until the end of the encounter or until they are incapacitated, this character adds a Success and 2 Advantage to all melee combat checks they make. However, opponents add a Success to all combat checks targeting this character. While Berserk is active, this character cannot make ranged combat checks. At the ened of the encounter (or when they are incapacitated), this character suffers 6 strain.'),
        # ('Block', 0, 'While wielding a shield, this character may use the Parry talent to reduce damage from ranged attacks as well as melee attacks targeting this character.'),
        # ('Blood Sacrifice', 1, 'Before this character makes a magic skill check, they may suffer a number of wounds to use this talent to add an equal number of Successes to the check. The number cannot exceed this character''s ranks in Blood Sacrifice.'),
        # ('Bulwark', 0, 'While wielding a weapon with the Defensive quality, this character may use Parry to reduce the damage of an attack targeting an egaged ally.'),
        # ('Chill of Nordros', 0, 'Cannot be taken with Flames of Kellos. When casting an Attack spell, this character may add the Ice effect without increasing the difficulty. This character can never add the Fire effect.'),
        # ('Cooridnated Assault', 1, 'Once per turn this character may use this talent to have a number of allies engaged with this character equal to this character''s leadership add an Advantage to all combat checks they make until the end of this character''s next turn. The range of this talent increases by one range band per rank of Coordinated Assult beyond the first.'),
        # ('Counteroffer', 0, 'Once per session, this character may use this talent to choose one player or non-nemesis adversary within medium range and make an opposed Negotiation versus Discipline check. If successful, the target becomes staggered until the end of their next turn.'),
        # ('Defensive Stance', 1, 'Once per round, this character may suffer a number of strain no greater than their ranks in Defensive Stance to use this talent. Then, until the end of this character''s next turn, upgrade the difficulty of all melee combat checks targeting this character a number of times equal to the strain suffered.'),
        # ('Dirty Tricks', 0, 'After this character inflicts a Critical Injury on a target, they may use this talent to upgrade the difficulty of that target''s next check.'),
        # ('Dominion of the Dimora', 0, 'Cannot take with Favor of the Fae. When casting an Attack spell, this character may add the Impact effect without increasing the difficulty. This character can never add the Manipulative effect.'),
        # ('Dual Wielder', 0, 'Your character may use this talent, as a maneuver, to decrease the difficulty of the next combined combat check they make during the same turn by one.'),
        # ('Encouraging Song', 0, 'While equipped with a musical instrument, this character may use this talent to make an Average Charm or Verse check. For each Success the check generates, one ally within medium range adds a Boost to their next skill check. For each Advantage, one ally benefiting from Encouraging Song heals 1 strain.'),
        # ('Exploit', 0, 'When this character makes a combat check with a Ranged or Melee (Light) weapon, they may suffer 2 strain to use this talent to add the Ensnare quality to the attack. The rating of the Ensnare quality is equal to this character''s ranks in Exploit.'),
        # ('Favor of the Fae', 0, 'Cannot be taken with Dominion of the Dimora. When casting an Attack spell, this character may add the Manipulative effect without increasing the difficulty. This character can never add the Impact effect.'),
        # ('Flames of Kellos', 0, 'Cannot be taken with Chill of Nordros. When casting an Attack spell, this character may add the Fire effect without increasing difficulty. This character can never add the Ice effect.'),
        # ('Flash of Insight', 0, 'When this character generates a Triumph on a knowledge skill check, roll 2 Boost and add the results to the check in addtion to spending the Triumph as usual.'),
        # ('Grapple', 0, 'This character may suffer 2 strain to use this talent. Until the start of this character''s next turn, enemies must spend two maneuvers to disengage from this character.'),
        # ('Heightened Awareness', 0, 'Allies within short range of this character add a Boost to thier Perception and Vigilance checks. Allies engaged with this character add 2 Boost instead.'),
        # ('Heroic Recovery', 0, 'Choose one characteristic when picking this talent. Once per encounter, spend one Story Point to use this talent to have this character heal strain equal to the rating of the chosen characteristic.'),
        # ('Impaling Strike', 0, 'When this character inflicts a Critical Injury with a melee weapon, until the end of the target''s next turn they may use this talent to immobilize the target (in addition to the other effects of the Critical Injury).'),
        # ('Inspring Rhetoric', 0, 'This character may use this talent to make an Average Leadership check. For each Success the check generates, one ally within short range heals one strain. For each Advantage, one ally benefiting from Inspiring Rhetoric heals one additional strain.'),
        # ('Inventor', 1, 'When this character makes a check to construct new items or modify existing ones, use this talent to add a number of Boosts to the check equal to the ranks of Inventor. In addition, this character may attempt to reconstruct devices that they have heard described but have not seen and no not have any kind of plans or schematics for.'),
        # ('Lucky Strike', 0, 'When this talent is chosen, choose one characteristic. After this character makes a successful combat check, you may spend one Story Point to use this talent to add damage equal to this character''s rank in that characteristic to one hit of the combat check.'),
        # ('Natural Communion', 0, 'When this character uses the Conjure magic action, the spell gains the Summon Ally effect without increasing the difficulty. All creatures your character summons must be naturally occuring animals native to the area.'),
        # ('Reckless Charge', 0, 'After using a maneuver to engage an adversary, this character may suffer 2 strain to use this talent. They then add 2 Successes and 2 Threat to the results of the next Brawl, Melee (Light), or Melee (Heavy) combat check they make this turn.'),
        # ('Shapeshifter (Improved)', 0, 'Once per session, this character may make a Hard Discipline check as an out-of-turn incidental either to trigger Shapeshifter or to avoid triggering it when they exceed their strain threshold.'),
        # ('Templar (Improved)', 'When this character casts the single Divine spell per encounter granted by the Templar talent, they do not add a Setback for wearing heavy armor (armor with +2 soak or higher), using a shield, or having at least one hand free.'),
        # ('Threaten', 1, 'After an enemy within short range of this character resolves a combat check that deals damage to one of this character''s allies, your character may suffer 3 strain to use this talent to inflict a number of strain on the adversary equal to this character''s ranks in Coercion. The range of this talent increases by one band per rank of Threaten beyond the first.'),
        # ('Scathing Tirade', 0, 'This character may use this talent to make an Average Coercion check. For each Success the check generates, one enemy within short range suffers 1 strain. For each Advantage one enemy affected by Scathing Tirade suffers 1 additional strain.'),
        # ('Side Step', 1, 'Once per round this character may suffer a number of strain no greater than their ranks in Side Step to use this talent. Then, until the end of this character''s next turn, upgrade the difficulty of all ranged combat checks targeting this character a number of times equal to the strain suffered.'),
        # ('Wraithbane', 0, 'This character counts the Critical rating of their weapon as one lower to a minimum of 1 when making an attack targeting an undead adversary.'),
        # ('Backstab', 0, 'This character may use this talent to attack an unaware adversary using a Melee (Light) weapon. A Backstab is a melee attack, and follows the normal rules for performing a combat check using the character''s Skulduggery skill instead of Melee (Light). If the check succeeds, each uncanceled Success adds +2 damage (instead of the normal +1).'),
        # ('Battle Casting', 0, 'This character does not add a Setback to magic skill checks for wearing hevy armor (armor with +2 soak or higher), using a shield, or not having at least one hand free.'),
        # ('Body Guard', 1, 'Once per round, this character may suffer a number of strain no greater than their ranks in Body Guard to use this talent. Choose one ally engaged with this character until the end of this character''s next turn, upgrade the difficulty of all combat checks targeting that ally a number of times equal to the strain suffered.'),
        # ('Cavalier', 0, 'While riding a mount trained for battle (typically a war mount or a flying mount) once per round your character may use this talent to direct the mount to perform an action.'),
        # ('Counterattack', 0, 'When this character uses the Improved Parry talent to hit an attacker, they may also activate an item quality of the weapon they used as if they had generated 2 Advantage on a combat check using that weapon.'),
        # ('Dissonance', 0, 'While wielding a musical instrument, this character may use this talent to make an Average Charm or Verse check. For each Success the check generates, one enemy of the GM''s choosing within medium range suffers 1 wound. For each Advantage, one enemy affected by Dissonance suffers 1 additional wound.'),
        # ('Dodge', 1, 'When this character is targeted by a combat check (ranged or melee), they may suffer a number of strain no greater than their ranks in Dodge to use this talent. Then, upgrade the difficulty of the combat check targeting this character a number of times equal to the strain suffered.'),
        # ('Dual Strike', 0, 'When resolving a combined check to attack with two weapons in a melee combat, your character may suffer 2 strain to use this talent to hit with the secondary weapon (insead of spend 2 Advantage).'),
        # ")

        #Adversary Abilities
        cur.execute("CREATE TABLE IF NOT EXISTS adversary_abilities (adver_name varchar(30), ability_name varchar(30), ability_descr text)")

        #Adversary Equipment
        cur.execute("CREATE TABLE IF NOT EXISTS adversary_equipment (adver_name varchar(30), equip_name varchar(30), is_weapon boolean)")

        #Weapon Stats
        cur.execute("CREATE TABLE IF NOT EXISTS weapon_stats (equip_name varchar(30), skill varchar(20), damage smallint, critical smallint, weapon_rng varchar(10))")

        #Weapon Qualities
        cur.execute("CREATE TABLE IF NOT EXISTS weapon_qualities (equip_name varchar(30), item_quality varchar(20), q_rank smallint)")

        #Gear Descriptions
        cur.execute("CREATE TABLE IF NOT EXISTS gear_descriptions (equip_name varchar(30) PRIMARY KEY, gear_descr text)")

        # Campaign list
        cur.execute("CREATE TABLE IF NOT EXISTS campaigns (campaign varchar(50) PRIMARY KEY, active boolean)")

        # Campaign players
        cur.execute("CREATE TABLE IF NOT EXISTS campaign_players (campaign varchar(50), player varchar(30), mel_def smallint, rng_def smallint, presence smallint, willpower smallint, cool smallint, vigilance smallint, attending boolean)")

        # Campaign Sessions
        cur.execute("CREATE TABLE IF NOT EXISTS campaign_sessions (campaign varchar(50), session varchar(50), active boolean)")

        # Session encounters
        cur.execute("CREATE TABLE IF NOT EXISTS session_encounters (session varchar(50), encounter varchar(50), encounter_type varchar(10), active boolean)")

        # Encounter data
        cur.execute("CREATE TABLE IF NOT EXISTS encounter_data (encounter varchar(50), id smallint, adver_name varchar(30), adver_type varchar(10), amt_in_grp smallint)")

        # Encounter injuries
        cur.execute("CREATE TABLE IF NOT EXISTS encounter_injuries (encounter varchar(50), id smallint, adver_name varchar(30), injury text)")

        conn.commit()
        conn.close()

def view_table(db, table):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table)
    rows = cur.fetchall()
    conn.close()
    return(rows)

def fetch_skills():
    skills_tuple = view_table("Terrinoth", "skill_list")
    skills = []
    for a, b, c in skills_tuple:
        skills.append(a)
    return skills

def fetch_groups(db):
    results = view_table(db, 'setting_groups')
    return results

def fetch_talents(db):
    talent_tuple = view_table(db, 'talent_descriptions')
    talents = {}
    for name, ranked, act, descr in talent_tuple:
        talents[name] = descr
    return talents

def fetch_linked_char(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM skill_list WHERE skill = ?", (key,))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_adversaries():
    adversary_tuple = view_table("Terrinoth", "adversary_stats")
    if len(adversary_tuple) > 1:
        adversaries = []
        for adver_name, adver_grp, adver_type, brawn, agility, intellect, cunning, willpower, presence, soak, wound_thresh, strain_thresh, mel_def, rng_def in adversary_tuple:
            insert_value = adver_name + " (" + adver_type +"): " + adver_grp
            adversaries.append(insert_value)
    else:
        adver_name = adversary_tuple[0][0]
        adver_grp = adversary_tuple[0][1]
        adver_type = adversary_tuple[0][2]

        adversaries = adver_name + " (" + adver_type +"): " + adver_grp

    return adversaries

def fetch_adversary_stats(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM adversary_stats WHERE adver_name = ?", (key,))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_adversary_type(db, key):
    adver_type = fetch_adversary_stats(db, key)[0][2]
    return adver_type

def is_talent_ranked(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT ranked FROM talent_descriptions WHERE talent_name = ?", (key,))
    output = cur.fetchone()[0]
    conn.close()

    return output == 1

def fetch_adversary_skills(db, key):
    if fetch_adversary_type(db, key) == 'Minion':
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM minion_skills WHERE adver_name = ?", (key,))
        rows = cur.fetchall()
        conn.close()

        skill_list = []
        for name, skill in rows:
            skill_list.append(skill)
        return skill_list

    else:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM non_minion_skills WHERE adver_name = ?", (key,))
        rows = cur.fetchall()
        conn.close()

        skill_list = {}
        for name, skill, rank in rows:
            skill_list[skill] = rank

        return skill_list

def fetch_adversary_talents(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM adversary_talents WHERE adver_name = (?)", (key,))
    rows = cur.fetchall()

    # rows = [('Greyhaven Wizard', 'Adversary 1', 1)]
    # talent_list = []
    talent_dict = {}

    for name, talent, rank in rows:
        if is_talent_ranked(db, talent):
            t_output = talent + " " + str(rank)
        else:
            t_output = talent

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM talent_descriptions WHERE talent_name = (?)", (talent,))
        stats = cur.fetchall()
        conn.close()

        for t_name, t_ranked, t_activate, t_descr in stats:
            talent_dict[t_output] = (t_activate, t_descr)

    return talent_dict.items()

def fetch_adversary_abilities(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM adversary_abilities WHERE adver_name = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    ability_input = ""
    ability_list = []
    for name, ability, descr in rows:
        ability_input = ability + ": " + descr
        ability_list.append(ability_input)
    return ability_list

def fetch_adversary_equipment(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM adversary_equipment WHERE adver_name = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    # [('Reanimate', 'Rusted Sword', 1)]
    equipment_list = []
    for adver_name, equip_name, is_weapon in rows:
        item_stats = []

        if is_weapon:
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM weapon_stats WHERE equip_name = (?)", (equip_name,))
            rows = cur.fetchall()
            conn.close()

            # equip_name, skill, damage, critical, weapon_rng
            # [('Rusted Sword', 'Melee (Light)', 5, 2, 'Engaged')]
            item_stats.append(rows[0])

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM weapon_qualities WHERE equip_name = (?)", (equip_name,))
        rows = cur.fetchall()
        conn.close()
        # returns [] if no qualities
        if rows:
            # [('Dagger', 'Accurate')]
            quality_list =[]
            for item, quality, q_rank in rows:
                quality_list.append(quality)
            equipment_to_return = item_stats + quality_list
            equipment_list.append(equipment_to_return)
        else:
            equipment_list.append(item_stats)
    return(equipment_list)

def fetch_item(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM weapon_stats WHERE equip_name = (?)" + (key,))
    rows = cur.fetchall()
    conn.close()

    if rows:
        return True
    else:
        return False

def fetch_weapon_damage(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM weapon_stats WHERE equip_name = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    damage = rows[0][2]
    return damage

def fetch_weapon_crit(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM weapon_stats WHERE equip_name = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    critical = rows[0][3]
    return critical

def fetch_weapon_qualities(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM weapon_qualities WHERE equip_name = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    all_qualities = []

    for equipment, quality, rank in rows:
        if int(rank) > 0:
            output = quality + " " + str(rank)
        else:
            output = quality
        all_qualities.append(output)

    return(all_qualities)


def is_quality_active(quality):
    conn = sqlite3.connect('master')
    cur = conn.cursor()
    cur.execute("SELECT active FROM quality_descriptions WHERE item_quality = (?)", (quality,))
    result = cur.fetchone()[0]
    active = result == 1
    conn.close()
    return active

def is_quality_ranked(quality):
    conn = sqlite3.connect('master')
    cur = conn.cursor()
    cur.execute("SELECT ranked FROM quality_descriptions WHERE item_quality = (?)", (quality,))
    result = cur.fetchone()[0]
    ranked = result == 1
    conn.close()
    return ranked

def fetch_session_encounters(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM session_encounters WHERE session = (?)", (key,))
    rows = cur.fetchall()
    conn.close()
    encounter_list = []

    for session, encounter, encounter_type, active in rows:
        encounter_input = encounter + " (" + encounter_type + ")"
        encounter_list.append(encounter_input)

    return encounter_list

def does_encounter_exist(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM session_encounters WHERE encounter = (?)", (key,))
    encounter = cur.fetchone()
    conn.close()

    if encounter:
        return True
    else:
        return False

def fetch_session_type(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM session_encounters WHERE encounter = (?)", (key,))
    rows = cur.fetchall()
    conn.close()
    encounter_type = rows[0][2]
    return encounter_type

def fetch_campaign_sessions(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaign_sessions WHERE campaign = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    session_list = []
    for campaign, session, active in rows:
        session_list.append(session)

    return session_list

def fetch_encounter_data(db, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM encounter_data WHERE encounter = (?)", (key,))
    rows = cur.fetchall()
    conn.close()

    encounter_adversaries = []

    for encounter, id, adversary, adver_type, amt in rows:
        if adver_type == 'Minion': # 1-Reanimate x 3 (Minion)
            input = str(id) + "-" + adversary + " x " + str(amt) + " (Minion)"
            encounter_adversaries.append(input)
        else:
            input = str(id) + "-" + adversary + " x " + str(amt) + " (%s)" % adver_type
            encounter_adversaries.append(input)

    return encounter_adversaries

def fetch_prev_injuries(db, encounter, id):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM encounter_injuries WHERE encounter = ? AND id = ?", (encounter, id))
    rows = cur.fetchall()
    conn.close()

    injury_list = []

    for encounter, id, adver_name, injury in rows:
        injury_list.append(injury)

    return(injury_list)

def fetch_players(db, campaign):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaign_players WHERE campaign = (?)", (campaign,))
    rows = cur.fetchall()
    conn.close()
    name_list = {}
    for campaign, name, mel_def, rng_def, presence, willpower, cool, vigilance, attending in rows:
        name_list[name]=attending
    return name_list

def fetch_player_stats(db, campaign):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaign_players WHERE campaign = (?) AND attending = 1", (campaign,))
    rows = cur.fetchall()
    conn.close()
    stats = {}
    for campaign, name, mel_def, rng_def, presence, willpower, cool, vigilance, attending in rows:
        stats[name] = (mel_def, rng_def, presence, willpower, cool, vigilance)
    return stats

def switch_to_active(db, segment, key):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    if segment == 'campaign':
        cur.execute("UPDATE campaigns SET active = 0 WHERE active = 1")
        cur.execute("UPDATE campaigns SET active = 1 WHERE campaign = (?)", (key,))
    elif segment == 'session':
        cur.execute("UPDATE campaign_sessions SET active = 0 WHERE active = 1")
        cur.execute("UPDATE campaign_sessions SET active = 1 WHERE session = (?)", (key,))
    elif segment == 'encounter':
        cur.execute("UPDATE session_encounters SET active = 0 WHERE active = 1")
        cur.execute("UPDATE session_encounters SET active = 1 WHERE encounter = (?)", (key,))
    conn.commit()
    conn.close()

def fetch_active(db, segment, *campaign):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    if segment == 'campaign':
        cur.execute("SELECT * FROM campaigns WHERE active = 1")
        try:
            rows = cur.fetchall()[0][0]
        except IndexError:
            rows = ""
    if segment == 'session':
        cur.execute("SELECT * FROM campaign_sessions WHERE active = 1")
        rows = cur.fetchall()[0][1]
    if segment == 'encounter':
        cur.execute("SELECT * FROM session_encounters WHERE active = 1")
        rows = cur.fetchall()[0][1]
    if segment == 'players':
        cur.execute("SELECT * FROM campaign_players WHERE campaign = (?) AND attending = 1", (campaign[0],))
    conn.close()
    return rows

def delete_campaign(db, campaign):
    result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
    if result == 'yes':
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        # gather list of sessions
        cur.execute("SELECT * FROM campaign_sessions WHERE campaign = (?)", (campaign,))
        sessions = cur.fetchall()
        for session in sessions:
            # gather list of encounters
            cur.execute("SELECT * FROM session_encounters WHERE session = (?)", (session[1],))
            encounters = cur.fetchall()
            # clear encounters of data then delete
            for encounter in encounters:
                cur.execute("DELETE FROM encounter_data WHERE encounter = (?)", (encounter[1],))
                cur.execute("DELETE FROM session_encounters WHERE encounter = (?)", (encounter[1],))
            # delete sessions
            cur.execute("DELETE FROM campaign_sessions WHERE session = (?)", (session[1],))
        # gather list of players
        cur.execute("SELECT * FROM campaign_players WHERE campaign = (?)", (campaign,))
        players = cur.fetchall()
        # delete players
        for player in players:
            cur.execute("DELETE FROM campaign_players WHERE player = (?)", (player[1],))
        # finally remove campaign
        cur.execute("DELETE FROM campaigns WHERE campaign = (?)", (campaign,))
        conn.commit()
        conn.close()

establish_master()
establish_initial()

# Make manual changes
# conn = sqlite3.connect('db to edit')
# cur = conn.cursor()
# cur.execute("Code to execute")
# conn.commit()
# conn.close()
