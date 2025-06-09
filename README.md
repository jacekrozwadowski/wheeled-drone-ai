# 4x4 vehicle powered by raspberry pi 5 with camera and range sensor



### Assembled vehicle

<img src="./images/dron.jpg" width="400">

---

### Drone elements

Robot-Chassis-NP - four-wheeled robot chassis

<img src="./images/robot-chassis-series-smart-mobile-robot-chassis-kit-options-for-wheels-and-chassis.jpg" width="150">

Raspberry Pi 5 8GB RAM, 2,4GHz, WiFi DualBand, Bluetooth, PCIe 2.0, 2x CSI/DSI, 2x USB 3.0, 2x 4Kp60 microHDMI

<img src="./images/raspberry-pi-5-8gb-ram-24ghz-wifi-dualband-bluetooth-pcie-20-2x-csidsi-2x-usb-30-2x-4kp60-microhdmi.jpg" width="150">

UPS HAT (EU) - uninterruptible power supply module UPS for Raspberry Pi

<img src="./images/ups-hat-eu-modul-zasilacza-bezprzerwowego-ups-dla-raspberry-pi.jpg" width="150">

Raspberry Pi Camera Module 3 Wide

<img src="./images/raspberry-pi-camera-module-3-wide.jpg" width="150">

Raspberry Pi Active Cooler - active cooling kit

<img src="./images/raspberry-pi-active-cooler-aktywny-zestaw-chlodzacy.jpg" width="150">

Cytron Maker Drive MX1508 - dual channel dc motor controller

<img src="./images/cytron-maker-drive-dwukanalowy-sterownik-silnikow-dc.jpg" width="150">

Basket for 4 AA R6 batteries with cover and switch

<img src="./images/koszyk-na-4-baterie-aa-r6-z-klapka-i-wlacznikiem.jpg" width="150">

Distance sensor module TOF10120

<img src="./images/modul-czujnika-odleglosci-tof10120.jpg" width="150">

---

### Wiring and pin layout

wiring

<img src="./images/wiring.png" width="400">

pin layout

<img src="./images/pin_layout.png" width="300">

---

### Create python environment
```bash
# create env
python3 -m venv --system-site-packages env

# activate it
source env/bin/activate

# install packages
pip install -r requirements.txt 
```

### Manual driving 
```bash
source env/bin/activate
python -m app.manual
```

### Object detection - original model
```bash
# on development env
python -m app.detection

# on car env
python -m app.detection --runtimeOnly
```

<img src="./images/detection.png" width="500">