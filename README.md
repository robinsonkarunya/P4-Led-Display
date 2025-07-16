# P4-Led-Display
# Raspberry Pi P4 RGB LED Matrix (80x40, 1/20 Scan)

This project configures and drives an **80x40 P4 RGB LED matrix** using a **Raspberry Pi** (tested with Pi 4) and a 20-way multiplexing scheme. It uses **custom GPIO pinout mappings** for a 3-chain parallel configuration.

## 💡 Features

- Supports 80x40 pixel P4 RGB LED Matrix
- 1/20 scan rate for efficient multiplexing
- Configured for Raspberry Pi 4 GPIO layout
- Multi-chain support (2 parallel 2 chains)
- Pinout based on `regular` configuration

---

## 🧠 GPIO Pinout Configuration

| Function         | GPIO Pin |
|------------------|----------|
| **Control Pins** ||
| Output Enable    | GPIO 2   |
| Clock            | GPIO 3   |
| Latch (Strobe)   | GPIO 4   |
| Address A        | GPIO 7   |
| Address B        | GPIO 8   |
| Address C        | GPIO 9   |
| Address D        | GPIO 16  |
| Address E        | GPIO 13  |
| **Chain 0** ||
| P0 R1            | GPIO 17  |
| P0 G1            | GPIO 18  |
| P0 B1            | GPIO 22  |
| P0 R2            | GPIO 23  |
| P0 G2            | GPIO 24  |
| P0 B2            | GPIO 25  |
| **Chain 1** ||
| P1 R1            | GPIO 27  |
| P1 G1            | GPIO 10  |
| P1 B1            | GPIO 11  |
| P1 R2            | GPIO 5   |
| P1 G2            | GPIO 6   |
| P1 B2            | GPIO 12  |
| **Chain 2** ||
| P2 R1            | GPIO 14  |
| P2 G1            | GPIO 21  |
| P2 B1            | GPIO 20  |
| P2 R2            | GPIO 15  |
| P2 G2            | GPIO 14  |
| P2 B2            | GPIO 19  |

> **Note**: GPIO usage overlaps with SPI/I2C/UART peripherals. Disable them if you're not using those interfaces.

---

## 🛠️ Requirements

- Raspberry Pi 4 (or compatible with 40 GPIO pins)
- 80x40 P4 RGB LED Matrix
- Level shifter (recommended for 5V panels)
- 5V Power supply for LED matrix
- Optional: C/C++ driver libraries like [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)

---

## 🚀 Getting Started

### 1. Clone the driver library 
```bash
for C programming
git clone https://github.com/MagnetoDynamics/P4-Led-Display-Using-Serial-Communication-usb-tty.git
cd P4-Led-Display-Using-Serial-Communication-usb-tty.git


for python 
sudo apt install -y build-essential python3-dev python3-pillow
make build-python PYTHON=$(which python3)
sudo make install-python

sample python code [
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# Matrix configuration
options = RGBMatrixOptions()
options.rows = 40
options.cols = 80
options.chain_length = 1
options.parallel = 3
options.hardware_mapping = 'regular'  # Your pinout matches 'regular'
options.multiplexing = 20             # Custom multiplexing (if supported by driver)
options.pwm_bits = 11
options.brightness = 70
options.show_refresh_rate = True

# Create matrix instance
matrix = RGBMatrix(options=options)

# Create a blank image
image = Image.new("RGB", (80, 40))
draw = ImageDraw.Draw(image)

# Load a truetype font
try:
    font = ImageFont.truetype("your location for fonts", 10)
except IOError:
    font = ImageFont.load_default()

# Draw text or graphics
draw.rectangle((0, 0, 80, 40), fill=(0, 0, 0))  # Clear screen
draw.text((5, 10), "Hello, World!", fill=(255, 0, 0), font=font)

# Display image
matrix.SetImage(image.convert('RGB'))

# Keep it displayed
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")

]

```


