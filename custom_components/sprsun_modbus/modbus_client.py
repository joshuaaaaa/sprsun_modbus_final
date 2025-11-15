"""Modbus client for SPRSUN Heat Pump."""
from __future__ import annotations

import errno
import logging
import time
from typing import Any, Optional
from inspect import signature

from pymodbus.client import (
    ModbusSerialClient,
    ModbusTcpClient,
    ModbusUdpClient,
)
from pymodbus.exceptions import ModbusException, ConnectionException

from .const import (
    CONF_MODBUS_SERIAL,
    CONF_MODBUS_TCP,
    CONF_MODBUS_UDP,
)

_LOGGER = logging.getLogger(__name__)


def _unit_param_name(callable_obj) -> Optional[str]:
    """Return the proper keyword for unit id depending on pymodbus version.

    Tries in this order: 'unit', 'slave', 'slave_id'.
    Returns None if none of them is supported (very unlikely).
    """
    try:
        params = signature(callable_obj).parameters
        for name in ("unit", "slave", "slave_id"):
            if name in params:
                return name
    except Exception:
        # Fallback if inspect.signature fails for any reason
        pass
    return None


def _add_unit_kw(method, kwargs: dict, unit_value: int) -> dict:
    """Attach correct unit/slave/slave_id kw to kwargs if supported."""
    kw = _unit_param_name(method)
    if kw:
        kwargs[kw] = unit_value
    return kwargs


class SPRSUNModbusClient:
    """SPRSUN Modbus client."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the Modbus client."""
        self.config = config
        self.client = None
        self.register_offset = config.get("register_offset", 0)
        self._last_connect_attempt = 0
        self._connect_retry_delay = 0
        self._operation_count = 0
        self._last_successful_op = 0
        self._reconnect_threshold = 100  # Reconnect after this many operations
        self._connect()

    def _connect(self) -> None:
        """Connect to Modbus device with retry logic."""
        # Close existing connection first
        if self.client:
            try:
                _LOGGER.debug("Closing existing client connection before reconnecting")
                # Ensure we close the connection properly
                if hasattr(self.client, 'close'):
                    self.client.close()
                # Give the device a moment to release the connection
                time.sleep(0.1)
            except Exception as err:
                _LOGGER.debug("Error closing existing client: %s", err)
            finally:
                self.client = None

        modbus_type = self.config.get("modbus_type", CONF_MODBUS_TCP)

        # Implement exponential backoff for reconnection attempts
        current_time = time.time()
        if self._last_connect_attempt > 0:
            time_since_last_attempt = current_time - self._last_connect_attempt
            if time_since_last_attempt < self._connect_retry_delay:
                _LOGGER.debug("Skipping reconnect attempt, backoff delay not elapsed")
                return

        self._last_connect_attempt = current_time

        try:
            # Increase timeout to 5 seconds for better reliability with slow converters
            if modbus_type == CONF_MODBUS_SERIAL:
                self.client = ModbusSerialClient(
                    port=self.config["serial_port"],
                    baudrate=self.config.get("baudrate", 19200),
                    timeout=5,
                )
            elif modbus_type == CONF_MODBUS_TCP:
                self.client = ModbusTcpClient(
                    host=self.config["host"],
                    port=self.config.get("port", 4196),
                    timeout=5,
                )
            elif modbus_type == CONF_MODBUS_UDP:
                self.client = ModbusUdpClient(
                    host=self.config["host"],
                    port=self.config.get("port", 4196),
                    timeout=5,
                )
            else:
                _LOGGER.error("Unknown modbus_type: %s", modbus_type)
                self.client = None
                return

            if self.client:
                connection_result = self.client.connect()

                # Check if connection was successful
                if connection_result:
                    _LOGGER.info("Connected to SPRSUN Heat Pump via %s", modbus_type)
                    # Reset retry delay and operation counter on successful connection
                    self._connect_retry_delay = 0
                    self._operation_count = 0
                    self._last_successful_op = time.time()
                else:
                    # Connection failed, increase retry delay with exponential backoff
                    self._connect_retry_delay = min(self._connect_retry_delay * 2 if self._connect_retry_delay > 0 else 2, 60)
                    _LOGGER.warning("Connection to Modbus device failed, will retry after %s seconds", self._connect_retry_delay)
                    self.client = None

        except Exception as err:
            # Connection error, increase retry delay with exponential backoff
            self._connect_retry_delay = min(self._connect_retry_delay * 2 if self._connect_retry_delay > 0 else 2, 60)
            _LOGGER.error("Failed to create/connect Modbus client: %s. Will retry after %s seconds", err, self._connect_retry_delay)
            self.client = None

    def close(self) -> None:
        """Close the Modbus connection."""
        if self.client:
            try:
                _LOGGER.debug("Closing Modbus client connection")
                self.client.close()
                # Give the device a moment to properly release resources
                time.sleep(0.1)
                _LOGGER.debug("Modbus client connection closed successfully")
            except Exception as err:
                _LOGGER.warning("Error closing Modbus client: %s", err)
            finally:
                self.client = None

    def _ensure_connected(self) -> bool:
        """Ensure client is connected; reconnect if needed."""
        if not self.client:
            self._connect()
            return self.client is not None

        # Check if we need to proactively reconnect to prevent stale connections
        if self._operation_count >= self._reconnect_threshold:
            _LOGGER.debug("Operation threshold reached (%d), proactively reconnecting", self._operation_count)
            self._connect()
            return self.client is not None

        # Check if client has a connected attribute and if it's False
        try:
            if hasattr(self.client, "connected") and not self.client.connected:
                _LOGGER.debug("Client reports disconnected, attempting reconnect")
                self._connect()
                return self.client is not None

            # For TCP/UDP clients, verify socket is still valid
            if hasattr(self.client, "socket") and self.client.socket:
                try:
                    # Try to peek at socket state without reading
                    import socket as sock_module
                    if hasattr(sock_module, 'SO_ERROR'):
                        error = self.client.socket.getsockopt(sock_module.SOL_SOCKET, sock_module.SO_ERROR)
                        if error != 0:
                            _LOGGER.debug("Socket has error state %d, reconnecting", error)
                            self._connect()
                            return self.client is not None
                except (OSError, AttributeError):
                    # Socket is likely closed or invalid
                    _LOGGER.debug("Socket appears invalid, reconnecting")
                    self._connect()
                    return self.client is not None

        except Exception as err:
            _LOGGER.debug("Error checking connection state: %s", err)
            self._connect()
            return self.client is not None

        return True

    def read_holding_register(
        self, register: int, count: int = 1, decimal_places: int = 0, slave: int = 1
    ) -> int | float | None:
        """Read holding register(s). Returns first register converted."""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                # Apply register offset if configured
                actual_address = register + self.register_offset

                kwargs = _add_unit_kw(self.client.read_holding_registers, {
                    "address": actual_address,
                    "count": count,
                }, slave)

                result = self.client.read_holding_registers(**kwargs)

                # Check if result is valid
                if result is None:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Null response reading register %d (actual address %d), retrying...",
                                    register, actual_address)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Null response reading register %d (actual address %d) after %d attempts",
                                register, actual_address, max_retries)
                    return None

                # Check for errors
                if hasattr(result, 'isError') and result.isError():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error response reading register %d (actual address %d): %s, retrying...",
                                    register, actual_address, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error response reading register %d (actual address %d): %s after %d attempts",
                                register, actual_address, result, max_retries)
                    return None

                if hasattr(result, "registers"):
                    regs = result.registers
                else:
                    # very old return types could be list-like
                    regs = list(result) if result is not None else []

                if not regs:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Empty response reading register %d, retrying...", register)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Empty response reading register %d after %d attempts", register, max_retries)
                    return None

                value = regs[0]

                # Handle signed 16-bit
                if value > 32767:
                    value = value - 65536

                # Increment operation counter on success
                self._operation_count += 1
                self._last_successful_op = time.time()

                if decimal_places == 0:
                    return int(value)
                return float(value / (10 ** decimal_places))

            except ConnectionException as err:
                # Connection-specific errors - force immediate reconnection
                if attempt < max_retries - 1:
                    _LOGGER.debug("Connection exception reading register %d: %s, forcing reconnect...", register, err)
                    self.client = None  # Force reconnection
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("Connection exception reading register %d: %s after %d attempts", register, err, max_retries)
                return None
            except OSError as err:
                # Handle connection refused and other OS-level errors
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection refused reading register %d, forcing reconnect...", register)
                        self.client = None  # Force reconnection
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection refused reading register %d after %d attempts", register, max_retries)
                    return None
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection error (errno %d) reading register %d, forcing reconnect...", err.errno, register)
                        self.client = None  # Force reconnection
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection error reading register %d: %s after %d attempts", register, err, max_retries)
                    return None
                # Other OS errors
                if attempt < max_retries - 1:
                    _LOGGER.debug("OS error reading register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("OS error reading register %d: %s after %d attempts", register, err, max_retries)
                return None
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Modbus exception reading register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Modbus exception reading register %d: %s after %d attempts", register, err, max_retries)
                return None
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Error reading register %d: %s after %d attempts", register, err, max_retries)
                return None

        return None

    def read_holding_registers_bulk(
        self,
        start_register: int,
        count: int,
        decimal_places: int = 0,
        slave: int = 1,
        raw: bool = False,
    ) -> list[int | float | None]:
        """Read multiple holding registers and return list of converted values.
        
        Args:
            start_register: Starting register address
            count: Number of registers to read
            decimal_places: Number of decimal places for value conversion (0 for INT)
            slave: Slave ID
            raw: If True, return raw unsigned values without signed conversion (for 32-bit values)
            
        Returns:
            List of converted values (same length as count), None for failed reads
        """
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return [None] * count

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                # Apply register offset if configured
                actual_address = start_register + self.register_offset

                kwargs = _add_unit_kw(self.client.read_holding_registers, {
                    "address": actual_address,
                    "count": count,
                }, slave)

                result = self.client.read_holding_registers(**kwargs)

                # Check if result is valid
                if result is None:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Null response reading registers %d-%d, retrying...",
                                    start_register, start_register + count - 1)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Null response reading registers %d-%d after %d attempts",
                                start_register, start_register + count - 1, max_retries)
                    return [None] * count

                # Check for errors
                if hasattr(result, 'isError') and result.isError():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error response reading registers %d-%d: %s, retrying...",
                                    start_register, start_register + count - 1, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error response reading registers %d-%d: %s after %d attempts",
                                start_register, start_register + count - 1, result, max_retries)
                    return [None] * count

                if hasattr(result, "registers"):
                    regs = result.registers
                else:
                    regs = list(result) if result is not None else []

                if not regs or len(regs) != count:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Invalid response length reading registers %d-%d (expected %d, got %d), retrying...",
                                    start_register, start_register + count - 1, count, len(regs) if regs else 0)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Invalid response length reading registers %d-%d after %d attempts",
                                start_register, start_register + count - 1, max_retries)
                    return [None] * count

                # Convert all values
                values = []
                for reg_value in regs:
                    # Handle signed 16-bit (only if not raw mode)
                    if not raw and reg_value > 32767:
                        reg_value = reg_value - 65536

                    if decimal_places == 0:
                        values.append(int(reg_value))
                    else:
                        values.append(float(reg_value / (10 ** decimal_places)))

                # Increment operation counter on success
                self._operation_count += 1
                self._last_successful_op = time.time()

                return values

            except ConnectionException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Connection exception reading registers %d-%d: %s, forcing reconnect...",
                                start_register, start_register + count - 1, err)
                    self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("Connection exception reading registers %d-%d: %s after %d attempts",
                              start_register, start_register + count - 1, err, max_retries)
                return [None] * count
            except OSError as err:
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection refused reading registers %d-%d, forcing reconnect...",
                                    start_register, start_register + count - 1)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection refused reading registers %d-%d after %d attempts",
                                  start_register, start_register + count - 1, max_retries)
                    return [None] * count
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection error (errno %d) reading registers %d-%d, forcing reconnect...",
                                    err.errno, start_register, start_register + count - 1)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection error reading registers %d-%d: %s after %d attempts",
                                  start_register, start_register + count - 1, err, max_retries)
                    return [None] * count
                if attempt < max_retries - 1:
                    _LOGGER.debug("OS error reading registers %d-%d: %s, retrying...",
                                start_register, start_register + count - 1, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("OS error reading registers %d-%d: %s after %d attempts",
                              start_register, start_register + count - 1, err, max_retries)
                return [None] * count
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Modbus exception reading registers %d-%d: %s, retrying...",
                                start_register, start_register + count - 1, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Modbus exception reading registers %d-%d: %s after %d attempts",
                            start_register, start_register + count - 1, err, max_retries)
                return [None] * count
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading registers %d-%d: %s, retrying...",
                                start_register, start_register + count - 1, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Error reading registers %d-%d: %s after %d attempts",
                            start_register, start_register + count - 1, err, max_retries)
                return [None] * count

        return [None] * count

    def read_coil(self, coil: int, slave: int = 1) -> bool | None:
        """Read single coil."""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                kwargs = _add_unit_kw(self.client.read_coils, {
                    "address": coil,
                    "count": 1,
                }, slave)

                result = self.client.read_coils(**kwargs)

                if result is None or getattr(result, "isError", lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error reading coil %d: %s, retrying...", coil, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error reading coil %d: %s after %d attempts", coil, result, max_retries)
                    return None

                if hasattr(result, "bits") and result.bits:
                    # Increment operation counter on success
                    self._operation_count += 1
                    self._last_successful_op = time.time()
                    return bool(result.bits[0])

                if attempt < max_retries - 1:
                    _LOGGER.debug("Empty/invalid bits when reading coil %d, retrying...", coil)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Empty/invalid bits when reading coil %d after %d attempts", coil, max_retries)
                return None

            except ConnectionException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Connection exception reading coil %d: %s, forcing reconnect...", coil, err)
                    self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("Connection exception reading coil %d: %s after %d attempts", coil, err, max_retries)
                return None
            except OSError as err:
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection refused reading coil %d, forcing reconnect...", coil)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection refused reading coil %d after %d attempts", coil, max_retries)
                    return None
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection error (errno %d) reading coil %d, forcing reconnect...", err.errno, coil)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection error reading coil %d: %s after %d attempts", coil, err, max_retries)
                    return None
                if attempt < max_retries - 1:
                    _LOGGER.debug("OS error reading coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("OS error reading coil %d: %s after %d attempts", coil, err, max_retries)
                return None
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Modbus exception reading coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Modbus exception reading coil %d: %s after %d attempts", coil, err, max_retries)
                return None
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Error reading coil %d: %s after %d attempts", coil, err, max_retries)
                return None

        return None

    def read_discrete_input(self, input_addr: int, slave: int = 1) -> bool | None:
        """Read single discrete input."""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                kwargs = _add_unit_kw(self.client.read_discrete_inputs, {
                    "address": input_addr,
                    "count": 1,
                }, slave)

                result = self.client.read_discrete_inputs(**kwargs)

                if result is None or getattr(result, "isError", lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error reading discrete input %d: %s, retrying...", input_addr, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error reading discrete input %d: %s after %d attempts", input_addr, result, max_retries)
                    return None

                if hasattr(result, "bits") and result.bits:
                    # Increment operation counter on success
                    self._operation_count += 1
                    self._last_successful_op = time.time()
                    return bool(result.bits[0])

                if attempt < max_retries - 1:
                    _LOGGER.debug("Empty/invalid bits when reading discrete input %d, retrying...", input_addr)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Empty/invalid bits when reading discrete input %d after %d attempts", input_addr, max_retries)
                return None

            except ConnectionException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Connection exception reading discrete input %d: %s, forcing reconnect...", input_addr, err)
                    self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("Connection exception reading discrete input %d: %s after %d attempts", input_addr, err, max_retries)
                return None
            except OSError as err:
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection refused reading discrete input %d, forcing reconnect...", input_addr)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection refused reading discrete input %d after %d attempts", input_addr, max_retries)
                    return None
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Connection error (errno %d) reading discrete input %d, forcing reconnect...", err.errno, input_addr)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.warning("Connection error reading discrete input %d: %s after %d attempts", input_addr, err, max_retries)
                    return None
                if attempt < max_retries - 1:
                    _LOGGER.debug("OS error reading discrete input %d: %s, retrying...", input_addr, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.warning("OS error reading discrete input %d: %s after %d attempts", input_addr, err, max_retries)
                return None
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Modbus exception reading discrete input %d: %s, retrying...", input_addr, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Modbus exception reading discrete input %d: %s after %d attempts", input_addr, err, max_retries)
                return None
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading discrete input %d: %s, retrying...", input_addr, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.debug("Error reading discrete input %d: %s after %d attempts", input_addr, err, max_retries)
                return None

        return None

    def read_holding_register_32bit(
        self, register: int, decimal_places: int = 0, slave: int = 1
    ) -> int | float | None:
        """Read 32-bit holding register (2 consecutive 16-bit registers) as UDINT.

        Returns value from 2 registers combined into 32-bit unsigned integer.
        First register is high word, second is low word.
        Used for: Working Hours (UDINT)
        """
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

                # Small delay between operations
                if self._operation_count > 0:
                    time.sleep(0.05)

                # Apply register offset if configured
                actual_address = register + self.register_offset

                # Read 2 consecutive registers
                kwargs = _add_unit_kw(self.client.read_holding_registers, {
                    "address": actual_address,
                    "count": 2,
                }, slave)

                result = self.client.read_holding_registers(**kwargs)

                if result is None or getattr(result, 'isError', lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error reading 32-bit register %d (actual address %d): %s, retrying...",
                                    register, actual_address, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error reading 32-bit register %d after %d attempts", register, max_retries)
                    return None

                if hasattr(result, "registers"):
                    regs = result.registers
                else:
                    regs = list(result) if result is not None else []

                if len(regs) < 2:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Incomplete response reading 32-bit register %d, retrying...", register)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Incomplete response reading 32-bit register %d", register)
                    return None

                # Combine two 16-bit registers into 32-bit unsigned integer (high word first)
                value = (regs[0] << 16) | regs[1]

                # Increment operation counter
                self._operation_count += 1
                self._last_successful_op = time.time()

                if decimal_places == 0:
                    return int(value)
                return float(value / (10 ** decimal_places))

            except (ConnectionException, OSError, ModbusException) as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading 32-bit register %d: %s, retrying...", register, err)
                    if isinstance(err, ConnectionException) or (isinstance(err, OSError) and err.errno in (errno.ECONNREFUSED, errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT)):
                        self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Error reading 32-bit register %d: %s after %d attempts", register, err, max_retries)
                return None
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Unexpected error reading 32-bit register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Unexpected error reading 32-bit register %d after %d attempts", register, err, max_retries)
                return None

        return None

    def read_holding_register_float32(
        self, register: int, slave: int = 1
    ) -> float | None:
        """Read 32-bit holding register (2 consecutive 16-bit registers) as IEEE 754 float32.

        Returns value from 2 registers interpreted as IEEE 754 float32.
        First register is high word, second is low word.
        Used for: Power_W, Water_Flow, Total_Power_Consumption, etc. (REAL with 2 registers)
        """
        import struct
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

                # Small delay between operations
                if self._operation_count > 0:
                    time.sleep(0.05)

                # Apply register offset if configured
                actual_address = register + self.register_offset

                # Read 2 consecutive registers
                kwargs = _add_unit_kw(self.client.read_holding_registers, {
                    "address": actual_address,
                    "count": 2,
                }, slave)

                result = self.client.read_holding_registers(**kwargs)

                if result is None or getattr(result, 'isError', lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Error reading float32 register %d (actual address %d): %s, retrying...",
                                    register, actual_address, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Error reading float32 register %d after %d attempts", register, max_retries)
                    return None

                if hasattr(result, "registers"):
                    regs = result.registers
                else:
                    regs = list(result) if result is not None else []

                if len(regs) < 2:
                    if attempt < max_retries - 1:
                        _LOGGER.debug("Incomplete response reading float32 register %d, retrying...", register)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.debug("Incomplete response reading float32 register %d", register)
                    return None

                # Combine two 16-bit registers into IEEE 754 float32
                # Big-endian byte order (high word first): >HH means two unsigned shorts, big-endian
                # Then convert to float: >f means float, big-endian
                bytes_data = struct.pack('>HH', regs[0], regs[1])
                float_value = struct.unpack('>f', bytes_data)[0]

                # Increment operation counter
                self._operation_count += 1
                self._last_successful_op = time.time()

                return float_value

            except (ConnectionException, OSError, ModbusException) as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Error reading float32 register %d: %s, retrying...", register, err)
                    if isinstance(err, ConnectionException) or (isinstance(err, OSError) and err.errno in (errno.ECONNREFUSED, errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT)):
                        self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Error reading float32 register %d: %s after %d attempts", register, err, max_retries)
                return None
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.debug("Unexpected error reading float32 register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.debug("Unexpected error reading float32 register %d after %d attempts", register, err, max_retries)
                return None

        return None

    def write_register(
        self, register: int, value: float, decimal_places: int = 0, slave: int = 1
    ) -> bool:
        """Write single holding register (16-bit)."""
        max_retries = 3
        retry_delay = 0.5

        # Convert to integer with decimal places
        int_value = int(round(value * (10 ** decimal_places)))

        # Ensure 16-bit unsigned range
        if int_value < 0:
            int_value = 65536 + int_value
        int_value &= 0xFFFF

        # Apply register offset if configured
        actual_address = register + self.register_offset

        _LOGGER.info("Writing register %d (40%03d, actual address %d): value=%.2f, int_value=%d (0x%04X), decimal_places=%d",
                    register, register + 1, actual_address, value, int_value, int_value, decimal_places)

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                kwargs = _add_unit_kw(self.client.write_register, {
                    "address": actual_address,
                    "value": int_value,
                }, slave)

                result = self.client.write_register(**kwargs)

                if result is None or getattr(result, "isError", lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Error writing register %d (40%03d): %s, retrying...",
                                      register, register + 1, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Error writing register %d (40%03d): %s after %d attempts",
                                register, register + 1, result, max_retries)
                    return False

                # Increment operation counter on success
                self._operation_count += 1
                self._last_successful_op = time.time()
                _LOGGER.info("Successfully wrote register %d (40%03d)", register, register + 1)
                return True

            except ConnectionException as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Connection exception writing register %d: %s, forcing reconnect...", register, err)
                    self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.error("Connection exception writing register %d: %s after %d attempts", register, err, max_retries)
                return False
            except OSError as err:
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Connection refused writing register %d, forcing reconnect...", register)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Connection refused writing register %d after %d attempts", register, max_retries)
                    return False
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Connection error (errno %d) writing register %d, forcing reconnect...", err.errno, register)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Connection error writing register %d: %s after %d attempts", register, err, max_retries)
                    return False
                if attempt < max_retries - 1:
                    _LOGGER.warning("OS error writing register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.error("OS error writing register %d: %s after %d attempts", register, err, max_retries)
                return False
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Modbus exception writing register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.error("Modbus exception writing register %d: %s after %d attempts", register, err, max_retries)
                return False
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Error writing register %d: %s, retrying...", register, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.error("Error writing register %d: %s after %d attempts", register, err, max_retries)
                return False

        return False

    def write_coil(self, coil: int, value: bool, slave: int = 1) -> bool:
        """Write single coil."""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if not self._ensure_connected():
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False

                # Small delay between operations to prevent buffer issues
                if self._operation_count > 0:
                    time.sleep(0.05)

                kwargs = _add_unit_kw(self.client.write_coil, {
                    "address": coil,
                    "value": bool(value),
                }, slave)

                result = self.client.write_coil(**kwargs)

                if result is None or getattr(result, "isError", lambda: True)():
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Error writing coil %d: %s, retrying...", coil, result)
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Error writing coil %d: %s after %d attempts", coil, result, max_retries)
                    return False

                # Increment operation counter on success
                self._operation_count += 1
                self._last_successful_op = time.time()
                return True

            except ConnectionException as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Connection exception writing coil %d: %s, forcing reconnect...", coil, err)
                    self.client = None
                    time.sleep(retry_delay)
                    continue
                _LOGGER.error("Connection exception writing coil %d: %s after %d attempts", coil, err, max_retries)
                return False
            except OSError as err:
                if err.errno == errno.ECONNREFUSED:
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Connection refused writing coil %d, forcing reconnect...", coil)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Connection refused writing coil %d after %d attempts", coil, max_retries)
                    return False
                elif err.errno in (errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT):
                    if attempt < max_retries - 1:
                        _LOGGER.warning("Connection error (errno %d) writing coil %d, forcing reconnect...", err.errno, coil)
                        self.client = None
                        time.sleep(retry_delay)
                        continue
                    _LOGGER.error("Connection error writing coil %d: %s after %d attempts", coil, err, max_retries)
                    return False
                if attempt < max_retries - 1:
                    _LOGGER.warning("OS error writing coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    continue
                _LOGGER.error("OS error writing coil %d: %s after %d attempts", coil, err, max_retries)
                return False
            except ModbusException as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Modbus exception writing coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.error("Modbus exception writing coil %d: %s after %d attempts", coil, err, max_retries)
                return False
            except Exception as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning("Error writing coil %d: %s, retrying...", coil, err)
                    time.sleep(retry_delay)
                    # _ensure_connected() will handle reconnection on next attempt
                    continue
                _LOGGER.error("Error writing coil %d: %s after %d attempts", coil, err, max_retries)
                return False

        return False
