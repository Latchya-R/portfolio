import sqlite3
import random
import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

DB_PATH = Path(__file__).parent / "hostel.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Complaints Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        room_number TEXT NOT NULL,
        student_name TEXT DEFAULT 'Hostel Resident',
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        urgency TEXT NOT NULL CHECK(urgency IN ('Low', 'Medium', 'High', 'Urgent')),
        status TEXT NOT NULL DEFAULT 'Registered' CHECK(status IN ('Registered', 'In Progress', 'Resolved')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        notes TEXT DEFAULT ''
    )
    """)

    # 2. Mess Menu Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mess_menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week TEXT NOT NULL,
        meal_type TEXT NOT NULL CHECK(meal_type IN ('Breakfast', 'Lunch', 'Snacks', 'Dinner')),
        timing TEXT NOT NULL,
        items TEXT NOT NULL,
        special_notes TEXT DEFAULT ''
    )
    """)

    # 3. Hostel Rules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hostel_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        rule_text TEXT NOT NULL
    )
    """)

    # 4. Staff Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        available_hours TEXT NOT NULL,
        location TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed initial data if tables are empty
    seed_database(cursor, conn)
    conn.close()

def get_default_menu_data():
    return [
        # Monday
        ("Monday", "Breakfast", "7:30 AM - 9:30 AM", "Uthappam, Red Chutney, White Chutney, Tea / Coffee", "South Indian Uthappam Breakfast"),
        ("Monday", "Lunch", "12:30 PM - 2:30 PM", "Steamed Rice, Sambar, Potato Curry, Rasam, Curd, Buttermilk, Papad", "Balanced Comfort Lunch"),
        ("Monday", "Snacks", "4:30 PM - 5:30 PM", "Sandwich, Hot Tea", "Evening Sandwich Refreshment"),
        ("Monday", "Dinner", "7:30 PM - 9:30 PM", "Parotta, Chicken Gravy / Veg Gravy, Kesari, Rice, Rasam, Buttermilk", "Parotta Special Dinner with Kesari"),
        # Tuesday
        ("Tuesday", "Breakfast", "7:30 AM - 9:30 AM", "Idly, Sambar, White Chutney, Tea / Coffee", "Soft Idly Morning"),
        ("Tuesday", "Lunch", "12:30 PM - 2:30 PM", "Chicken Biryani / Veg Biryani, Potato Chips, Sweet, Buttermilk, Rice, Sambar, Rasam, Curd", "Tuesday Biryani Special Feast"),
        ("Tuesday", "Snacks", "4:30 PM - 5:30 PM", "Biscuits / Cookies, Hot Masala Tea & Coffee", "Evening Tea"),
        ("Tuesday", "Dinner", "7:30 PM - 9:30 PM", "Rice, Pachadi, Curry, Sambar, Rasam, Buttermilk, Ice Cream", "Dinner with Ice Cream Dessert"),
        # Wednesday
        ("Wednesday", "Breakfast", "7:30 AM - 9:30 AM", "Tomato Rice, Chutney / Raitha, Tea & Coffee", "Flavorful Tomato Rice"),
        ("Wednesday", "Lunch", "12:30 PM - 2:30 PM", "Rice, Chicken Gravy / Chicken 65, Greens (Keerai), Beetroot, Sambar, Rasam, Curd, Buttermilk, Gobi 65, Carrot Halwa", "Grand Wednesday Feast with Chicken 65 / Gobi 65 & Carrot Halwa"),
        ("Wednesday", "Snacks", "4:30 PM - 5:30 PM", "Samosa, Hot Masala Tea", "Crispy Evening Samosa"),
        ("Wednesday", "Dinner", "7:30 PM - 9:30 PM", "Gobi Fried Rice / Poori / Idly / Rice, Podi, Sambar, Rasam, Buttermilk", "Choice of Gobi Fried Rice, Poori, or Idly with Podi"),
        # Thursday
        ("Thursday", "Breakfast", "7:30 AM - 9:30 AM", "Pongal, Sambar, Coconut Chutney, Tea / Coffee", "Hot Ghee Pongal & Sambar"),
        ("Thursday", "Lunch", "12:30 PM - 2:30 PM", "Rice, Sambar, Rasam, Egg, Curd, Buttermilk, Ice Cream", "Wholesome Lunch with Egg & Ice Cream"),
        ("Thursday", "Snacks", "4:30 PM - 5:30 PM", "Veg Cutlet / Biscuits, Hot Tea, Coffee", "Evening Tea"),
        ("Thursday", "Dinner", "7:30 PM - 9:30 PM", "Chapathi, Tomato Curry, Vegetable Gravy, Buttermilk", "Chapathi with Tomato & Veg Gravy"),
        # Friday
        ("Friday", "Breakfast", "7:30 AM - 9:30 AM", "Idly, Sambar, Red Chutney, Tea / Coffee", "Classic Idly with Red Chutney"),
        ("Friday", "Lunch", "12:30 PM - 2:30 PM", "Rice, Sambar, Curries, Rasam, Curd, Buttermilk, Potato Chips", "South Indian Meals with Potato Chips"),
        ("Friday", "Snacks", "4:30 PM - 5:30 PM", "Tea, Coffee, Evening Snacks", "Evening Refreshment"),
        ("Friday", "Dinner", "7:30 PM - 9:30 PM", "Dosa, Chicken Gravy / Sambar, Red Chutney, White Chutney", "Hot Crispy Dosa with Chicken Gravy & Dual Chutneys"),
        # Saturday
        ("Saturday", "Breakfast", "7:30 AM - 10:00 AM", "Bread Rice / Bread Toast & Butter, Jam, Tea & Coffee", "Weekend Breakfast"),
        ("Saturday", "Lunch", "12:30 PM - 2:30 PM", "Rice, Sambar, Greens (Keerai), Potato Curry, Rasam, Curd, Buttermilk, Ice Cream", "Saturday Lunch with Greens & Ice Cream"),
        ("Saturday", "Snacks", "4:30 PM - 5:30 PM", "Snack of the Day, Hot Tea & Coffee", "Evening Refreshment"),
        ("Saturday", "Dinner", "7:30 PM - 9:30 PM", "Variety Rice (Lemon Rice, Tamarind Rice, Curd Rice, Sambar Rice, Tomato Rice, Coconut Rice), Papad, Pickle", "Grand Variety Rice Night"),
        # Sunday
        ("Sunday", "Breakfast", "7:30 AM - 10:30 AM", "Dosa, Red Chutney, White Chutney (Special morning tea served at 10:00 AM)", "Dosa Morning with Special 10 AM Tea"),
        ("Sunday", "Lunch", "12:30 PM - 2:30 PM", "Non-Veg: Chicken Gravy / Chilli Chicken / Mutton Biryani (alternate weeks), Steamed Rice, Carrot Curry, Dal, Sambar, Rasam, Curd, Buttermilk, Papad | Veg: Steamed Rice, Carrot Curry, Dal, Sambar, Rasam, Curd, Buttermilk, Chips/Cutlet/Pakoda, Sweet", "Grand Sunday Special Lunch"),
        ("Sunday", "Snacks", "4:30 PM - 5:30 PM", "Veg Puff, Hot Tea", "Crunchy Veg Puff & Tea"),
        ("Sunday", "Dinner", "7:30 PM - 9:30 PM", "Chapathi, Tomato Curry, Vegetable Gravy, Buttermilk", "Light Sunday Chapathi Dinner")
    ]

def reload_mess_menu():
    """Wipes and reloads the mess menu with the updated college schedule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mess_menu")
    menu_data = get_default_menu_data()
    cursor.executemany("""
    INSERT INTO mess_menu (day_of_week, meal_type, timing, items, special_notes)
    VALUES (?, ?, ?, ?, ?)
    """, menu_data)
    conn.commit()
    conn.close()

def seed_database(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    # Always ensure the updated menu is present
    cursor.execute("SELECT COUNT(*) FROM mess_menu")
    if cursor.fetchone()[0] == 0:
        menu_data = get_default_menu_data()
        cursor.executemany("""
        INSERT INTO mess_menu (day_of_week, meal_type, timing, items, special_notes)
        VALUES (?, ?, ?, ?, ?)
        """, menu_data)

    # Check if hostel_rules has data
    cursor.execute("SELECT COUNT(*) FROM hostel_rules")
    if cursor.fetchone()[0] == 0:
        rules_data = [
            ("Curfew & Timings", "Hostel Entry Deadline", "The main hostel gate closes strictly at 10:00 PM for all residents. Late entry requires prior written approval from the Chief Warden."),
            ("Curfew & Timings", "Mess Timings", "Breakfast: 7:30 AM - 9:30 AM (Sundays until 10:30 AM), Lunch: 12:30 PM - 2:30 PM, Evening Snacks: 4:30 PM - 5:30 PM, Dinner: 7:30 PM - 9:30 PM. Food is not permitted in rooms except during sickness."),
            ("Curfew & Timings", "Quiet Hours", "Strict silence must be maintained from 11:00 PM to 6:00 AM in corridors, study rooms, and individual rooms to ensure undisturbed sleep and study time."),
            ("Visitors & Guests", "Visitor Policy", "Day visitors (parents/guardians) are permitted in the reception lounge only between 9:00 AM and 6:00 PM. No unauthorized visitors or persons of opposite gender are allowed in student rooms."),
            ("Visitors & Guests", "Overnight Stay", "Overnight guest stays are strictly prohibited in student rooms. Guest house rooms may be booked via the Warden's office subject to availability."),
            ("Electrical Appliances", "Permitted Devices", "Laptops, mobile phones, tablet chargers, and study lamps are permitted."),
            ("Electrical Appliances", "Prohibited High-Power Appliances", "Electric kettles, immersion rods, induction cooktops, room heaters, blowers, and air fryers are strictly prohibited due to electrical load and fire hazard risks. Unauthorized items will be confiscated and fined Rs. 1000."),
            ("Discipline & Safety", "Fire Safety & Hazards", "Tampering with fire extinguishers, smoke detectors, electrical panels, or lighting candles/incense inside rooms is strictly prohibited."),
            ("Discipline & Safety", "Substance Prohibition", "Smoking, alcohol consumption, drugs, or possession of any intoxicating substances is completely banned and grounds for immediate expulsion."),
            ("Leave Application", "Night Out & Leave Procedure", "Students traveling out of station or staying out overnight must apply for out-pass on the hostel portal at least 24 hours in advance with parent consent SMS/email verification.")
        ]
        cursor.executemany("""
        INSERT INTO hostel_rules (category, title, rule_text)
        VALUES (?, ?, ?)
        """, rules_data)

    # Check if staff_contacts has data
    cursor.execute("SELECT COUNT(*) FROM staff_contacts")
    if cursor.fetchone()[0] == 0:
        contacts_data = [
            ("Maintenance", "Head of Maintenance & Estate", "Mr. Rajesh Kumar", "+91-98765-43210", "estate.maintenance@university.edu", "8:00 AM - 8:00 PM (On-call 24/7 for emergencies)", "Estate Office, Ground Floor Block A"),
            ("Maintenance", "Hostel Electrician", "Mr. Suresh Sharma", "+91-98765-43211", "electrician.hostel@university.edu", "9:00 AM - 6:00 PM", "Hostel Utility Room #G-04"),
            ("Maintenance", "Hostel Plumber", "Mr. Ramesh Yadav", "+91-98765-43212", "plumber.hostel@university.edu", "9:00 AM - 6:00 PM", "Hostel Utility Room #G-05"),
            ("Maintenance", "Carpenter & Locksmith", "Mr. Mohan Lal", "+91-98765-43213", "carpenter.hostel@university.edu", "10:00 AM - 5:00 PM", "Estate Workshop"),
            ("Warden", "Chief Hostel Warden", "Dr. A. K. Sundaram", "+91-98765-11100", "chiefwarden@university.edu", "10:00 AM - 5:00 PM (Emergency 24/7)", "Warden Residence / Main Admin Block #102"),
            ("Warden", "Resident Deputy Warden (Boys Block)", "Prof. R. Venkat", "+91-98765-11101", "warden.boys@university.edu", "6:00 PM - 10:00 PM (Emergency 24/7)", "Boys Hostel Office, Block B, Room 101"),
            ("Warden", "Resident Deputy Warden (Girls Block)", "Dr. Meenakshi Rao", "+91-98765-11102", "warden.girls@university.edu", "6:00 PM - 10:00 PM (Emergency 24/7)", "Girls Hostel Office, Block G, Room 101"),
            ("Security", "Campus Main Gate Security Desk", "Security In-Charge", "+91-98765-99999", "security@university.edu", "24 Hours / 7 Days", "Campus Main Security Gate 1"),
            ("Medical", "Hostel Health Center & Ambulance", "Dr. Priya Verma (Medical Officer)", "+91-98765-88888", "healthcenter@university.edu", "24 Hours / 7 Days Emergency Ambulance", "Campus Health Center, Ground Floor")
        ]
        cursor.executemany("""
        INSERT INTO staff_contacts (category, role, name, phone, email, available_hours, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, contacts_data)

    conn.commit()

def generate_complaint_id() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Find next sequence or random 4-digit
    while True:
        num = random.randint(1000, 9999)
        comp_id = f"CMP-{num}"
        cursor.execute("SELECT id FROM complaints WHERE id = ?", (comp_id,))
        if not cursor.fetchone():
            conn.close()
            return comp_id

def create_complaint(
    room_number: str,
    description: str,
    urgency: str,
    category: str = "General",
    student_name: str = "Hostel Resident",
    notes: str = ""
) -> Dict[str, Any]:
    comp_id = generate_complaint_id()
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO complaints (id, room_number, student_name, category, description, urgency, status, created_at, updated_at, notes)
    VALUES (?, ?, ?, ?, ?, ?, 'Registered', ?, ?, ?)
    """, (comp_id, room_number.strip(), student_name.strip(), category.strip(), description.strip(), urgency, now_iso, now_iso, notes))
    conn.commit()

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (comp_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)

def get_complaint(complaint_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ? COLLATE NOCASE", (complaint_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_complaints(room_number: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if room_number:
        cursor.execute("""
        SELECT * FROM complaints 
        WHERE room_number LIKE ? 
        ORDER BY created_at DESC LIMIT ?
        """, (f"%{room_number.strip()}%", limit))
    else:
        cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_complaint_status(complaint_id: str, new_status: str, notes: str = "") -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE complaints
    SET status = ?, updated_at = ?, notes = CASE WHEN ? != '' THEN ? ELSE notes END
    WHERE id = ? COLLATE NOCASE
    """, (new_status, now_iso, notes, notes, complaint_id.strip()))
    conn.commit()

    cursor.execute("SELECT * FROM complaints WHERE id = ? COLLATE NOCASE", (complaint_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_mess_menu(day_of_week: Optional[str] = None, meal_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM mess_menu WHERE 1=1"
    params = []
    if day_of_week:
        query += " AND day_of_week LIKE ? COLLATE NOCASE"
        params.append(day_of_week.strip())
    if meal_type:
        query += " AND meal_type LIKE ? COLLATE NOCASE"
        params.append(meal_type.strip())
    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_hostel_rules(category: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM hostel_rules WHERE 1=1"
    params = []
    if category:
        query += " AND category LIKE ? COLLATE NOCASE"
        params.append(f"%{category.strip()}%")
    if keyword:
        query += " AND (title LIKE ? OR rule_text LIKE ?)"
        params.extend([f"%{keyword.strip()}%", f"%{keyword.strip()}%"])
    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_staff_contacts(category: Optional[str] = None, role_or_name: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM staff_contacts WHERE 1=1"
    params = []
    if category:
        query += " AND category LIKE ? COLLATE NOCASE"
        params.append(f"%{category.strip()}%")
    if role_or_name:
        query += " AND (role LIKE ? OR name LIKE ? OR category LIKE ?)"
        params.extend([f"%{role_or_name.strip()}%", f"%{role_or_name.strip()}%", f"%{role_or_name.strip()}%"])
    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized and verified successfully!")
