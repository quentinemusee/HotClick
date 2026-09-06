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
    |  0.5.0  |      2024-03-21 | Adapt the code to work with the img     |
    |         |                 | directory being created.                |
    |---------|-----------------|-----------------------------------------|
    |  0.5.0  |      2024-03-21 | Remove the color_selection image and    |
    |         |                 | add the theme.json file                 |
    |---------|-----------------|-----------------------------------------|
    |  1.0.0  |      2026-09-07 | Make the compilation cross-platform     |
    |         |                 | (Windows / macOS Intel / macOS Apple    |
    |         |                 | Silicon / Linux), and rename the        |
    |         |                 | resulting binary and archive to         |
    |         |                 | "HotClick-{version}-{os}-{arch}".       |
    |         |                 | Embed img/icon.png as the application's |
    |         |                 | icon (icon.ico on Windows, icon.icns    |
    |         |                 | on macOS), generated on the fly with    |
    |         |                 | Pillow.                                 |
    |         |                 | Switch macOS builds from --onefile to   |
    |         |                 | onedir (a real .app bundle), since      |
    |         |                 | --onefile + windowed .app bundles are   |
    |         |                 | deprecated by PyInstaller (a .app       |
    |         |                 | can't be a single file) and needed for  |
    |         |                 | the icon to actually show in Finder.    |
    |         |                 | Preserve unix executable permissions    |
    |         |                 | when zipping, so the binary/.app is     |
    |         |                 | still runnable once unzipped.           |
     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""


# =--------------= #
# Libraries import #
# =--------------= #

from   PIL                  import Image
import os
import sys
import shutil
import zipfile
import platform
import PyInstaller.__main__

# =----------------------------------= #


# =--------= #
# Authorship #
# =--------= #

__author__       = "Quentin Raimbaud"
__contact__      = "quentin.raimbaud.contact@gmail.com"
__date__         = "2026-09-07"
__maintainer__   = "Quentin Raimbaud"
__status__       = "Development"
__version__      = "1.0.0"

# =-------------------------------------------------= #


# =-------------= #
# Global variable #
# =-------------= #

# Retrieve the version of the software from the main.py.
VERSION: str
with open("src/main.py", 'r') as file:
    VERSION = f"""v{file.read().split("__version__")[1].split('"')[1]}"""


def _get_os_name() -> str:
    """
    Return a normalized, human-friendly OS name.

    :returns: The normalized, human-friendly OS name.
    :rtype: str
    """

    system: str = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    # Fallback: use whatever platform.system() returned, lower-cased.
    return system.lower()


def _get_arch_name() -> str:
    """
    Return a normalized, human-friendly CPU architecture name.

    :returns: The normalized, human-friendly CPU architecture name.
    :rtype: str
    """

    machine: str = platform.machine().lower()
    if machine in ("amd64", "x86_64", "x64", "em64t", "intel64"):
        return "x64"
    elif machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("i386", "i686", "x86"):
        return "x86"
    # Fallback: use whatever platform.machine() returned.
    return machine


# Platform identification, computed once and reused everywhere below.
OS_NAME: str   = _get_os_name()
ARCH_NAME: str = _get_arch_name()

# Binaries only carry a ".exe" extension on Windows.
BINARY_EXT: str = ".exe" if OS_NAME == "windows" else ""

# Name PyInstaller gives its output (derived from "src/main.py").
DIST_BINARY_NAME: str = f"main{BINARY_EXT}"

# Final, renamed binary and archive base name, shared by both artifacts:
# e.g. "HotClick-v0.5.0-macos-arm64", "HotClick-v0.5.0-windows-x64", ...
ARTIFACT_BASENAME: str = f"HotClick-{VERSION}-{OS_NAME}-{ARCH_NAME}"
BINARY_NAME: str       = f"{ARTIFACT_BASENAME}{BINARY_EXT}"
APP_NAME: str          = f"{ARTIFACT_BASENAME}.app"
ARCHIVE_NAME: str      = f"{ARTIFACT_BASENAME}.zip"

# Source icon, and its platform-specific, PyInstaller-ready counterpart.
# There is no standard, PyInstaller-embeddable icon format on Linux,
# so ICON_PATH stays None there and no --icon flag is passed.
ICON_SOURCE: str = os.path.join("img", "icon.png")
if OS_NAME == "windows":
    ICON_PATH = os.path.join("img", "icon.ico")
elif OS_NAME == "macos":
    ICON_PATH = os.path.join("img", "icon.icns")
else:
    ICON_PATH = None

# =-------------------------------------------------------------------= #


# =-------------------= #
# Compilation functions #
# =-------------------= #

def _prepare_icon() -> None:
    """
    Convert "img/icon.png" into the icon format expected by
    PyInstaller on the current platform: "img/icon.ico" on Windows,
    "img/icon.icns" on macOS. Does nothing on other platforms.
    """

    if ICON_PATH is None:
        return

    print(f"    - Generating \"{ICON_PATH}\" from \"{ICON_SOURCE}\".")
    image = Image.open(ICON_SOURCE)

    if OS_NAME == "windows":
        # Multi-resolution .ico, embedded directly into the .exe by PyInstaller.
        image.save(ICON_PATH, sizes=[
            (16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256),
        ])
    elif OS_NAME == "macos":
        # Pillow can write .icns from any OS (no need for iconutil/sips).
        image.save(ICON_PATH, format="ICNS")


def _locate_compiled_output() -> str:
    """
    Locate whatever PyInstaller produced: a single binary file on
    Windows/Linux (--onefile), or a .app bundle directory on macOS
    (onedir + --windowed: --onefile and windowed .app bundles are
    incompatible and now deprecated by PyInstaller).

    :returns: The path to the produced binary file or .app bundle.
    :rtype: str
    """

    if OS_NAME == "macos":
        app_path = os.path.join("dist", "main.app")
        if os.path.isdir(app_path):
            return app_path
        raise FileNotFoundError(
            f"Could not locate the PyInstaller .app bundle at \"{app_path}\"."
        )

    binary_path = os.path.join("dist", DIST_BINARY_NAME)
    if os.path.isfile(binary_path):
        return binary_path
    raise FileNotFoundError(
        f"Could not locate the PyInstaller output binary at \"{binary_path}\"."
    )


def compile_code() -> None:
    """Compile the main.py source code."""

    # Generate the platform-appropriate icon file from img/icon.png.
    _prepare_icon()

    # Build the PyInstaller argument list.
    # NOTE: --onefile combined with a windowed macOS .app bundle is
    # deprecated (a .app bundle can't be a single file), so macOS
    # builds use onedir (PyInstaller's default) instead.
    args = ["--windowed", "src/main.py"]
    if OS_NAME != "macos":
        args.insert(0, "--onefile")
    if ICON_PATH is not None:
        args.insert(0, f"--icon={ICON_PATH}")

    PyInstaller.__main__.run(args)

    # Copy the resulting binary/.app bundle to the current (root)
    # directory, renamed with the version, OS and architecture.
    compiled_output: str = _locate_compiled_output()

    if OS_NAME == "macos":
        print(f"    - Copy and rename to \"{APP_NAME}\" the resulting .app bundle.")
        if os.path.exists(APP_NAME):
            shutil.rmtree(APP_NAME)
        shutil.copytree(compiled_output, APP_NAME)
        # Make sure the bundle's inner unix executable stays runnable.
        os.chmod(os.path.join(APP_NAME, "Contents", "MacOS", "main"), 0o755)
    else:
        print(f"    - Copy and rename to \"{BINARY_NAME}\" the resulting binary.")
        shutil.copy(compiled_output, BINARY_NAME)
        # On non-Windows platforms, PyInstaller doesn't set the executable
        # bit by default in every environment; make sure it's runnable.
        if OS_NAME != "windows":
            os.chmod(BINARY_NAME, 0o755)


def _zip_write(zip_object: zipfile.ZipFile, filepath: str) -> None:
    """
    Add a file to the zip archive while preserving its unix
    permission bits. Needed because Python's zipfile module drops
    them by default, which would silently strip the executable bit
    off the binary/.app once the archive is unzipped elsewhere.

    :param zip_object: The opened ZipFile to write into.
    :type zip_object: zipfile.ZipFile
    :param filepath: The path of the file to add.
    :type filepath: str
    """

    zip_info = zipfile.ZipInfo.from_file(filepath, filepath)
    zip_info.compress_type = zipfile.ZIP_DEFLATED
    zip_info.external_attr = (os.stat(filepath).st_mode & 0xFFFF) << 16
    with open(filepath, "rb") as source, zip_object.open(zip_info, 'w') as dest:
        shutil.copyfileobj(source, dest)


def zip_binary() -> None:
    """Zip the resulting binary (or macOS .app bundle) and application's icon."""

    # Create a ZipFile object.
    with zipfile.ZipFile(ARCHIVE_NAME, 'w') as zip_object:
        if OS_NAME == "macos":
            # Add every file of the .app bundle, preserving its
            # directory structure and executable permissions.
            print(f"    - Zipping {APP_NAME}/")
            for root, _, files in os.walk(APP_NAME):
                for filename in files:
                    _zip_write(zip_object, os.path.join(root, filename))
        else:
            # Add the binary file to the zip file.
            print(f"    - Zipping {BINARY_NAME}")
            _zip_write(zip_object, BINARY_NAME)

        # Add the "img/icon.png" file to the zip file.
        print("    - Zipping img/icon.png")
        zip_object.write(ICON_SOURCE, compress_type=zipfile.ZIP_DEFLATED)

        # Add the "theme.json" file to the zip file.
        print("    - Zipping theme.json")
        zip_object.write("theme.json", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "README.md" file to the zip file.
        print("    - Zipping README.md")
        zip_object.write("README.md", compress_type=zipfile.ZIP_DEFLATED)

        # Add the "LICENSE" file to the zip file.
        print("    - Zipping LICENSE")
        zip_object.write("LICENSE", compress_type=zipfile.ZIP_DEFLATED)


def clean() -> None:
    """Clean the temporary files created while compiling."""

    # Try to delete the "main.spec" file.
    # noinspection PyBroadException
    try:
        print("    - Removing main.spec")
        os.remove("main.spec")
    except Exception:
        pass

    # Try to delete the "build" directory.
    # noinspection PyBroadException
    try:
        print("    - Removing build")
        shutil.rmtree("build")
    except Exception:
        pass

    # Try to delete the "dist" directory.
    # noinspection PyBroadException
    try:
        print("    - Removing dist")
        shutil.rmtree("dist")
    except Exception:
        pass

    # Try to delete the "__pycache__" directory.
    # noinspection PyBroadException
    try:
        print("    - Removing __pycache__")
        shutil.rmtree("__pycache__")
    except Exception:
        pass

    # Try to delete the generated platform-specific icon file.
    # noinspection PyBroadException
    try:
        if ICON_PATH is not None:
            print(f"    - Removing {ICON_PATH}")
            os.remove(ICON_PATH)
    except Exception:
        pass

# =--------------------------------------------------------------------------= #


# =-----------= #
# Main function #
# =-----------= #

def main() -> None:
    """Main function."""

    print(f"/> Detected platform: {OS_NAME}-{ARCH_NAME}")

    # Compile the code.
    print("/> Compiling...")
    compile_code()

    # Create a zip archive containing the binary
    # file and the application's icon.
    print("/> Zipping...")
    zip_binary()

    # Clean the compilation files.
    print("/> Cleaning...")
    clean()

    # Exit with a status code 0.
    sys.exit(0)

# =---------------------------------------------------= #


#   Run the main function is
# this script is run directly.
if __name__ == "__main__":
    main()
