"""Config flow for Fireboard integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN, 
    CONF_USERNAME, 
    CONF_PASSWORD, 
    CONF_POLLING_INTERVAL, 
    DEFAULT_POLLING_INTERVAL, 
    MIN_POLLING_INTERVAL
)
from .api import FireBoardApiClient

class FireBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fireboard."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = FireBoardApiClient(
                user_input[CONF_USERNAME], 
                user_input[CONF_PASSWORD], 
                session
            )

            try:
                await client.authenticate()
            except Exception:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title="Fireboard", 
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(
                CONF_POLLING_INTERVAL, 
                default=DEFAULT_POLLING_INTERVAL
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLLING_INTERVAL)),
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FireBoardOptionsFlowHandler(config_entry)


class FireBoardOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.entry = config_entry 

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_polling = self.entry.options.get(
            CONF_POLLING_INTERVAL, 
            self.entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        )

        options_schema = vol.Schema({
            vol.Required(
                CONF_POLLING_INTERVAL, 
                default=current_polling
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLLING_INTERVAL)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )