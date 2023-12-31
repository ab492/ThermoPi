## WeatherPi Energy Analysis

By using an energy monitor, we know that the Raspberry Pi running `WeatherPi` uses around 2 watts (W) of energy. What does that mean and how do we transfer that into something tangible so we can power the Raspberry Pi with a solar panel and battery?

### What is a watt?
A watt (W) is a basic unit of power in electrical systems. It measures how much energy is used or produced per second. A kilowatt is 1000 watts.

The relationship between watts, current and voltage can be explained by the following relationship:
```
Power (P) = Voltage (V) x Current (I)
```

So here we have power (measured in watts). Current (measured in amperes) which is the flow of electrical charge moving through a circuit. Voltage (measured in volts) which is the electrical force that drives the current through a circuit; it can be helpful to think of it as the pressure that pushes electrical charges along.

### Breaking Down Kilowatt-Hour
A kilowatt-hour (kWh) is a unit of energy that measures how much electricity is used over time. If you have a device that uses 1 kilowatt of power and you run it for 1 hour, it would use 1kWh of energy.

You can use the following formula to calculate kWh:

```
kWh = Power (W) × Hours (H) ÷ 1,000
```

So to run `WeatherPi` for one day requires 0.048kWh.

### Battery Storage
When looking for battery storage we need to consider days of autonomy to ensure the device can operate through periods of bad weather or low sunlight. For a project like this we'll look at 3 days of autonomy.

For 5 days power, we require 0.144kWh (`3 x 0.048`). We'll also add a 25% error margin to account for inefficiencies and variances in sunlight (though this could be increased to 50% if cost is reasonable). That brings our total to 0.18kWh (`0.144 x 1.25`).

So we require a battery with at least 0.18kWh, or 180 watt-hours, of capacity to power the device for 3 days.

Options:
https://uk.eco-worthy.com/collections/lithium-batteries/products/12v-20ah-portable-lifepo4-deep-cycle-rechargeable-battery - Eco-Worthy reviews are crap!




