## Fireboard Home Assistant Integration
An unofficial integration to connect Fireboard 2 thermometers to Home Assistant via the Fireboard Cloud API.

### Overview
This integration polls the Fireboard API to expose sensors for Temperature Probes, Battery Level, and Signal Strength (RSSI).

**Important:** The Fireboard API has a rate limit of ~200 requests/hour. The default polling interval is set to 60 seconds to stay well within this limit. This integration makes 3 calls to get all of the data so our data resolution floor is 1 api call every 60s. This will situate us at 180 requests/hour.

### Installation
**1. HACS**: Add this repository URL as a Custom Repository in HACS (Category: Integration).

**2. Download**: Search for "Fireboard" in HACS and download the integration.

**3. Restart**: Restart Home Assistant.

**4. Configure**: Go to Settings > Devices & Services > Add Integration, search for "Fireboard", and enter your credentials.

### Requirements
Fireboard account with at least one active device.

## Lastly
Thanks for checking this out! This is my first full HACS/HA integration! I've contributed to a few others but nothing to call my own. If you enjoyed the integration please send me some coffee to fuel more work in the future 

<a href="https://www.buymeacoffee.com/ADeadPixel" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Thanks again! 