#! /usr/bin/python3
# template_list.py
# 2022-12-26
#
# FHIR R4 List Resource

from settings import DEFAULT_LIST_ID

TEMPLATE_LIST = {
    "resourceType": "List",
      "id": DEFAULT_LIST_ID,
      "text": {
        "status": "generated",
        "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"ID: " + DEFAULT_LIST_ID + "List of Payer mTLS Connections</div>"
      },
      "status": "current",
      "mode": "snapshot",
      "title": "mTLS Payer List"
}