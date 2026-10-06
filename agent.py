import re
import datetime
from typing import Dict, Any, Optional, Tuple, List
from database import (
    create_complaint,
    get_complaint,
    get_complaints,
    get_mess_menu,
    get_hostel_rules,
    get_staff_contacts
)

# In-memory session store for multi-turn dialogues
# session_id -> { "state": ..., "data": {}, "history": [] }
SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "state": "IDLE",
            "pending_data": {},
            "history": []
        }
    return SESSIONS[session_id]

def reset_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]

def classify_urgency(text: str) -> str:
    """
    Classifies a maintenance complaint into:
    - Urgent: fire, smoke, sparks, electrical board smoke, major flooding, gas leak
    - High: water leakage from ceiling/pipes, bathroom leakage, broken door lock, no water
    - Medium: fan not working, room light not working, socket dead, AC weak, furniture broken
    - Low: squeaky door, loose screw, paint chip, dustbin replacement, minor scratch
    """
    lower = text.lower()

    # 1. Urgent Indicators (Critical safety, fire, electrical hazard)
    urgent_keywords = [
        "smoke", "fire", "spark", "sparking", "flame", "burning", "electric shock",
        "explosion", "gas leak", "short circuit", "burst", "electrical board",
        "power board burning", "switchboard spark", "emergency"
    ]
    for kw in urgent_keywords:
        if kw in lower:
            return "Urgent"

    # 2. High Indicators (Active water damage, security breaches, essential utilities halted)
    high_keywords = [
        "water leakage", "water leak", "leaking from the ceiling", "leaking from ceiling",
        "leaking ceiling", "pipe burst", "flooding", "bathroom leak", "no water",
        "tap broken", "flush broken", "door lock broken", "broken lock", "cannot lock",
        "stuck inside", "water dripping from ceiling", "geyser leak", "water overflowing",
        "toilet overflowing", "main door broken", "window shattered"
    ]
    for kw in high_keywords:
        if kw in lower:
            return "High"

    # 3. Medium Indicators (Standard appliance/fixture breakdowns affecting daily convenience)
    medium_keywords = [
        "fan", "fan not working", "light not working", "room light", "tube light",
        "bulb", "switch", "socket", "plug", "ac not working", "ac cooling",
        "air conditioner", "study table", "chair broken", "bed broken",
        "mattress damaged", "wifi not working", "no internet", "lan port",
        "geyser not heating", "not working", "broken", "malfunction", "flickering"
    ]
    for kw in medium_keywords:
        if kw in lower:
            return "Medium"

    # 4. Low Indicators (Minor aesthetics, non-urgent comfort, requests)
    low_keywords = [
        "squeak", "squeaky", "hinge", "loose latch", "paint", "peeling",
        "dustbin", "trash can", "cobweb", "curtain", "curtain rod",
        "broom", "cleaning request", "slow drain", "mirror dirty", "door sticker"
    ]
    for kw in low_keywords:
        if kw in lower:
            return "Low"

    # Default baseline for complaints
    return "Medium"

def detect_category(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["water", "leak", "leakage", "tap", "pipe", "flush", "drain", "bathroom", "toilet", "washbasin", "shower", "geyser"]):
        return "Plumbing"
    if any(w in lower for w in ["fan", "light", "bulb", "tube", "switch", "socket", "wire", "power", "smoke", "spark", "electric", "board", "fuse"]):
        return "Electrical"
    if any(w in lower for w in ["door", "window", "lock", "key", "table", "chair", "bed", "cupboard", "wardrobe", "drawer", "hinge", "latch"]):
        return "Carpentry"
    if any(w in lower for w in ["clean", "dust", "dirt", "garbage", "trash", "dustbin", "cobweb", "cockroach", "pest", "insect"]):
        return "Cleanliness & Pest Control"
    if any(w in lower for w in ["wifi", "internet", "lan", "network", "router"]):
        return "Internet & Network"
    return "General Maintenance"

def extract_room_number(text: str) -> Optional[str]:
    # Matches patterns like: "room 205", "rm 205", "room no 205", "room no. 205", "room #205", "in room 501", "room 205B"
    patterns = [
        r'(?:room|rm)\s*(?:no\.?|number|#)?\s*([A-Za-z0-9\-]+)',
        r'(?:in|for|at)\s+room\s*(?:no\.?|number|#)?\s*([A-Za-z0-9\-]+)',
        r'\b(?:room)\s*:\s*([A-Za-z0-9\-]+)',
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            # Avoid matching purely common words if mistakenly matched
            if val.lower() not in ["the", "my", "is", "a", "our", "no", "not"]:
                return val.upper()

    # Fallback: if the input is simply a 2-4 digit number like "205" or "B-205"
    bare_match = re.match(r'^\s*([A-Za-z]?\-?[0-9]{2,4}[A-Za-z]?)\s*$', text.strip())
    if bare_match:
        return bare_match.group(1).upper()

    return None

def is_complaint_intent(text: str) -> bool:
    lower = text.lower()
    complaint_triggers = [
        "not working", "not functioning", "broken", "leak", "leaking", "leakage",
        "smoke", "spark", "damaged", "repair", "fix", "faulty", "issue in",
        "problem with", "complaint", "stopped working", "dripping", "overflow",
        "burst", "choked", "stuck", "loose", "shattered", "blown", "flicker"
    ]
    # Check if any trigger is present
    for trigger in complaint_triggers:
        if trigger in lower:
            # Exclude asking for who to contact for maintenance
            if "who should i contact" in lower or "who to contact" in lower or "contact for maintenance" in lower:
                return False
            return True
    return False

def is_complaint_status_query(text: str) -> Optional[str]:
    """Returns complaint ID if user is querying a specific complaint, or None."""
    lower = text.lower()
    # Check for CMP-XXXX format
    m = re.search(r'\b(CMP\-\d{4,6})\b', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return None

class HostelAssistantAgent:
    def process_message(self, user_message: str, session_id: str = "default") -> Dict[str, Any]:
        text = user_message.strip()
        lower = text.lower()
        session = get_session(session_id)
        state = session.get("state", "IDLE")

        # 1. Multi-turn Handling: If we were awaiting room number
        if state == "AWAITING_ROOM_NUMBER":
            extracted_room = extract_room_number(text)
            if extracted_room:
                # We have the missing information! Complete the complaint
                pending = session.get("pending_data", {})
                description = pending.get("description", "Maintenance issue")
                urgency = pending.get("urgency", "Medium")
                category = pending.get("category", "General")
                student_name = pending.get("student_name", "Hostel Resident")

                complaint = create_complaint(
                    room_number=extracted_room,
                    description=description,
                    urgency=urgency,
                    category=category,
                    student_name=student_name
                )

                # Reset session state
                session["state"] = "IDLE"
                session["pending_data"] = {}

                urgency_icon = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠",
                    "Urgent": "🚨"
                }.get(urgency, "📋")

                response_text = (
                    f"✅ **Maintenance Complaint Registered Successfully!**\n\n"
                    f"• **Complaint ID:** `{complaint['id']}`\n"
                    f"• **Room:** {complaint['room_number']}\n"
                    f"• **Issue:** {complaint['description']}\n"
                    f"• **Category:** {complaint['category']}\n"
                    f"• **Urgency:** {urgency_icon} **{complaint['urgency']}**\n"
                    f"• **Status:** **{complaint['status']}**\n\n"
                    f"Our hostel maintenance team has been notified. You can check the status anytime by asking for `{complaint['id']}`."
                )

                if urgency == "Urgent":
                    response_text += "\n\n⚠️ *Due to the urgent nature of this issue, the emergency estate supervisor has also been alerted.*"

                return {
                    "response": response_text,
                    "action": "complaint_created",
                    "data": complaint
                }
            else:
                # Still didn't get a valid room number
                return {
                    "response": "I didn't quite catch the room number. Could you please share your room number (e.g., **Room 205** or **304**)?",
                    "action": "awaiting_room",
                    "data": {"pending": session.get("pending_data")}
                }

        # 2. Check for Specific Complaint Status Query (e.g. "What is the status of CMP-1024?")
        comp_id = is_complaint_status_query(text)
        if comp_id:
            complaint = get_complaint(comp_id)
            if complaint:
                urgency_icon = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠",
                    "Urgent": "🚨"
                }.get(complaint['urgency'], "📋")

                status_badge = {
                    "Registered": "📝 Registered",
                    "In Progress": "⚙️ In Progress",
                    "Resolved": "✅ Resolved"
                }.get(complaint['status'], complaint['status'])

                resp = (
                    f"🔍 **Status for Complaint `{complaint['id']}`**\n\n"
                    f"• **Room:** {complaint['room_number']}\n"
                    f"• **Category:** {complaint['category']}\n"
                    f"• **Description:** {complaint['description']}\n"
                    f"• **Urgency:** {urgency_icon} {complaint['urgency']}\n"
                    f"• **Current Status:** **{status_badge}**\n"
                    f"• **Registered On:** {complaint['created_at']}\n"
                )
                if complaint.get('notes'):
                    resp += f"• **Team Notes:** {complaint['notes']}\n"
                return {
                    "response": resp,
                    "action": "complaint_status",
                    "data": complaint
                }
            else:
                return {
                    "response": f"❌ Could not find any registered complaint with ID `{comp_id}`. Please double check the ID.",
                    "action": "complaint_not_found",
                    "data": None
                }

        # 3. Check for Maintenance Complaint Intent
        if is_complaint_intent(text):
            urgency = classify_urgency(text)
            category = detect_category(text)
            room_no = extract_room_number(text)

            if not room_no:
                # Missing room number -> Ask the student for it
                session["state"] = "AWAITING_ROOM_NUMBER"
                session["pending_data"] = {
                    "description": text,
                    "urgency": urgency,
                    "category": category,
                    "student_name": "Hostel Resident"
                }

                urgency_note = ""
                if urgency == "Urgent":
                    urgency_note = " 🚨 **This looks like an urgent safety issue!**"

                return {
                    "response": (
                        f"I have identified this as a **{category} maintenance complaint**{urgency_note}.\n\n"
                        f"Could you please specify your **room number** so I can register this ticket for you right away?"
                    ),
                    "action": "ask_missing_room",
                    "data": {
                        "category": category,
                        "urgency": urgency,
                        "description": text
                    }
                }
            else:
                # Room number is already provided! Immediately create complaint
                complaint = create_complaint(
                    room_number=room_no,
                    description=text,
                    urgency=urgency,
                    category=category,
                    student_name="Hostel Resident"
                )

                urgency_icon = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠",
                    "Urgent": "🚨"
                }.get(urgency, "📋")

                response_text = (
                    f"✅ **Maintenance Complaint Registered Successfully!**\n\n"
                    f"• **Complaint ID:** `{complaint['id']}`\n"
                    f"• **Room:** {complaint['room_number']}\n"
                    f"• **Issue:** {complaint['description']}\n"
                    f"• **Category:** {complaint['category']}\n"
                    f"• **Urgency:** {urgency_icon} **{complaint['urgency']}**\n"
                    f"• **Status:** **{complaint['status']}**\n\n"
                    f"Our maintenance team has received your ticket. You can track this complaint anytime using `{complaint['id']}`."
                )

                if urgency == "Urgent":
                    response_text += "\n\n🚨 **Warning:** Our on-duty electrician and estate warden have been flagged immediately for urgent intervention."

                return {
                    "response": response_text,
                    "action": "complaint_created",
                    "data": complaint
                }

        # 4. Handle "Who should I contact for maintenance?" & Contacts Queries
        if any(w in lower for w in ["who should i contact", "who to contact", "contact for maintenance", "contact", "phone", "number", "email", "warden", "electrician", "plumber", "ambulance", "security"]):
            # Check if specific role mentioned
            role_filter = None
            if "electrician" in lower:
                role_filter = "Electrician"
            elif "plumber" in lower:
                role_filter = "Plumber"
            elif "warden" in lower:
                role_filter = "Warden"
            elif "security" in lower:
                role_filter = "Security"
            elif "medical" in lower or "ambulance" in lower or "doctor" in lower:
                role_filter = "Medical"
            elif "maintenance" in lower:
                role_filter = "Maintenance"

            contacts = get_staff_contacts(role_or_name=role_filter)
            if not contacts:
                contacts = get_staff_contacts()

            lines = ["📞 **Hostel Maintenance & Emergency Contacts Directory:**\n"]
            for c in contacts[:5]:
                lines.append(
                    f"• **{c['role']}** ({c['name']})\n"
                    f"  📱 Phone: `{c['phone']}` | 🕒 Hours: {c['available_hours']}\n"
                    f"  📍 Location: {c['location']} | ✉️ {c['email']}\n"
                )
            lines.append("For routine repairs, you can also tell me your issue directly (e.g., *'The fan in room 205 is not working'*) and I will lodge the official ticket!")

            return {
                "response": "\n".join(lines),
                "action": "contacts_info",
                "data": contacts
            }

        # 5. Handle Mess Timings / Specific Meal Queries ("What time is dinner?")
        if any(meal in lower for meal in ["dinner", "lunch", "breakfast", "snacks", "mess timing", "timing", "time is"]):
            # Check which meal
            target_meal = None
            if "dinner" in lower:
                target_meal = "Dinner"
            elif "lunch" in lower:
                target_meal = "Lunch"
            elif "breakfast" in lower:
                target_meal = "Breakfast"
            elif "snack" in lower:
                target_meal = "Snacks"

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day = None
            for d in days:
                if d.lower() in lower:
                    target_day = d
                    break
            if "tomorrow" in lower:
                tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                target_day = tomorrow.strftime("%A")
            elif not target_day:
                target_day = datetime.datetime.now().strftime("%A")

            menu_rows = get_mess_menu(day_of_week=target_day, meal_type=target_meal)
            
            if target_meal and menu_rows:
                row = menu_rows[0]
                resp = (
                    f"🍽️ **Hostel {target_meal} Timing & Details ({target_day})**:\n\n"
                    f"• **Serving Time:** ⏰ **{row['timing']}**\n"
                    f"• **{target_day}'s {target_meal} Menu:** {row['items']}\n"
                    f"• **Dining Hall:** Main Hostel Central Mess (Ground Floor)\n\n"
                    f"*Note: Please carry your Student ID / Mess Card.*"
                )
                return {
                    "response": resp,
                    "action": "mess_timing",
                    "data": row
                }
            elif not target_meal and any(w in lower for w in ["mess time", "mess timing", "meal time", "food timing"]):
                # Return general mess timings
                all_meals = get_mess_menu(day_of_week="Monday")
                lines = ["🍽️ **Official Hostel Mess Meal Timings:**\n"]
                for m in all_meals:
                    lines.append(f"• **{m['meal_type']}:** ⏰ `{m['timing']}`")
                lines.append("\n*Meals are served in the Central Dining Hall.*")
                return {
                    "response": "\n".join(lines),
                    "action": "mess_timings_all",
                    "data": all_meals
                }

        # 6. Handle Mess Menu Queries ("What is today's mess menu?", "mess menu")
        if any(w in lower for w in ["mess menu", "food menu", "today's menu", "todays menu", "what is on menu", "what is for lunch", "what is for dinner", "what is for breakfast"]):
            # Detect day of week requested or default to today
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_day = None
            for d in days:
                if d.lower() in lower:
                    target_day = d
                    break
            
            if "tomorrow" in lower:
                tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                target_day = tomorrow.strftime("%A")
            elif not target_day:
                target_day = datetime.datetime.now().strftime("%A")

            menu_items = get_mess_menu(day_of_week=target_day)
            lines = [f"🍴 **Hostel Mess Menu for {target_day}:**\n"]
            for item in menu_items:
                meal_icon = {
                    "Breakfast": "🍳",
                    "Lunch": "🍛",
                    "Snacks": "☕",
                    "Dinner": "🍲"
                }.get(item["meal_type"], "🍽️")

                lines.append(
                    f"### {meal_icon} {item['meal_type']} (`{item['timing']}`)\n"
                    f"{item['items']}\n"
                )

            lines.append("Enjoy your meal! Let me know if you need info about other days or dietary guidelines.")
            return {
                "response": "\n".join(lines),
                "action": "mess_menu",
                "data": {"day": target_day, "menu": menu_items}
            }

        # 7. Handle Hostel Rules ("What are the hostel rules?", curfews, visitors, appliances)
        if any(w in lower for w in ["rule", "rules", "curfew", "visitor", "guest", "appliance", "heater", "kettle", "leave", "outpass", "discipline", "quiet"]):
            # Check specific rule subtopic
            keyword = None
            if "curfew" in lower or "timing" in lower or "gate" in lower:
                keyword = "Curfew"
            elif "visitor" in lower or "guest" in lower:
                keyword = "Visitor"
            elif "appliance" in lower or "kettle" in lower or "heater" in lower or "iron" in lower:
                keyword = "Appliance"
            elif "leave" in lower or "outpass" in lower or "night out" in lower:
                keyword = "Leave"

            rules = get_hostel_rules(keyword=keyword)
            if not rules:
                rules = get_hostel_rules()

            lines = ["📜 **Official University Hostel Guidelines & Rules:**\n"]
            for r in rules[:4]:
                lines.append(f"• **{r['title']}** ({r['category']}):\n  {r['rule_text']}\n")

            lines.append("Compliance with hostel policies ensures a safe and comfortable environment for all residents.")
            return {
                "response": "\n".join(lines),
                "action": "hostel_rules",
                "data": rules
            }

        # 8. Check complaints by room ("Show complaints for room 205")
        if "complaint" in lower and any(w in lower for w in ["list", "show", "all", "my complaints", "status"]):
            room_no = extract_room_number(text)
            complaints = get_complaints(room_number=room_no, limit=5)
            if complaints:
                lines = [f"📋 **Recent Complaints Registered" + (f" for Room {room_no}:**\n" if room_no else ":**\n")]
                for c in complaints:
                    lines.append(f"• `{c['id']}` - **{c['status']}** | Urgency: **{c['urgency']}** | {c['description']} (Room: {c['room_number']})")
                return {
                    "response": "\n".join(lines),
                    "action": "complaints_list",
                    "data": complaints
                }
            else:
                return {
                    "response": "No complaints found matching that room or query." + (" You can report a new issue anytime!" if not room_no else f" Room {room_no} has zero pending complaints!"),
                    "action": "complaints_empty",
                    "data": []
                }

        # 9. Greeting / General Help Fallback
        if any(w in lower for w in ["hi", "hello", "hey", "help", "who are you", "what can you do"]):
            return {
                "response": (
                    "👋 **Hello! I am your AI Hostel Assistant.**\n\n"
                    "I am connected to the official university hostel database. Here is what I can help you with:\n\n"
                    "1. 🍽️ **Mess & Food:** Ask *'What time is dinner?'* or *'What is today's mess menu?'*\n"
                    "2. 🛠️ **Maintenance Complaints:** Report issues like *'The fan in room 205 is not working'* or *'There is water leakage in my bathroom'* (I'll automatically classify urgency: Low, Medium, High, Urgent and file the ticket).\n"
                    "3. 📜 **Hostel Rules:** Ask *'What are the hostel rules?'*, curfew timings, or electrical appliance policies.\n"
                    "4. 📞 **Staff Directory:** Ask *'Who should I contact for maintenance?'* or warden contacts.\n"
                    "5. 🔍 **Ticket Tracking:** Ask *'Check status of CMP-1001'* or *'Show complaints for room 205'*.\n\n"
                    "How can I assist you right now?"
                ),
                "action": "greeting",
                "data": None
            }

        # General intelligent fallback
        return {
            "response": (
                "I didn't quite find an exact match in the hostel database for that query.\n\n"
                "You can ask me about:\n"
                "• **Mess Details:** *'What time is dinner?'* or *'What is today's mess menu?'*\n"
                "• **Hostel Rules:** *'What are the hostel rules?'*\n"
                "• **Maintenance Contacts:** *'Who should I contact for maintenance?'*\n"
                "• **Lodge a Complaint:** *'The fan in room 205 is not working'* or *'There is water leakage in my bathroom'*"
            ),
            "action": "unknown",
            "data": None
        }

# Global singleton agent
agent = HostelAssistantAgent()
