# boot.py
import gc
gc.collect()

from time import ticks_ms, sleep
import network
import secrets

wifis = secrets.wifis

def do_connect(timeout_ms=50000, min_try_ms=10000):
    wlan = network.WLAN(network.STA_IF)

    # If already connected, do nothing
    if wlan.isconnected() and wlan.status() == network.STAT_GOT_IP:
        print("WiFi already connected")
        print("IP:", wlan.ifconfig())
        return wlan

    # Clean WiFi reset
    wlan.active(False)
    sleep(2)
    wlan.active(True)
    sleep(2)

    for ssid, password in wifis.items():
        print(f"Connecting to {ssid} ...")

        wlan.disconnect()
        sleep(2)

        print(f">>> wlan.connect({ssid})")
        wlan.connect(ssid, password)

        start = ticks_ms()
        last_status = None

        while True:
            elapsed = ticks_ms() - start
            status = wlan.status()

            if status != last_status:
                print(f"  status: {status} ({elapsed//1000}s)")
                last_status = status

            # Success
            if status == network.STAT_GOT_IP:
                print(f"Connected to {ssid}")
                print("IP:", wlan.ifconfig())
                return wlan

            # Ignore early failures — ESP32 needs time
            if elapsed > min_try_ms and status < 0:
                print(f"Confirmed failure on {ssid}")
                break

            # Absolute timeout
            if elapsed > timeout_ms:
                print(f"Timeout connecting to {ssid}")
                break

            sleep(0.5)

        # Give firmware time to recover before next SSID
        sleep(3)

    print("WiFi connection failed for all networks")
    return wlan


wlan = do_connect()
