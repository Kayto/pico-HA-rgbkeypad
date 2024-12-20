"""
config.py
Configuration file for:
    Standalone MQTT HomeAssistant Keypad
    Wifi connected RGB Keypad
Author: AdamT117 (kayto@github.com)

Refer to README.md for setup and usage.

Version Control:
---------------
Version: 1.0.1
Date: 2024-12-14
Change History:
- 1.0.0 (2024-12-09): Initial release
- 1.0.1 (2024-12-14): All key colours set
"""

# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# MQTT Configuration
MQTT_HOST = "your_mqtt_host"
MQTT_USERNAME = "your_mqtt_username"
MQTT_PASSWORD = "your_mqtt_password"

# MQTT Topics
# change names to suit
mqtt_publish_topic = "RGBKEY"
mqtt_client_id = "RGB_KEY"
mqtt_subscribe_topic = "RGBHA/#"

# Debug messages
# if debug_mode: if debug_mode: print("Debug: ...")
debug_mode = False  # Set to True to enable debug messages

# Set white key brightness for idle/default state
# added to provide contrast and reduce colour bleed from adjacent keys.
# adjust to preference or (0, 0, 0) for OFF.
default_keypad_color = (6, 6, 6)
