from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Optional
from patterns.observer_pattern import SlotSubject

class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted on a ParkingSlot."""
    pass

class SlotState(ABC):
    """Abstract State interface defining valid operations on a ParkingSlot."""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def reserve(self, slot: 'ParkingSlot', vehicle_number: str, reserved_by: str) -> str:
        pass

    @abstractmethod
    def cancel_reservation(self, slot: 'ParkingSlot') -> str:
        pass

    @abstractmethod
    def occupy(self, slot: 'ParkingSlot', vehicle_number: str) -> str:
        pass

    @abstractmethod
    def vacate(self, slot: 'ParkingSlot', simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        pass

class AvailableState(SlotState):
    """Concrete State representing an empty, unreserved parking slot."""
    @property
    def name(self) -> str:
        return "Available"

    def reserve(self, slot: 'ParkingSlot', vehicle_number: str, reserved_by: str) -> str:
        old_state = self.name
        slot.vehicle_number = vehicle_number.upper().strip()
        slot.reserved_by = reserved_by.strip()
        slot.reserved_at = datetime.now().isoformat()
        slot.set_state(ReservedState())
        msg = f"Slot {slot.slot_id} reserved for vehicle {slot.vehicle_number}."
        slot.notify({
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "action": "RESERVE",
            "old_state": old_state,
            "new_state": slot.state_name,
            "vehicle_number": slot.vehicle_number,
            "fee": 0.0,
            "details": f"Reserved by {slot.reserved_by}"
        })
        return msg

    def cancel_reservation(self, slot: 'ParkingSlot') -> str:
        raise InvalidStateTransitionError(f"Cannot cancel reservation: Slot {slot.slot_id} is currently Available.")

    def occupy(self, slot: 'ParkingSlot', vehicle_number: str) -> str:
        old_state = self.name
        slot.vehicle_number = vehicle_number.upper().strip()
        slot.occupied_at = datetime.now().isoformat()
        slot.set_state(OccupiedState())
        msg = f"Vehicle {slot.vehicle_number} parked in Slot {slot.slot_id}."
        slot.notify({
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "action": "VEHICLE_ENTRY",
            "old_state": old_state,
            "new_state": slot.state_name,
            "vehicle_number": slot.vehicle_number,
            "fee": 0.0,
            "details": "Direct check-in from Available state"
        })
        return msg

    def vacate(self, slot: 'ParkingSlot', simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        raise InvalidStateTransitionError(f"Cannot vacate: Slot {slot.slot_id} is already Available.")

class ReservedState(SlotState):
    """Concrete State representing a reserved parking slot awaiting vehicle arrival."""
    @property
    def name(self) -> str:
        return "Reserved"

    def reserve(self, slot: 'ParkingSlot', vehicle_number: str, reserved_by: str) -> str:
        raise InvalidStateTransitionError(f"Slot {slot.slot_id} is already Reserved for {slot.vehicle_number}.")

    def cancel_reservation(self, slot: 'ParkingSlot') -> str:
        old_state = self.name
        prev_vehicle = slot.vehicle_number
        slot.vehicle_number = None
        slot.reserved_by = None
        slot.reserved_at = None
        slot.set_state(AvailableState())
        msg = f"Reservation cancelled for Slot {slot.slot_id} (Vehicle: {prev_vehicle})."
        slot.notify({
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "action": "CANCEL_RESERVATION",
            "old_state": old_state,
            "new_state": slot.state_name,
            "vehicle_number": prev_vehicle or "-",
            "fee": 0.0,
            "details": "Reservation cancelled by user"
        })
        return msg

    def occupy(self, slot: 'ParkingSlot', vehicle_number: str) -> str:
        clean_vehicle = vehicle_number.upper().strip()
        if slot.vehicle_number and slot.vehicle_number != clean_vehicle:
            raise InvalidStateTransitionError(
                f"Slot {slot.slot_id} is reserved for {slot.vehicle_number}, cannot check in {clean_vehicle}."
            )
        old_state = self.name
        slot.vehicle_number = clean_vehicle
        slot.occupied_at = datetime.now().isoformat()
        slot.set_state(OccupiedState())
        msg = f"Reserved vehicle {slot.vehicle_number} checked into Slot {slot.slot_id}."
        slot.notify({
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "action": "RESERVED_CHECKIN",
            "old_state": old_state,
            "new_state": slot.state_name,
            "vehicle_number": slot.vehicle_number,
            "fee": 0.0,
            "details": f"Reservation fulfilled by {slot.reserved_by or 'Customer'}"
        })
        return msg

    def vacate(self, slot: 'ParkingSlot', simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        raise InvalidStateTransitionError(
            f"Cannot vacate a Reserved slot ({slot.slot_id}). Cancel the reservation instead."
        )

class OccupiedState(SlotState):
    """Concrete State representing an actively occupied parking slot."""
    @property
    def name(self) -> str:
        return "Occupied"

    def reserve(self, slot: 'ParkingSlot', vehicle_number: str, reserved_by: str) -> str:
        raise InvalidStateTransitionError(f"Cannot reserve: Slot {slot.slot_id} is currently Occupied.")

    def cancel_reservation(self, slot: 'ParkingSlot') -> str:
        raise InvalidStateTransitionError(f"Cannot cancel reservation: Slot {slot.slot_id} is Occupied.")

    def occupy(self, slot: 'ParkingSlot', vehicle_number: str) -> str:
        raise InvalidStateTransitionError(
            f"Slot {slot.slot_id} is already Occupied by {slot.vehicle_number}."
        )

    def vacate(self, slot: 'ParkingSlot', simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        old_state = self.name
        departing_vehicle = slot.vehicle_number or "UNKNOWN"
        fee, duration_hrs = slot.calculate_fee(simulated_hours)

        slot.vehicle_number = None
        slot.reserved_by = None
        slot.reserved_at = None
        slot.occupied_at = None
        slot.set_state(AvailableState())

        msg = (
            f"Vehicle {departing_vehicle} exited Slot {slot.slot_id}. "
            f"Duration: {duration_hrs:.1f} hrs | Parking Fee: Rs. {fee:.2f}"
        )
        slot.notify({
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "action": "VEHICLE_EXIT",
            "old_state": old_state,
            "new_state": slot.state_name,
            "vehicle_number": departing_vehicle,
            "fee": fee,
            "details": f"Duration: {duration_hrs:.1f} hrs @ Rs. {slot.hourly_rate:.0f}/hr"
        })
        return msg, fee

STATE_MAP = {
    "Available": AvailableState,
    "Reserved": ReservedState,
    "Occupied": OccupiedState
}

class ParkingSlot(SlotSubject):
    """Context class in the State Pattern and Concrete Subject in the Observer Pattern."""
    def __init__(
        self,
        slot_id: str,
        zone: str,
        vehicle_type: str,
        hourly_rate: float,
        state_name: str = "Available",
        vehicle_number: Optional[str] = None,
        reserved_by: Optional[str] = None,
        reserved_at: Optional[str] = None,
        occupied_at: Optional[str] = None
    ):
        super().__init__()
        self.slot_id = slot_id
        self.zone = zone
        self.vehicle_type = vehicle_type
        self.hourly_rate = hourly_rate
        self.vehicle_number = vehicle_number
        self.reserved_by = reserved_by
        self.reserved_at = reserved_at
        self.occupied_at = occupied_at
        state_cls = STATE_MAP.get(state_name, AvailableState)
        self._state: SlotState = state_cls()

    @property
    def state_name(self) -> str:
        return self._state.name

    def set_state(self, new_state: SlotState) -> None:
        self._state = new_state

    def reserve(self, vehicle_number: str, reserved_by: str) -> str:
        return self._state.reserve(self, vehicle_number, reserved_by)

    def cancel_reservation(self) -> str:
        return self._state.cancel_reservation(self)

    def occupy(self, vehicle_number: str) -> str:
        return self._state.occupy(self, vehicle_number)

    def vacate(self, simulated_hours: Optional[float] = None) -> Tuple[str, float]:
        return self._state.vacate(self, simulated_hours)

    def calculate_fee(self, simulated_hours: Optional[float] = None) -> Tuple[float, float]:
        if simulated_hours is not None and simulated_hours > 0:
            hours = float(simulated_hours)
        elif self.occupied_at:
            try:
                start_dt = datetime.fromisoformat(self.occupied_at)
                elapsed_sec = (datetime.now() - start_dt).total_seconds()
                hours = max(1.0, round(elapsed_sec / 3600.0, 2))
            except ValueError:
                hours = 1.0
        else:
            hours = 1.0
        fee = round(hours * self.hourly_rate, 2)
        return fee, hours
