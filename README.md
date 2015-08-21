# pitools

Something running on my RaspberryPi.

Started as a server which allow non-root program retrive sensor data.

# Features

* `curl -L 127.0.0.1:9876/sensor/env` read Adafruit sensor data
* set a cron job for `curl 127.0.0.1:9876/photo/daily` to record your daily activities into a 10FPS video
* send `GET` request to `127.0.0.1:9876/photo/shot` to take a photo, the file path will be returned in plain text

# License

See LICENSE file.
