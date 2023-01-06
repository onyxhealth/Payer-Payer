#! /usr/bin/env python3
# get_ccert.py
# 2022-12-30
# @ekivemark
#
# Search for Payer Public mTLS Cert in HAPI
# Return Cert as a .pem file
import json
import argparse
from icecream import ic

from settings import DEFAULT_CERT_FILE, DEFAULT_CERT_INFO, FHIR_BASE_URI, TOKEN_REQUIRED
from fhir_calls import call_fhir
from bundle_handler import get_field

BEGIN_CERT = "-----BEGIN CERTIFICATE-----"
END_CERT = "-----END CERTIFICATE-----"
INDENT = 4

PUBLIC_CERT_EXTENSION = "http://hl7.org/fhir/us/ndh/StructureDefinition/base-ext-secureExchangeArtifacts"

CLI = argparse.ArgumentParser()

CLI.add_argument(
    "--payer_name",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    help="Payer Name to search for"
)
CLI.add_argument(
    "--cert_file_target",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    default=[DEFAULT_CERT_FILE,],
    help="Public Cert File name to write to. "
)
CLI.add_argument(
    "--search_parameters",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    default=[],
    help="Additional Search parameters instead of, or in addition to Payer Name."
)
CLI.add_argument(
    "--verbose",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    default=['False'],
    help="Provide Verbose output."
)


def find_payer(payername="", searchparams=""):
    data = {"resourceType": "Organization"}
    query = FHIR_BASE_URI + "/Endpoint?"
    if len(payername) > 0:
        query += "organization.name=" + payername + "&_total=accurate"
    if len(searchparams) > 0:
        if query[-1] not in ['?', '&']:
            query += "&"
        query += searchparams
    status, resp = call_fhir(data_file=data, calltype="GET",query=query, get_token=TOKEN_REQUIRED)
    total = 0
    if "total" in resp.keys():
        total = resp['total']
    if total == 1:
        unique = True
    else:
        unique = False
    response = {"query": query,
                "status": status,
                "results": total,
                "uniqueMatch": unique,
                "response": resp,
                }
    return response


def get_mtls_cert(resource, organization_info={}, verbose=False):
#  "extension": [
#    {
#     "url": "secureExchangeArtifactsType",
#     "valueString": "mtls Public Certificate"
#     },
#     {
#     "url": "certificate",
#     "valueBase64Binary": "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"
#     },
#     {
#     "url": "expirationDate",
#     "valueDateTime": "2023-08-10T15:00:00.000Z"
#     }
#   ]
    if 'extension' in resource.keys():
        cert_info = {}
        cert_info['identifier'] = get_field(resource, 'identifier')
        cert_info['address'] = get_field(resource, "address")
        cert_info['name'] = get_field(resource, "name")
        cert_info['organization'] = organization_info
        for e in resource['extension']:
            if e['url'] == PUBLIC_CERT_EXTENSION:
                for m in e['extension']:
                    if m['url'] == "secureExchangeArtifactsType":
                        cert_info['certificateType'] = m['valueString']
                    if m['url'] == "certificate":
                        cert_info['publicCertificate'] = m['valueBase64Binary']
        if verbose:
            ic(cert_info)
        return cert_info


def get_org_info(reference):
    if len(reference) > 0:
        data_file = {"resourceType": "Organization"}
        query = FHIR_BASE_URI + "/" + reference
        status, response = call_fhir(data_file=data_file, calltype="GET", query=query, get_token=TOKEN_REQUIRED)
        if status == 200:
            organization = {'id': response['id'],
                            'identifier': response['identifier'],
                            'name': response['name']}
            return organization


def base64_to_cert(bin_cert):
    start_offset = 0
    end_offset = 0
    line_len = 64
    if bin_cert.startswith(BEGIN_CERT):
        start_offset = len(BEGIN_CERT)
    if bin_cert.endswith(END_CERT):
        end_offset = len(END_CERT)
    out_cert = [BEGIN_CERT,]

    line_cert = [bin_cert[i:i+line_len] for i in range(start_offset, len(bin_cert)-(start_offset+end_offset), line_len)]

    out_cert.extend(line_cert)
    out_cert.append(END_CERT)
    # ic(out_cert)
    txt_cert = ""
    for s in out_cert:
        txt_cert += s + "\n"
    # ic(txt_cert)
    return txt_cert


def write_cert(cert, filename, verbose=False):
    with open(filename, "w") as cf:
        # decoded = base64.b64decode(cert)
        # cert_txt = subprocess.check_output(["openssl",
        #                                     "x509",
        #                                     "-text",
        #                                     "-noout",
        #                                     "-in",
        #                                     decoded])
        cert_txt = base64_to_cert(cert)
        if verbose:
            ic(cert_txt)
        cf.write(cert_txt)
    return cert_txt


def clean_string(input_str,remove=['|', '>', '<']):
    """
    :type input_str: str
    :type remove: list
    """
    # remove dangerous characters from input string
    if input_str is None:
        return
    cleaned = input_str
    for r in remove:
        cleaned = cleaned.replace(r, "")
        # ic(cleaned)
    return cleaned


if __name__ == "__main__":
    args = CLI.parse_args()
    verbose = False
    if args.verbose:
        if args.verbose[0].lower() == "false":
            verbose = False
        else:
            verbose = True
    if args.payer_name:
        payername = clean_string(args.payer_name[0])
    else:
        payername = ""
    if args.cert_file_target:
        certfile = clean_string(args.cert_file_target[0])
    else:
        certfile = DEFAULT_CERT_FILE
    certinfo = certfile + ".txt"
    if args.search_parameters:
        searchparam = clean_string(args.search_parameters[0], remove=[">", "<"])
    else:
        searchparam = ""
    # ic(payername, certfile, certinfo, searchparam)
    endpoint_resp = {}
    if len(payername + searchparam) > 0:
        endpoint_resp = find_payer(payername, searchparam)

    if endpoint_resp:
        if endpoint_resp['uniqueMatch']:
            print("Unique Match found")
            cert_info = {}
            if "entry" in endpoint_resp['response']:
                if verbose:
                    ic(endpoint_resp['response']['entry'][0]['resource'])
                if 'managingOrganization' in endpoint_resp['response']['entry'][0]['resource'].keys():
                    organization = get_org_info(endpoint_resp['response']['entry'][0]['resource']['managingOrganization']['reference'])
                    if verbose:
                        ic(organization)
                cert_info = get_mtls_cert(endpoint_resp['response']['entry'][0]['resource'], organization, verbose=verbose)
                if verbose:
                    ic(f"Do we have a publicCertificate: {cert_info}")
                if 'publicCertificate' in cert_info.keys():
                    # Convert the cert data
                    # Write it to the target file
                    # write the info file
                    cert_text = write_cert(cert_info['publicCertificate'], certfile, verbose=verbose)
                    if verbose:
                        ic(cert_text)
                    with open(certinfo, "w") as ci:
                        del cert_info['publicCertificate']
                        cert_info['certificateFile'] = certfile
                        ci.write(json.dumps(cert_info, indent=INDENT))
                        print(f"Certificate information written to {certinfo}")
                    if cert_text:
                        print(f"certificate file: {certfile}")
            ic(cert_info)
    else:
        print("Done.")