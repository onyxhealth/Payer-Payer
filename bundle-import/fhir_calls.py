#! /usr/bin/env python3
# fhir_tooling
# : fhir_calls.py
# icare_plan-net
__author__ = "@ekivemark"
# 2021-08-20 6:33 PM
# generic tools for interacting with FHIR APIs

import json
import logging
import os
import requests

from urllib.parse import urlencode
from settings import FHIR_BASE_URI, TENANT, CLIENT_ID, CLIENT_SECRET, TOKEN_REQUIRED
from AccessToken.AccessToken import AccessToken
TOKEN = AccessToken(CLIENT_ID, CLIENT_SECRET, FHIR_BASE_URI, TENANT)


def is_next(content):
    """
    """
    if 'link' in content:
        for l in content['link']:
            if l['relation'] == 'next':
                return l['url']
    return


def call_fhir(data_file, calltype="GET", query="", get_token=TOKEN_REQUIRED):
    """
    GET PUT or POST DELETE to FHIR
    """
    if get_token:
        access_token = TOKEN.get_token()
        headers ={"Accept": "application/json",
                  "Authorization": "Bearer %s" %access_token,
                  "Content-Type": "application/json"}
    else:
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json"}
    if "resourceType" in data_file.keys():
        resource = data_file["resourceType"]
    else:
        message = f"No resourceType in data_file"
        logging.info(message)
        return 500, message
    if "id" in data_file.keys():
        fhir_id = data_file['id']
    else:
        if calltype in ["PUT", "DELETE"]:
            if "id" not in data_file.keys():
                message = f"No id in data_file"
                return 500, message
        else:
            fhir_id = ""

    if calltype.upper() == "PUT":
        query = FHIR_BASE_URI + "/" + resource + "/" + fhir_id
        response = requests.put(query, data=json.dumps(data_file), headers=headers)
    elif calltype.upper() == "POST":
        query = FHIR_BASE_URI + "/" + resource
        response = requests.post(query, data=json.dumps(data_file), headers=headers)
    elif calltype.upper() == "DELETE":
        query = FHIR_BASE_URI + "/" + resource + "/" + fhir_id
        response = requests.delete(query, headers=headers)
    else:
        # calltype.upper() == "GET":
        if not query:
            query = FHIR_BASE_URI + "/" + resource + "/" + fhir_id
        # print(f"Query: {query}")
        response = requests.get(query, headers=headers)
    try:
        resp = response.json()
    except ValueError:
        resp = {}
    if response.status_code not in [200,201, 204]:
        logging.info(f"{response.status_code}:Problem with {calltype} call to FHIR PaaS")
        logging.info(response.content)
    logging.debug(resp)
    return response.status_code, resp
