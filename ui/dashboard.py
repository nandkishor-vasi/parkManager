import streamlit as st
import pandas as pd
import plotly.express as px
from patterns.state_pattern import InvalidStateTransitionError
from services.parking_service import ParkingLotService


def inject_custom_css() -> None:
    st.markdown("""
    <style>
        /* Hide Streamlit Default Header */
        header[data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }
        .stApp {
            background-color: #F8F9FD !important;
            color: #1E293B !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 1420px !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
            color: #1E293B !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5 {
            color: #1E293B !important;
        }

        /* Sidebar Radio Buttons */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background-color: #F8FAFC !important;
            padding: 8px 12px !important;
            border-radius: 10px !important;
            margin-bottom: 6px !important;
            border: 1px solid #E2E8F0 !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            border-color: #635BFF !important;
            background-color: #EEF2FF !important;
        }

        /* Form Controls */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input[type="text"],
        input[type="number"] {
            background-color: #F8FAFC !important;
            color: #1E293B !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="select"] span,
        div[data-baseweb="input"] input {
            color: #1E293B !important;
            -webkit-text-fill-color: #1E293B !important;
        }

        /* Buttons */
        .stButton > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: #635BFF !important;
            color: #4F46E5 !important;
            background-color: #EEF2FF !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #635BFF 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 12px rgba(99, 91, 255, 0.3) !important;
        }
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span {
            color: #FFFFFF !important;
        }

        /* Brand Logo */
        .pm-logo {
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.5px;
            margin-bottom: 1.2rem;
            padding-left: 0.2rem;
        }
        .pm-logo .purple { color: #5B4DFF !important; display: block; }
        .pm-logo .dark { color: #1E293B !important; display: block; font-size: 1.25rem; font-weight: 700; }

        /* Top Header Bar */
        .pm-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            padding: 14px 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
            margin-bottom: 20px;
            border: 1px solid #E2E8F0;
        }

        /* Counter Pills */
        .pm-stats-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .pm-stats-pill {
            display: flex;
            align-items: center;
            gap: 10px;
            background: #F8FAFC;
            padding: 6px 14px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
        }
        .pm-stat-num {
            background: #FFFFFF;
            padding: 3px 8px;
            border-radius: 7px;
            font-weight: 800;
            color: #1E293B !important;
            font-size: 0.85rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .pm-stat-txt {
            color: #64748B !important;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .pm-rev-pill {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: #FFFFFF !important;
            padding: 8px 16px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.88rem;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        }

        /* 2D Architectural Lot Canvas */
        .pm-lot-canvas {
            position: relative;
            background: #FFFFFF;
            border-radius: 22px;
            padding: 28px 44px;
            box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
            border: 1px solid #E2E8F0;
        }
        .pm-gate-entry {
            position: absolute;
            right: 0;
            top: 32px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 0.88rem;
            color: #16A34A !important;
        }
        .pm-gate-entry-bar {
            width: 7px;
            height: 64px;
            background: #22C55E;
            border-radius: 6px 0 0 6px;
            box-shadow: -3px 0 12px rgba(34, 197, 94, 0.35);
        }
        .pm-gate-exit {
            position: absolute;
            right: 0;
            bottom: 32px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 0.88rem;
            color: #DC2626 !important;
        }
        .pm-gate-exit-bar {
            width: 7px;
            height: 64px;
            background: #EF4444;
            border-radius: 6px 0 0 6px;
            box-shadow: -3px 0 12px rgba(239, 68, 68, 0.35);
        }

        /* Driving Lane Arrows */
        .pm-lane-row {
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 8px 40px;
            color: #CBD5E1 !important;
            font-size: 1.55rem;
            font-weight: 900;
            letter-spacing: 2px;
            user-select: none;
        }

        /* Parking Block Grid */
        .pm-blocks-row {
            display: grid;
            grid-template-columns: 1fr 42px 1fr 42px 1fr;
            align-items: center;
            margin: 6px 0;
        }
        .pm-v-arrow {
            text-align: center;
            color: #CBD5E1 !important;
            font-size: 1.5rem;
            font-weight: 900;
        }
        .pm-block-table {
            width: 100%;
            border-collapse: collapse;
        }
        .pm-bay-cell {
            width: 50%;
            height: 54px;
            border-top: 1.5px solid #E2E8F0;
            border-bottom: 1.5px solid #E2E8F0;
            text-align: center;
            vertical-align: middle;
            position: relative;
            padding: 4px 8px;
            background-color: #FFFFFF;
        }
        .pm-bay-cell.left-col {
            border-right: 1.5px solid #E2E8F0;
        }
        .pm-bay-cell:hover {
            background-color: #F8FAFC;
        }
        .pm-bay-label {
            color: #94A3B8 !important;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .pm-car-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }
        .pm-plate-tag {
            font-size: 0.62rem;
            font-weight: 700;
            color: #334155 !important;
            background: #F1F5F9;
            padding: 2px 5px;
            border-radius: 4px;
            margin-top: 2px;
        }

        /* Bottom User Profile in Sidebar */
        .pm-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 10px;
            border-top: 1px solid #E2E8F0;
            margin-top: 16px;
        }
        .pm-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #635BFF 0%, #3B82F6 100%);
            color: #FFFFFF !important;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.85rem;
        }
    </style>
    """, unsafe_allow_html=True)


def get_topdown_car_svg(color_variant: str, facing: str = "right") -> str:
    palettes = {
        "white": {"body": "#F8FAFC", "stroke": "#94A3B8", "roof": "#FFFFFF", "glass": "#1E293B"},
        "red":   {"body": "#EF4444", "stroke": "#B91C1C", "roof": "#F87171", "glass": "#1E293B"},
        "blue":  {"body": "#2563EB", "stroke": "#1D4ED8", "roof": "#60A5FA", "glass": "#0F172A"},
    }
    p = palettes.get(color_variant, palettes["white"])
    rotate = "transform='rotate(180 42 18)'" if facing == "left" else ""
    parts = [
        '<svg width="84" height="36" viewBox="0 0 84 36" fill="none" xmlns="http://www.w3.org/2000/svg">',
        f'<g {rotate}>',
        '<rect x="6" y="5" width="72" height="28" rx="10" fill="rgba(15,23,42,0.12)" />',
        '<rect x="14" y="2" width="13" height="4" rx="2" fill="#0F172A" />',
        '<rect x="57" y="2" width="13" height="4" rx="2" fill="#0F172A" />',
        '<rect x="14" y="30" width="13" height="4" rx="2" fill="#0F172A" />',
        '<rect x="57" y="30" width="13" height="4" rx="2" fill="#0F172A" />',
        f'<rect x="5" y="4" width="74" height="28" rx="10" fill="{p["body"]}" stroke="{p["stroke"]}" stroke-width="1.5"/>',
        f'<path d="M52 7 L64 9 L64 27 L52 29 Z" fill="{p["glass"]}" />',
        f'<path d="M23 8 L14 10 L14 26 L23 28 Z" fill="{p["glass"]}" />',
        f'<path d="M26 6 L50 6 L48 9 L28 9 Z" fill="{p["glass"]}" />',
        f'<path d="M28 27 L48 27 L50 30 L26 30 Z" fill="{p["glass"]}" />',
        f'<rect x="25" y="9" width="26" height="18" rx="4" fill="{p["roof"]}" />',
        '<rect x="76" y="7" width="3" height="5" rx="1.5" fill="#FEF08A" />',
        '<rect x="76" y="24" width="3" height="5" rx="1.5" fill="#FEF08A" />',
        '<rect x="5" y="8" width="2.5" height="5" rx="1" fill="#DC2626" />',
        '<rect x="5" y="23" width="2.5" height="5" rx="1" fill="#DC2626" />',
        '</g></svg>'
    ]
    return "".join(parts)


def render_bay_cell_html(slot: dict, col_side: str) -> str:
    side_cls = "left-col" if col_side == "left" else "right-col"
    state = slot["state"]
    sid = slot["slot_id"]

    if state == "Available":
        inner = f'<span class="pm-bay-label">{sid}</span>'
    else:
        if state == "Reserved":
            car_color = "blue"
            badge_prefix = "RSV"
        else:
            red_slots = {"A4", "C2", "C5", "E2", "F1", "B3", "D6"}
            car_color = "red" if sid in red_slots else "white"
            badge_prefix = slot["vehicle_number"] or sid

        facing = "right" if col_side == "left" else "left"
        svg = get_topdown_car_svg(car_color, facing=facing)
        inner = (
            f'<div class="pm-car-wrap" title="Slot {sid} ({state}) - {slot["vehicle_number"] or ""}">'
            f'{svg}<span class="pm-plate-tag">{sid}: {badge_prefix}</span></div>'
        )

    return f'<td class="pm-bay-cell {side_cls}">{inner}</td>'


def render_block_table_html(block_code: str, slot_map: dict) -> str:
    rows_html = []
    for r in range(1, 5):
        left_id = f"{block_code}{r}"
        right_id = f"{block_code}{r+4}"
        left_slot = slot_map.get(left_id, {"slot_id": left_id, "state": "Available", "vehicle_number": None})
        right_slot = slot_map.get(right_id, {"slot_id": right_id, "state": "Available", "vehicle_number": None})
        rows_html.append(f"<tr>{render_bay_cell_html(left_slot, 'left')}{render_bay_cell_html(right_slot, 'right')}</tr>")
    return f'<table class="pm-block-table">{"".join(rows_html)}</table>'


def render_dashboard(service: ParkingLotService) -> None:
    inject_custom_css()
    analytics = service.get_analytics()
    slots = service.get_all_slots()

    if slots and "-" in slots[0]["slot_id"]:
        service.db.seed_sample_data()
        slots = service.get_all_slots()
        analytics = service.get_analytics()

    slot_map = {s["slot_id"]: s for s in slots}

    # ----------------- STREAMLINED LEFT SIDEBAR -----------------
    with st.sidebar:
        st.markdown('<div class="pm-logo"><span class="purple">Parking</span><span class="dark">Manager</span></div>', unsafe_allow_html=True)

        nav_page = st.radio(
            "Navigation",
            [
                "Parking Spaces",
                "Dashboard",
                "Booking & Check-In",
                "Reports & History",
                "Problems & Alerts",
                "Roles & Architecture"
            ],
            label_visibility="collapsed"
        )

        st.divider()
        st.markdown("**Quick Slot Action (State Pattern)**")
        slot_ids = [s["slot_id"] for s in slots]
        selected_slot_id = st.selectbox("Select Bay on Map", slot_ids, index=0)
        selected_slot = slot_map[selected_slot_id]

        state_badge = {
            "Available": "Available",
            "Reserved": "Reserved",
            "Occupied": "Occupied"
        }.get(selected_slot["state"], selected_slot["state"])
        st.caption(f"**{selected_slot_id}** ({selected_slot['zone']}) — {state_badge} | Rs. {selected_slot['hourly_rate']:.0f}/hr")

        action_choice = st.selectbox(
            "Transition Operation",
            ["Park Vehicle (Occupy)", "Reserve Bay (Blue Car)", "Cancel Reservation", "Vehicle Exit (Vacate)"]
        )

        if action_choice == "Park Vehicle (Occupy)":
            default_v = selected_slot["vehicle_number"] or ""
            v_no = st.text_input("Vehicle Plate", value=default_v, placeholder="e.g. MH14MQ2219")
            if st.button("Park Vehicle Now", type="primary", use_container_width=True):
                try:
                    msg = service.vehicle_entry(selected_slot_id, v_no)
                    st.toast(msg)
                    st.rerun()
                except (InvalidStateTransitionError, ValueError) as err:
                    st.error(str(err))

        elif action_choice == "Reserve Bay (Blue Car)":
            v_no = st.text_input("Vehicle Plate", placeholder="e.g. MH12AB1234")
            c_name = st.text_input("Reserved For", placeholder="e.g. Nandkishor V.")
            if st.button("Confirm Reservation", type="primary", use_container_width=True):
                try:
                    msg = service.reserve_slot(selected_slot_id, v_no, c_name)
                    st.toast(msg)
                    st.rerun()
                except (InvalidStateTransitionError, ValueError) as err:
                    st.error(str(err))

        elif action_choice == "Cancel Reservation":
            if st.button("Release Reservation", type="primary", use_container_width=True):
                try:
                    msg = service.cancel_reservation(selected_slot_id)
                    st.toast(msg)
                    st.rerun()
                except (InvalidStateTransitionError, ValueError) as err:
                    st.error(str(err))

        elif action_choice == "Vehicle Exit (Vacate)":
            sim_hrs = st.slider("Parking Duration (Hrs)", 0.5, 12.0, 2.0, 0.5)
            if st.button("Process Exit & Bill", type="primary", use_container_width=True):
                try:
                    msg, _ = service.vehicle_exit(selected_slot_id, simulated_hours=sim_hrs)
                    st.toast(msg)
                    st.rerun()
                except (InvalidStateTransitionError, ValueError) as err:
                    st.error(str(err))

        st.divider()
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("Empty Lot", use_container_width=True):
                service.db.initialize_clean_slots()
                service.notification_observer.notifications.clear()
                st.rerun()
        with c_btn2:
            if st.button("Demo Cars", use_container_width=True):
                service.db.seed_sample_data()
                service.notification_observer.notifications.clear()
                st.rerun()

        st.markdown(
            '<div class="pm-profile">'
            '<div class="pm-avatar">NV</div>'
            '<div>'
            '<div style="font-weight:700; font-size:0.86rem; color:#1E293B;">Nandkishor Vasi</div>'
            '<div style="font-size:0.74rem; color:#64748B;">Admin • PCCOE</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

    # ----------------- TOP HEADER BAR WITH REVENUE & COUNTERS -----------------
    filled_count = analytics["occupied"] + analytics["reserved"]
    empty_count = analytics["available"]
    total_rev = analytics["total_revenue"]

    topbar_html = (
        f'<div class="pm-topbar">'
        f'<div style="font-weight:800; font-size:1.1rem; color:#1E293B;">Parking Lot Management Canvas</div>'
        f'<div class="pm-stats-container">'
        f'<div class="pm-stats-pill">'
        f'<span class="pm-stat-num">{filled_count}</span><span class="pm-stat-txt">Filled</span>'
        f'<span class="pm-stat-num">{empty_count}</span><span class="pm-stat-txt">Empty</span>'
        f'</div>'
        f'<div class="pm-rev-pill">Revenue: Rs. {total_rev:.2f}</div>'
        f'</div></div>'
    )
    st.markdown(topbar_html, unsafe_allow_html=True)

    # ----------------- MAIN CONTENT AREA -----------------
    if nav_page == "Parking Spaces":
        block_a = render_block_table_html("A", slot_map)
        block_b = render_block_table_html("B", slot_map)
        block_c = render_block_table_html("C", slot_map)
        block_d = render_block_table_html("D", slot_map)
        block_e = render_block_table_html("E", slot_map)
        block_f = render_block_table_html("F", slot_map)

        lot_html = (
            f'<div class="pm-lot-canvas">'
            f'<div class="pm-gate-entry"><span>Entry</span><div class="pm-gate-entry-bar"></div></div>'
            f'<div class="pm-gate-exit"><span>Exit</span><div class="pm-gate-exit-bar"></div></div>'
            f'<div class="pm-lane-row"><span>&#129144;</span><span>&#129144;</span><span>&#129144;</span></div>'
            f'<div class="pm-blocks-row">'
            f'<div>{block_a}</div><div class="pm-v-arrow">&#129147;</div>'
            f'<div>{block_b}</div><div class="pm-v-arrow">&#129147;</div>'
            f'<div>{block_c}</div>'
            f'</div>'
            f'<div class="pm-lane-row" style="padding: 16px 40px;">'
            f'<span>&#129144; &#129146;</span><span>&#129144; &#129146;</span><span>&#129144; &#129146;</span>'
            f'</div>'
            f'<div class="pm-blocks-row">'
            f'<div>{block_d}</div><div class="pm-v-arrow">&#129147;</div>'
            f'<div>{block_e}</div><div class="pm-v-arrow">&#129147;</div>'
            f'<div>{block_f}</div>'
            f'</div>'
            f'<div class="pm-lane-row" style="margin-top: 6px;">'
            f'<span>&#129146;</span><span>&#129146;</span><span>&#129146;</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(lot_html, unsafe_allow_html=True)
        st.markdown(
            "<div style='margin-top:10px; font-size:0.85rem; color:#475569;'>"
            "<strong>Legend:</strong> White & Red Cars = <code>OccupiedState</code> | "
            "Blue Car = <code>ReservedState</code> | "
            "Bay Code (A1–F8) = <code>AvailableState</code>. "
            "Click <strong>Demo Cars</strong> in the sidebar to load initial sample traffic."
            "</div>",
            unsafe_allow_html=True
        )

    elif nav_page == "Dashboard":
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Bays", analytics["total"])
        k2.metric("Occupied Bays", analytics["occupied"], f"{analytics['occupancy_rate']}%")
        k3.metric("Reserved Bays", analytics["reserved"])
        k4.metric("Cumulative Revenue", f"Rs. {analytics['total_revenue']:.2f}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Block-wise Occupancy Breakdown")
            rows = []
            for z, counts in analytics["zone_stats"].items():
                for st_name in ["Available", "Reserved", "Occupied"]:
                    rows.append({"Block": z, "State": st_name, "Bays": counts[st_name]})
            fig_bar = px.bar(
                pd.DataFrame(rows), x="Block", y="Bays", color="State", barmode="group",
                color_discrete_map={"Available": "#CBD5E1", "Reserved": "#2563EB", "Occupied": "#EF4444"}
            )
            fig_bar.update_layout(height=360, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(color="#1E293B"))
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("##### State Distribution")
            df_pie = pd.DataFrame([
                {"State": "Available", "Count": analytics["available"]},
                {"State": "Reserved", "Count": analytics["reserved"]},
                {"State": "Occupied", "Count": analytics["occupied"]},
            ])
            fig_pie = px.pie(
                df_pie, names="State", values="Count", hole=0.5, color="State",
                color_discrete_map={"Available": "#E2E8F0", "Reserved": "#2563EB", "Occupied": "#5B4DFF"}
            )
            fig_pie.update_layout(height=360, paper_bgcolor="#FFFFFF", font=dict(color="#1E293B"))
            st.plotly_chart(fig_pie, use_container_width=True)

    elif nav_page == "Booking & Check-In":
        st.subheader("Interactive Reservation & Check-In Desk")
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            with st.form("reserve_form"):
                st.markdown("**Reserve an Available Bay (`AvailableState -> ReservedState`)**")
                avail_ids = [s["slot_id"] for s in slots if s["state"] == "Available"]
                r_slot = st.selectbox("Available Bay", avail_ids if avail_ids else ["None"])
                r_veh = st.text_input("Vehicle Number", placeholder="MH14MQ2219")
                r_name = st.text_input("Driver Name", placeholder="Nandkishor Vasi")
                if st.form_submit_button("Create Reservation", type="primary"):
                    try:
                        msg = service.reserve_slot(r_slot, r_veh, r_name)
                        st.success(msg)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        with col_form2:
            with st.form("exit_form"):
                st.markdown("**Process Vehicle Check-Out (`OccupiedState -> AvailableState`)**")
                occ_ids = [s["slot_id"] for s in slots if s["state"] == "Occupied"]
                e_slot = st.selectbox("Occupied Bay", occ_ids if occ_ids else ["None"])
                e_hrs = st.number_input("Billable Duration (Hours)", 0.5, 24.0, 2.0, 0.5)
                if st.form_submit_button("Complete Exit & Generate Bill", type="primary"):
                    try:
                        msg, _ = service.vehicle_exit(e_slot, simulated_hours=e_hrs)
                        st.success(msg)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    elif nav_page == "Reports & History":
        st.subheader("Live Audit Trail (`ActivityLoggerObserver` + SQLite)")
        logs = service.db.get_activity_logs(limit=100)
        if logs:
            df_l = pd.DataFrame(logs)[["timestamp", "slot_id", "zone", "action", "old_state", "new_state", "vehicle_number", "fee", "details"]]
            df_l.columns = ["Timestamp", "Bay", "Block", "Event", "Old State", "New State", "Vehicle", "Fee (Rs.)", "Details"]
            st.dataframe(df_l, use_container_width=True, hide_index=True)
        else:
            st.info("No state transitions logged yet.")

    elif nav_page == "Problems & Alerts":
        st.subheader("Live Observer Alert Stream (`NotificationServiceObserver`)")
        for note in service.notification_observer.notifications:
            st.info(note)
        if not service.notification_observer.notifications:
            st.caption("No new session alerts. Trigger a slot state change from the sidebar to see Observer broadcasts.")

    elif nav_page == "Roles & Architecture":
        st.subheader("Software Design Patterns Architecture")
        st.markdown("""
        - **State Pattern (`patterns/state_pattern.py`)**: `ParkingSlot` delegates `reserve()`, `cancel_reservation()`, `occupy()`, and `vacate()` to `AvailableState`, `ReservedState`, and `OccupiedState`.
        - **Observer Pattern (`patterns/observer_pattern.py`)**: Every valid transition on `ParkingSlot` (`SlotSubject`) broadcasts an event dictionary to `ActivityLoggerObserver`, `DashboardMetricsObserver`, and `NotificationServiceObserver`.
        """)