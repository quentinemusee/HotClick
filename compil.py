#!/usr/bin/env python
# -*- coding: utf-8 *-*


"""
    This program allow to compile
    and zip the HotClick's main file.

     _____________________________________________________________________
    | VERSION | DATE YYYY-MM-DD |                 CONTENT                 |
    |=====================================================================|
    |  0.1.0  |      2024-03-12 | Initial release.                        |
    |---------|-----------------|-----------------------------------------|
    |  0.2.0  |      2024-03-13 | Make the code cleaner, clean also the   |
    |         |                 | binary and add a zip mechanism.         |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

import os
import sys
import shutil
import zipfile
import PyInstaller.__main__

# =---------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2024-03-13"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__version__      = "0.2.0"

# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Retrieve the version of the software from the main.py.
with open("main.py", 'r') as file:
    VERSION: str = file.read().split("__version__")[1].split('"')[1]

# =--------------------------------------------------------------= #


# =-------------------= #
# Compilation functions #
# =-------------------= #

def compile_code() -> None:
    """Compile the main.py source code."""

    # Compile main.py. 
    PyInstaller.__main__.run([
        "--noconsole",
        "--onefile",
        "-w",
        "main.py",
    ])

    # Copy the resulting binary to the current (root) directory.
    shutil.copy("./dist/main.exe", f"HotClickv{VERSION}.exe")


def clean() -> None:
    """Clean the temporary files created while compiling."""

    # Try to delete the binary file.
    try:
        os.remove(f"HotClickv{VERSION}.exe")
    except Exception:
        pass 

    # Try to delete the "main.spec" file.
    try:
        os.remove("main.spec")
    except Exception:
        pass 

    # Try to delete the "build" directory.
    try:
        shutil.rmtree("build")
    except Exception:
        pass  

    # Try to delete the "dist" directory.
    try:
        shutil.rmtree("dist")
    except Exception:
        pass  

    # Try to delete the "__pycache__" directory.
    try:
        shutil.rmtree("__pycache__")
    except Exception:
        pass  


def zip_binary() -> None:
    """Zip the resulting binary and application's icon."""

    # Create a ZipFile object.
    with zipfile.ZipFile(f"HotClickv{VERSION}.zip", 'w') as zip_object:
        # Add the binary file to the zip file.
        zip_object.write(f"HotClickv{VERSION}.exe", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "icon.png" file to the zip file.
        zip_object.write("icon.png", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "README.md" file to the zip file.
        zip_object.write("README.md", compress_type=zipfile.ZIP_DEFLATED)

# =--------------------------------------------------------------= #


# =-----------= #
# Main function #
# =-----------= #

def main() -> None:
    """Main function."""

    # Compile the code.
    compile_code()

    # Create a zip archive containing the binary
    # file and the application's icon.
    zip_binary()

    # Clean the compilation files.
    clean()

    # Wait for the user to press enter then exit.
    input("Press enter to exit.")

    # Exit with a status code 0.
    sys.exit(0)

# =-------------------------------------------= #


#   Run the main function is
# this script is run directly.
if __name__ == "__main__":
    main()
