#!/bin/python3
"""
check_jenkins_ready.py

Ping a Jenkins server until its login screen is reachable.

Usage:
    ./check_jenkins_ready.py <jenkins_base_url>

Example:
    ./check_jenkins_ready.py http://localhost:8080

Exits:
    0  if Jenkins login page is detected before timeout
    1  if 5 minutes elapse without detecting the login page
    2  if usage is incorrect
"""

import sys
import time
from urllib import request, error

TIMEOUT_SECONDS = 5 * 60 # 5 * 60
POLLING_INTERVAL = 30 # 30

def jenkins_login_ready(base_url: str) -> bool:
    """
    Try to fetch <base_url>/login and look for the Jenkins login form
    (we check for the presence of 'j_username' in the HTML).
    Returns True if found, False otherwise.
    Raises URLError on HTTP/network failures.
    """
    login_url = base_url.rstrip('/') + '/login'
    resp = request.urlopen(login_url, timeout=10)
    body = resp.read()
    # The Jenkins login page always contains an <input name="j_username" …>
    return b'j_username' in body


def main(polling_interval, timeout_seconds):
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <jenkins_base_url>", file=sys.stderr)
        sys.exit(2)

    base_url = sys.argv[1]
    start_time = time.time()

    print(f"POLLING INTERVAL: { polling_interval }s")
    print(f"TIMEOUT VALUE: { timeout_seconds }s")

    while True:
        try:
            if jenkins_login_ready(base_url):
                print("-> Jenkins login page detected. Exiting with code 0.")
                sys.exit(0)
            else:
                print("-> Connected but did not see login form yet. Retrying in { polling_interval } s...")
        except error.URLError as e:
            # e.g. Connection refused, name not resolved, timeout, etc.
            print(f"-> Connection failed: {e}. Retrying in { polling_interval } s...")
        except Exception as e:
            # Any unexpected exception (just in case)
            print(f"-> Unexpected error: {e}. Retrying in { polling_interval } s...")

        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            print(f"-> Timeout ({ timeout_seconds } s) reached; Jenkins never showed login. Exiting with code 1.")
            sys.exit(1)

        time.sleep(polling_interval)


if __name__ == "__main__":
    main(POLLING_INTERVAL, TIMEOUT_SECONDS)
