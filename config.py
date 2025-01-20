"""
config.py
Configuration file for:
    main.py
    Standalone MQTT HomeAssistant Keypad
    Wifi connected RGB Keypad
Author: AdamT117 (kayto@github.com)

Refer to README.md for setup and usage.

Version Control:
---------------
Version: 1.0.1
Date: 2024-12-23
Change History:
- 1.0.0 (2024-12-09): Initial release
- 1.0.1 (2024-12-23): Button set definitions added

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

"""
Summary of `button_set_conditions`:
- It maps button sets (0 or 1) to specific key conditions for assigning colors.
- Each button set contains:
  - Key coordinates `(x, y)` or `(None, y)` for rows/columns.
  - RGB color values and their corresponding names.
  - A `'default'` key for unmatched conditions.

To modify:
- Add a new condition: `(x, y): ((R, G, B), 'ColorName')`.
- Update an existing condition: Change the RGB or name for a specific key.
- Change the default: Update the `'default'` key.

Example:
- To make key `(0, 0)` Yellow in button set 0, add `(0, 0): ((255, 255, 0), 'Yellow')` under `button_set_conditions[0]`.
"""
button_set_conditions = {
    0: {
        (1, 0): ((0, 0, 255), 'Blue'),
        (2, 0): ((120, 0, 160), 'Purple'),
        (None, 3): ((255, 75, 0), 'Orange'),
        (None, (1, 2)): ((0, 225, 0), 'Green'),
        'default': ((255, 0, 0), 'Red'),
    },
    1: {
        (1, 0): ((255, 255, 0), 'Yellow'), #  (contrast to Blue)
        (2, 0): ((100, 255, 0),  'Light Green'),#  (contrast to Purple)
        (None, 3): ((0, 180, 255), 'Cyan'), #  (contrast to Orange)
        (None, (1, 2)): ((255, 00, 255), 'Magenta'),  #  (contrast to Green)
        'default': ((0, 0, 255), 'Blue'),  # Blue (contrast to Red)
    },
}

