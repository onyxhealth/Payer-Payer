# mTLS Bundle Importer

This is a Python app that will clone the Payer-Payer bundle and import the records to a dockerized HAPI server running locally.

The configuration can be changed in the settings.py file to point to an alternative location.

## Implementation

These instructions are based on installation in MacOS. They should be easily adapted to Windows or Linux.

1. Install a dockerized HAPI server. Follow the instructions in the /hapi-docker folder.
2. Install Python 3.8+
3. run the following commands in a terminal window:


    python -m venv v_env 
    source ./v_env/bin/activate
    python -m pip install -r requirements.txt

4. review the settings in settings.py
5. run the import process with --help to understand the command line parameters


    python -m main --help 

6. Run the import process


    python -m main

## Find an mTLS Public Certificate


    python -m get_cert

To get help:

    python -m get_cert --help

usage: get_cert.py [-h] [--payer_name PAYER_NAME] [--cert_file_target CERT_FILE_TARGET] [--search_parameters SEARCH_PARAMETERS]

optional arguments:
  -h, --help            show this help message and exit
  --payer_name PAYER_NAME
                        Payer Name to search for
  --cert_file_target CERT_FILE_TARGET
                        Public Cert File name to write to.
  --search_parameters SEARCH_PARAMETERS
                        Additional Search parameters instead of, or in addition to Payer Name.


An information file about the public certificate will be written to a file that uses the same name and extension as the cert_file_target parameter with the addition of ".txt"

e.g.  ./tmp/public_cert.pem will have an information file of
./tmp/public_cert.pem.txt


## Get mTLS Endpoint Address 

Returns mTLS Endpoint from FHIR Server


    python -m get_endpoint --payer_name Diamond

Get help:

    
    python -m get_endpoint --help


### Help information

```markdown

usage: get_endpoint.py [-h] [--payer_name PAYER_NAME] [--search_parameters SEARCH_PARAMETERS] [--info_file_target INFO_FILE_TARGET] [--verbose VERBOSE]

optional arguments:
  -h, --help            show this help message and exit
  --payer_name PAYER_NAME
                        Payer Name to search for
  --search_parameters SEARCH_PARAMETERS
                        Additional Search parameters instead of, or in addition to Payer Name.
  --info_file_target INFO_FILE_TARGET
                        Info File name to write to for endpoint info.
  --verbose VERBOSE     Provide Verbose output.


```