import streamlit as st
import random

st.set_page_config(page_title="Dynamic D&D Engine", page_icon="⚔️", layout="wide")

# ==========================================
# 1. INITIALIZE GLOBAL ENGINE STATE
# ==========================================
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "player": {
            "name": "Eldrin",
            "class": "Rogue",
            "hp": 25,
            "max_hp": 25,
            "level": 1,
            "gold": 15,
            "stats": {"Strength": 10, "Dexterity": 16, "Constitution": 12, "Intelligence": 13, "Wisdom": 11, "Charisma": 14}
        },
        "inventory": ["Iron Dagger", "Leather Armor", "Rope (50ft)", "Health Potion"],
        "world": {
            "location": "The Whispering Caverns",
            "danger_level": "Medium",
            "current_scenario": "You stand before a massive, iron-reinforced wooden door deeply embedded into the cavern wall. Faint, rhythmic chanting echoes from behind it. To your right, a narrow, moss-covered crevice looks just wide enough to squeeze through. A broken spear lies shattered on the stone floor.",
            "consequence_log": ["Your adventure begins in the depths of the Whispering Caverns."]
        },
        "dice_history": []
    }

gs = st.session_state.game_state

# Helper function to modify stats/attributes safely
def log_event(message):
    gs["world"]["consequence_log"].insert(0, message)

# ==========================================
# 2. APP LAYOUT
# ==========================================
st.title("🎲 Interactive D&D World Sandbox")
st.caption("A fully mechanical text RPG framework running entirely in your browser.")

col_sidebar, col_main = st.columns([1, 2])

# ==========================================
# SIDEBAR: CHARACTER SHEET & DICE TRAY
# ==========================================
with col_sidebar:
    st.header("🛡️ Character Sheet")
    
    # Core Metadata
    st.subheader(f"{gs['player']['name']} the {gs['player']['class']}")
    st.write(f"**Level:** {gs['player']['level']}")
    st.metric(label="🪙 Gold Pieces", value=f"{gs['player']['gold']} gp")
    
    # HP Bar
    hp_pct = max(0.0, min(1.0, gs['player']['hp'] / gs['player']['max_hp']))
    st.progress(hp_pct, text=f"HP: {gs['player']['hp']} / {gs['player']['max_hp']}")
    
    # Attribute Scores
    st.markdown("### 📊 Attributes")
    stat_cols = st.columns(2)
    for idx, (stat, value) in enumerate(gs["player"]["stats"].items()):
        modifier = (value - 10) // 2
        mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
        stat_cols[idx % 2].markdown(f"**{stat}:** {value} `({mod_str})`")
        
    # Inventory Tracking
    st.markdown("### 🎒 Inventory")
    if gs["inventory"]:
        for item in gs["inventory"]:
            if st.button(f"🗑️ Drop {item}", key=f"drop_{item}", use_container_width=True):
                gs["inventory"].remove(item)
                log_event(f"You discarded {item} from your inventory.")
                st.rerun()
    else:
        st.info("Your pack is entirely empty.")
        
    # Interactive item finder
    new_item = st.text_input("✨ Forage / Find Item:", placeholder="e.g., Golden Key")
    if st.button("Add to Pack") and new_item:
        gs["inventory"].append(new_item)
        log_event(f"You acquired: {new_item}.")
        st.rerun()

    st.write("---")
    
    # Built-in Interactive Dice Tray
    st.markdown("### 🎲 The Dice Tray")
    dice_types = {"d4": 4, "d6": 6, "d8": 8, "d10": 10, "d12": 12, "d20": 20, "d100": 100}
    dice_cols = st.columns(3)
    
    for i, (dice_name, sides) in enumerate(dice_types.items()):
        if dice_cols[i % 3].button(f"Roll {dice_name}", use_container_width=True):
            roll = random.randint(1, sides)
            gs["dice_history"].insert(0, f"Rolled a {dice_name}: **{roll}**")
            
    if gs["dice_history"]:
        st.markdown(f"**Last Roll:** {gs['dice_history'][0]}")
        with st.expander("Roll History"):
            for h in gs["dice_history"]:
                st.write(h)

# ==========================================
# MAIN PANEL: CONTEXT, WORLD & CONSEQUENCES
# ==========================================
with col_main:
    st.header(f"📍 Location: {gs['world']['location']}")
    
    # Environment block
    st.info(gs["world"]["current_scenario"])
    
    st.subheader("⚡ Choose Your Action")
    st.write("Because this framework adapts to your decisions, select a mechanical approach below or type a custom action.")
    
    # Preset Mechanical Actions
    act_col1, act_col2, act_col3 = st.columns(3)
    
    with act_col1:
        if st.button("🚪 Force the Iron Door (STR Check)", use_container_width=True):
            roll = random.randint(1, 20)
            mod = (gs["player"]["stats"]["Strength"] - 10) // 2
            total = roll + mod
            if total >= 14:
                gs["world"]["current_scenario"] = "With a mighty heave, the iron door splinters open! You stumble into a brightly lit ritual chamber. Three cultists freeze mid-chant and draw their daggers!"
                gs["player"]["gold"] += 10
                log_event(f"Succeeded STR Check ({total}). Broke open the iron door, found 10gp on the floor.")
            else:
                damage = random.randint(2, 6)
                gs["player"]["hp"] -= damage
                log_event(f"Failed STR Check ({total}). The door didn't budge and you strained your shoulder for {damage} damage.")
            st.rerun()
            
    with act_col2:
        if st.button("🕳️ Squeeze via Crevice (DEX Check)", use_container_width=True):
            roll = random.randint(1, 20)
            mod = (gs["player"]["stats"]["Dexterity"] - 10) // 2
            total = roll + mod
            if total >= 12:
                gs["world"]["current_scenario"] = "Your nimble frame slips effortlessly through the damp mossy rocks. You bypass the heavy door entirely and find yourself on an elevated ledge overlooking a sleeping Ogre guard."
                if "Rope (50ft)" in gs["inventory"]:
                    st.toast("Your Rope might be useful here!")
                log_event(f"Succeeded DEX Check ({total}). Safely navigated the narrow rock crevice.")
            else:
                gs["world"]["current_scenario"] = "You get completely wedged halfway into the crack! As you frantically wiggle free, your armor scrapes loudly against the stone, alerting whatever is on the other side."
                log_event(f"Failed DEX Check ({total}). Got stuck and made a loud noise.")
            st.rerun()

    with act_col3:
        if st.button("🧪 Drink Health Potion", use_container_width=True):
            if "Health Potion" in gs["inventory"]:
                gs["inventory"].remove("Health Potion")
                heal = random.randint(4, 10)
                gs["player"]["hp"] = min(gs["player"]["max_hp"], gs["player"]["hp"] + heal)
                log_event(f"Drank a Health Potion and restored {heal} HP.")
            else:
                st.error("You don't have any Health Potions left!")
            st.rerun()

    # Custom Sandbox Action Form
    st.write("---")
    st.markdown("#### 💬 Freeform Sandbox Option")
    with st.form("sandbox_action"):
        custom_action = st.text_input("Describe exactly what you want to do with the environment:", 
                                     placeholder="e.g., I pick up the broken spear and use it to search the ceiling for traps.")
        submitted = st.form_submit_button("Execute Sandbox Action")
        
        if submitted and custom_action:
            # Simple simulation engine processing choices dynamically
            d20_check = random.randint(1, 20)
            
            if "spear" in custom_action.lower() and d20_check >= 8:
                gs["world"]["current_scenario"] = "Using the discarded shaft of the spear, you poke at a strange tile above. A heavy iron dart shoots down, shattering against the stone floor where you would have stepped! The path forward is safe."
                log_event(f"Custom Action Success ({d20_check}): Leveraged objects in the room to trigger a trap safely.")
            elif d20_check <= 5:
                loss = random.randint(3, 7)
                gs["player"]["hp"] -= loss
                gs["world"]["current_scenario"] = f"Your attempt to '{custom_action}' goes horribly awry as you misjudge your surroundings. A crumbling piece of the architecture falls onto you."
                log_event(f"Custom Action Blunder ({d20_check}): '{custom_action}' backfired, causing {loss} damage.")
            else:
                gs["world"]["current_scenario"] = f"You carefully execute: '{custom_action}'. The world shifts around your choice, revealing a dark stone staircase heading downward into complete blackness."
                log_event(f"Custom Action Evaluated ({d20_check}): Checked environment based on custom input.")
            st.rerun()

    # Dynamic Narrative & Consequence Log
    st.markdown("### 📜 Log of Realistic Consequences")
    for log in gs["world"]["consequence_log"]:
        st.write(f"> {log}")

    # Administrative Reset
    if st.button("🔄 Reset Universe"):
        st.session_state.clear()
        st.rerun()
