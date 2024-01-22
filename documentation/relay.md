In order to control the heating system with the Raspberry Pi I need to use a relay.

## What is a relay?
A relay is an electrically operated switch which allows you to control a high power circuit (like the heating system) with a low powered circuit (like one powered by the Raspberry Pi). Relays consist of an electromagnet and a switch: when electric current passes through the coil of the electromagnet, it creates a magnetic field that connects the switch.

## NO or NC
A relay has two options for controlling a circuit: Normally Open (NO) or Normally Closed (NC). For something like a thermostat, we want the circuit to be normally open (i.e. the circuit is broken) since we don't want a thermostat on all the time. When we want it on, we'll energise the relay which will connect the normally open circuit to common and complete the circuit, thus turning our thermostat on.

## Which Relay to Use?
I've chosen a Waveshare 3 terminal relay, since at most I'll want to control the temperature in 3 zones (for now). The key information about this relay is that it's suitable for high power circuits, being able to work with loads up to 5A 250V AC or 5A 30V DC.

It's also important to note that this is low active, meaning that setting low turns the relay on.

## Replacing the Thermostat
In the back of the existing thermostat where 4 cables: a timer, live (L), switched live (SL) and neutral (N).

Live and neutral allow the thermostat to be powered (giving it the ability to have a complete circuit) and the switched live is this missing piece of the circuit that is completed when the thermostat needs to turn the boiler on. 

For my purposes, I only needed two of these cables: switched live will be in the NO connection of my relay since the default is no connection; live will go into the common port of my relay. When I energise the relay, it'll complete the circuit between live and switched live and turn the heating on.

## Relay Specific Info

| Channel No. | BCM | 
|----------|----------|
| CH1 | 26 |
| CH2 | 20 |
| CH3 | 21 | 

[Original Link](https://thepihut.com/products/raspberry-pi-relay-board)
[Wiki Information](https://www.waveshare.com/wiki/RPi_Relay_Board)
[Manufacturer Information](https://www.waveshare.com/rpi-relay-board.htm)