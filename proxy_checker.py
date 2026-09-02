import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

TEST_URL = "https://httpbin.org/ip"
TIMEOUT = 10
MAX_WORKERS = 10


def check_proxy(proxy):
    """Check whether a proxy can connect to the test endpoint."""

    proxies = {
        "http": proxy,
        "https": proxy
    }

    start_time = time.time()

    try:
        response = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        latency = round((time.time() - start_time) * 1000, 2)

        return {
            "proxy": proxy,
            "working": True,
            "latency_ms": latency,
            "status_code": response.status_code,
            "error": None
        }

    except requests.RequestException as error:
        return {
            "proxy": proxy,
            "working": False,
            "latency_ms": None,
            "status_code": None,
            "error": str(error)
        }


def load_proxies(filename="proxies.txt"):
    """Load proxies from a text file."""

    with open(filename, "r", encoding="utf-8") as file:
        return [
            line.strip()
            for line in file
            if line.strip() and not line.startswith("#")
        ]


def main():
    print("OpenProxyTools")
    print("-" * 30)

    proxies = load_proxies()

    if not proxies:
        print("No proxies found in proxies.txt")
        return

    print(f"Checking {len(proxies)} proxies...\n")

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(check_proxy, proxy): proxy
            for proxy in proxies
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["working"]:
                print(
                    f"[WORKING] {result['proxy']} "
                    f"- {result['latency_ms']}ms"
                )
            else:
                print(f"[FAILED] {result['proxy']}")

    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    working = sum(
        1 for result in results
        if result["working"]
    )

    print("\n" + "-" * 30)
    print(f"Working proxies: {working}/{len(results)}")
    print("Results saved to results.json")


if __name__ == "__main__":
    main()
