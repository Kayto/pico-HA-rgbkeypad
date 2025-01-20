"""
main.py

Standalone MQTT HomeAssistant Keypad
Wifi connected RGB Keypad
Author: AdamT117 (kayto@github.com)

Refer to README.md for setup and usage.

Version Control:
---------------
Version: 1.0.2
Date: 2024-12-21
Change History:
- 1.0.0 (2024-12-09): Initial release
- 1.0.1 (2024-12-14): All key colours set
- 1.0.2 (2024-12-21): Second button set toggle added on [0,3]
                    : Keypad Light ON/OFF toggle added on [3,3]
                    : Simple user definition added for Key colours in config.py 
                    : MQTT Publish modified to allow second button set
                    : MQTT Subscribe modified to allow second button set

"""
import network
import time
from machine import Timer
from umqtt.simple import MQTTClient
from rgbkeypad import RGBKeypad
from config import WIFI_SSID, WIFI_PASSWORD, MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, mqtt_publish_topic, mqtt_client_id, mqtt_subscribe_topic, debug_mode, default_keypad_color

keypad = RGBKeypad()

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

# Set up timer for button checking
button_timer = Timer(-1)
button_timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t: check_buttons())
print("Button timer initialized")

# Create a dictionary to store the last press time for each key
last_press_times = {}
DEBOUNCE_TIME_MS = 200  # Adjust this value to change debounce sensitivity

# Main loop with message handling
print("Starting main loop...")
last_check = time.ticks_ms()
CHECK_INTERVAL = 50  # Check every 50ms

# make all the keys default at start and to notify Wifi connected
keypad.color = default_keypad_color

# define default start button set, toggle on 0,3 key
button_set_0_3 = 0

# define keypad lights ON/OFF status, toggle on 3,3 key
keypad_onoff_status_3_3 = 1

# define keypad colour mapping
from config import button_set_conditions

# Function to toggle debug messages
def set_debug_mode(mode):
    global debug_mode
    debug_mode = mode
    if debug_mode:
        print("Debug mode enabled")
    else:
        print("Debug mode disabled")
        
def check_onoff():
    if keypad_onoff_status_3_3 == 0:
        keypad.clear()
           
# Refactor the callback function to use the mapping
def get_key_color(button_set, key_x, key_y):
    for condition, (color, color_name) in button_set_conditions[button_set].items():
        if condition == 'default':
            continue
        x_cond, y_cond = condition
        if (x_cond is None or key_x == x_cond) and (y_cond is None or key_y in (y_cond if isinstance(y_cond, tuple) else [y_cond])):
            return color, color_name
    return button_set_conditions[button_set]['default']

def mqtt_callback(topic, msg):
    global last_activity_time
    last_activity_time = time.time()  # Reset activity timer
    if debug_mode: print("Debug: Callback triggered with topic:", topic)

    # Only process if keypad is ON
    if keypad_onoff_status_3_3 == 1:
        if debug_mode: print("Keypad is ON")
        try:
            payload = msg.decode('utf-8')
            print("Received MQTT message - Topic: {}, Payload: {}".format(topic.decode(), payload))
            
            button_set = int(payload[0])
            key_x = int(payload[1])
            key_y = int(payload[2])
            status = int(payload[3])

            key = keypad.get_key(key_x, key_y)
            if status == 1:
                key.color, color_name = get_key_color(button_set_0_3, key_x, key_y)
                if debug_mode:
                    print("Debug: Updated key ({}, {}) to {}".format(key_x, key_y, color_name))
            else:
                key.color = default_keypad_color  # Turn off the key
                if debug_mode:
                    print("Debug: Turned off key ({}, {})".format(key_x, key_y))
        except Exception as e:
            print("Error processing MQTT message:", e)

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
    # Check the state of all buttons only when pressed
    button_states = keypad.get_keys_pressed()
    
    for i, pressed in enumerate(button_states):
        key = keypad.keys[i]
        # ON OFF Status Check ==========================
        # Row y=3, x=3 is toggles the RGB lights ON/OFF       
        if key.x == 3 and key.y == 3 and pressed and is_valid_press(key):
            global keypad_onoff_status_3_3
            keypad_onoff_status_3_3 = 1 - keypad_onoff_status_3_3
            if debug_mode: print("Button at x=3, y=3 pressed! Lights ON/OFF status: {}".format(keypad_onoff_status_3_3))
            if keypad_onoff_status_3_3 == 1:
                keypad.color = default_keypad_color
                if debug_mode: print("Lights ON")
                connect_mqtt()                
            else:
                check_onoff()
                
        # Button Set Status Check ==========================        
        # Row y=3, x=0 is toggles the button sets       
        if key.x == 0 and key.y == 3 and pressed and is_valid_press(key):
            global button_set_0_3
            button_set_0_3 = 1 - button_set_0_3
            if debug_mode: print("Button at x=0, y=3 pressed! Toggle button set: {}".format(button_set_0_3))
            connect_mqtt()  # Reconnect to MQTT server after toggle change
            
        # Action Button Check ==========================    
        # Only process keys in rows y0 to y2 and when the button is pressed
        # remaining Row y=3 is motion notifications only
        if key.y <= 2 and pressed and is_valid_press(key):
            subtopic = "{}/{}/{}{}".format(mqtt_publish_topic, button_set_0_3, key.x, key.y)
            payload = "1"
            if debug_mode: print("Key pressed at ({}, {}), publishing to topic: {}, payload: {}".format(key.x, key.y, subtopic, payload))
        # then publish to RGBKEY/<button_set_0_3>/xy subtopics   
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









