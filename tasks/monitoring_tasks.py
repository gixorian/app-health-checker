import requests


def check_site_status(url: str, timeout: int = 2):
    """
    Pings a URL and returns UP if the status code is 2xx or 3xx,
    otherwise returns DOWN.
    """

    try:
        response = requests.get(url, timeout=timeout)

        if 200 <= response.status_code < 400:
            status = "UP"
        else:
            status = "DOWN"

        return {"url": url, "status": status, "code": response.status_code}
    except Exception as e:
        return {"url": url, "status": "DOWN", "error": str(e)}
