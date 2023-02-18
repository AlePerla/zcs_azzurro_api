"""ZCS Azzurro API."""
from __future__ import annotations
import logging
from typing import Any

import requests

from .errors import DeviceOfflineError, HttpRequestError

_LOGGER = logging.getLogger(__name__)


class Inverter:
    """Class implementing ZCS Azzurro API for inverters."""

    ENDPOINT = "https://third.zcsazzurroportal.com:19003"
    AUTH_KEY = "Authorization"
    AUTH_VALUE = "Zcs eHWAeEq0aYO0"
    CLIENT_AUTH_KEY = "client"
    CONTENT_TYPE = "application/json"
    REQUEST_TIMEOUT = 5

    HISTORIC_DATA_KEY = "historicData"
    HISTORIC_DATA_COMMAND = "historicData"

    REALTIME_DATA_KEY = "realtimeData"
    REALTIME_DATA_COMMAND = "realtimeData"

    DEVICES_ALARMS_KEY = "deviceAlarm"
    DEVICES_ALARMS_COMMAND = "deviceAlarm"

    COMMAND_KEY = "command"
    PARAMS_KEY = "params"
    PARAMS_THING_KEY = "thingKey"
    PARAMS_REQUIRED_VALUES_KEY = "requiredValues"
    PARAMS_START_KEY = "start"
    PARAMS_END_KEY = "end"

    RESPONSE_SUCCESS_KEY = "success"
    RESPONSE_VALUES_KEY = "value"

    # Values of required values
    REQUIRED_VALUES_ALL = "*"
    REQUIRED_VALUES_SEP = ","

    def __init__(self, client: str, thing_serial: str, name: str | None = None) -> None:
        """Class initialization."""
        self.client = client
        self._thing_serial = thing_serial
        self.name = name or self._thing_serial

    def _post_request(self, data: dict) -> requests.Response:
        """client: the client to set in header.

        data: the dictionary to be sent as json
        return: the response from request.
        """
        headers = {
            Inverter.AUTH_KEY: Inverter.AUTH_VALUE,
            Inverter.CLIENT_AUTH_KEY: self.client,
            "Content-Type": Inverter.CONTENT_TYPE,
        }

        _LOGGER.debug(
            "post_request called with client %s, data %s. headers are %s",
            self.client,
            data,
            headers,
        )
        response = requests.post(
            Inverter.ENDPOINT,
            headers=headers,
            json=data,
            timeout=Inverter.REQUEST_TIMEOUT,
        )
        if response.status_code == 401:
            raise HttpRequestError(f"{response.status_code}: Authentication Error")
        return response

    def realtime_data_request(
        self,
        required_values: list[str] | None = None,
    ) -> dict:
        """Request realtime data."""
        if not required_values:
            required_values = [Inverter.REQUIRED_VALUES_ALL]
        data = {
            Inverter.REALTIME_DATA_KEY: {
                Inverter.COMMAND_KEY: Inverter.REALTIME_DATA_COMMAND,
                Inverter.PARAMS_KEY: {
                    Inverter.PARAMS_THING_KEY: self._thing_serial,
                    Inverter.PARAMS_REQUIRED_VALUES_KEY: Inverter.REQUIRED_VALUES_SEP.join(
                        required_values
                    ),
                },
            }
        }
        response = self._post_request(data)
        if not response.ok:
            raise HttpRequestError(f"Request error: {response.status_code}")
        response_data: dict[str, Any] = response.json()[Inverter.REALTIME_DATA_KEY]
        _LOGGER.debug("fetched realtime data %s", response_data)
        if not response_data[Inverter.RESPONSE_SUCCESS_KEY]:
            raise DeviceOfflineError("Device request did not succeed")
        return response_data[Inverter.PARAMS_KEY][
            Inverter.RESPONSE_VALUES_KEY
        ][0][self._thing_serial]

    def alarms_request(self) -> dict:
        """Request alarms."""
        required_values = [Inverter.REQUIRED_VALUES_ALL]
        data = {
            Inverter.DEVICES_ALARMS_KEY: {
                Inverter.COMMAND_KEY: Inverter.DEVICES_ALARMS_COMMAND,
                Inverter.PARAMS_KEY: {
                    Inverter.PARAMS_THING_KEY: self._thing_serial,
                    Inverter.PARAMS_REQUIRED_VALUES_KEY: Inverter.REQUIRED_VALUES_SEP.join(
                        required_values
                    ),
                },
            }
        }
        response = self._post_request(data)
        if not response.ok:
            raise HttpRequestError("Response did not return correctly")
        response_data: dict[str, Any] = response.json()[
            Inverter.DEVICES_ALARMS_KEY
        ]
        _LOGGER.debug("fetched realtime data %s", response_data)
        if not response_data[Inverter.RESPONSE_SUCCESS_KEY]:
            raise DeviceOfflineError("Device request did not succeed")
        return response_data[Inverter.PARAMS_KEY][
            Inverter.RESPONSE_VALUES_KEY
        ][0][self._thing_serial]

    @property
    def identifier(self) -> str:
        """object identifier."""
        return f"{self.client}_{self._thing_serial}"

    def check_connection(self) -> bool:
        try:
            self.realtime_data_request([])
            return True
        except (HttpRequestError, DeviceOfflineError):
            return False
