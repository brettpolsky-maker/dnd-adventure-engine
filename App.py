import streamlit as st
import random

st.set_page_config(page_title="D&D Campaign Engine v2", page_icon="🎲", layout="wide")

# ==========================================
# 1. CHARACTER DATABASE
# ==========================================
CHARACTERS = {
    "Valerie the Paladin": {
        "class": "Paladin",
        "hp": 30,
        "max_hp": 30,
        "gold": 25,
        "xp": 0,
        "level": 1,
        "hit_dice": 2,
        "in_combat": False,
        "primary_stat": "Strength",
        "stats": {"Strength": 16, "Dexterity": 10, "Constitution": 14, "Intelligence": 9, "Wisdom": 12, "Charisma": 14},
        "inventory": ["Longsword", "Plate Armor", "Holy Symbol", "Health Potion"],
        "avatar": "🛡️",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80"
    },
    "Eldrin the Rogue": {
        "class": "Rogue",
        "hp": 22,
        "max_hp": 22,
        "gold": 45,
        "xp": 0,
        "level": 1,
        "hit_dice": 2,
        "in_combat": False,
        "primary_stat": "Dexterity",
        "stats": {"Strength": 10, "Dexterity": 17, "Constitution": 12, "Intelligence": 13, "Wisdom": 11, "Charisma": 14},
        "inventory": ["Twin Daggers", "Leather Armor", "Thieves' Tools", "Smoke Bomb"],
        "avatar": "🗡️",
        "image_url": "https://images.unsplash.com/photo-1514539079130-25950c84af65?auto=format&fit=crop&w=400&q=80"
    },
    "Faelar the Wizard": {
        "class": "Wizard",
        "hp": 16,
        "max_hp": 16,
        "gold": 60,
        "xp": 0,
        "level": 1,
        "hit_dice": 2,
        "in_combat": False,
        "primary_stat": "Intelligence",
        "stats": {"Strength": 8, "Dexterity": 14, "Constitution": 11, "Intelligence": 18, "Wisdom": 13, "Charisma": 10},
        "inventory": ["Arcane Staff", "Spellbook", "Component Pouch", "Mana Elixir"],
        "avatar": "🔮",
        "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=400&q=80"
    },
    "Kaelen the Ranger": {
        "class": "Ranger",
        "hp": 24,
        "max_hp": 24,
        "gold": 20,
        "xp": 0,
        "level": 1,
        "hit_dice": 2,
        "in_combat": False,
        "primary_stat": "Wisdom",
        "stats": {"Strength": 12, "Dexterity": 15, "Constitution": 13, "Intelligence": 10, "Wisdom": 15, "Charisma": 9},
        "inventory": ["Longbow", "20 Arrows", "Hunting Trap", "Antitoxin"],
        "avatar": "🏹",
        "image_url": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=400&q=80"
    }
}

# ==========================================
# 2. INITIALIZE GLOBAL ENGINE STATE
# ==========================================
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "chosen_char": None,
        "player": {},
        "inventory": [],
        "world": {
            "location": "The Whispering Caverns",
            "current_scenario": "You stand before a massive, iron-reinforced wooden door deeply embedded into the cavern wall. Faint, rhythmic chanting echoes from behind it. To your right, a narrow, moss-covered crevice looks just wide enough to squeeze through. A broken spear lies shattered on the stone floor.",
            "consequence_log": ["Your adventure begins. Choose your approach wisely."]
        },
        "dice_history": [],
        "last_action_result": ""
    }

gs = st.session_state.game_state

def log_event(message):
    gs["world"]["consequence_log"].insert(0, message)

# ==========================================
# SCREEN A: CHARACTER SELECTION
# ==========================================
if gs["chosen_char"] is None:
    st.title("🎲 Choose Your Hero")
    st.write("Select your adventurer. Stats determine rolling modifiers, and XP allows you to level up!")
    
    char_cols = st.columns(4)
    for idx, (name, data) in enumerate(CHARACTERS.items()):
        with char_cols[idx]:
            st.image(data["image_url"], use_container_width=True)
            st.subheader(f"{data['avatar']} {name}")
            st.caption(f"Primary: **{data['primary_stat']}**")
            
            for stat, val in data["stats"].items():
                mod = (val - 10) // 2
                mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
                st.write(f"• **{stat}:** {val} `({mod_str})`")
                
            if st.button(f"Claim {data['class']}", key=f"select_{name}", use_container_width=True):
                gs["chosen_char"] = name
                # Safely rebuild configuration to isolate stat dictionaries per app run
                gs["player"] = {k: (v.copy() if isinstance(v, dict) else v) for k, v in data.items()}
                gs["inventory"] = data["inventory"].copy()
                log_event(f"{name} stepped into the dark caverns.")
                st.rerun()

# ==========================================
# SCREEN B: ACTIVE GAME INTERFACE
# ==========================================
else:
    if gs["player"]["hp"] <= 0:
        st.title("💀 Campaign Over")
        st.error(f"{gs['chosen_char']} has fallen in battle within {gs['world']['location']}.")
        if st.button("🔄 Restart Campaign from Beginning", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

    if gs["player"]["in_combat"]:
        st.error("⚔️ COMBAT MODE ENGAGED - Enemies have surrounded you!")
    else:
        st.title("🎲 Interactive D&D World Sandbox")

    col_sidebar, col_main = st.columns([1, 2])

    # SIDEBAR: ADVANCED CHARACTER SHEET
    with col_sidebar:
        st.header("🛡️ Character Status")
        st.image(gs["player"]["image_url"], width=130)
        st.subheader(gs["chosen_char"])
        st.write(f"**Level:** {gs['player']['level']}")
        
        xp_val = gs["player"]["xp"]
        st.progress(xp_val / 100, text=f"XP: {xp_val} / 100")
        
        hp_pct = max(0.0, min(1.0, gs['player']['hp'] / gs['player']['max_hp']))
        st.progress(hp_pct, text=f"HP: {gs['player']['hp']} / {gs['player']['max_hp']}")
        st.metric(label="🪙 Gold Pieces", value=f"{gs['player']['gold']} gp")
        
        st.markdown("### ⛺ Camp Mechanics")
        st.write(f"Hit Dice Left: **{gs['player']['hit_dice']}**")
        if gs["player"]["in_combat"]:
            st.button("⛺ Take a Short Rest", disabled=True, help="You cannot rest while in active combat!")
        else:
            if st.button("⛺ Take a Short Rest", use_container_width=True):
                if gs["player"]["hit_dice"] > 0:
                    gs["player"]["hit_dice"] -= 1
                    heal = random.randint(1, 8) + ((gs["player"]["stats"]["Constitution"] - 10) // 2)
                    heal = max(1, heal)
                    gs["player"]["hp"] = min(gs["player"]["max_hp"], gs["player"]["hp"] + heal)
                    st.toast(f"Regained {heal} HP from resting!", icon="❤️")
                    log_event(f"Took a short rest. Expended 1 Hit Die, recovered {heal} HP.")
                    st.rerun()
                else:
                    st.warning("You have no Hit Dice remaining. You must press forward.")

        st.markdown("### 📊 Attributes")
        stat_cols = st.columns(2)
        for idx, (stat, value) in enumerate(gs["player"]["stats"].items()):
            modifier = (value - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
            stat_cols[idx % 2].markdown(f"**{stat}:** {value} `({mod_str})`")
            
        st.markdown("### 🎒 Pack Space")
        if gs["inventory"]:
            cols = st.columns(2)
            for i, item in enumerate(gs["inventory"]):
                if cols[i % 2].button(f"🗑️ {item}", key=f"drop_{item}_{i}", use_container_width=True):
                    gs["inventory"].remove(item)
                    log_event(f"You threw away {item}.")
                    st.rerun()
        else:
            st.info("Your pack is empty.")

    # MAIN PANEL: STORY & MECHANICAL CHECKS
    with col_main:
        st.header(f"📍 Location: {gs['world']['location']}")
        st.info(gs["world"]["current_scenario"])
        
        if gs["last_action_result"]:
            st.markdown(gs["last_action_result"])
            st.write("---")

        st.subheader("⚡ Choose Your Approach")
        st.write("Type your intention below. Select the matching attribute modifier you want to exploit.")

        with st.form("sandbox_action"):
            custom_action = st.text_input("Describe your exact action:", placeholder="e.g., I ambush the cultists from the shadows.")
            selected_stat = st.selectbox("Which attribute modifier rolls this action?", list(gs["player"]["stats"].keys()))
            submitted = st.form_submit_button("🎲 Roll Check & Resolve")
            
            if submitted and custom_action:
                d20_roll = random.randint(1, 20)
                mod = (gs["player"]["stats"][selected_stat] - 10) // 2
                total_check = d20_roll + mod
                
                target_dc = 14 if gs["player"]["in_combat"] else 12
                success = total_check >= target_dc
                mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
                roll_summary = f"Rolled d20 ({d20_roll}) {mod_str} = **{total_check}** vs DC {target_dc}."
                
                if success:
                    xp_gained = random.randint(20, 35)
                    gold_gained = random.randint(5, 15)
                    gs["player"]["xp"] += xp_gained
                    gs["player"]["gold"] += gold_gained
                    
                    st.toast(f"✨ +{xp_gained} XP | 🪙 +{gold_gained} Gold!", icon="💰")
                    
                    if gs["player"]["in_combat"]:
                        gs["player"]["in_combat"] = False
                        gs["world"]["current_scenario"] = "Through tactical cleverness, you break the enemy rank! The surviving monsters scatter back into the darkness, leaving behind a cleared passageway into a glistening underground lake chamber."
                        log_event(f"Won combat check via {selected_stat} ({total_check}). Encounter cleared.")
                    else:
                        if "door" in custom_action.lower():
                            gs["world"]["current_scenario"] = "Your action shatters the doorway completely. You enter an ancient ritual sanctum. An intricate chest glowing with blue runes sits untouched at an altar ahead."
                        else:
                            gs["world"]["current_scenario"] = "Your calculated action completely pays off. You alter the environment in your favor, discovering a carved stone stairwell slipping downwards into a deeper cavern level."
                        log_event(f"Successful non-combat room exploration via {selected_stat} ({total_check}).")
                    
                    if gs["player"]["xp"] >= 100:
                        gs["player"]["level"] += 1
                        gs["player"]["max_hp"] += 6
                        gs["player"]["hp"] = gs["player"]["max_hp"]
                        gs["player"]["hit_dice"] += 1
                        gs["player"]["xp"] -= 100
                        p_stat = gs["player"]["primary_stat"]
                        gs["player"]["stats"][p_stat] += 2
                        st.balloons()
                        st.toast("🦅 LEVEL UP! Maximum health increased and primary stat grew!", icon="✨")
                    
                    gs["last_action_result"] = f"🟢 **Success!** {roll_summary}\n\nYou effectively accomplish: *\"{custom_action}\"*."
                
                else:
                    damage_taken = random.randint(4, 9)
                    gs["player"]["hp"] -= damage_taken
                    st.toast(f"💥 Damage Taken: -{damage_taken} HP!", icon="🩸")
                    
                    if gs["player"]["in_combat"]:
                        gs["world"]["current_scenario"] = f"The adversary deflects your advance! You get driven backward onto the hard stone floor, sustaining {damage_taken} damage as the enemy combatants close their perimeter tighter."
                        log_event(f"Failed combat strike via {selected_stat} ({total_check}). Took {damage_taken} damage.")
                    else:
                        gs["player"]["in_combat"] = True
                        gs["world"]["current_scenario"] = f"Your execution of *\"{custom_action}\"* goes totally sideways, making an immense noise and stumbling straight into an active ambush party! Dark figures emerge from behind the stalagmites with weapons drawn."
                        log_event(f"Blundered exploration check ({total_check}). Alerted nearby denizens and entered Combat.")
                    
                    gs["last_action_result"] = f"🔴 **Failure!** {roll_summary}\n\nYour attempt to *\"{custom_action}\"* breaks apart with negative consequences."
                
                st.rerun()

    st.write("---")
    if st.button("🔄 Abandon Progress & Change Hero"):
        st.session_state.clear()
        st.rerun()
