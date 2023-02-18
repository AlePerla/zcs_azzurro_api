from requests.exceptions import HTTPError


class DeviceOfflineError(Exception):
    """Class for offline device error"""

    def __init__(self, *args):
        super().__init__(args)


class HttpRequestError(HTTPError):
    """Class for requests errors"""

    def __init__(self, *args):
        super().__init__(args)
