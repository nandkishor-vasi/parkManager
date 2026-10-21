from typing import List, Dict, Any, Tuple, Optional
from database.db_manager import DatabaseManager
from patterns.state_pattern import ParkingSlot
from patterns.observer_pattern import (
    ActivityLoggerObserver,
    DashboardMetricsObserver,
    NotificationServiceObserver
)

class ParkingLotService:
    """Facade/Service coordinating ParkingSlot State transitions, Observers, and SQLite persistence."""
    def __init__(
        self,
        db_manager: DatabaseManager,
        dashboard_observer: DashboardMetricsObserver,
        notification_observer: NotificationServiceObserver
    ):
        self.db = db_manager
        self.logger_observer = ActivityLoggerObserver(self.db)
        self.dashboard_observer = dashboard_observer
        self.notification_observer = notification_observer

    def _load_slot_entity(self, slot_id: str) -> ParkingSlot:
        data = self.db.get_slot(slot_id)
        if not data:
            raise ValueError(f"Slot {slot_id} not found.")
        slot = ParkingSlot(
            slot_id=data["slot_id"],
            zone=data["zone"],
            vehicle_type=data["vehicle_type"],
            hourly_rate=data["hourly_rate"],
            state_name=data["state"],
            vehicle_number=data["vehicle_number"],
            reserved_by=data["reserved_by"],
            reserved_at=data["reserved_at"],
            occupied_at=data["occupied_at"]
        )
        slot.attach(self.logger_observer)
        slot.attach(self.dashboard_observer)
        slot.attach(self.notification_observer)
        return slot

    def reserve_slot(self, slot_id: str, vehicle_number: str, reserved_by: str) -> str:
        if not vehicle_number.strip() or not reserved_by.strip():
            raise ValueError("Both Vehicle Number and Customer Name are required for reservation.")
        slot = self._load_slot_entity(slot_id)
        msg = slot.reserve(vehicle_number, reserved_by)
        self.db.update_slot(slot)
        return msg

    def cancel_reservation(self, slot_id: str) -> str:
        slot = self._load_slot_entity(slot_id)
        msg = slot.cancel_reservation()
        self.db.update_slot(slot)
        return msg

    def vehicle_entry(self, slot_id: str, vehicle_number: str) -> str:
        if not vehicle_number.strip():
            raise ValueError("Vehicle Number is required for entry.")
        slot = self._load_slot_entity(slot_id)
        msg = slot.occupy(vehicle_number)
        self.db.update_slot(slot)
        return msg

    def vehicle_exit(self, slot_id: str, simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        slot = self._load_slot_entity(slot_id)
        msg, fee = slot.vacate(simulated_hours=simulated_hours)
        self.db.update_slot(slot)
        return msg, fee

    def get_all_slots(self) -> List[Dict[str, Any]]:
        return self.db.get_all_slots()

    def get_analytics(self) -> Dict[str, Any]:
        slots = self.db.get_all_slots()
        logs = self.db.get_activity_logs(limit=200)

        total = len(slots)
        available = sum(1 for s in slots if s["state"] == "Available")
        reserved = sum(1 for s in slots if s["state"] == "Reserved")
        occupied = sum(1 for s in slots if s["state"] == "Occupied")
        total_revenue = sum(float(l.get("fee", 0.0) or 0.0) for l in logs)

        zone_stats: Dict[str, Dict[str, int]] = {}
        for s in slots:
            z = s["zone"]
            if z not in zone_stats:
                zone_stats[z] = {"Available": 0, "Reserved": 0, "Occupied": 0, "Total": 0}
            zone_stats[z][s["state"]] += 1
            zone_stats[z]["Total"] += 1

        return {
            "total": total,
            "available": available,
            "reserved": reserved,
            "occupied": occupied,
            "occupancy_rate": round((occupied / total) * 100, 1) if total else 0.0,
            "total_revenue": round(total_revenue, 2),
            "zone_stats": zone_stats
        }
