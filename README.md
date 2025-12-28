## Firstly
Thanks for checking this out! This is my first full HACS/HA integration! I've contributed to a few others but nothing to call my own. If you enjoyed the integration please send me some coffee to fuel more work in the future https://buymeacoffee.com/adeadpixel! Thanks again! 

## FireBoard Home Assistant Integration
An unofficial integration to connect FireBoard 2 thermometers to Home Assistant via the FireBoard Cloud API.

### Overview
This integration polls the FireBoard API to expose sensors for Temperature Probes, Battery Level, and Signal Strength (RSSI).

Important: The FireBoard API has a rate limit of ~200 requests/hour. The default polling interval is set to 60 seconds to stay well within this limit.

### Installation
**1. HACS**: Add this repository URL as a Custom Repository in HACS (Category: Integration).

**2. Download**: Search for "FireBoard" in HACS and download the integration.

**3. Restart**: Restart Home Assistant.

**4. Configure**: Go to Settings > Devices & Services > Add Integration, search for "FireBoard", and enter your credentials.

### Requirements
FireBoard account with at least one active device.