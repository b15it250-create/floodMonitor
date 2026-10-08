import os
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.database import init_db, connect
from utils.logic import (
    flood_risk_score,
    risk_label,
    flood_report_priority,
    sensor_anomaly,
    shelter_occupancy_percent,
    nearest_shelters,
    estimate_image_flood_coverage
)
from utils.services import ask_ai, get_weather

load_dotenv()
init_db()

APP_NAME = os.getenv("APP_NAME", "FloodWatch AI")
REGION_NAME = os.getenv("REGION_NAME", "Demo Flood-Prone Region")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
WARNING_LEVEL = float(os.getenv("WARNING_RIVER_LEVEL_M", "4.5"))
DANGER_LEVEL = float(os.getenv("DANGER_RIVER_LEVEL_M", "5.5"))
CRITICAL_LEVEL = float(os.getenv("CRITICAL_RIVER_LEVEL_M", "6.2"))
HEAVY_RAIN = float(os.getenv("HEAVY_RAIN_24H_MM", "120"))
CRITICAL_RISK_THRESHOLD = float(os.getenv("CRITICAL_RISK_THRESHOLD", "80"))
CONTROL_LAT = float(os.getenv("CONTROL_LAT", "26.1445"))
CONTROL_LON = float(os.getenv("CONTROL_LON", "91.7362"))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title=APP_NAME, page_icon="🌊", layout="wide")


def df_query(sql, params=()):
    conn = connect()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql, params=()):
    conn = connect()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def sensor_snapshot():
    sensors = df_query("SELECT * FROM sensors WHERE status='Active'")
    rows = []

    for _, sensor in sensors.iterrows():
        readings = df_query(
            "SELECT * FROM sensor_readings WHERE sensor_id=? ORDER BY reading_time DESC LIMIT 2",
            (int(sensor["id"]),)
        )

        if readings.empty:
            continue

        current = readings.iloc[0]
        previous_level = None
        hours_delta = 0

        if len(readings) > 1:
            prev = readings.iloc[1]
            previous_level = float(prev["water_level_m"])
            t1 = pd.to_datetime(current["reading_time"])
            t0 = pd.to_datetime(prev["reading_time"])
            hours_delta = max((t1-t0).total_seconds()/3600, 0.01)

        anomaly = sensor_anomaly(
            float(current["water_level_m"]),
            previous_level,
            hours_delta
        )

        risk = flood_risk_score(
            float(current["water_level_m"]),
            WARNING_LEVEL,
            DANGER_LEVEL,
            float(current["rainfall_24h_mm"]),
            HEAVY_RAIN,
            float(current["soil_saturation_pct"]),
            float(current["drainage_blockage_pct"]),
            anomaly["rise_rate"]
        )

        rows.append({
            "sensor_id": int(sensor["id"]),
            "sensor_name": sensor["sensor_name"],
            "ward": sensor["ward"],
            "river_name": sensor["river_name"],
            "lat": sensor["lat"],
            "lon": sensor["lon"],
            "water_level_m": float(current["water_level_m"]),
            "rainfall_24h_mm": float(current["rainfall_24h_mm"]),
            "soil_saturation_pct": float(current["soil_saturation_pct"]),
            "drainage_blockage_pct": float(current["drainage_blockage_pct"]),
            "rise_rate_mph": anomaly["rise_rate"],
            "anomaly": anomaly["message"],
            "risk_score": risk,
            "risk_level": risk_label(risk),
            "reading_time": current["reading_time"]
        })

    return pd.DataFrame(rows)


def refresh_report_priorities():
    reports = df_query("SELECT * FROM flood_reports WHERE status!='Resolved'")
    for _, row in reports.iterrows():
        score = flood_report_priority(
            float(row["water_depth_cm"]),
            int(row["people_affected"]),
            int(row["houses_affected"]),
            int(row["road_blocked"]),
            row["created_at"]
        )
        execute(
            "UPDATE flood_reports SET priority_score=?, updated_at=? WHERE id=?",
            (score, datetime.now().isoformat(timespec="seconds"), int(row["id"]))
        )


refresh_report_priorities()

with st.sidebar:
    st.title(APP_NAME)
    st.caption(f"Flood detection & early warning for {REGION_NAME}")

    role = st.selectbox("Use as", ["Citizen", "Field Responder", "Flood Control Admin"])

    if role == "Citizen":
        page = st.radio(
            "Navigation",
            [
                "Citizen Home",
                "Report Flooding",
                "Find Shelter",
                "Flood Safety Guide",
                "Flood AI Assistant"
            ]
        )
    elif role == "Field Responder":
        page = st.radio(
            "Navigation",
            [
                "Responder Dashboard",
                "Priority Flood Reports",
                "Sensor Monitor",
                "Shelter Operations"
            ]
        )
    else:
        page = st.radio(
            "Navigation",
            [
                "Flood Command Dashboard",
                "Early Warning Center",
                "Risk Hotspots",
                "Sensor Data Entry",
                "Image Flood Estimator",
                "Weather Monitor",
                "AI Flood Advisor"
            ]
        )

    st.divider()
    st.caption("SQLite • optional AI • optional live weather")


if page == "Citizen Home":
    st.title(f"🌊 {APP_NAME}")
    st.subheader("Detect early. Warn faster. Evacuate safer.")

    sensors = sensor_snapshot()
    reports = df_query("SELECT * FROM flood_reports WHERE status!='Resolved'")

    high_risk = int((sensors["risk_score"] >= 70).sum()) if not sensors.empty else 0
    critical = int((sensors["risk_score"] >= CRITICAL_RISK_THRESHOLD).sum()) if not sensors.empty else 0

    c1,c2,c3 = st.columns(3)
    c1.metric("Active Flood Reports", len(reports))
    c2.metric("High-Risk Sensors", high_risk)
    c3.metric("Critical Sensors", critical)

    if critical:
        st.error(
            "Critical flood risk is detected in the demo monitoring data. "
            "In a real deployment, follow official evacuation instructions immediately."
        )
    else:
        st.info("Monitor official alerts and avoid entering floodwater.")

    st.write(
        "Use this platform to report local flooding, find nearby shelters, "
        "check safety guidance, and view flood warnings."
    )


elif page == "Report Flooding":
    st.title("Report Flooding")

    with st.form("flood_report", clear_on_submit=True):
        c1,c2 = st.columns(2)

        with c1:
            reporter = st.text_input("Reporter Name")
            phone = st.text_input("Phone")
            ward = st.selectbox("Ward / Zone", ["Ward 1","Ward 2","Ward 3","Ward 4","Ward 5"])
            location = st.text_input("Location / Landmark")
            lat = st.number_input("Latitude", value=CONTROL_LAT, format="%.6f")
            lon = st.number_input("Longitude", value=CONTROL_LON, format="%.6f")

        with c2:
            depth = st.number_input("Approx. Water Depth (cm)", 0.0, 500.0, 20.0, step=5.0)
            affected = st.number_input("People Affected", 0, 10000, 1)
            houses = st.number_input("Houses Affected", 0, 5000, 0)
            road_blocked = st.checkbox("Road is blocked by floodwater")
            description = st.text_area("Description")
            photo = st.file_uploader("Optional Photo", type=["jpg","jpeg","png"])

        if st.form_submit_button("Submit Flood Report", use_container_width=True):
            if not reporter.strip() or not location.strip():
                st.error("Reporter name and location are required.")
            else:
                image_path = None

                if photo:
                    safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name.replace(' ','_')}"
                    p = UPLOAD_DIR / safe_name
                    p.write_bytes(photo.getbuffer())
                    image_path = str(p)

                now = datetime.now().isoformat(timespec="seconds")
                score = flood_report_priority(
                    depth, affected, houses, int(road_blocked), now
                )

                execute("""INSERT INTO flood_reports
                    (reporter_name,phone,ward,location_text,lat,lon,water_depth_cm,
                     people_affected,houses_affected,road_blocked,description,image_path,
                     status,priority_score,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?, 'Open',?,?,?)""",
                    (
                        reporter,phone,ward,location,lat,lon,depth,affected,houses,
                        int(road_blocked),description,image_path,score,now,now
                    )
                )
                st.success(f"Flood report submitted. Response priority: {score}/100")


elif page == "Find Shelter":
    st.title("Find Nearest Flood Shelter")

    lat = st.number_input("Your Latitude", value=CONTROL_LAT, format="%.6f")
    lon = st.number_input("Your Longitude", value=CONTROL_LON, format="%.6f")

    if st.button("Find Nearby Shelters", use_container_width=True):
        shelters = df_query("SELECT * FROM shelters WHERE status='Open'")
        ranked = nearest_shelters(lat,lon,shelters.to_dict("records"))

        if not ranked:
            st.warning("No shelter records available.")
        else:
            for shelter in ranked[:5]:
                with st.container(border=True):
                    pct = shelter_occupancy_percent(
                        int(shelter["occupied"]),
                        int(shelter["capacity"])
                    )

                    status = (
                        "FULL" if pct >= 100
                        else "NEAR FULL" if pct >= 90
                        else "AVAILABLE"
                    )

                    st.markdown(f"### {shelter['name']}")
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Distance", f"{shelter['distance_km']:.2f} km")
                    c2.metric("Occupancy", f"{pct:.1f}%")
                    c3.metric("Status", status)
                    st.write(shelter["address"])
                    st.caption(
                        f"Food units: {shelter['food_units']} | "
                        f"Water units: {shelter['water_units']} | "
                        f"Medical kits: {shelter['medical_kits']}"
                    )


elif page == "Flood Safety Guide":
    st.title("Flood Safety Guide")

    st.markdown("### Before Flooding")
    st.write(
        "• Keep medicines, documents, drinking water and emergency supplies ready.\n"
        "• Charge phones and power banks.\n"
        "• Know the nearest shelter and higher-ground route.\n"
        "• Monitor official rainfall and river-level alerts."
    )

    st.markdown("### During Flooding")
    st.write(
        "• Move to higher ground early when advised.\n"
        "• Never walk, swim or drive through moving floodwater.\n"
        "• Stay away from electric poles, wires and submerged equipment.\n"
        "• Keep children and elderly people away from contaminated water.\n"
        "• Follow official evacuation instructions."
    )

    st.markdown("### After Flooding")
    st.write(
        "• Return only when authorities say it is safe.\n"
        "• Treat floodwater as contaminated.\n"
        "• Check structures for damage before entering.\n"
        "• Photograph damage safely for records and relief claims."
    )


elif page == "Flood AI Assistant":
    st.title("Flood AI Assistant")
    st.caption("Works without an API key; Groq is used when configured in .env.")

    question = st.text_area(
        "Ask a flood-safety question",
        placeholder="The river is rising quickly. When should we evacuate?"
    )

    if st.button("Get Guidance", use_container_width=True):
        answer, mode = ask_ai(question, f"Region: {REGION_NAME}")
        st.warning(answer)
        st.caption(mode)


elif page == "Responder Dashboard":
    st.title("Flood Responder Dashboard")

    sensors = sensor_snapshot()
    reports = df_query("SELECT * FROM flood_reports WHERE status!='Resolved'")

    critical = int((sensors["risk_score"] >= CRITICAL_RISK_THRESHOLD).sum()) if not sensors.empty else 0
    affected = int(reports["people_affected"].sum()) if not reports.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Open Flood Reports", len(reports))
    c2.metric("Critical Sensors", critical)
    c3.metric("People Affected", affected)
    c4.metric("Shelters", int(df_query("SELECT COUNT(*) c FROM shelters WHERE status='Open'").iloc[0]["c"]))

    if not reports.empty:
        st.subheader("Top Response Priorities")
        st.dataframe(
            reports[
                ["id","ward","location_text","water_depth_cm","people_affected",
                 "houses_affected","road_blocked","priority_score","status"]
            ].sort_values("priority_score", ascending=False).head(10),
            use_container_width=True
        )


elif page == "Priority Flood Reports":
    st.title("Priority Flood Reports")

    reports = df_query(
        "SELECT * FROM flood_reports WHERE status!='Resolved' ORDER BY priority_score DESC"
    )

    if reports.empty:
        st.success("No active flood reports.")
    else:
        for _, row in reports.iterrows():
            with st.container(border=True):
                st.markdown(f"### #{int(row['id'])} — {row['location_text']} — {row['ward']}")

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Priority", f"{float(row['priority_score']):.1f}")
                c2.metric("Water Depth", f"{float(row['water_depth_cm']):.0f} cm")
                c3.metric("People Affected", int(row["people_affected"]))
                c4.metric("Houses", int(row["houses_affected"]))

                st.write(row["description"] or "No description")

                x,y = st.columns(2)
                with x:
                    if st.button("Mark Response Assigned", key=f"assigned_{int(row['id'])}", use_container_width=True):
                        execute(
                            "UPDATE flood_reports SET status='Assigned', updated_at=? WHERE id=?",
                            (datetime.now().isoformat(timespec="seconds"), int(row["id"]))
                        )
                        st.rerun()

                with y:
                    if st.button("Mark Resolved", key=f"resolved_{int(row['id'])}", use_container_width=True):
                        execute(
                            "UPDATE flood_reports SET status='Resolved', updated_at=? WHERE id=?",
                            (datetime.now().isoformat(timespec="seconds"), int(row["id"]))
                        )
                        st.rerun()


elif page == "Sensor Monitor":
    st.title("Flood Sensor Monitor")

    sensors = sensor_snapshot()

    if sensors.empty:
        st.warning("No sensor readings available.")
    else:
        st.dataframe(
            sensors[
                ["sensor_name","ward","river_name","water_level_m","rainfall_24h_mm",
                 "soil_saturation_pct","drainage_blockage_pct","rise_rate_mph",
                 "risk_score","risk_level","anomaly"]
            ],
            use_container_width=True
        )

        st.subheader("Current Sensor Risk")
        fig = px.bar(
            sensors.sort_values("risk_score", ascending=False),
            x="sensor_name",
            y="risk_score",
            color="risk_level",
            text_auto=True
        )
        fig.update_layout(yaxis_range=[0,100], xaxis_title="", yaxis_title="Flood Risk Score")
        st.plotly_chart(fig, use_container_width=True)


elif page == "Shelter Operations":
    st.title("Flood Shelter Operations")

    shelters = df_query("SELECT * FROM shelters ORDER BY ward,name")

    for _, row in shelters.iterrows():
        with st.container(border=True):
            pct = shelter_occupancy_percent(int(row["occupied"]),int(row["capacity"]))

            st.markdown(f"### {row['name']} — {row['ward']}")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Occupancy", f"{row['occupied']}/{row['capacity']}")
            c2.metric("Occupancy %", f"{pct:.1f}%")
            c3.metric("Food Units", int(row["food_units"]))
            c4.metric("Medical Kits", int(row["medical_kits"]))

            st.progress(min(pct/100,1.0))

            new_occ = st.number_input(
                "Update Occupancy",
                min_value=0,
                max_value=int(row["capacity"]),
                value=int(row["occupied"]),
                key=f"occ_{int(row['id'])}"
            )

            if st.button("Update Shelter", key=f"upd_{int(row['id'])}"):
                execute(
                    "UPDATE shelters SET occupied=? WHERE id=?",
                    (int(new_occ), int(row["id"]))
                )
                st.rerun()


elif page == "Flood Command Dashboard":
    st.title("Flood Command Dashboard")

    password = st.text_input("Admin Password", type="password")
    if password != ADMIN_PASSWORD:
        st.warning("Enter the admin password configured in .env.")
        st.stop()

    sensors = sensor_snapshot()
    reports = df_query("SELECT * FROM flood_reports")
    active = reports[reports["status"] != "Resolved"].copy() if not reports.empty else reports

    high_risk = int((sensors["risk_score"] >= 70).sum()) if not sensors.empty else 0
    affected = int(active["people_affected"].sum()) if not active.empty else 0
    houses = int(active["houses_affected"].sum()) if not active.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("High-Risk Sensors", high_risk)
    c2.metric("Active Reports", len(active))
    c3.metric("People Affected", affected)
    c4.metric("Houses Affected", houses)

    if not sensors.empty:
        st.subheader("Flood Risk by Monitoring Point")
        st.plotly_chart(
            px.bar(
                sensors.sort_values("risk_score",ascending=False),
                x="sensor_name",
                y="risk_score",
                color="risk_level",
                text_auto=True
            ),
            use_container_width=True
        )

        st.subheader("Monitoring Map")
        geo = sensors[["lat","lon"]].dropna()
        if not geo.empty:
            st.map(geo)

    if not active.empty:
        st.subheader("Flood Report Map")
        geo = active[["lat","lon"]].dropna()
        if not geo.empty:
            st.map(geo)


elif page == "Early Warning Center":
    st.title("Flood Early Warning Center")

    password = st.text_input("Admin Password", type="password", key="warningpass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    sensors = sensor_snapshot()

    if sensors.empty:
        st.info("No sensor data available.")
    else:
        for _, row in sensors.sort_values("risk_score",ascending=False).iterrows():
            with st.container(border=True):
                st.markdown(f"### {row['sensor_name']} — {row['ward']}")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Water Level", f"{row['water_level_m']:.2f} m")
                c2.metric("24h Rainfall", f"{row['rainfall_24h_mm']:.1f} mm")
                c3.metric("Rise Rate", f"{row['rise_rate_mph']:.2f} m/h")
                c4.metric("Risk", f"{row['risk_score']:.1f} — {row['risk_level']}")

                if row["risk_score"] >= CRITICAL_RISK_THRESHOLD:
                    message = (
                        f"CRITICAL flood risk at {row['sensor_name']} ({row['ward']}). "
                        f"Water level {row['water_level_m']:.2f} m, "
                        f"rainfall {row['rainfall_24h_mm']:.1f} mm/24h."
                    )
                    st.error(message)

                    if st.button("Create Critical Alert", key=f"alert_{int(row['sensor_id'])}"):
                        execute(
                            "INSERT INTO alerts (ward,alert_level,message,risk_score,created_at) VALUES (?,?,?,?,?)",
                            (
                                row["ward"],"CRITICAL",message,float(row["risk_score"]),
                                datetime.now().isoformat(timespec="seconds")
                            )
                        )
                        st.success("Alert logged.")
                elif row["risk_score"] >= 70:
                    st.warning("High flood risk. Increase monitoring and prepare evacuation resources.")
                elif row["risk_score"] >= 50:
                    st.info("Moderate flood risk. Continue close monitoring.")
                else:
                    st.success("Risk currently below major warning level.")


elif page == "Risk Hotspots":
    st.title("Ward Flood Risk Hotspots")

    password = st.text_input("Admin Password", type="password", key="hotspotpass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    sensors = sensor_snapshot()
    reports = df_query("SELECT * FROM flood_reports WHERE status!='Resolved'")

    wards = sorted(set(sensors["ward"].tolist()) | set(reports["ward"].tolist()))
    rows = []

    for ward in wards:
        ws = sensors[sensors["ward"] == ward]
        wr = reports[reports["ward"] == ward]

        sensor_risk = float(ws["risk_score"].max()) if not ws.empty else 0
        report_priority = float(wr["priority_score"].mean()) if not wr.empty else 0
        affected = int(wr["people_affected"].sum()) if not wr.empty else 0
        blocked = int(wr["road_blocked"].sum()) if not wr.empty else 0

        combined = min(
            100,
            sensor_risk*0.58
            + report_priority*0.24
            + min(affected,500)*0.025
            + blocked*8
        )

        rows.append({
            "ward":ward,
            "max_sensor_risk":round(sensor_risk,1),
            "avg_report_priority":round(report_priority,1),
            "people_affected":affected,
            "blocked_roads":blocked,
            "combined_risk":round(combined,1),
            "risk_level":risk_label(combined)
        })

    risk = pd.DataFrame(rows).sort_values("combined_risk",ascending=False)
    st.dataframe(risk,use_container_width=True)

    st.plotly_chart(
        px.bar(
            risk,
            x="ward",
            y="combined_risk",
            color="risk_level",
            text_auto=True
        ),
        use_container_width=True
    )


elif page == "Sensor Data Entry":
    st.title("Sensor Data Entry / IoT Simulation")

    password = st.text_input("Admin Password", type="password", key="sensorpass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    sensors = df_query("SELECT * FROM sensors WHERE status='Active' ORDER BY sensor_name")
    selected_name = st.selectbox("Sensor", sensors["sensor_name"].tolist())
    sensor = sensors[sensors["sensor_name"] == selected_name].iloc[0]

    with st.form("sensor_reading_form"):
        water_level = st.number_input("Water Level (m)", 0.0, 20.0, 4.0, step=0.05)
        rainfall = st.number_input("Rainfall in last 24h (mm)", 0.0, 1000.0, 80.0, step=5.0)
        soil = st.slider("Soil Saturation (%)",0,100,70)
        drainage = st.slider("Drainage Blockage (%)",0,100,30)

        if st.form_submit_button("Save Sensor Reading",use_container_width=True):
            execute("""INSERT INTO sensor_readings
                (sensor_id,water_level_m,rainfall_24h_mm,soil_saturation_pct,
                 drainage_blockage_pct,reading_time)
                VALUES (?,?,?,?,?,?)""",
                (
                    int(sensor["id"]),water_level,rainfall,soil,drainage,
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            st.success("Sensor reading added.")
            st.rerun()

    history = df_query(
        "SELECT * FROM sensor_readings WHERE sensor_id=? ORDER BY reading_time ASC",
        (int(sensor["id"]),)
    )

    if not history.empty:
        history["reading_time"] = pd.to_datetime(history["reading_time"])
        st.plotly_chart(
            px.line(
                history,
                x="reading_time",
                y="water_level_m",
                markers=True,
                title=f"Water Level Trend — {selected_name}"
            ),
            use_container_width=True
        )


elif page == "Image Flood Estimator":
    st.title("Image-Based Flood Coverage Estimator")
    st.caption(
        "Prototype computer-vision feature. It estimates visible water-like regions using color segmentation. "
        "It is useful for a hackathon demo but is not a certified flood-mapping system."
    )

    password = st.text_input("Admin Password", type="password", key="imagepass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    uploaded = st.file_uploader("Upload a flood/road image",type=["jpg","jpeg","png"])

    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()),dtype=np.uint8)
        image = cv2.imdecode(file_bytes,cv2.IMREAD_COLOR)

        if image is None:
            st.error("Could not read the image.")
        else:
            coverage, mask, overlay = estimate_image_flood_coverage(image)

            c1,c2 = st.columns(2)
            with c1:
                st.image(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),caption="Original Image",use_container_width=True)
            with c2:
                st.image(cv2.cvtColor(overlay,cv2.COLOR_BGR2RGB),caption="Estimated Water-Like Regions",use_container_width=True)

            st.metric("Estimated Visible Water Coverage",f"{coverage:.1f}%")

            if coverage >= 60:
                st.error("Large water-like area detected in the image.")
            elif coverage >= 30:
                st.warning("Moderate water-like area detected.")
            else:
                st.info("Limited water-like area detected.")


elif page == "Weather Monitor":
    st.title("Live Weather Monitor")

    password = st.text_input("Admin Password", type="password", key="weatherpass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    weather = get_weather()

    if not weather.get("available"):
        st.info(weather["message"])
        st.caption("Add OPENWEATHER_API_KEY and WEATHER_CITY to .env to enable live data.")
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("City",weather["city"])
        c2.metric("Temperature",f"{weather['temperature']:.1f} °C")
        c3.metric("Humidity",f"{weather['humidity']}%")
        c4.metric("Rain (1h)",f"{weather['rain_1h']} mm")
        st.success(f"Condition: {weather['condition']} | Wind: {weather['wind_speed']} m/s")


elif page == "AI Flood Advisor":
    st.title("AI Flood Command Advisor")

    password = st.text_input("Admin Password",type="password",key="aipass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    sensors = sensor_snapshot()
    reports = df_query("SELECT * FROM flood_reports WHERE status!='Resolved'")

    context = (
        f"Region: {REGION_NAME}. Sensors: {len(sensors)}. "
        f"Maximum current flood risk: {float(sensors['risk_score'].max()) if not sensors.empty else 0:.1f}. "
        f"Open flood reports: {len(reports)}. "
        f"People affected: {int(reports['people_affected'].sum()) if not reports.empty else 0}. "
        f"Houses affected: {int(reports['houses_affected'].sum()) if not reports.empty else 0}."
    )

    question = st.text_area(
        "Ask the advisor",
        placeholder="Which locations should receive evacuation attention first?"
    )

    if st.button("Generate Flood Recommendation",use_container_width=True):
        answer,mode=ask_ai(question,context)
        st.warning(answer)
        st.caption(mode)
