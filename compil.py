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
    |---------|-----------------|-----------------------------------------|
    |  0.3.0  |      2024-03-13 | Remove the input at the end of the      |
    |         |                 | compilation.                            |
    |         |                 | Add a trivial logs mechanism using      |
    |         |                 | the print function.                     |
    |         |                 | Don't clean the binary file anymore.    |
    |         |                 | Don't rename the binary with the        |
    |         |                 | version of the software anymore.        |
    |---------|-----------------|-----------------------------------------|
    |  0.4.0  |      2024-03-17 | Adapt the code to work with the main.py |
    |         |                 | file being within the src directory.    |
    |---------|-----------------|-----------------------------------------|
    |  0.5.0  |      2024-03-21 | Adapt the code to work with the igm     |
    |         |                 | directory being created.                |
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
__date__         = "2024-03-21"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__version__      = "0.5.0"

# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Retrieve the version of the software from the main.py.
with open("src/main.py", 'r') as file:
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
        "src/main.py",
    ])

    # Copy the resulting binary to the current (root) directory.
    print(f"Copy and rename to \"HotClickv{VERSION}.exe\" the resulting binary.")
    shutil.copy("./dist/main.exe", f"HotClick.exe")


def clean() -> None:
    """Clean the temporary files created while compiling."""

    # Try to delete the "main.spec" file.
    try:
        print("    -Removing main.spec")
        os.remove("main.spec")
    except Exception:
        pass 

    # Try to delete the "build" directory.
    try:
        print("    -Removing build")
        shutil.rmtree("build")
    except Exception:
        pass  

    # Try to delete the "dist" directory.
    try:
        print("    -Removing dist")
        shutil.rmtree("dist")
    except Exception:
        pass  

    # Try to delete the "__pycache__" directory.
    try:
        print("    -Removing __pycache__")
        shutil.rmtree("__pycache__")
    except Exception:
        pass  


def zip_binary() -> None:
    """Zip the resulting binary and application's icon."""

    # Create a ZipFile object.
    with zipfile.ZipFile(f"HotClickv{VERSION}.zip", 'w') as zip_object:
        # Add the binary file to the zip file.
        print(f"    -Zipping HotClick.exe")
        zip_object.write(f"HotClick.exe", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "img/icon.png" file to the zip file.
        print("    -Zipping img/icon.png")
        zip_object.write("img/icon.png", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "img/color_selection.png" file to the zip file.
        print("    -Zipping img/color_selection.png")
        zip_object.write("img/color_selection.png", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "README.md" file to the zip file.
        print("    -Zipping README.md")
        zip_object.write("README.md", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "LICENSE" file to the zip file.
        print("    -Zipping LICENSE")
        zip_object.write("LICENSE", compress_type=zipfile.ZIP_DEFLATED)

# =---------------------------------------------------------------------------= #


# =-----------= #
# Main function #
# =-----------= #

def main() -> None:
    """Main function."""

    # Compile the code.
    print("Compiling...")
    compile_code()

    # Create a zip archive containing the binary
    # file and the application's icon.
    print("Zipping...")
    zip_binary()

    # Clean the compilation files.
    print("Cleaning...")
    clean()

    # Exit with a status code 0.
    sys.exit(0)

# =------------------------------------------= #


#   Run the main function is
# this script is run directly.
if __name__ == "__main__":
    main()
