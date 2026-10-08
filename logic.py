from datetime import datetime
import math

def flood_risk_score(water_level_m, warning_level_m, danger_level_m,
                     rainfall_24h_mm, heavy_rain_mm,
                     soil_saturation_pct, drainage_blockage_pct,
                     trend_m_per_hour=0.0):
    if danger_level_m <= warning_level_m:
        danger_level_m = warning_level_m + 1.0

    if water_level_m <= warning_level_m:
        level_component = (water_level_m / max(warning_level_m,0.1)) * 35
    else:
        level_component = 35 + (
            (water_level_m-warning_level_m) /
            (danger_level_m-warning_level_m)
        ) * 25

    rain_component = min(rainfall_24h_mm / max(heavy_rain_mm,1), 1.5) * 18
    soil_component = min(soil_saturation_pct,100) * 0.10
    drainage_component = min(drainage_blockage_pct,100) * 0.08
    trend_component = min(max(trend_m_per_hour,0),1.5) * 8

    return round(min(level_component + rain_component + soil_component + drainage_component + trend_component,100),1)

def risk_label(score):
    if score >= 85: return "CRITICAL"
    if score >= 70: return "HIGH"
    if score >= 50: return "MODERATE"
    if score >= 30: return "WATCH"
    return "LOW"

def flood_report_priority(depth_cm, people_affected, houses_affected, road_blocked, created_at):
    try:
        created = datetime.fromisoformat(created_at)
    except Exception:
        created = datetime.now()

    age_hours = max(0,(datetime.now()-created).total_seconds()/3600)

    score = (
        min(depth_cm,300)*0.45
        + min(people_affected,1000)*0.18
        + min(houses_affected,300)*0.9
        + int(bool(road_blocked))*12
        + min(age_hours,48)*0.35
    )
    return round(min(score,100),1)

def sensor_anomaly(current_level, previous_level, hours_delta):
    if previous_level is None or hours_delta <= 0:
        return {"anomaly":False,"rise_rate":0.0,"message":"Insufficient historical data"}

    rate = (current_level-previous_level)/hours_delta

    if rate >= 0.5:
        return {"anomaly":True,"rise_rate":round(rate,2),"message":"Rapid water-level rise detected"}
    if rate >= 0.25:
        return {"anomaly":True,"rise_rate":round(rate,2),"message":"Unusual water-level rise detected"}

    return {"anomaly":False,"rise_rate":round(rate,2),"message":"Water-level change within expected range"}

def shelter_occupancy_percent(occupied, capacity):
    return round((occupied/capacity)*100,1) if capacity else 0

def haversine_km(lat1,lon1,lat2,lon2):
    R=6371.0
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp,dl=math.radians(lat2-lat1),math.radians(lon2-lon1)
    a=math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))

def nearest_shelters(lat,lon,shelters):
    result=[]
    for s in shelters:
        row=dict(s)
        if row.get("lat") is None or row.get("lon") is None:
            continue
        row["distance_km"]=round(haversine_km(lat,lon,float(row["lat"]),float(row["lon"])),2)
        result.append(row)
    return sorted(result,key=lambda x:x["distance_km"])

def estimate_image_flood_coverage(image_bgr):
    import cv2
    import numpy as np

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # Broad blue/cyan range for visible water.
    lower_blue = np.array([85, 35, 30])
    upper_blue = np.array([135, 255, 255])
    blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Brown/muddy floodwater heuristic.
    lower_brown = np.array([5, 25, 25])
    upper_brown = np.array([30, 220, 210])
    brown = cv2.inRange(hsv, lower_brown, upper_brown)

    mask = cv2.bitwise_or(blue, brown)
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)

    coverage = (mask>0).mean()*100
    overlay = image_bgr.copy()
    overlay[mask>0] = (
        0.65*overlay[mask>0] + 0.35*np.array([255,80,20])
    ).astype(np.uint8)

    return round(float(coverage),1), mask, overlay
