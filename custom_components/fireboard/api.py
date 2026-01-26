"""Wrapper for Fireboard Cloud API."""
import aiohttp
import logging
import async_timeout
from .const import API_URL, AUTH_URL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = "HA-FB/1.2.0"

class FireBoardApiClient:
    def __init__(self, username, password, session: aiohttp.ClientSession):
        self._username = username
        self._password = password
        self._session = session
        self._token = None

    async def _request(self, method, url, **kwargs):
        """Internal method to handle requests."""
        headers = kwargs.get("headers", {})
        headers["User-Agent"] = USER_AGENT
        
        if self._token:
            headers["Authorization"] = f"Token {self._token}"
            
        kwargs["headers"] = headers
        
        # kwargs.setdefault("allow_redirects", False)

        try:
            async with async_timeout.timeout(10):
                return await self._session.request(method, url, **kwargs)
        except Exception as e:
            _LOGGER.error("Socket error connecting to Fireboard: %s", e)
            raise

    async def authenticate(self):
        """Get auth token."""
        try:
            temp_token = self._token
            self._token = None 
            
            resp = await self._request(
                "POST",
                AUTH_URL,
                json={"username": self._username, "password": self._password},
            )

            if resp.status != 200:
                self._token = temp_token
                raise Exception(f"Auth failed: {resp.status}")
                
            data = await resp.json()
            self._token = data.get("key")
            return True
            
        except Exception as e:
            _LOGGER.error("Error authenticating with Fireboard: %s", e)
            raise

    async def _get_full_device_details(self, device_uuid):
        """Helper: Fetch full details for a specific device."""
        try:
            url = f"{API_URL}/devices/{device_uuid}.json"
            resp = await self._request("GET", url)
            
            if resp.status == 200:
                return await resp.json()
        except Exception:
            pass
        return None

    async def _get_device_temps(self, device_uuid):
        """Helper: Fetch real-time temps for a specific device."""
        try:
            url = f"{API_URL}/devices/{device_uuid}/temps.json"
            resp = await self._request("GET", url)
            
            if resp.status == 200:
                return await resp.json()
        except Exception:
            pass
        return None

    async def get_devices(self):
        """Fetch devices with optimized API usage."""
        if not self._token:
            await self.authenticate()

        try:
            resp = await self._request("GET", f"{API_URL}/devices.json")
            
            if resp.status in (401, 403, 302, 301):
                _LOGGER.warning("Auth issue (Status: %s). Re-authenticating...", resp.status)
                await self.authenticate()
                resp = await self._request("GET", f"{API_URL}/devices.json")

            if resp.status != 200:
                _LOGGER.error("API Error: Status %s (Likely Rate Limited)", resp.status)
                raise Exception(f"API Error: Status {resp.status}")
            
            resp.raise_for_status()
            skeleton_devices = await resp.json()
            
            final_devices = []

            for skeleton in skeleton_devices:
                uuid = skeleton.get("uuid")
                if uuid:
                    full_details = await self._get_full_device_details(uuid)
                    device_data = full_details if full_details else skeleton

                    channel_temperatures = await self._get_device_temps(uuid)
                    if channel_temperatures:
                        device_data["latest_temps"] = channel_temperatures

                        channel_temperature_map = {
                            item.get("channel"): item.get("temp") 
                            for item in channel_temperatures
                        }

                        for channel in device_data.get("channels", []):
                            ch_id = channel.get("channel")
                            
                            if ch_id in channel_temperature_map:
                                channel["current_temp"] = channel_temperature_map[ch_id]

                    
                    final_devices.append(device_data)
                else:
                    final_devices.append(skeleton)

            return final_devices
            
        except Exception as e:
            _LOGGER.error("Error fetching Fireboard data: %s", e)
            raise
