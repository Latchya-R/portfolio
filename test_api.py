import unittest
from fastapi.testclient import TestClient
from main import app
import database

client = TestClient(app)

class TestHostelApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()

    def test_root_index(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("HostelMate AI", response.text)

    def test_qa_dinner_time(self):
        response = client.post("/api/chat", json={
            "message": "What time is dinner?",
            "session_id": "test_api_qa"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("7:30 PM - 9:30 PM", data["response"])
        self.assertEqual(data["action"], "mess_timing")

    def test_qa_hostel_rules(self):
        response = client.post("/api/chat", json={
            "message": "What are the hostel rules?",
            "session_id": "test_api_qa"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Guidelines & Rules", data["response"])
        self.assertEqual(data["action"], "hostel_rules")

    def test_qa_maintenance_contacts(self):
        response = client.post("/api/chat", json={
            "message": "Who should I contact for maintenance?",
            "session_id": "test_api_qa"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Rajesh Kumar", data["response"])
        self.assertEqual(data["action"], "contacts_info")

    def test_qa_mess_menu(self):
        response = client.post("/api/chat", json={
            "message": "What is today's mess menu?",
            "session_id": "test_api_qa"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Hostel Mess Menu", data["response"])
        self.assertEqual(data["action"], "mess_menu")

    def test_complaint_direct_creation(self):
        response = client.post("/api/chat", json={
            "message": "The fan in room 205 is not working.",
            "session_id": "session_direct_comp"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["action"], "complaint_created")
        complaint = data["data"]
        self.assertEqual(complaint["room_number"], "205")
        self.assertEqual(complaint["urgency"], "Medium")
        self.assertEqual(complaint["status"], "Registered")
        self.assertTrue(complaint["id"].startswith("CMP-"))

    def test_complaint_multi_turn_missing_room(self):
        session_id = "session_multiturn_comp"
        # Turn 1: Issue without room
        res1 = client.post("/api/chat", json={
            "message": "There is water leakage in my bathroom.",
            "session_id": session_id
        })
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["action"], "ask_missing_room")
        self.assertIn("room number", data1["response"].lower())
        self.assertEqual(data1["data"]["urgency"], "High")

        # Turn 2: User provides room number
        res2 = client.post("/api/chat", json={
            "message": "Room 304",
            "session_id": session_id
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["action"], "complaint_created")
        comp = data2["data"]
        self.assertEqual(comp["room_number"], "304")
        self.assertEqual(comp["urgency"], "High")
        self.assertEqual(comp["status"], "Registered")

    def test_urgency_classification_smoke(self):
        res = client.post("/api/chat", json={
            "message": "There is smoke coming from an electrical board in room 108",
            "session_id": "session_urgent"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["action"], "complaint_created")
        self.assertEqual(data["data"]["urgency"], "Urgent")
        self.assertEqual(data["data"]["status"], "Registered")

    def test_complaints_endpoint(self):
        res = client.get("/api/complaints")
        self.assertEqual(res.status_code, 200)
        complaints = res.json()
        self.assertIsInstance(complaints, list)
        self.assertGreater(len(complaints), 0)

        # Filter by room
        res_filtered = client.get("/api/complaints?room_number=205")
        self.assertEqual(res_filtered.status_code, 200)
        filtered = res_filtered.json()
        for c in filtered:
            self.assertEqual(c["room_number"], "205")

    def test_mess_menu_and_rules_endpoints(self):
        res_menu = client.get("/api/mess-menu")
        self.assertEqual(res_menu.status_code, 200)
        self.assertGreater(len(res_menu.json()), 0)

        res_rules = client.get("/api/rules")
        self.assertEqual(res_rules.status_code, 200)
        self.assertGreater(len(res_rules.json()), 0)

        res_contacts = client.get("/api/contacts")
        self.assertEqual(res_contacts.status_code, 200)
        self.assertGreater(len(res_contacts.json()), 0)

if __name__ == "__main__":
    unittest.main()
