

"""
main.py

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
import network
import time
from machine import Timer
from umqtt.simple import MQTTClient
from rgbkeypad import RGBKeypad
from config import WIFI_SSID, WIFI_PASSWORD, MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, mqtt_publish_topic, mqtt_client_id, mqtt_subscribe_topic, debug_mode, default_keypad_color

# Function to toggle debug messages
def set_debug_mode(mode):
    global debug_mode
    debug_mode = mode
    if debug_mode:
        print("Debug mode enabled")
    else:
        print("Debug mode disabled")

# Create a dictionary to store the last press time for each key
last_press_times = {}
DEBOUNCE_TIME_MS = 200  # Adjust this value to change debounce sensitivity

keypad = RGBKeypad()

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")
# make all the keys default at start and to notify Wifi connected
keypad.color = default_keypad_color

def mqtt_callback(topic, msg):
    global last_activity_time
    last_activity_time = time.time()  # Reset activity timer
    if debug_mode: print("Debug: Callback triggered with topic:", topic)
    try:
        payload = msg.decode('utf-8')
        print("Received MQTT message - Topic: {}, Payload: {}".format(topic.decode(), payload))
        
        key_x = int(payload[0])
        key_y = int(payload[1])
        status = int(payload[2])

        key = keypad.get_key(key_x, key_y)
        if status == 1:
            if key.x == 1 and key.y == 0:
                key.color = (0, 0, 255)  # Blue for x=0, y=1
                if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Blue'))
            elif key.y == 3:
                key.color = (255, 75, 0)  # Orange for y=3 row
                if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Orange'))
            elif key.x == 2 and key.y == 0:
                key.color = (120, 0, 160)  # Purple for x=2, y=0
                if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Purple'))
            elif key.y in [1, 2]:
                key.color = (0, 225, 0)  # Green for y=1 or y=2
                if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Green'))
            else:
                key.color = (255, 0, 0)  # Red for ON
                if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Red'))
        else:
            key.color = default_keypad_color    # Dim white for OFF
            if debug_mode: print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, 'Dim White'))
    except Exception as e:
        print("Error processing MQTT message: {}".format(e))

def is_valid_press(key):
    # Check if enough time has passed since the last press
    current_time = time.ticks_ms()
    key_id = (key.x, key.y)
    
    if key_id not in last_press_times:
        last_press_times[key_id] = current_time
        return True
    
    time_diff = time.ticks_diff(current_time, last_press_times[key_id])
    if time_diff >= DEBOUNCE_TIME_MS:
        last_press_times[key_id] = current_time
        return True
    
    return False

def check_buttons():
    global last_activity_time
    # Check the state of all buttons and publish to RGBKEY/xy subtopics only when pressed
    button_states = keypad.get_keys_pressed()
    
    for i, pressed in enumerate(button_states):
        key = keypad.keys[i]
        # Only process keys in rows y0 to y2 and when the button is pressed
        # Row y=3 is motion notifications only
        if key.y <= 2 and pressed and is_valid_press(key):
            subtopic = "{}/{}{}".format(mqtt_publish_topic, key.x, key.y)
            payload = "1"
            print("Key pressed at ({}, {}), publishing to topic: {}, payload: {}".format(key.x, key.y, subtopic, payload))
            try:
                mqtt_client.publish(subtopic, payload)
            except Exception as e:
                print("Failed to publish message:", e)
def connect_mqtt():
    # Connect to MQTT broker with error handling
    global mqtt_client
    
    if debug_mode: print("Debug: Starting MQTT connection...")
    try:
        mqtt_client = MQTTClient(
            client_id=mqtt_client_id,
            server=MQTT_HOST,
            user=MQTT_USERNAME,
            password=MQTT_PASSWORD,
            keepalive=30
        )
        
        mqtt_client.set_callback(mqtt_callback)
        
        try:
            mqtt_client.connect()
            if debug_mode: print("Debug: MQTT connection successful")
        except Exception as e:
            print("Error during MQTT connect:", e)
            raise e
        
        mqtt_client.subscribe(mqtt_subscribe_topic.encode())
        print("Connected and subscribed to {}".format(mqtt_subscribe_topic))
        return mqtt_client
    except Exception as e:
        print("Error in connect_mqtt:", e)
        raise e

# Initial MQTT connection
mqtt_client = connect_mqtt()

# Set up timer for button checking
button_timer = Timer(-1)
button_timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t: check_buttons())
print("Button timer initialized")

# Main loop with message handling
print("Starting main loop...")
last_check = time.ticks_ms()
CHECK_INTERVAL = 50  # Check every 50ms

while True:
    try:
        # Non-blocking message check
        if mqtt_client.sock != None:
            mqtt_client.sock.setblocking(False)
            try:
                last_msg_check = time.ticks_ms()
                mqtt_client.check_msg()
                if time.ticks_diff(time.ticks_ms(), last_msg_check) > 5000:  # 5 second timeout
                    print("Warning: Message check timeout")
                    raise Exception("Message check timeout")
            except Exception as check_error:
                print("Message check error:", check_error)
                mqtt_client = connect_mqtt()  # Force reconnection on timeout
        
        # Periodic connection check and reconnect if needed
        if time.ticks_diff(time.ticks_ms(), last_check) > CHECK_INTERVAL:
            if not mqtt_client.sock:
                print("Connection lost, reconnecting...")
                mqtt_client = connect_mqtt()
            last_check = time.ticks_ms()
        
        # Small delay to prevent CPU overload
        time.sleep_ms(10)
        
    except Exception as e:
        print("Main loop error:", e)
        try:
            print("Attempting to reconnect...")
            mqtt_client = connect_mqtt()
        except Exception as reconnect_error:
            print("Reconnection failed:", reconnect_error)
            time.sleep(5)



