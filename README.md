# About Door Lock
The python scripts in this repository are for the hardware part. The hardware means **Raspberry Pi 3 Model B** (some other H/W components) running on Debian based Linux distro Raspbian.

For the app to control this door lock visit this [repository](https://github.com/suvambasak/HomeLock.git).

For the backend/server-side of the lock visit this [repository](https://github.com/suvambasak/lock-server.git).

<br><br>

## Components
1. Pi Camera
2. HC-SRO4 Ultrasonic Sensor (Trig = 6,
Echo = 13)
3. 28BYJ-48 Stepper Motor and ULN2003 Driver (pin: 4, 17, 27, 22)
4. Push button (pin 26)
5. LED (pin 19)

<br><br>
<p align='center' width='100%'>
    <img width='600' hight='400' src='https://github.com/suvambasak/door-lock/blob/master/img/pi.jpg?raw=true'>
</p>
<br><br>


## Setup

<br>

### Installation and Dependencies
- Install python packages `python3-crypto`, `python3-rpi.gpio `, `python3-picamera` and `git`

```bash
$ sudo apt install python3-crypto python3-rpi.gpio python3-picamera git
```
- Clone the repository and chnage the directory
```bash
$ git clone https://github.com/suvambasak/door-lock.git
$ cd door-lock
```

- Check all components is working with `CircuitTest.py`
```bash
$ python3 CircuitTest.py
```
<br>

### Start
- Before you start this you need to start server [side](https://github.com/suvambasak/lock-server.git) first.
- Execute `Device.py`
```bash
$ python3 Device.py
```