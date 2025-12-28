FireBoard Home Assistant Integration

An unofficial integration to connect FireBoard 2 thermometers to Home Assistant via the FireBoard Cloud API.
Overview

This integration polls the FireBoard API to expose sensors for Temperature Probes, Battery Level, and Signal Strength (RSSI) without requiring local MQTT bridges.

Important: The FireBoard API has a rate limit of ~200 requests/hour. The default polling interval is set to 60 seconds to stay well within this limit. Do not lower the interval below 20 seconds.
Installation

    HACS: Add this repository URL as a Custom Repository in HACS (Category: Integration).

    Download: Search for "FireBoard" in HACS and download the integration.

    Restart: Restart Home Assistant.

    Configure: Go to Settings > Devices & Services > Add Integration, search for "FireBoard", and enter your credentials.

Requirements
    FireBoard account with at least one active device.