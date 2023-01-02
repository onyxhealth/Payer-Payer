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


def get_mtls_cert(resource, organization_info={}):
    if 'extension' in resource.keys():
        cert_info = {}
        cert_info['identifier'] = get_field(resource, 'identifier')
        cert_info['address'] = get_field(resource, "address")
        cert_info['name'] = get_field(resource, "name")
        cert_info['organization'] = organization_info
        for e in resource['extension']:
            if e['url'] == "http://hl7.org/fhir/us/directory-query/StructureDefinition/secureExchangeArtifacts":
                for m in e['extension']:
                    if m['url'] == "secureExchangeArtifactsType":
                        cert_info['certificateType'] = m['valueString']
                    if m['url'] == "certificate":
                        cert_info['publicCertificate'] = m['valueBase64Binary']
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


def write_cert(cert, filename):
    with open(filename, "w") as cf:
        # decoded = base64.b64decode(cert)
        # cert_txt = subprocess.check_output(["openssl",
        #                                     "x509",
        #                                     "-text",
        #                                     "-noout",
        #                                     "-in",
        #                                     decoded])
        cert_txt = base64_to_cert(cert)
        # ic(cert_txt)
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
                # ic(endpoint_resp['response']['entry'][0]['resource'])
                if 'managingOrganization' in endpoint_resp['response']['entry'][0]['resource'].keys():
                    organization = get_org_info(endpoint_resp['response']['entry'][0]['resource']['managingOrganization']['reference'])
                cert_info = get_mtls_cert(endpoint_resp['response']['entry'][0]['resource'], organization)
                if 'publicCertificate' in cert_info.keys():
                    # Convert the cert data
                    # Write it to the target file
                    # write the info file
                    cert_text = write_cert(cert_info['publicCertificate'], certfile)
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