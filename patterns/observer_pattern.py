from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

class SlotObserver(ABC):
    """Abstract Observer interface for receiving ParkingSlot state change updates."""
    @abstractmethod
    def update(self, event_data: Dict[str, Any]) -> None:
        pass

class SlotSubject(ABC):
    """Abstract Subject interface for managing observers."""
    def __init__(self):
        self._observers: List[SlotObserver] = []

    def attach(self, observer: SlotObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: SlotObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_data: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event_data)

class ActivityLoggerObserver(SlotObserver):
    """Concrete Observer that logs all state transitions to SQLite."""
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def update(self, event_data: Dict[str, Any]) -> None:
        self.db_manager.log_activity(
            slot_id=event_data.get("slot_id"),
            zone=event_data.get("zone"),
            action=event_data.get("action"),
            old_state=event_data.get("old_state"),
            new_state=event_data.get("new_state"),
            vehicle_number=event_data.get("vehicle_number", "-"),
            fee=event_data.get("fee", 0.0),
            details=event_data.get("details", "")
        )

class DashboardMetricsObserver(SlotObserver):
    """Concrete Observer that updates real-time dashboard summary metrics in memory/session."""
    def __init__(self):
        self.last_updated: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.recent_events: List[Dict[str, Any]] = []

    def update(self, event_data: Dict[str, Any]) -> None:
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.recent_events.insert(0, event_data)
        self.recent_events = self.recent_events[:10]

class NotificationServiceObserver(SlotObserver):
    """Concrete Observer that generates user/system alerts on state changes."""
    def __init__(self):
        self.notifications: List[str] = []

    def update(self, event_data: Dict[str, Any]) -> None:
        slot_id = event_data.get("slot_id")
        action = event_data.get("action")
        vehicle = event_data.get("vehicle_number", "N/A")
        old_s = event_data.get("old_state")
        new_s = event_data.get("new_state")
        fee = event_data.get("fee", 0.0)

        msg = f"[{datetime.now().strftime('%H:%M:%S')}] Slot {slot_id}: {action} ({old_s} -> {new_s}) | Vehicle: {vehicle}"
        if fee and fee > 0:
            msg += f" | Fee Charged: Rs. {fee:.2f}"
        self.notifications.insert(0, msg)
        self.notifications = self.notifications[:15]
