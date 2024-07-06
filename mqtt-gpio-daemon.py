#!/usr/bin/python3 -u
import time
import paho.mqtt.client as mqtt

gpio_shutter = ["rollo"]

allowed_gpio = ["115", "11", "50", "60", "61", "65", "88", "117"]

default_on = ["115", "50"]

debug = True

def debug_print(msg):
    if debug:
        print(msg)

def on_connect(client, userdata, flags, rc):
    client.subscribe("cmnd/bbb/+")
    client.subscribe("homeassistant/status")
    debug_print ("Connected")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        debug_print("Unexpected disconnection.")

def on_message(client, userdata, msg):
    debug_print ("Topic: " + msg.topic)
    if msg.topic.startswith("cmnd/bbb"):
        gpio = msg.topic.replace("cmnd/bbb/","")
        debug_print ("GPIO: " + gpio)
    
        state = msg.payload.decode()
        debug_print ("payload: " + state)
    
        allowed = check_allowed_gpio(gpio)
    
        if allowed:
            if state == "ON":
                if gpio in default_on:
                    set_gpio_state(gpio, "1")
                else:
                    set_gpio_state(gpio, "0")
    
            elif state == "OFF":
                if gpio in default_on:
                    set_gpio_state(gpio, "0")
                else:
                    set_gpio_state(gpio, "1")
    
            get_state(gpio)
    
        if gpio == "opendoor":
            debug_print ("Haustür: " + state)
            direction = state
            set_gpio_state("46", "0")
            time.sleep(2)
            set_gpio_state("46", "1")
    
        if gpio == "rollosusanne":
            debug_print ("Rollo Susanne: " + state)
            direction = state
            if direction == "OPEN":
                set_gpio_state("72", "1")
                set_gpio_state("74", "1")
                time.sleep(0.5)
                set_gpio_state("72", "0")
            elif direction == "CLOSE":
                set_gpio_state("72", "1")
                set_gpio_state("74", "1")
                time.sleep(0.5)
                set_gpio_state("74", "0")
            else:
                set_gpio_state("72", "1")
                set_gpio_state("74", "1")
    
        if gpio == "rollogarage":
            debug_print ("Rollo Garage: " + state)
            direction = state
            if direction == "OPEN":
                set_gpio_state("26", "0")
                set_gpio_state("44", "1")
            elif direction == "CLOSE":
                set_gpio_state("26", "0")
                set_gpio_state("44", "0")
            else:
                set_gpio_state("26", "1")
                set_gpio_state("44", "1")
    
        if gpio == "rollobad":
            debug_print ("Rollo Bad: " + state)
            direction = state
            if direction == "OPEN":
                set_gpio_state("30", "0")
                set_gpio_state("31", "1")
            elif direction == "CLOSE":
                set_gpio_state("30", "0")
                set_gpio_state("31", "0")
            else:
                set_gpio_state("30", "1")
                set_gpio_state("31", "1")
    
        if gpio == "rolloschlaffenster":
            debug_print ("Rollo Schlaf Fenster: " + state)
            direction = state
            if direction == "OPEN":
                set_gpio_state("88", "0")
                set_gpio_state("61", "1")
            elif direction == "CLOSE":
                set_gpio_state("88", "0")
                set_gpio_state("61", "0")
            else:
                set_gpio_state("88", "1")
                set_gpio_state("61", "1")
    
        if gpio == "rolloschlaftuer":
            debug_print ("Rollo schlaf: " + state)
            direction = state
            if direction == "OPEN":
                set_gpio_state("11", "0")
                set_gpio_state("89", "0")
            elif direction == "CLOSE":
                set_gpio_state("11", "0")
                set_gpio_state("89", "1")
            else:
                set_gpio_state("11", "1")
                set_gpio_state("89", "1")
    
        if gpio in gpio_shutter:
            up,down,direction = state.split(",")
            set_gpio_state(up, "1")
            set_gpio_state(down, "1")
            time.sleep(1)
            if direction == "OPEN":
                set_gpio_state(down, "1")
                set_gpio_state(up, "0")
            elif direction == "CLOSE":
                set_gpio_state(up, "1")
                set_gpio_state(down, "0")
            else:
                set_gpio_state(up, "1")
                set_gpio_state(down, "1")

def set_gpio_state(gpio, state):
    fo = open("/sys/class/gpio/gpio" + gpio + "/value", "r+")
    fo.write(state)
    fo.close()

def get_state(p):
    fo = open("/sys/class/gpio/gpio" + p + "/value", "r")
    gpio_status = fo.read(1)
    if gpio_status == "0" and p not in default_on:
        debug_print("ON")
        client.publish("stat/bbb/" + p, "ON")
    elif gpio_status == "1" and p not in default_on:
        debug_print("OFF")
        client.publish("stat/bbb/" + p, "OFF")
    elif gpio_status == "0" and p in default_on:
        debug_print("OFFin")
        client.publish("stat/bbb/" + p, "OFF")
    elif gpio_status == "1" and p in default_on:
        debug_print("ONin")
        client.publish("stat/bbb/" + p, "ON")
    fo.close()

def check_allowed_gpio(p):
    if p in allowed_gpio:
        return True
    else:
        return False

client = mqtt.Client()
client.connect("192.168.178.210",1883,60)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.loop_forever()

