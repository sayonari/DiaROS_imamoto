# DiaROS
**[日本語バージョンはこちら](README_jp.md)**

## Author
Ryota Nishimura (Tokushima University)  
nishimura@is.tokushima-u.ac.jp

## Developer
- Ryota Nishimura
- Takahiro Mori https://bitbucket.org/takahiro_mori_win/

## Overview
This is a ROS2-compatible version of a real-time spoken dialogue system. The system itself is simple and its contents are simple, but you can understand how to make a spoken dialogue system ROS-compatible. Basically, the system consists of ROS wrapped communication between modules of a python implementation of a spoken dialogue system. This configuration makes it possible to monitor the communication contents in ROS, and to check, record, and replay the communication contents, thus dramatically increasing the efficiency of system development and debugging.

## Cautions
- This configuration still contains bugs. It is still in the bug-fixing stage.
- Dashboard (nodejs, vue implementation) does not work.
        - The spoken dialog system works without it.


# How to install the system
The system installation procedure is described below.

## 0. System environment (during development)
- OS: Ubuntu 20.04.3


## 1. install ROS2 Foxy
https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Binary.html

- Execute in order
- It should finish without any problems and the test should work.


### (extra) I want to test with Turtlesim too!
https://docs.ros.org/en/foxy/Tutorials.html

```shell
$ sudo apt update
$ sudo apt install ros-foxy-turtlesim
````shell

````shell
[shell 1]
$ ros2 run turtlesim turtlesim_node

[shell 2] $ ros2 run turtlesim turtlesim_node
$ ros2 run turtlesim turtle_teleop_key
````


## 2. Python environment installation
### 2.1 pyenv installation
Pyenv installation notes for a fresh Ubuntu 20.04 environment
https://qiita.com/sho1_24/items/96c3c9e71629de3801fb

- Installing libraries
``shell
$ sudo apt install git gcc make zlib1g-dev libffi-dev libbz2-dev libssl-dev libreadline-dev libsqlite3-dev python3-tk tk-dev
````

- Installing pyenv
```
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
$ git clone https://github.com/pyenv/pyenv-update.git ~/.pyenv/plugins/pyenv-update
```

- Set environment variables
The ``PYTHONPATH`` setting is the default module installation location for python, and the ``-user`` setting is the default installation location for python. --user and the module installation location with --user should be appended.  
Pay attention to the python version, etc.
```bash
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
If [ -f ~/.bashrc ]; then .

# for pyenv(python)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
PPTMP=`python -c "import site; print (site.getsitepackages()[0])"`
export PYTHONPATH="$PPTMP:$PYTHONPATH"
PPTMP=`python -m site --user-site`
export PYTHONPATH="$PPTMP:$PYTHONPATH"
```


Create symbolic link to standard OS python command
```shell
$ sudo apt install python-is-python3
```

### 2.2 Python installation
```
Check for installable version
$ pyenv install -l | less

Install Python
$ pyenv install 3.8.13

Set version
$ pyenv global 3.8.13
```


## 3. installation of spoken dialogue system

### 3.1 Key acquisition and deployment of A3RT and Google API 
- Get API key for A3RT
- Copy and paste the API key into a text file and save it (text file containing only the API key)
- Place the text file in the following location (replace the HOME directory with your own)
```
/home/nishimura/secret/nishimura_A3RT_APIKEY.data
```

- Create a Google API key and put it in the following directory.
````
/home/nishimura/secret/nishimura_SDS.json
```

- Add the paths to the A3RT API key and Google API key to the environment variables.  
Add the following to `~/.bashrc`.
```shell
export GOOGLE_APPLICATION_CREDENTIALS="/home/nishimura/secret/nishimura_SDS.json"
export A3RT_APIKEY="/home/nishimura/secret/nishimura_A3RT_APIKEY.data"
```


### 3.2 Voice Dialogue System Module Installation
Execute the following in ``DiaROS/DiaROS_py``.

```bash
$ python -m pip install . --user
````


### 3.3 Installation of python modules for spoken dialogue system

**■Installing google cloud speech api**
```shell:
$ python -m pip install google gcloud google-auth google-api-core google-cloud-speech grpc-google-cloud-speech-v1beta1 grpcio grpcio-tools
````

```shell:
$ python -m pip install -U numpy scipy requests pyworld matplotlib==2.*
```

**■Installing pyaudio**

````shell:
$ sudo apt-get install portaudio19-dev
$ pip install pyaudio
```


**■Installing aubio**.

You can't just pip it in.
Download and install the latest version from github.

(Download via pip command!).

````shell:
$ python -m pip install git+https://github.com/aubio/aubio/
````

**■Other installations**.
```shell:
$ python -m pip install gtts playsound
```

### 3.4 Building the ROS package (MSG)
First, install colcon.
```bash
$ sudo apt install python3-colcon-common-extensions
```

In ``/home/nishimura/program/DiaROS/DiaROS_ros``, run

```bash
# Move directories and configure environment
$ cd /home/nishimura/program/DiaROS/DiaROS_ros
$ . /home/nishimura/ros2_foxy/ros2-linux/local_setup.bash

# Build msg folder (interfaces)
$ colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
$ . . /install/local_setup.bash

# Build ros2 module (diaros_package)
$ colcon build --packages-select diaros_package
$ . . /install/local_setup.bash
``` 





## 4. dashboard installation
Note: The following is still buggy and cannot be realized, because the versions of the nodejs and vue modules do not match and the development environment cannot be reproduced. Please let me know if anyone has been able to get it to work.

### 4.1 npm install
````
$ sudo apt update
$ sudo apt install curl
$ curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
$ sudo apt-get install -y nodejs
# $ sudo apt-get install gcc g++ make
````

confirm ````
```
$ node -v
$ npm -v
```

Upgrade npm version.
```
$ sudo npm install -g npm
```

### 4.2 Dashboard Installation
Dashboard: server and client installation
```bash
$ cd /home/nishimura/program/DiaROS/dialogue-dashboard

# Install modules
$ cd 
$ sudo npm install -g typescript
$ sudo npm install -g require
$ sudo npm i @types/node
$ sudo npm audit fix --force


# Install server
$ cd server
$ sudo npm ci
$ sudo npm run build

# Install client
$ cd ...
$ sudo npm ci
$ sudo npm run build
Run the following as instructed

Run the following as instructed
```shell:
$ sudo npm audit fix --force
````

If ERESOLVE could not resolve
https://github.com/vuejs/vue-cli/issues/6270
```
$ npm i --legacy-peer-deps
```

If you get Error: Rule can only have one resource source
https://stackoverflow.com/questions/64373393/error-rule-can-only-have-one-resource-source-provided-resource-and-test-incl
```
$ sudo npm uninstall webpack
$ sudo npm install webpack@^4.45.0
```

Cannot find module 'webpack/lib/RuleSet'.
https://github.com/vuejs/vue-loader/issues/1586
```
$ sudo npm i vue-loader

$ sudo npm install --save-dev webpack webpack-cli html-webpack-plugin webpack-dev-server webpack-dev-middleware
````



## 5. run steps

### 5.1 Start the spoken dialogue system
```bash
$ cd /home/nishimura/program/DiaROS/DiaROS_ros
$ . /home/nishimura/ros2_foxy/ros2-linux/local_setup.bash
$ . /home/nishimura/program/DiaROS/DiaROS_ros/install/local_setup.bash
# Run spoken dialog system
$ ros2 launch diaros_package sdsmod.launch.py
``` 


### 5.2 (not yet working) dashboard launch
```bash
$ cd C:\sayonari\DiaROS\dialogue-dashboard
$ npm run start # start server
$ npm run serve # start client
````

### 5.3 (not working yet) run ros module for dashboard and admin tools
```bash
$ cd C:\sayonari\DiaROS\spoken-dialogue-system
$ call C:\dev\ros2_foxy\local_setup.bat
$ call install\local_setup.bat
ros2 run diaros_package dr # Dashboard integration
ros2 run diaros_package mm # for admin tools
```










## The following are workarounds for runtime errors.
### 9.1 If your sound device (USB headset) is not recognized!
https://kazuhira-r.hatenablog.com/entry/2020/02/28/000625

```
## Check the version
$ sudo apt search ^linux-headers-

# 5.13.0-41 looked new, put it in!
$ sudo apt install linux-image-5.13.0-41-generic linux-headers-5.13.0-41-generic linux-modules-extra-5.13.0-41-generic
```


### 9.2 voice.py without voice synthesis for windows!
When I try to load gtts with python, it says ``■No module named gi``.
```
$ python
>>> import gtts
(error) No module named gi
```` $ python >>> import gtts (error)

In that case, execute the following.  
https://stackoverflow.com/questions/71369726/no-module-named-gi
```
$ sudo apt install libcairo2-dev
$ sudo apt install libxt-dev
$ sudo apt install libgirepository1.0-dev
$ pip install pycairo
$ pip install PyGObject
```


### 9.3 Fix default sound device
https://wolfgang-ziegler.com/blog/prevent-changing-of-default-ubuntu-sound-device

- Check input device list.
```
$ pactl list short sources
```` $ pactl list short sources

- Set to default.
```
$ pactl set-default-source alsa_input.usb-Sennheiser_Communications_Sennheiser_USB_headset-00.mono-fallback
```

- Add the above settings to '~/.bashrc'.


### 9.4 Unknown PCM cards appear every time
https://stackoverflow.com/questions/31603555/unknown-pcm-cards-pcm-rear-pyaudio
````
ALSA lib pcm_dsnoop.c:641:(snd_pcm_dsnoop_open) unable to open slave
ALSA lib pcm_dmix.c:1089:(snd_pcm_dmix_open) unable to open slave
ALSA lib pcm.c:2642:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
ALSA lib pcm.c:2642:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
ALSA lib pcm.c:2642:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
ALSA lib pcm_oss.c:377:(_snd_pcm_oss_open) Unknown field port
ALSA lib pcm_oss.c:377:(_snd_pcm_oss_open) Unknown field port
ALSA lib pcm_usb_stream.c:486:(_snd_pcm_usb_stream_open) Invalid type for card
ALSA lib pcm_usb_stream.c:486:(_snd_pcm_usb_stream_open) Invalid type for card
ALSA lib pcm_dmix.c:1089:(snd_pcm_dmix_open) unable to open slave
Unknown PCM cards are removed by

Unknown PCM cards are removed by commenting out relevant lines in '/usr/share/alsa/alsa.conf'.  
(Comment out settings for cards you don't use or don't know.)


