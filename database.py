import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import math

DB_PATH = Path("data/floodwatch.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_name TEXT NOT NULL,
        ward TEXT NOT NULL,
        river_name TEXT NOT NULL,
        lat REAL,
        lon REAL,
        normal_level_m REAL NOT NULL,
        status TEXT DEFAULT 'Active'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id INTEGER NOT NULL,
        water_level_m REAL NOT NULL,
        rainfall_24h_mm REAL NOT NULL,
        soil_saturation_pct REAL NOT NULL,
        drainage_blockage_pct REAL NOT NULL,
        reading_time TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS flood_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_name TEXT NOT NULL,
        phone TEXT,
        ward TEXT NOT NULL,
        location_text TEXT NOT NULL,
        lat REAL,
        lon REAL,
        water_depth_cm REAL DEFAULT 0,
        people_affected INTEGER DEFAULT 0,
        houses_affected INTEGER DEFAULT 0,
        road_blocked INTEGER DEFAULT 0,
        description TEXT,
        image_path TEXT,
        status TEXT DEFAULT 'Open',
        priority_score REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS shelters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ward TEXT NOT NULL,
        address TEXT NOT NULL,
        lat REAL,
        lon REAL,
        capacity INTEGER NOT NULL,
        occupied INTEGER DEFAULT 0,
        food_units INTEGER DEFAULT 0,
        water_units INTEGER DEFAULT 0,
        medical_kits INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Open'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ward TEXT NOT NULL,
        alert_level TEXT NOT NULL,
        message TEXT NOT NULL,
        risk_score REAL NOT NULL,
        created_at TEXT NOT NULL
    )""")

    conn.commit()

    if cur.execute("SELECT COUNT(*) FROM sensors").fetchone()[0] == 0:
        seed_demo_data(conn)

    conn.close()

def seed_demo_data(conn):
    cur = conn.cursor()
    now = datetime.now()

    sensors = [
        ("River Gauge A","Ward 1","Brahmaputra Tributary",26.1450,91.7350,3.2,"Active"),
        ("River Gauge B","Ward 2","Local River",26.1434,91.7380,2.7,"Active"),
        ("Canal Sensor C","Ward 3","Drainage Canal",26.1478,91.7390,1.8,"Active"),
        ("Embankment Sensor D","Ward 4","Flood Channel",26.1491,91.7335,2.5,"Active")
    ]
    cur.executemany("""INSERT INTO sensors
        (sensor_name,ward,river_name,lat,lon,normal_level_m,status)
        VALUES (?,?,?,?,?,?,?)""", sensors)

    # Demo 24-hour readings
    sensor_ids = [r[0] for r in cur.execute("SELECT id FROM sensors ORDER BY id").fetchall()]
    base_levels = [4.2, 3.8, 2.2, 3.5]
    for idx, sensor_id in enumerate(sensor_ids):
        for h in range(24, 0, -3):
            t = now - timedelta(hours=h)
            level = base_levels[idx] + (24-h)*0.035 + math.sin(h/4)*0.08
            rainfall = max(0, 70 + (24-h)*2.5 + idx*8)
            soil = min(100, 62 + (24-h)*1.1 + idx*4)
            drainage = min(100, 25 + idx*10 + (24-h)*0.7)
            cur.execute("""INSERT INTO sensor_readings
                (sensor_id,water_level_m,rainfall_24h_mm,soil_saturation_pct,
                 drainage_blockage_pct,reading_time)
                VALUES (?,?,?,?,?,?)""",
                (sensor_id,round(level,2),round(rainfall,1),round(soil,1),round(drainage,1),t.isoformat(timespec="seconds")))

    shelters = [
        ("Higher Secondary School","Ward 1","Main Road",26.1456,91.7354,300,90,240,220,28,"Open"),
        ("Community Hall","Ward 2","Market Road",26.1439,91.7383,180,110,150,140,18,"Open"),
        ("College Auditorium","Ward 4","College Road",26.1494,91.7332,450,170,360,330,42,"Open")
    ]
    cur.executemany("""INSERT INTO shelters
        (name,ward,address,lat,lon,capacity,occupied,food_units,water_units,medical_kits,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", shelters)

    reports = [
        ("Rita","9000000011","Ward 2","Near weekly market",26.1436,91.7382,55,38,9,1,"Water entered market lane and nearby houses."),
        ("Aman","9000000012","Ward 1","Riverside colony",26.1452,91.7356,72,65,17,1,"Floodwater rising rapidly in low-lying houses."),
        ("Nisha","9000000013","Ward 3","Near primary school",26.1475,91.7388,28,18,4,0,"Waterlogging around school road.")
    ]

    for i,row in enumerate(reports):
        created = now - timedelta(hours=(i+1)*3)
        depth, people, houses, blocked = row[6],row[7],row[8],row[9]
        priority = min(100, depth*0.55 + people*0.25 + houses*1.3 + blocked*12 + (i+1)*2)
        cur.execute("""INSERT INTO flood_reports
            (reporter_name,phone,ward,location_text,lat,lon,water_depth_cm,
             people_affected,houses_affected,road_blocked,description,image_path,
             status,priority_score,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,NULL,'Open',?,?,?)""",
            (*row,priority,created.isoformat(timespec="seconds"),created.isoformat(timespec="seconds")))

    conn.commit()
