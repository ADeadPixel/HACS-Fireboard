"""Wrapper for Fireboard Cloud API."""
import aiohttp
import logging
import async_timeout

_LOGGER = logging.getLogger(__name__)
API_URL = "https://fireboard.io/api/v1"
AUTH_URL = "https://fireboard.io/api/rest-auth/login/"

USER_AGENT = "HA-FB/0.1.0"

class FireBoardApiClient:
    def __init__(self, username, password, session: aiohttp.ClientSession):
        self._username = username
        self._password = password
        self._session = session
        self._token = None

    async def _request(self, method, url, **kwargs):
        """Internal method to handle requests with consistent headers."""
        headers = kwargs.get("headers", {})
        
        headers["User-Agent"] = USER_AGENT
        
        if self._token:
            headers["Authorization"] = f"Token {self._token}"
            
        kwargs["headers"] = headers

        try:
            async with async_timeout.timeout(10):
                resp = await self._session.request(method, url, **kwargs)
                
                if resp.status in (401, 403) and self._token:
                    pass
                    
                return resp
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
                self._token = temp_token # Restore old token if auth fails
                _LOGGER.error("Auth failed: %s", resp.status)
                raise Exception(f"Auth failed: {resp.status}")
                
            data = await resp.json()
            self._token = data.get("key")
            return True
            
        except Exception as e:
            _LOGGER.error("Error authenticating with Fireboard: %s", e)
            raise

    async def get_devices(self):
        """Fetch all devices and their current channels/temps."""
        if not self._token:
            await self.authenticate()

        try:
            resp = await self._request("GET", f"{API_URL}/devices.json")
            
            if resp.status == 401:
                _LOGGER.warning("Token expired, re-authenticating...")
                await self.authenticate()
                # Retry the request
                resp = await self._request("GET", f"{API_URL}/devices.json")
            
            resp.raise_for_status()
            return await resp.json()
            
        except Exception as e:
            _LOGGER.error("Error fetching Fireboard data: %s", e)
            raise