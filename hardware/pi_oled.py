from time import sleep
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from safety.alert_state import get_alert

I2C_PORT = 1
I2C_ADDRESS = 0x3C


def create_display():
    serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
    device = ssd1306(serial)
    device.contrast(255)
    return device


def show_boot_screen(device):
    with canvas(device) as draw:
        draw.text((0, 0), "CAREBRIDGE", fill="white")
        draw.text((0, 16), "SYSTEM STARTING", fill="white")
        draw.text((0, 30), "QWEN       OK", fill="white")
        draw.text((0, 42), "WHISPER    OK", fill="white")
        draw.text((0, 54), "PIPEWIRE   OK", fill="white")


def show_normal_screen(device, patient="Arjun", location="Home"):
    with canvas(device) as draw:
        draw.text((0, 0), "CAREBRIDGE", fill="white")
        draw.text((0, 14), "SYSTEM NORMAL", fill="white")
        draw.text((0, 28), f"PATIENT: {patient}", fill="white")
        draw.text((0, 40), f"ROOM: {location}", fill="white")
        draw.text((0, 52), "MONITORING...", fill="white")


def show_alert_screen(device, alert):
    reason = str(alert.get("reason") or "HELP")
    patient = str(alert.get("patient") or "Arjun")
    location = str(alert.get("location") or "Unknown")

    with canvas(device) as draw:
        draw.text((0, 0), "!!! ALERT !!!", fill="white")
        draw.text((0, 14), reason[:20], fill="white")
        draw.text((0, 28), f"PATIENT: {patient}", fill="white")
        draw.text((0, 40), f"ROOM: {location}", fill="white")
        draw.text((0, 52), "CAREGIVER NEEDED", fill="white")


def update_display(device, patient="Arjun", location="Home"):
    alert = get_alert()

    if alert.get("active"):
        show_alert_screen(device, alert)
    else:
        show_normal_screen(device, patient, location)


if __name__ == "__main__":
    print("Initializing CareBridge Pi OLED...")

    device = create_display()

    print("OLED: OK")
    show_boot_screen(device)

    sleep(5)

    print("CAREBRIDGE: SYSTEM NORMAL")

    while True:
        update_display(device)
        sleep(2)
