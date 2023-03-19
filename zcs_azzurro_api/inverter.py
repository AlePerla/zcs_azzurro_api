"""ZCS Azzurro API."""
from __future__ import annotations
import logging
from typing import Any

import requests

from .errors import DeviceOfflineError, HttpRequestError

_LOGGER = logging.getLogger(__name__)

from .const import (
    ENDPOINT,
    AUTH_KEY,
    AUTH_VALUE,
    CLIENT_AUTH_KEY,
    CONTENT_TYPE,
    REQUEST_TIMEOUT,
    REALTIME_DATA_KEY,
    REALTIME_DATA_COMMAND,
    DEVICES_ALARMS_KEY,
    DEVICES_ALARMS_COMMAND,
    COMMAND_KEY,
    PARAMS_KEY,
    PARAMS_THING_KEY,
    PARAMS_REQUIRED_VALUES_KEY,
    RESPONSE_SUCCESS_KEY,
    RESPONSE_VALUES_KEY,
    REQUIRED_VALUES_ALL,
    REQUIRED_VALUES_SEP
)


class Inverter:
    """Class implementing ZCS Azzurro API for inverters."""

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
            AUTH_KEY: AUTH_VALUE,
            CLIENT_AUTH_KEY: self.client,
            "Content-Type": CONTENT_TYPE,
        }

        _LOGGER.debug(
            "post_request called with client %s, data %s. headers are %s",
            self.client,
            data,
            headers,
        )
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 401:
            raise HttpRequestError(
                f"{response.status_code}: Authentication Error",
                status_code=response.status_code)
        return response

    def realtime_data_request(
            self,
            required_values: list[str] | None = None,
    ) -> dict:
        """Request realtime data."""
        if not required_values:
            required_values = [REQUIRED_VALUES_ALL]
        data = {
            REALTIME_DATA_KEY: {
                COMMAND_KEY: REALTIME_DATA_COMMAND,
                PARAMS_KEY: {
                    PARAMS_THING_KEY: self._thing_serial,
                    PARAMS_REQUIRED_VALUES_KEY: REQUIRED_VALUES_SEP.join(
                        required_values
                    ),
                },
            }
        }
        response = self._post_request(data)
        if not response.ok:
            raise HttpRequestError(
                f"Request error: {response.status_code}",
                status_code=response.status_code)
        response_data: dict[str, Any] = response.json()[REALTIME_DATA_KEY]
        _LOGGER.debug("fetched realtime data %s", response_data)
        if not response_data[RESPONSE_SUCCESS_KEY]:
            raise DeviceOfflineError("Device request did not succeed")
        return response_data[PARAMS_KEY][
            RESPONSE_VALUES_KEY
        ][0][self._thing_serial]

    def alarms_request(self) -> dict:
        """Request alarms."""
        required_values = [REQUIRED_VALUES_ALL]
        data = {
            DEVICES_ALARMS_KEY: {
                COMMAND_KEY: DEVICES_ALARMS_COMMAND,
                PARAMS_KEY: {
                    PARAMS_THING_KEY: self._thing_serial,
                    PARAMS_REQUIRED_VALUES_KEY: REQUIRED_VALUES_SEP.join(
                        required_values
                    ),
                },
            }
        }
        response = self._post_request(data)
        if not response.ok:
            raise HttpRequestError(
                "Response did not return correctly",
                status_code=response.status_code)
        response_data: dict[str, Any] = response.json()[
            DEVICES_ALARMS_KEY
        ]
        _LOGGER.debug("fetched realtime data %s", response_data)
        if not response_data[RESPONSE_SUCCESS_KEY]:
            raise DeviceOfflineError("Device request did not succeed")
        return response_data[PARAMS_KEY][
            RESPONSE_VALUES_KEY
        ][0][self._thing_serial]

    @property
    def identifier(self) -> str:
        """object identifier."""
        return f"{self.client}_{self._thing_serial}"

    def check_connection(self) -> bool | None:
        self.realtime_data_request([])
        return True
