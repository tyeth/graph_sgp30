import time
import board
import busio
import displayio
import adafruit_sgp30
import adafruit_sht31d
import adafruit_si7021
import math
# from circuitpython_uplot.uplot import Uplot as uplot
# from circuitpython_uplot.ubar import ubar
from circuitpython_uplot.uplot import Uplot, color
from circuitpython_uplot.ubar import ubar

# Setting up the display
display = board.DISPLAY

# Configuring display dimensions
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Defining the plot
plot = Uplot(
    0,
    0,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    background_color=color.BLACK,
    padding=10,
    box_color=color.WHITE,
)
maingroup = displayio.Group(max_size=10)
maingroup.append(plot)
display.root_group = maingroup

# Set the variable to control which sensor to use: 0 for SHT31, 1 for Si7021, 2 for both
# -1 for no sensors (For bar chart testing)
sensor_selection = -1

# Create the I2C bus
i2c = busio.I2C(board.SCL1, board.SDA1, frequency=400000)

if(sensor_selection == 0 or sensor_selection == 2):
    # Create the SHT3x sensor
    sht3x = adafruit_sht31d.SHT31D(i2c)
    sht3x.heater = False
    sht3x.repeatability = adafruit_sht31d.REP_HIGH
    sht3x.mode = adafruit_sht31d.MODE_SINGLE
    
if(sensor_selection == 1 or sensor_selection == 2):
    # Create the SI7021 sensor
    si7021 = adafruit_si7021.SI7021(i2c)
    si7021.heater_enable = False

if(sensor_selection != -1):
    # Create the SGP30 sensor
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

    # Initialize the sensors
    sgp30.iaq_init()

def get_absolute_humidity(temperature, humidity):
    # approximation formula from Sensirion SGP30 Driver Integration chapter 3.15
    absolute_humidity = (
        216.7
        * (
            (humidity / 100.0)
            * 6.112
            * math.exp((17.62 * temperature) / (243.12 + temperature))
            / (273.15 + temperature)
        )
    )  # [g/m^3]
    absolute_humidity_scaled = int(1000.0 * absolute_humidity)  # [mg/m^3]
    return absolute_humidity_scaled


# Create a list to store the data
data = []

plot = Uplot(x = 0,         \
    y = 0,                  \
    width = 100,            \
    height = 100,           \
    padding = 25,           \
    show_box = True,        \
    background_color = 0,   \
    box_color = 16777215,   \
    tickx_height = 8,       \
    ticky_height = 8,       \
    scale = 1               \
    )


# Loop forever
while True:
    if sensor_selection != -1:
        if sensor_selection == 0 or sensor_selection == 2:
            # Get the humidity and temperature data from the SHT3x sensor
            humidity = sht3x.relative_humidity
            temperature = sht3x.temperature
            print(f"SHT3x Humidity: {humidity:.3f} %, Temperature: {temperature:.3f} C")

        if sensor_selection == 1 or sensor_selection == 2:
            # Get the humidity and temperature data from the SI7021 sensor
            si7021_humidity = si7021.relative_humidity
            si7021_temperature = si7021.temperature
            print(f"SI7021 Humidity: {si7021_humidity:.3f} %, Temperature: {si7021_temperature:.3f} C")

        if sensor_selection == 0:
            average_humidity = humidity
            average_temperature = temperature
        elif sensor_selection == 1:
            average_humidity = si7021_humidity
            average_temperature = si7021_temperature
        else:
            average_humidity = (humidity + si7021_humidity) / 2
            average_temperature = (temperature + si7021_temperature) / 2

        sgp30.set_iaq_relative_humidity(average_temperature, average_humidity/100.0)
        time.sleep(0.1)
        # Get the VOC and CO2 data from the SGP30 sensor
        voc = sgp30.TVOC
        co2 = sgp30.eCO2
        print(f"VOC: {voc} ppb, CO2: {co2} ppm")
        # Add the data to the list
        data.append((voc, co2, average_humidity, average_temperature))
    else:
        # Add dummy data to the list
        data.append((55, 20, 25, 30, 35, 10))


    # Plot the data
    # plot = ubar(plot=plot,     \
    #     x = 0,                 \
    #     y = 0,                 \
    #     x: list[Unknown],
    # y: list[Unknown],
    # color: int = 16777215,
    # fill: bool = False,
    # bar_space: int = 16,
    # xstart: int = 50,
    # projection: bool = False,
    # color_palette: Unknown | None = None,
    # max_value: Unknown | None = None
    #     )
    my_ubar = ubar(plot, \
            [d[3] for d in data], \
            [d[0] for d in data],  \
            0xFF1000, \
            True, \
            projection=False, \
            max_value=500, \
            #color=0x00FF00, fill=True, bar_space=16, xstart=50, projection=True, max_value=1000)
    # .figure(title="VOC + CO2")
    # plot.add_subplot("111", xlabel="Time (s)", ylabel="Value")
    # plot.plot([d[3] for d in data], [d[0] for d in data], label="VOC")
    # plot.plot([d[3] for d in data], [d[1] for d in data], label="CO2")
    # plot.plot([d[3] for d in data], [d[2] for d in data], label="Relative Humidity")
    # plot.legend()
    
)
    time.sleep(2)
    # Changing all the bars to Yellow
    my_ubar.update_colors(
        [color.YELLOW, color.YELLOW, color.YELLOW, color.YELLOW, color.YELLOW, color.YELLOW]
    )

    time.sleep(2)

    # Changing the 3 bar to Purple
    my_ubar.update_bar_color(2, color.PURPLE)

    # Wait 1 second
    time.sleep(1)
