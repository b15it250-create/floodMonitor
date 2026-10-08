# How IBM Bob Was Used in FloodWatch AI

## Overview

IBM Bob was used as an AI coding assistant during the development of FloodWatch AI. It supported requirement analysis, architecture planning, code generation, refactoring, debugging, environment configuration, API integration, computer-vision prototyping, validation, and documentation.

The developer remained responsible for selecting the final project features, reviewing generated code, testing workflows, validating flood-safety logic, and preparing the final demonstration.

## 1. Ask Mode

IBM Bob was initially used in Ask Mode to study the flood-detection problem.

Example questions included:

- Which variables are useful for flood-risk detection?
- How can water-level rise rate improve early warning?
- How can rainfall, soil saturation, and drainage blockage be combined with river level?
- How can citizen flood reports be prioritized?
- How can the nearest shelter be found without a paid maps API?
- What computer-vision feature can be demonstrated using flood images?
- How should optional AI and weather APIs be configured?

Ask Mode helped identify these modules:

- River/water-level monitoring
- Rainfall monitoring
- Soil-saturation monitoring
- Drainage-blockage monitoring
- Rapid-rise anomaly detection
- Flood-risk scoring
- Citizen flood reporting
- Flood-report priority scoring
- Shelter management
- Nearest-shelter search
- Ward flood-risk hotspots
- Image-based flood estimation
- Weather integration
- AI flood advisor

## 2. Plan Mode

IBM Bob was used in Plan Mode to organize the project before implementation.

The architecture was separated into:

```text
app.py
utils/database.py
utils/logic.py
utils/services.py
.env
.env.example
README.md
HOW_IBM_BOB_WAS_USED.md
```

### `app.py`

Responsible for:

- Citizen interface
- Responder interface
- Flood-control admin interface
- Forms
- Sensor dashboards
- Maps
- Charts
- Image upload
- Shelter management

### `utils/database.py`

Responsible for:

- SQLite connection
- Sensor registration
- Sensor readings
- Flood reports
- Shelters
- Alerts
- Demo data

### `utils/logic.py`

Responsible for:

- Flood-risk score
- Risk labels
- Citizen-report priority
- Sensor anomaly detection
- Shelter distance
- Image flood-coverage estimation

### `utils/services.py`

Responsible for:

- Groq AI integration
- Rule-based flood guidance
- OpenWeather integration
- API fallback and error handling

## 3. Agent Mode

IBM Bob was used in Agent Mode to help implement the project across multiple files.

It assisted with:

- Creating the SQLite schema
- Generating demo sensor data
- Creating flood-report forms
- Adding GPS and photo support
- Implementing the flood-risk algorithm
- Adding rapid-rise anomaly detection
- Building sensor dashboards
- Creating the Early Warning Center
- Implementing flood-report prioritization
- Building shelter workflows
- Adding nearest-shelter calculation
- Creating risk-hotspot analytics
- Adding OpenCV flood-image estimation
- Integrating `.env`
- Adding optional Groq AI
- Adding optional weather data
- Improving validation and fallback behavior

## 4. Flood Risk Algorithm

IBM Bob helped design a transparent flood-risk algorithm that combines:

- Current water level
- Warning level
- Danger level
- 24-hour rainfall
- Soil saturation
- Drainage blockage
- Water-level rise rate

The combined score is limited to 100.

This makes the logic easy for hackathon evaluators to understand.

## 5. Rapid-Rise Anomaly Detection

IBM Bob helped implement a simple anomaly detector using consecutive water-level readings.

The system calculates:

```text
rise rate = change in water level / elapsed time
```

If the water rises unusually quickly, the system generates an anomaly warning even before the absolute water level reaches the highest threshold.

This demonstrates the difference between simple threshold monitoring and trend-aware early warning.

## 6. Flood Report Prioritization

IBM Bob helped create a response score based on:

- Water depth
- People affected
- Houses affected
- Road blockage
- Waiting time

This allows field responders to focus on reports with the greatest likely impact.

## 7. Flood Image Estimator

IBM Bob was used to prototype an OpenCV-based image-analysis feature.

The module:

1. Converts the image to HSV color space.
2. Detects broad blue/cyan water-like regions.
3. Detects muddy-brown water-like regions.
4. Cleans the mask using morphological operations.
5. Calculates the percentage of the visible image classified as water-like.
6. Highlights the detected regions.

This feature is intentionally presented as a prototype rather than a scientific flood-classification model.

## 8. Nearest Shelter Search

IBM Bob helped implement the Haversine formula to calculate approximate distance between the citizen and shelters.

This provides a useful shelter-ranking feature without requiring a paid map-routing service.

## 9. Environment Configuration

IBM Bob helped separate configuration from source code using `.env`.

The project uses:

```env
APP_NAME
REGION_NAME
ADMIN_PASSWORD
GROQ_API_KEY
GROQ_MODEL
OPENWEATHER_API_KEY
WEATHER_CITY
WARNING_RIVER_LEVEL_M
DANGER_RIVER_LEVEL_M
CRITICAL_RIVER_LEVEL_M
HEAVY_RAIN_24H_MM
CRITICAL_RISK_THRESHOLD
CONTROL_LAT
CONTROL_LON
```

## 10. AI Flood Advisor

IBM Bob helped design the AI assistant so the project remains usable without an external AI API.

Flow:

```text
User Question
      |
      v
Is GROQ_API_KEY configured?
     / \
   Yes  No
   |     |
 Groq   Built-in flood guidance
   |     |
   +----> Response
```

If the AI request fails, the system automatically falls back to rule-based flood guidance.

## 11. Weather Integration

IBM Bob assisted with optional OpenWeather support.

When enabled, the system can display:

- Temperature
- Humidity
- Wind speed
- Rainfall
- Current weather condition

The project continues to run normally if the API is not configured.

## 12. Validation and Error Handling

IBM Bob was used to review issues such as:

- Missing sensor readings
- Empty DataFrames
- Invalid API keys
- Network failures
- Missing images
- Incorrect GPS fields
- Missing shelter data
- Optional service failures
- Duplicate Streamlit widget keys

Fallback behavior was added to prevent optional features from breaking the core system.

## 13. Refactoring

IBM Bob helped separate:

- Database functions
- Flood calculations
- External services
- User interface

This improved:

- Readability
- Maintainability
- Debugging
- Reusability
- Hackathon presentation quality

## 14. Documentation

IBM Bob was used to help prepare:

- Problem statement
- Solution statement
- README
- Installation instructions
- `.env` configuration
- Demo flow
- Future improvements
- IBM Bob usage documentation

## 15. Example IBM Bob Prompts

### Ask Mode

```text
Analyze a flood-detection and early-warning project for a hackathon.
Suggest features using river level, rainfall, soil saturation, drainage,
citizen flood reports, shelters, and optional weather/AI services.
```

### Plan Mode

```text
Create a modular Streamlit + SQLite implementation plan for a flood
detection and early-warning platform. Include flood-risk scoring,
rapid water-level rise detection, sensor history, citizen flood reports,
report priority, shelters, risk hotspots, an OpenCV image-analysis demo,
.env configuration, weather API support, and Groq AI fallback.
```

### Agent Mode

```text
Implement the project across multiple Python files. Create the SQLite
database, Streamlit UI, risk algorithm, sensor anomaly logic, flood-report
workflow, shelter finder, risk dashboards, OpenCV flood estimator,
AI fallback, weather integration, environment configuration, validation,
and documentation.
```

## Final Summary

IBM Bob helped accelerate FloodWatch AI from a flood-monitoring concept into a complete working prototype. Its strongest contributions were architecture planning, multi-file code generation, flood-risk logic, anomaly detection, database integration, image-analysis prototyping, API integration, debugging, refactoring, and documentation.
