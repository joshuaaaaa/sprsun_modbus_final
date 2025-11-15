"""Config flow for SPRSUN Heat Pump Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_MODBUS_TYPE,
    CONF_MODBUS_SERIAL,
    CONF_MODBUS_TCP,
    CONF_MODBUS_UDP,
    CONF_SERIAL_PORT,
    CONF_BAUDRATE,
    CONF_SLAVE_ID,
    CONF_REGISTER_OFFSET,
    DEFAULT_PORT,
    DEFAULT_BAUDRATE,
    DEFAULT_SLAVE_ID,
    DEFAULT_TCP_PORT,
    DEFAULT_REGISTER_OFFSET,
    REG_STATUS,
)
from .modbus_client import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)


class SPRSUNConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SPRSUN Heat Pump Modbus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._modbus_type: str | None = None

    async def _test_connection(self, config: dict) -> tuple[bool, str | None]:
        """Test connection to Modbus device."""
        client = None
        try:
            # Create client with a timeout
            import asyncio

            client = await asyncio.wait_for(
                self.hass.async_add_executor_job(SPRSUNModbusClient, config),
                timeout=10.0
            )

            # Try to read status register with timeout
            slave_id = config.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
            result = await asyncio.wait_for(
                self.hass.async_add_executor_job(
                    client.read_holding_register, REG_STATUS, 1, 0, slave_id
                ),
                timeout=10.0
            )

            if result is not None:
                _LOGGER.info("Connection test successful, read value: %s", result)
                return True, None
            else:
                _LOGGER.warning("Connection test failed: Unable to read status register")
                return False, "cannot_connect"

        except asyncio.TimeoutError:
            _LOGGER.error("Connection test timed out - device may be unreachable or slow to respond")
            return False, "timeout"
        except Exception as err:
            _LOGGER.error("Connection test failed with error: %s (type: %s)", err, type(err).__name__)
            return False, "cannot_connect"
        finally:
            # Always ensure client is properly closed
            if client is not None:
                try:
                    await self.hass.async_add_executor_job(client.close)
                    _LOGGER.debug("Connection test cleanup completed")
                except Exception as cleanup_err:
                    _LOGGER.warning("Error during connection cleanup: %s", cleanup_err)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._modbus_type = user_input[CONF_MODBUS_TYPE]
            
            # Redirect to appropriate step based on type
            if self._modbus_type == CONF_MODBUS_TCP:
                return await self.async_step_tcp()
            if self._modbus_type == CONF_MODBUS_UDP:
                return await self.async_step_udp()
            if self._modbus_type == CONF_MODBUS_SERIAL:
                return await self.async_step_serial()

        # Ask for modbus type first
        data_schema = vol.Schema(
            {
                vol.Required(CONF_MODBUS_TYPE, default=CONF_MODBUS_TCP): vol.In(
                    {
                        CONF_MODBUS_SERIAL: "RTU-Serial",
                        CONF_MODBUS_TCP: "RTU-TCP",
                        CONF_MODBUS_UDP: "RTU-UDP",
                    }
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle TCP configuration."""
        errors = {}
        
        if user_input is not None:
            # Add modbus type to config
            user_input[CONF_MODBUS_TYPE] = CONF_MODBUS_TCP
            
            # Test connection
            success, error = await self._test_connection(user_input)
            
            if success:
                # Create unique ID
                unique_id = f"{CONF_MODBUS_TCP}_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SPRSUN (TCP {user_input[CONF_HOST]}:{user_input[CONF_PORT]})",
                    data=user_input,
                )
            else:
                errors["base"] = error or "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.0.166"): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_TCP_PORT): cv.port,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=247)
                ),
                vol.Optional(CONF_REGISTER_OFFSET, default=DEFAULT_REGISTER_OFFSET): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=10000)
                ),
            }
        )

        return self.async_show_form(step_id="tcp", data_schema=data_schema, errors=errors)

    async def async_step_udp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle UDP configuration."""
        errors = {}
        
        if user_input is not None:
            # Add modbus type to config
            user_input[CONF_MODBUS_TYPE] = CONF_MODBUS_UDP
            
            # Test connection
            success, error = await self._test_connection(user_input)
            
            if success:
                # Create unique ID
                unique_id = f"{CONF_MODBUS_UDP}_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SPRSUN (UDP {user_input[CONF_HOST]}:{user_input[CONF_PORT]})",
                    data=user_input,
                )
            else:
                errors["base"] = error or "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.0.166"): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_TCP_PORT): cv.port,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=247)
                ),
                vol.Optional(CONF_REGISTER_OFFSET, default=DEFAULT_REGISTER_OFFSET): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=10000)
                ),
            }
        )

        return self.async_show_form(step_id="udp", data_schema=data_schema, errors=errors)

    async def async_step_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Serial configuration."""
        errors = {}
        
        if user_input is not None:
            # Add modbus type to config
            user_input[CONF_MODBUS_TYPE] = CONF_MODBUS_SERIAL
            
            # Test connection
            success, error = await self._test_connection(user_input)
            
            if success:
                # Create unique ID
                unique_id = f"{CONF_MODBUS_SERIAL}_{user_input[CONF_SERIAL_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SPRSUN (Serial {user_input[CONF_SERIAL_PORT]})",
                    data=user_input,
                )
            else:
                errors["base"] = error or "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_PORT, default=DEFAULT_PORT): cv.string,
                vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
                    [9600, 19200, 38400, 57600, 115200]
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=247)
                ),
                vol.Optional(CONF_REGISTER_OFFSET, default=DEFAULT_REGISTER_OFFSET): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=10000)
                ),
            }
        )

        return self.async_show_form(step_id="serial", data_schema=data_schema, errors=errors)
