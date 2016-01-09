## pitools

A set of flask blueprints to be used on RaspberryPi, which allow you to retrieve sensor data or send data to hardware devices via simple HTTP request.

## Installation

Notice: Adafruit_Python_BMP package has not yet been released to PyPI, so you need to manually get its source code [here][Adafruit_Python_BMP].

```bash
# Install Adafruit_Python_BMP package
# Enter source code folder for Adafrui_Python_BMP
cd Adafruit_BMP
sudo python setup.py install
cd ..

# Install pitools
cd pitools
sudo python setup.py install

# All other dependencies will be automatically installed
```

## Usage

Currently the available modules are:

* `pitools.camera`
* `pitools.sensors.bmp085`

There is a minimal working flask server in `examples/server.py`.
Install the camera and BMP085 sensor hardware and run `sudo python server.py` to start it,
and visit `http://<your_raspberry_pi_IP>:9876/camera/shot` for a photo captured,
or visit `http://<your_raspberry_pi_IP>:9876/sensors/bmp085/all` for data from your BMP085 sensor.

## Test

Install [nosetests][nosetests] and run `sudo nosetests -v` to see the test result.

## License

See LICENSE file.

  [Adafruit_Python_BMP]: https://github.com/adafruit/Adafruit_Python_BMP
  [nosetests]: https://nose.readthedocs.org/
