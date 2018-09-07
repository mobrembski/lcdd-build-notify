# lcdd-build-notify

lcdd-build-notify is a very simple python3 script used to indicate that building is in progress.

It uses forking mechanism, so first time you run this script->shows message on LCD->second time->removes message.

## Installation

  - Install pylcdd library:
    ```sh
    $ pip3 install pylcddc
    ```
  - Configure connection to you LCDd server inside script:
    ```python
    SERVER_ADDRESS = str('localhost')
    SERVER_PORT = int('13666')
    ```
    In most cases, localhost with 13666 will be enough.
  - Copy your script somewhere inside your PATH. I recommend /usr/local/bin:
    ```sh
    $ cp lcdd_build_notify.py /usr/local/bin
    ```
    
## Configuration

Depends on IDE you use. You must invoke lcdd-build-notify.py before your build starts and after it finishes.
In Qt Creator, you can add custom build steps in Projects->Building->Build steps.
