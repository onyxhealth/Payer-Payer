# Dockerized HAPI:
FHIR_BASE_URI = "http://localhost:8080/fhir"
# National Directory RI
# FHIR_BASE_URI = "https://national-directory.fast.hl7.org/fhir"
CLIENT_ID = "ADD_CLIENT_ID"
CLIENT_SECRET = "ADD_CLIENT_SECRET"
TENANT = "ADD_TENANT_ID"
TOKEN_REQUIRED = False
DEFAULT_LIST_ID = "mtls-payer-list"
DEFAULT_REPO = "https://github.com/onyxhealth/Payer-Payer"
BUNDLE_FOLDER = "/bundles"

# -----------------------
# get_cert.py
# -----------------------

DEFAULT_CERT_FILE = "./tmp/public_cert.pem"
DEFAULT_CERT_INFO = DEFAULT_CERT_FILE + ".txt"
DEFAULT_INFO_FILE = "./tmp/payer_endpoint.txt"
