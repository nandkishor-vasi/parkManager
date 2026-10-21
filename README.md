# Smart Parking Management System (Live SQLite Edition)
**Software Design Patterns Case Study (State Pattern & Observer Pattern)**

## Live Database Architecture
- **No Fixed/Static `.db` File**: The ZIP package contains pure source code and documentation. When you run `streamlit run app.py`, `DatabaseManager` automatically creates a live `smart_parking.db` file on the fly with all slots initialized to `Available`.
- **Live Operations**:
  - Add or delete custom slots and zones live from the **➕ Manage Slots** tab.
  - Perform real-time vehicle check-ins, reservations, cancellations, and check-outs from the sidebar.
  - Choose between **Live Clock Elapsed Time** or **Simulated Duration Override** when billing exiting vehicles.
  - Toggle between an **Empty Lot (All Available)** and **Sample Demo Traffic** anytime with one click in the sidebar.

## Project Structure
```text
smart_parking_system/
├── app.py                        # Streamlit entry point
├── requirements.txt              # Python package dependencies
├── README.md                     # Setup & execution guide
├── patterns/
│   ├── state_pattern.py          # ParkingSlot Context & Available/Reserved/Occupied States
│   └── observer_pattern.py       # SlotSubject & Logger/Dashboard/Notification Observers
├── database/
│   └── db_manager.py             # Dynamic SQLite table creation & live CRUD operations
├── services/
│   └── parking_service.py        # Business logic coordinating State, Observers & DB
├── ui/
│   └── dashboard.py              # Interactive Streamlit UI, slot manager & live analytics
└── docs/
    └── uml_class_diagram.png     # UML Class Diagram matching the implementation
```

## Windows Setup & Execution Instructions
Open **Command Prompt (cmd)** or **PowerShell** inside the extracted `smart_parking_system` folder and run:

```powershell
# 1. Create a Python virtual environment
python -m venv venv

# 2. Activate the virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1
# Or on Command Prompt (cmd.exe):
# venv\Scripts\activate.bat

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit application (creates live smart_parking.db automatically)
streamlit run app.py
```
