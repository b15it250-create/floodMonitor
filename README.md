# FloodWatch AI — Smart Flood Detection & Early Warning Platform

FloodWatch AI is a complete hackathon-ready flood detection, monitoring, early-warning, and response platform built with Python, Streamlit, SQLite, Plotly, OpenCV, and optional AI/weather integrations.

## Main Features

### Citizen Module
- Report flooding with GPS coordinates and optional photo
- Record water depth, people affected, houses affected, and blocked roads
- Find nearest flood shelters
- Flood safety guide
- AI/rule-based flood assistant

### Field Responder Module
- Priority flood-report queue
- Assign and resolve flood reports
- Sensor monitoring
- Shelter occupancy operations

### Flood Control Admin Module
- Flood Command Dashboard
- Early Warning Center
- Water-level monitoring
- Rainfall monitoring
- Soil-saturation monitoring
- Drainage-blockage monitoring
- Rapid-rise anomaly detection
- Ward flood-risk hotspots
- IoT sensor data simulation
- Image-based flood coverage estimator
- Optional live weather
- Optional AI flood command advisor

## Flood Risk Score

The flood-risk engine combines:

- Current river/water level
- Warning and danger levels
- 24-hour rainfall
- Soil saturation
- Drainage blockage
- Water-level rise rate

The result is converted to:

- LOW
- WATCH
- MODERATE
- HIGH
- CRITICAL

## Rapid Water-Level Detection

FloodWatch AI compares the latest sensor reading with the previous reading and calculates the water-level rise rate in metres per hour.

Fast changes trigger anomaly messages such as:

- Unusual water-level rise detected
- Rapid water-level rise detected

This helps identify flood danger before the absolute water level reaches the highest threshold.

## Citizen Flood Report Priority

Citizen reports receive a response-priority score based on:

- Reported water depth
- People affected
- Houses affected
- Whether a road is blocked
- Time since the report was submitted

## Image Flood Coverage Estimator

The project includes a prototype computer-vision module using OpenCV.

A user can upload a flood image and the system estimates visible water-like regions using broad blue/cyan and muddy-brown color segmentation.

The tool displays:

- Original image
- Highlighted water-like regions
- Estimated visible water coverage percentage

This feature is intended for hackathon demonstration and educational prototyping. It is not a scientific flood-mapping or satellite-analysis system.

## Flood Shelter Finder

Citizens can enter their GPS coordinates and receive nearby shelters ranked by geographic distance using the Haversine formula.

The basic shelter finder does not require a paid map API.

## Optional Live Weather

Add an OpenWeather API key inside `.env`:

```env
OPENWEATHER_API_KEY=your_key
WEATHER_CITY=Guwahati
```

The Weather Monitor can then display:

- Temperature
- Humidity
- Wind speed
- Rainfall in the last hour
- Current weather condition

## Optional AI

Add a Groq API key:

```env
GROQ_API_KEY=your_key
```

When no API key is available, FloodWatch AI automatically uses built-in flood-safety guidance.

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenCV
- NumPy
- Requests
- python-dotenv
- Local image uploads

## Project Structure

```text
floodwatch_ai_flood_detection/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── HOW_IBM_BOB_WAS_USED.md
├── run_app.bat
├── .streamlit/
│   └── config.toml
├── data/
│   └── floodwatch.db
├── uploads/
└── utils/
    ├── database.py
    ├── logic.py
    └── services.py
```

## Installation

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Windows users can also run:

```text
run_app.bat
```

## Default Admin Password

```text
admin123
```

Change it in `.env`.

## Problem Statement

Floods can develop quickly due to intense rainfall, rising river levels, saturated soil, blocked drainage, embankment failure, or prolonged upstream rainfall. In many vulnerable areas, flood information is scattered across manual river gauges, local observations, citizen phone calls, social media, and government reports. By the time the danger becomes obvious, roads may already be blocked, homes may be inundated, and evacuation may become difficult.

Traditional flood monitoring may focus mainly on water level while ignoring other useful risk indicators such as rainfall, soil saturation, drainage blockage, and the rate at which water is rising. Citizens may also have no simple way to report localized flooding or find the nearest shelter. Emergency teams need a single system that combines sensor information, local reports, risk levels, shelters, and response priorities.

There is therefore a need for a low-cost flood-detection and early-warning platform that can combine multiple flood indicators, identify abnormal water-level changes, detect high-risk locations, receive citizen flood reports, and support faster evacuation and response.

## Solution Statement

FloodWatch AI is a smart flood detection, early-warning, and response platform built using Python, Streamlit, SQLite, Plotly, and OpenCV.

The system monitors water level, 24-hour rainfall, soil saturation, drainage blockage, and water-level rise rate. These factors are combined into an automatic flood-risk score, allowing monitoring points to be classified as LOW, WATCH, MODERATE, HIGH, or CRITICAL.

A sensor-anomaly engine detects unusually rapid increases in water level, while an Early Warning Center highlights locations that may require evacuation preparation. Administrators can also enter simulated IoT sensor readings to demonstrate how the platform would work with real sensors.

Citizens can report flooding with GPS coordinates, estimated water depth, affected people, affected houses, road blockage information, and photo evidence. Reports receive a response-priority score so responders can focus on the most serious locations first.

The platform includes ward-level flood-risk hotspot analysis, shelter occupancy management, a nearest-shelter finder, flood-safety guidance, an image-based visible-water estimator, optional live weather integration, and an optional AI flood command advisor.

The core platform remains functional without paid APIs.

## Hackathon Pitch

"FloodWatch AI turns scattered flood information into an actionable early-warning system. It combines river level, rainfall, soil saturation, drainage blockage, rapid-rise detection, citizen flood reports, shelters, and AI-assisted response planning in one low-cost platform designed to help communities detect floods earlier and evacuate more safely."

## Suggested Demo Flow

1. Admin enters a new high river-level sensor reading.
2. FloodWatch calculates an increased flood-risk score.
3. Rapid water-level rise is detected.
4. The Early Warning Center marks the sensor HIGH or CRITICAL.
5. A citizen reports 70 cm of floodwater with houses affected.
6. The report receives a high response-priority score.
7. The responder dashboard shows the report near the top.
8. The citizen uses the nearest-shelter finder.
9. Admin reviews ward-level flood hotspots.
10. A flood image is uploaded to demonstrate water-coverage estimation.
11. Live weather can be displayed when an API key is configured.
12. The AI Flood Advisor suggests response priorities.

## Future Improvements

- Real IoT ultrasonic river sensors
- Automated rainfall gauges
- River-basin upstream sensor network
- SMS/WhatsApp flood alerts
- Satellite flood mapping
- Drone flood imagery
- GIS floodplain layers
- Machine-learning flood forecasting
- Rainfall forecast integration
- Historical flood-model training
- Automatic siren/alert triggering
- Offline mobile app
- Government emergency-system integration
