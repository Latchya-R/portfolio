import unittest
import database
from agent import HostelAssistantAgent, classify_urgency, extract_room_number, reset_session

class TestHostelAssistant(unittest.TestCase):
    def setUp(self):
        database.init_db()
        self.agent = HostelAssistantAgent()
        reset_session("test_session_1")
        reset_session("test_session_2")
        reset_session("test_session_3")

    def test_urgency_classification(self):
        # Specific examples from prompt:
        # "My room light is not working" -> Medium
        # "Water is leaking from the ceiling" -> High
        # "There is smoke coming from an electrical board" -> Urgent
        self.assertEqual(classify_urgency("My room light is not working"), "Medium")
        self.assertEqual(classify_urgency("Water is leaking from the ceiling"), "High")
        self.assertEqual(classify_urgency("There is smoke coming from an electrical board"), "Urgent")
        
        # Additional validation
        self.assertEqual(classify_urgency("The fan in room 205 is not working."), "Medium")
        self.assertEqual(classify_urgency("There is water leakage in my bathroom."), "High")
        self.assertEqual(classify_urgency("Squeaky door hinge in room 101"), "Low")

    def test_room_number_extraction(self):
        self.assertEqual(extract_room_number("The fan in room 205 is not working."), "205")
        self.assertEqual(extract_room_number("Water leak in rm 304B"), "304B")
        self.assertEqual(extract_room_number("room no. 112"), "112")
        self.assertEqual(extract_room_number("205"), "205")
        self.assertIsNone(extract_room_number("There is water leakage in my bathroom."))

    def test_qa_dinner_timing(self):
        res = self.agent.process_message("What time is dinner?", session_id="test_qa")
        self.assertIn("7:30 PM - 9:30 PM", res["response"])
        self.assertEqual(res["action"], "mess_timing")

    def test_qa_hostel_rules(self):
        res = self.agent.process_message("What are the hostel rules?", session_id="test_qa")
        self.assertIn("Guidelines & Rules", res["response"])
        self.assertEqual(res["action"], "hostel_rules")

    def test_qa_maintenance_contacts(self):
        res = self.agent.process_message("Who should I contact for maintenance?", session_id="test_qa")
        self.assertIn("Rajesh Kumar", res["response"])
        self.assertIn("+91-98765-43210", res["response"])
        self.assertEqual(res["action"], "contacts_info")

    def test_qa_mess_menu(self):
        res = self.agent.process_message("What is today's mess menu?", session_id="test_qa")
        self.assertIn("Hostel Mess Menu", res["response"])
        self.assertEqual(res["action"], "mess_menu")

    def test_complaint_with_room_provided(self):
        msg = "The fan in room 205 is not working."
        res = self.agent.process_message(msg, session_id="test_session_1")
        self.assertEqual(res["action"], "complaint_created")
        complaint = res["data"]
        self.assertIsNotNone(complaint)
        self.assertTrue(complaint["id"].startswith("CMP-"))
        self.assertEqual(complaint["room_number"], "205")
        self.assertEqual(complaint["urgency"], "Medium")
        self.assertEqual(complaint["status"], "Registered")
        self.assertEqual(complaint["category"], "Electrical")

        # Verify persisted in SQLite
        db_complaint = database.get_complaint(complaint["id"])
        self.assertIsNotNone(db_complaint)
        self.assertEqual(db_complaint["id"], complaint["id"])
        self.assertEqual(db_complaint["status"], "Registered")

    def test_complaint_multi_turn_missing_room(self):
        # Step 1: User states issue without room
        msg1 = "There is water leakage in my bathroom."
        res1 = self.agent.process_message(msg1, session_id="test_session_2")
        self.assertEqual(res1["action"], "ask_missing_room")
        self.assertIn("room number", res1["response"].lower())

        # Step 2: User provides room number
        msg2 = "Room 304"
        res2 = self.agent.process_message(msg2, session_id="test_session_2")
        self.assertEqual(res2["action"], "complaint_created")
        complaint = res2["data"]
        self.assertEqual(complaint["room_number"], "304")
        self.assertEqual(complaint["urgency"], "High")
        self.assertEqual(complaint["status"], "Registered")
        self.assertEqual(complaint["category"], "Plumbing")

        # Step 3: Check status query
        status_query = f"What is the status of {complaint['id']}?"
        res3 = self.agent.process_message(status_query, session_id="test_session_2")
        self.assertEqual(res3["action"], "complaint_status")
        self.assertIn("Registered", res3["response"])

    def test_all_user_urgency_examples(self):
        # 1. "My room light is not working" -> Medium
        res1 = self.agent.process_message("My room light is not working", session_id="u1")
        self.assertEqual(res1["data"]["urgency"], "Medium")

        # 2. "Water is leaking from the ceiling" -> High
        res2 = self.agent.process_message("Water is leaking from the ceiling", session_id="u2")
        self.assertEqual(res2["data"]["urgency"], "High")

        # 3. "There is smoke coming from an electrical board" -> Urgent
        res3 = self.agent.process_message("There is smoke coming from an electrical board", session_id="u3")
        self.assertEqual(res3["data"]["urgency"], "Urgent")

        # 4. "The fan in room 205 is not working." -> Medium
        res4 = self.agent.process_message("The fan in room 205 is not working.", session_id="u4")
        self.assertEqual(res4["data"]["urgency"], "Medium")
        self.assertEqual(res4["data"]["status"], "Registered")

        # 5. "There is water leakage in my bathroom." -> High (Missing room, then provided)
        res5 = self.agent.process_message("There is water leakage in my bathroom.", session_id="u5")
        self.assertEqual(res5["action"], "ask_missing_room")
        self.assertEqual(res5["data"]["urgency"], "High")

        res5_follow = self.agent.process_message("104", session_id="u5")
        self.assertEqual(res5_follow["action"], "complaint_created")
        self.assertEqual(res5_follow["data"]["urgency"], "High")
        self.assertEqual(res5_follow["data"]["room_number"], "104")
        self.assertEqual(res5_follow["data"]["status"], "Registered")

    def test_meal_by_day(self):
        res = self.agent.process_message("What is for lunch on Wednesday?", session_id="meal_test")
        self.assertIn("Wednesday", res["response"])
        self.assertIn("Chicken 65", res["response"])

        res_dinner = self.agent.process_message("What is for dinner on Wednesday?", session_id="meal_test2")
        self.assertIn("Gobi Fried Rice", res_dinner["response"])

        res_sun_bf = self.agent.process_message("What is for breakfast on Sunday?", session_id="meal_test3")
        self.assertIn("Dosa", res_sun_bf["response"])
        self.assertIn("Red Chutney", res_sun_bf["response"])

if __name__ == "__main__":
    unittest.main()
