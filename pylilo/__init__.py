"""Connect with LILO."""

import asyncio
import logging
import time

import bleak
from bleak_retry_connector import BleakClient, BLEDevice, establish_connection

_LOGGER = logging.getLogger(__name__)


class LILO:
    """Connects to LILO to get information."""

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the class object."""
        self.ble_device = ble_device
        self._cached_services = None
        self.client = None
        self.name = "LILO"
        self.prev_time = 0

        self.result = {
            "time": None,
            "light": None,
        }

    def set_ble_device(self, ble_device) -> None:
        self.ble_device = ble_device

    def disconnect(self) -> None:
        self.client = None
        self.ble_device = None

    async def connect(self) -> None:
        """Ensure connection to device is established."""
        if self.client and self.client.is_connected:
            return

        # Check again while holding the lock
        if self.client and self.client.is_connected:
            return
        _LOGGER.debug(f"{self.name}: Connecting; RSSI: {self.ble_device.rssi}")
        try:
            self.client = await establish_connection(
                BleakClient,
                self.ble_device,
                self.name,
                self._disconnected,
                cached_services=self._cached_services,
                ble_device_callback=lambda: self.ble_device,
            )
            _LOGGER.debug(f"{self.name}: Connected; RSSI: {self.ble_device.rssi}")
        except Exception:
            _LOGGER.debug(f"{self.name}: Error connecting to device")

    def _disconnected(self, client: BleakClient) -> None:
        """Disconnected callback."""
        _LOGGER.debug(
            f"{self.name}: Disconnected from device; RSSI: {self.ble_device.rssi}"
        )
        self.client = None

    async def gatherdata(self):
        """Connect to the LILO to get data."""
        if self.ble_device is None:
            return self.result
        if time.time() - self.prev_time < 1:
            return self.result
        self.prev_time = time.time()
        await self.connect()
        chars = {
            "53e11633-b840-4b21-93ce-081726ddc739": "time",
            "53e11632-b840-4b21-93ce-081726ddc739": "light",
        }
        light = {
            "00": "Off",
            "01": "Photo mode",
            "02": "Spring",
            "03": "Summer" 
        }
        try:
            tasks = []
            for char, _ in chars.items():
                tasks.append(asyncio.create_task(self.client.read_gatt_char(char)))
            results = await asyncio.gather(*tasks)
            res_dict = dict(zip(chars.values(), results))
            
            self.result["time"] = res_dict["time"][0]
            self.result["light"] = res_dict["light"][0]

        except Exception:
            _LOGGER.debug(f"{self.name}: Not connected to device")

        return self.result


async def discover():
    """Start looking for a LILO."""
    devices = await bleak.BleakScanner.discover()
    for device in devices:
        if device.name == "LILO":
            return device


async def main():
    """Run manually."""
    ble_device = await discover()
    _LOGGER.debug(ble_device)
    lilo = LILO(ble_device)
    while True:
        time.sleep(1)
        _LOGGER.debug(await lilo.gatherdata())


if __name__ == "__main__":
    asyncio.run(main())
