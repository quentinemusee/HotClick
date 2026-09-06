# HotClick
A simple Hotkey software to bind hotkeys to click on screen.

## Installing HotClick
HotClick requires no installation process: simply download the latest release from the [official GitHub release section](https://github.com/quentinemusee/HotClick/releases) and execute the HotClick.exe binary it contains.
Currently, only Windows binaries are among the releases, but if you want to use this software on a different platform that supports Python, you can follow these steps to run the Python source code directly:
1. Install Python. The process depends on the platform you're using, but the [Python official website](https://www.python.org/downloads/) downloads section is a decent place to start.
2. Clone the [official GitHub repository](https://github.com/quentinemusee/HotClick) using either your git command line or directly from the website.
3. **[OPTIONAL]** Create a virtual environment within the cloned repository and activate it using the following commands:
~~~
python -m venv venv
./venv/Scripts/activate
~~~
4. Download the library dependencies using the **requirements.txt** file within the cloned repo via the following command:
~~~
python -m pip install -r requirements.txt
~~~
5. **You're ready to go!** Finally, run the Python source code using:
~~~
python main.py
~~~

## Q&A
1. _Why does your software use both the keyboard and pynput.keyboard libraries? Doesn't this amount to importing two different libraries for the same purpose? If you're going to use pynput.mouse, why not get rid of the keyboard library?_
**The reason I didn't get rid of the keyboard library is simple: it's much easier to use and read than pynput.keyboard. I'm aware of the "duplicate dependency" this creates, but when I tried to migrate all the code that calls keyboard, the result was functional but inelegant and unreadable. I'll do a proper migration the day pynput.keyboard makes it possible to check at any time whether a given key is pressed, and to do so cross-platform.**
