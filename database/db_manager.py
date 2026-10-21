import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DatabaseManager:
    """Handles live SQLite persistence for the 2D Floor-Plan Smart Parking System."""
    def __init__(self, db_path: str = "smart_parking_live.db"):
        self.db_path = db_path
        self.init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Dynamically creates SQLite tables on startup if they do not exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parking_slots (
                    slot_id TEXT PRIMARY KEY,
                    zone TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    hourly_rate REAL NOT NULL,
                    state TEXT NOT NULL,
                    vehicle_number TEXT,
                    reserved_by TEXT,
                    reserved_at TEXT,
                    occupied_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    slot_id TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    vehicle_number TEXT,
                    fee REAL DEFAULT 0.0,
                    details TEXT
                )
            """)
            conn.commit()
            cursor.execute("SELECT COUNT(*) as cnt FROM parking_slots")
            if cursor.fetchone()["cnt"] == 0:
                self.seed_sample_data()

    def _generate_48_floor_slots(self) -> List[tuple]:
        """Generates the 48 bays matching Blocks A, B, C (Top) and D, E, F (Bottom), bays 1-8 each."""
        blocks = [
            ("A", "Block A (Standard)", "4-Wheeler", 50.0),
            ("B", "Block B (Standard)", "4-Wheeler", 50.0),
            ("C", "Block C (EV / Exec)", "EV 4-Wheeler", 80.0),
            ("D", "Block D (VIP)", "Executive SUV", 90.0),
            ("E", "Block E (Standard)", "4-Wheeler", 50.0),
            ("F", "Block F (Compact)", "4-Wheeler", 40.0),
        ]
        slots = []
        for blk_code, zone_name, v_type, rate in blocks:
            for num in range(1, 9):
                slot_id = f"{blk_code}{num}"
                slots.append((slot_id, zone_name, v_type, rate, "Available", None, None, None, None))
        return slots

    def initialize_clean_slots(self) -> None:
        """Resets all 48 bays to Available with empty logs."""
        slots = self._generate_48_floor_slots()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parking_slots")
            cursor.execute("DELETE FROM activity_logs")
            cursor.executemany("""
                INSERT INTO parking_slots
                (slot_id, zone, vehicle_type, hourly_rate, state, vehicle_number, reserved_by, reserved_at, occupied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, slots)
            conn.commit()

    def seed_sample_data(self) -> None:
        """Seeds the exact 12 Filled / 36 Empty layout shown in the ParkingManager UI reference."""
        now = datetime.now()
        two_hrs_ago = (now - timedelta(hours=2, minutes=10)).isoformat()
        one_hr_ago = (now - timedelta(hours=1, minutes=20)).isoformat()
        thirty_min_ago = (now - timedelta(minutes=35)).isoformat()

        base_slots = self._generate_48_floor_slots()
        # Map of active slots matching the visual floor plan (12 active bays out of 48)
        active_overrides = {
            "A1": ("Occupied", "MH14MQ2219", None, None, two_hrs_ago),
            "A4": ("Occupied", "MH12AB4455", None, None, one_hr_ago),
            "A7": ("Occupied", "MH14XY9081", None, None, two_hrs_ago),
            "B8": ("Occupied", "MH12EV0099", None, None, one_hr_ago),
            "C2": ("Occupied", "MH14DX7711", None, None, two_hrs_ago),
            "C5": ("Occupied", "MH12TW8810", None, None, one_hr_ago),
            "D2": ("Reserved", "MH14VIP001", "Pradnya K.", thirty_min_ago, None),
            "E1": ("Occupied", "MH12GH1122", None, None, two_hrs_ago),
            "E2": ("Occupied", "MH14RS5566", None, None, one_hr_ago),
            "E4": ("Reserved", "MH12JK3344", "Vikas S.", thirty_min_ago, None),
            "F1": ("Occupied", "MH14LM9900", None, None, one_hr_ago),
            "F6": ("Occupied", "MH12PQ7788", None, None, two_hrs_ago),
        }

        final_slots = []
        for s in base_slots:
            sid, zone, vtype, rate, _, _, _, _, _ = s
            if sid in active_overrides:
                st_name, veh, res_by, res_at, occ_at = active_overrides[sid]
                final_slots.append((sid, zone, vtype, rate, st_name, veh, res_by, res_at, occ_at))
            else:
                final_slots.append(s)

        sample_logs = [
            ((now - timedelta(hours=2, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), "A1", "Block A (Standard)", "VEHICLE_ENTRY", "Available", "Occupied", "MH14MQ2219", 0.0, "Direct check-in"),
            ((now - timedelta(hours=1, minutes=50)).strftime("%Y-%m-%d %H:%M:%S"), "C2", "Block C (EV / Exec)", "VEHICLE_ENTRY", "Available", "Occupied", "MH14DX7711", 0.0, "Direct check-in"),
            ((now - timedelta(hours=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), "B2", "Block B (Standard)", "VEHICLE_EXIT", "Occupied", "Available", "MH12ZZ4040", 100.0, "Duration: 2.0 hrs @ Rs. 50/hr"),
            ((now - timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), "D2", "Block D (VIP)", "RESERVE", "Available", "Reserved", "MH14VIP001", 0.0, "Reserved by Pradnya K."),
            ((now - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"), "E4", "Block E (Standard)", "RESERVE", "Available", "Reserved", "MH12JK3344", "0.0", "Reserved by Vikas S."),
        ]

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parking_slots")
            cursor.execute("DELETE FROM activity_logs")
            cursor.executemany("""
                INSERT INTO parking_slots
                (slot_id, zone, vehicle_type, hourly_rate, state, vehicle_number, reserved_by, reserved_at, occupied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, final_slots)
            cursor.executemany("""
                INSERT INTO activity_logs
                (timestamp, slot_id, zone, action, old_state, new_state, vehicle_number, fee, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_logs)
            conn.commit()

    def add_custom_slot(self, slot_id: str, zone: str, vehicle_type: str, hourly_rate: float) -> None:
        clean_id = slot_id.upper().strip()
        if not clean_id:
            raise ValueError("Slot ID cannot be empty.")
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT slot_id FROM parking_slots WHERE slot_id = ?", (clean_id,))
            if cursor.fetchone():
                raise ValueError(f"Slot {clean_id} already exists.")
            cursor.execute("""
                INSERT INTO parking_slots
                (slot_id, zone, vehicle_type, hourly_rate, state, vehicle_number, reserved_by, reserved_at, occupied_at)
                VALUES (?, ?, ?, ?, 'Available', NULL, NULL, NULL, NULL)
            """, (clean_id, zone.strip(), vehicle_type.strip(), float(hourly_rate)))
            conn.commit()

    def delete_slot(self, slot_id: str) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state FROM parking_slots WHERE slot_id = ?", (slot_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Slot {slot_id} not found.")
            if row["state"] != "Available":
                raise ValueError(f"Cannot delete Slot {slot_id} while it is {row['state']}.")
            cursor.execute("DELETE FROM parking_slots WHERE slot_id = ?", (slot_id,))
            conn.commit()

    def get_all_slots(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parking_slots ORDER BY slot_id ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_slot(self, slot_id: str) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parking_slots WHERE slot_id = ?", (slot_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}

    def update_slot(self, slot) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE parking_slots
                SET state = ?, vehicle_number = ?, reserved_by = ?, reserved_at = ?, occupied_at = ?
                WHERE slot_id = ?
            """, (
                slot.state_name,
                slot.vehicle_number,
                slot.reserved_by,
                slot.reserved_at,
                slot.occupied_at,
                slot.slot_id
            ))
            conn.commit()

    def log_activity(
        self,
        slot_id: str,
        zone: str,
        action: str,
        old_state: str,
        new_state: str,
        vehicle_number: str,
        fee: float,
        details: str
    ) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs
                (timestamp, slot_id, zone, action, old_state, new_state, vehicle_number, fee, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                slot_id,
                zone,
                action,
                old_state,
                new_state,
                vehicle_number,
                fee,
                details
            ))
            conn.commit()

    def get_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
