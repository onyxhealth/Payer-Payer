# mTLS Bundle Importer

This is a Python app that will clone the Payer-Payer bundle and import the records to a dockerized HAPI server running locally.

The configuration can be changed in the settings.py file to point to an alternative location.

## Implementation

These instructions are based on installation in MacOS. They should be easily adapted to Windows or Linux.

1. Install a dockerized HAPI server. Follow the instructions in the /hapi-docker folder.
2. Install Python 3.8+
3. run the following commands in a terminal window:


    python -m venv v_venv 
    source ./v_venv/bin/activate
    python -m pip install -r requirements.txt

4. review the settings in settings.py
5. run the import process with --help to understand the command line parameters


    python -m main --help 

6. Run the import process


    python -m main

