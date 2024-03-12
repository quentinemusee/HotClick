import main
import PyInstaller.__main__
import os
import shutil
import sys
import subprocess

def compile_code(): 
    PyInstaller.__main__.run([
        "--noconsole",
        "--onefile",
        "-w",
        "main.py",
    ])

    shutil.copy("./dist/main.exe", "main.exe")

def clean():
    try:
        os.remove("main.spec")
    except Exception: pass 

    try:
        shutil.rmtree("build")
    except Exception: pass  

    try:
        shutil.rmtree("dist")
    except Exception: pass  

    try:
        shutil.rmtree("__pycache__")
    except Exception: pass  

def main() -> None:
    """Main function."""

    # Compile the code.
    compile_code()

    # Clean the compilation files.
    clean()

if __name__ == "__main__":
    main()
