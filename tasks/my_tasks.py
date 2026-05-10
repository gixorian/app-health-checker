import time


def debug_sleep(seconds: int = 5):
    print(f"Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    return f"Slept for {seconds} succesfully."
