import streamlit as st
from database.db_manager import DatabaseManager
from patterns.observer_pattern import DashboardMetricsObserver, NotificationServiceObserver
from services.parking_service import ParkingLotService
from ui.dashboard import render_dashboard

st.set_page_config(
    page_title="ParkingManager — Smart Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_service() -> ParkingLotService:
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = DatabaseManager("smart_parking_live.db")
    if "dashboard_observer" not in st.session_state:
        st.session_state.dashboard_observer = DashboardMetricsObserver()
    if "notification_observer" not in st.session_state:
        st.session_state.notification_observer = NotificationServiceObserver()

    return ParkingLotService(
        db_manager=st.session_state.db_manager,
        dashboard_observer=st.session_state.dashboard_observer,
        notification_observer=st.session_state.notification_observer
    )

def main() -> None:
    service = get_service()
    render_dashboard(service)

if __name__ == "__main__":
    main()
