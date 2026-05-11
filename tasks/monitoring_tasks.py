import requests
import subprocess
import platform


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


def ping_host(hostname: str, count: int = 1):
    """
    Pings a host to check network connectivity.
    :param hostname: The IP or Domain to ping (e.g., '8.8.8.8' or 'google.com')
    :param count: Number of packets to send
    """
    # Determine the flag for packet count based on OS (Linux/macOS use -c, Windows uses -n)
    param = "-n" if platform.system().lower() == "windows" else "-c"

    command = ["ping", param, str(count), hostname]

    # Run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        return f"SUCCESS: {hostname} is reachable."
    else:
        return f"FAILURE: {hostname} is unreachable."
