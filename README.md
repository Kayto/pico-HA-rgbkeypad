# Standalone MQTT Home Assistant Keypad Controller

Wifi connected RGB Keypad
using **main.py**

Author: AdamT117 (kayto@github.com)

## What is it?

The code allows the use of a Pimironi RGB keypad as a standalone Home Assistant HA control/notification pad.
Using with a Pi Pico W allows 'wireless' control via MQTT, so you just need to power the Pico.
The pad can provide notification and/or key actions to monitor and control your HA switches and sensors.

What is the point though?

Yes, you can control HA via the webinterface, mobile app or a fancy touchscreen set up. None of which is always that quick or accesible.
I just wanted a simple keypad I could plug in anywhere and via wifi give me an immediate heads up on whether I had left the heating or all the lights on.
OK if thats not enough, then just enjoy the Dr. Evil style level of insight on motion detection and control at the push of a nice RGB button.

![](https://github.com/Kayto/pico-HA-rgbkeypad/blob/main/docs/20241210_175045.jpg)

### Hardware Requirements:
---------
1. Raspberry Pi Pico W:
   - Microcontroller with built-in Wi-Fi capability.
   - Dual-core ARM Cortex-M0+ processor.
   - 264KB SRAM and 2MB onboard flash memory.

2. Pico RGB Keypad:
   - 4x4 RGB LED keypad designed for the Raspberry Pi Pico.
   - Features individually addressable RGB LEDs.
   - Compatible with MicroPython and CircuitPython.
   - Source: https://shop.pimoroni.com/products/pico-rgb-keypad-base

### Software and Dependencies:

The project utilises micropython.
The main.py contains the MQTT and RGB keypad handling. 
Thonny is a good coding UI to get started.

All other files are libraries, using umqtt and pico-rgbkeypad.

 1. Micropython (RPi Pico) - https://micropython.org/
    - License: MIT
    - Copyright © 2014-2024 Damien P. George and contributors
 
 2. umqtt (simple.py) - https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple
    - License: MIT
    - Part of micropython-lib
    - Copyright © micropython-lib contributors
 
 3. rgbkeypad.py - Custom library for RGB Keypad
    - Based on Martin O'Hanlon's RGB Keypad
    - Source: https://github.com/martinohanlon/pico-rgbkeypad/tree/main
    - License: MIT
    - Copyright © 2021 Martin O'Hanlon

### Set up File Structure:
```code
Raspberry Pi Pico
    ├── main.py
    ├── config.py	
    └── lib/
        ├── rgbkeypad.py
        └── umqtt/
            └── simple.py
```			
### Config set up

Credentials for wifi and mqtt should be placed between the quotes within the config.py.

## EXAMPLE RGB KeyMap and MQTT Reference for Home Assistant (HA) Setup

The following assume you have the MQTT Mosquitto broker setup on your Home Assistant.

The following is to assist with Home Assistant handling.
Please use the following as an example, to set up your handling within HomeAssistant.
The hard coding in the main.py relates to.
- key colours
- brightness
- row y=3 acts as notification only, no publish.
It should be obvious where to look if you want to customise.

### RGB KeyMap

| Key y/x | x=0     | x=1      | x=2     | x=3      |
|-|-|-|-|-|
| y=0     | Heating | Cooling  | 'Spare' | 'Spare'  |
| y=1     | RLight1 | RLight2  | Lamp1   | Light3   |
| y=2     | BLight1 | BLamp1   | BLamp2  | Light4   |
| y=3     | Z1Motion| Z2Motion | Z3Motion| Z4Motion |

Colour set up for the keys is handled within the main.py. 
The example is set up as follows. 
- climate control on keys 0,0 and 1,0.
- switches on rows y=1 and y=2
- motion notification on y=3
- all keys apart from motion row have a switch action.

| Key y/x | x=0     | x=1      | x=2     | x=3      |
|-|-|-|-|-|
| y=0     | RED     | BLUE     |         |          |
| y=1     | GREEN   | GREEN    | GREEN   | GREEN    |
| y=2     | GREEN   | GREEN    | GREEN   | GREEN    |
| y=3     | ORANGE  | ORANGE   | ORANGE  | ORANGE   |

## Example MQTT Reference

### From RGB Keypad - RGB Keypad presses send payload 1 to HA.

- Automation name = RGBKEY x,y,payload
- MQTT Topic = RGBKEY/xy
- Payload = 1
- RGB Keypad publishes message based on key map. HA receives and an HA automation toggles the relevant entity status.
Note that main.py ignores key presses (publishing) for motion on y=3 as these keys are just for incoming notifications.

The following lines provide automation name, subscribe topic, payload, short description, entity id.

| Automation Name | MQTT Topic | Payload | Description | Entity ID             |
|-|-|-|-|-|
| RGBKEY 0,0,1    | RGBKEY/00 | 1       | Heating     | climate.heating        |
| RGBKEY 1,0,1    | RGBKEY/10 | 1       | Cooling     | climate.cooling        |
| RGBKEY 0,1,1    | RGBKEY/01 | 1       | RLight1     | light.RLight1          |
| RGBKEY 1,1,1    | RGBKEY/11 | 1       | RLight2     | light.RLight2          |
| RGBKEY 2,1,1    | RGBKEY/21 | 1       | Lamp1       | light.Lamp1            |
| RGBKEY 3,1,1    | RGBKEY/31 | 1       | Light3      | light.Light3           |
| RGBKEY 0,2,1    | RGBKEY/02 | 1       | ALight1     | switch.ALight1         |
| RGBKEY 1,2,1    | RGBKEY/12 | 1       | BLamp1      | light.BLamp1           |
| RGBKEY 2,2,1    | RGBKEY/22 | 1       | BLamp2      | light.BLamp2           |
| RGBKEY 3,2,1    | RGBKEY/32 | 1       | Light4      | light.Light4           |
| RGBKEY 0,3,1    | RGBKEY/03 | 1       | Z1Motion    | binary_sensor.Z1Motion |
| RGBKEY 1,3,1    | RGBKEY/13 | 1       | Z2Motion    | binary_sensor.Z1Motion |
| RGBKEY 2,3,1    | RGBKEY/23 | 1       | Z3Motion    | binary_sensor.Z1Motion |
| RGBKEY 3,3,1    | RGBKEY/33 | 1       | Z4Motion    | binary_sensor.Z1Motion |

Note that there are two spare keys at 2,0 and 3,0

### From HA to RGB Keypad - Status change within HA sends MQTT payload to the RGB Keypad.

- Automation name = KEY x,y,payload
- MQTT Topic = RGBHA/'entitiy description'
- Payload = Three digits (key.x key.y status)
- Status = 0 for off, 1 for on
- HA publishes message, via an automation, based on entity status (ON/OFF). RGB Keypad receives message and updates keypad colour status.
The y=3 motion devices only publish on detection, the automation handler resets the detection after a defined time period (10s), to reduce need for MQTT detection clear message.

The following lines provide automation name, publish topic, payload, short description, entity id.

| Automation Name | MQTT Topic     | Payload | Description | Entity ID |
|-|-|-|-|-|
| KEY 0,0,1       | RGBHA/Heating  | 001 | Heating ON  | climate.heating |
| KEY 0,0,0       | RGBHA/Heating  | 000 | Heating OFF | climate.heating |
| KEY 1,0,1       | RGBHA/Cooling  | 101 | Cooling ON  |  climate.cooling |
| KEY 1,0,0       | RGBHA/Cooling  | 100 | Cooling OFF |  climate.cooling |
| KEY 0,1,1       | RGBHA/RLight1  | 011 | RLight1 ON  | light.RLight1  |
| KEY 0,1,0       | RGBHA/RLight1  | 010 | RLight1 OFF | light.RLight1  |
| KEY 1,1,1       | RGBHA/RLight2  | 111 | RLight2 ON  | light.RLight2 |
| KEY 1,1,0       | RGBHA/RLight2  | 110 | RLight2 OFF | light.RLight2 |
| KEY 2,1,1       | RGBHA/Lamp1    | 211 | Lamp1 ON    | light.Lamp1 |
| KEY 2,1,0       | RGBHA/Lamp1    | 210 | Lamp1 OFF   | light.Lamp1 |
| KEY 3,1,1       | RGBHA/Light3   | 311 | Light3 ON   | light.Light3 |
| KEY 3,1,0       | RGBHA/Light3   | 310 | Light3 OFF  | light.Light3 |
| KEY 0,2,1       | RGBHA/ALight1  | 021 | ALight1 ON  | switch.ALight1 |
| KEY 0,2,0       | RGBHA/ALight1  | 020 | ALight1 OFF | switch.ALight1 |
| KEY 1,2,1       | RGBHA/BLamp1   | 121 | BLamp1 ON   | light.BLamp1 |
| KEY 1,2,0       | RGBHA/BLamp1   | 120 | BLamp1 OFF  | light.BLamp1 |
| KEY 2,2,1       | RGBHA/BLamp2   | 221 | BLamp2 ON   | light.BLamp2 |
| KEY 2,2,0       | RGBHA/BLamp2   | 220 | BLamp2 OFF  | light.BLamp2 |
| KEY 3,2,1       | RGBHA/Light4   | 321 | Light4 ON   | light.Light4 |
| KEY 3,2,0       | RGBHA/Light4   | 320 | Light4 OFF  | light.Light4 |
| KEY 0,3,1       | RGBHA/Z1Motion | 031 | Z1Motion ON | binary_sensor.Z1Motion |
| KEY 1,3,1       | RGBHA/Z2Motion | 131 | Z2Motion ON | binary_sensor.Z2Motion |
| KEY 2,3,1       | RGBHA/Z3Motion | 231 | Z3Motion ON | binary_sensor.Z3Motion |
| KEY 3,3,1       | RGBHA/Z4Motion | 331 | Z4Motion ON | binary_sensor.Z4Motion |

## General Home Assistant (HA) Automation Setup

The automations can be set up via the HA UI or alternatively manually using the example yaml.

### Configuration Setup
To enable separate automation files (recommended) for the keypad, make sure that your configuration.yaml contains the following:

```yaml
# My own handmade automations
automation manual: !include_dir_merge_list automations/
# create automations folder in the HA config folder and place yaml files here.

# Automations I create in the UI
automation ui: !include automations.yaml
```

This configuration allows you to:
- Keep keypad automations in separate files for better organization
- Maintain UI-created automations separately
- Easily backup and version control your automations

### Example HA Automation YAML Configurations

See example automation code below based on the example mapping above.

#### HA Subscription

**Example RGB Keypad to HA automation - Light/Switch Entity**
```yaml
- alias: RGBKEY 0,2,1
  description: BLight1
  triggers:
  - trigger: mqtt
    topic: RGBKEY/02
    payload: "1"
  conditions: []
  actions:
  - action: switch.toggle
    data: {}
    target:
      entity_id: switch.BLight1
  mode: single
```

**Example RGB Keypad to HA automation - Climate Entity**
```yaml
- alias: RGBKEY 0,0,1
  description: Heating
  triggers:
  - trigger: mqtt
    topic: RGBKEY/00
    payload: "1"
  conditions: []
  actions:
  - action: climate.toggle
    data: {}
    target:
      entity_id: climate.heating
  mode: single
```  
#### HA Publish

**Example HA to RGB Keypad automation for Light/Switch Entity ON/OFF**
```yaml
- alias: KEY 0,2,1
  description: BLight1 ON
  triggers:
  - trigger: state
    entity_id:
    - switch.BLight1
    to: 'on'
  conditions: []
  actions:
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/BLight1
      payload: '021'
      retain: true
  mode: single

- alias: KEY 0,2,0
  description: BLight1 OFF
  triggers:
  - trigger: state
    entity_id:
    - switch.BLight1
    to: 'off'
  conditions: []
  actions:
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/BLight1
      payload: '020'
      retain: true
  mode: single
```
**Example HA to RGB Keypad automation - Climate Entity ON/OFF**
```yaml
- alias: KEY 0,0,1
  description: Heating
  triggers:
  - trigger: state
    entity_id:
    - climate.heating
    attribute: hvac_action
    to: heating
    for:
      hours: 0
      minutes: 0
      seconds: 1
  conditions: []
  actions:
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/Heating
      payload: '001'
      retain: true
  mode: single

- alias: KEY 0,0,0
  description: Heating
  triggers:
  - trigger: state
    entity_id:
    - climate.heating
    attribute: hvac_action
    to: 'off'
  conditions: []
  actions:
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/Heating
      payload: '000'
      retain: true
  mode: single
```
**Example HA to RGB Keypad automation - Motion Entity**
```yaml
- alias: KEY 0,3,1
  description: Z1Motion
  triggers:
  - trigger: state
    entity_id:
    - binary_sensor.Z1Motion
    for:
      hours: 0
      minutes: 0
      seconds: 0
    to: 'on'
  conditions: []
  actions:
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/Z1Motion
      payload: '031'
  - delay:
      hours: 0
      minutes: 0
      seconds: 10
      milliseconds: 0
  - action: mqtt.publish
    metadata: {}
    data:
      evaluate_payload: false
      qos: '0'
      topic: RGBHA/Z1Motion
      payload: '030'
  mode: single
```
Version Control:
---------------
Version: 1.0.1
Date: 2024-12-14

Change History:
- 1.0.0 (2024-12-09): Initial release
- 1.0.1 (2024-12-14): All key colours set
- 1.0.2 (2024-12-21): Second button set toggle added on [0,3] : Keypad Light ON/OFF toggle added on [3,3] : Simple user definition added for Key colours in config.py : MQTT Publish modified to allow second button set : MQTT Subscribe modified to allow second button set
