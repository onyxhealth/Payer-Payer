#! /usr/bin/env python3
# bundle_handler.py
# 2022-12-24
# @ekivemark
#
# break out bundles
# load to HAPI

import json
from settings import FHIR_BASE_URI, TOKEN_REQUIRED, DEFAULT_LIST_ID, BUNDLE_FOLDER
from fhir_calls import call_fhir, is_next
from icecream import ic
from template_list import TEMPLATE_LIST

# ic.disable()


def bundle_seq_load(dir_list=[], path="./"+BUNDLE_FOLDER):
    # for each bundle load organization, then get id and update endpoint
    # then load endpoint
    processed_bundle = {"Organization": [],
                        "Endpoint": []}
    for f in dir_list:
        if f.lower() == ".git":
            pass
        else:
            bundle = bundle_get_file(path + "/" + f)
            org = org_from_bundle(bundle)
            org_fhir_id = org['resource']['id']
            endpoint_ref = org['resource']['endpoint'][0]['reference']
            # look for endpoint.reference and save it
            ic(org['resource']['endpoint'])
            ic("We are working with these ids:", org_fhir_id, endpoint_ref)
            # temporarily remove endpoint reference
            ic("org before removing endpoint",org)
            del org['resource']['endpoint']
            ic("org after removing endpoint", org)
            if org:
                status, resp = add_to_fhir(org)
                ic("committed org to FHIR", status, resp)
                if status in [200, 201]:
                    ic("finding org_fhir_id", resp)
                    org_fhir_id = get_resource_fhir_id(resp, rt="Organization",)
                    processed_bundle["Organization"].append(org_fhir_id)
            # get the endpoint from bundle
            ic("after org update", org_fhir_id)
            endpoint = endpoint_from_bundle(bundle)
            # update with org_fhir_id
            if org_fhir_id:
                endpoint = update_org_id(endpoint, org_fhir_id)
            if endpoint:
                status, resp = add_to_fhir(endpoint)
                if status in [200, 201]:
                    ic("finding endpoint_fhir_id", resp)
                    endpoint_fhir_id = get_resource_fhir_id(resp, rt="Endpoint")
                    # Use Endpoint ID to update Organization with PUT
                    ic("We have the Endpoint FHIR Id", endpoint_fhir_id)
                    # Re-write Organization with Endpoint reference
                    if add_ep_to_org(org_fhir_id, endpoint_fhir_id):
                        print(f"Endpoint (Endpoint/{endpoint_fhir_id}) updated in Organization/{org_fhir_id}")
                    #   GET Organization
                    #   Add endpoint.reference
                    #   PUT Organization
                    processed_bundle["Endpoint"].append(endpoint_fhir_id)
    return processed_bundle


def add_to_fhir(entry={}):
    # Add to FHIR via POST
    # or update via PUT
    i = entry['resource']
    ic(i['id'])
    query = FHIR_BASE_URI + "/" + i["resourceType"] + "/?identifier=" + i['identifier'][0]['value'] + "&_total=accurate"
    status, response = resource_get(data={"resourceType": i["resourceType"]},
                                    calltype="GET",
                                    query=query)
    if status == 404:
        data_file = entry
        if "id" in data_file.keys():
            del data_file["id"]
        status, response = call_fhir(data_file=data_file, calltype="POST")
        ic("We got a 404 in bundle_process\n", status)

    elif "entry" in response.keys():
        # we have a record to potentially update
        ic("Get with search on identifier\n")
        if "resourceType" in response['entry'][0].keys():
            if response['entry'][0]['resource']['meta']['lastUpdated'] < i["meta"]['lastUpdated']:
                # Is the imported record newer than the existing record? if yes, upate with PUT
                data_file = i["entry"]['resource']
                data_file['id'] = response['resource']['entry'][0]['id']
                status, response = call_fhir(data_file=data_file, calltype="PUT")
                ic("result from PUT\n", status, response.keys())
    elif "entry" not in response.keys():
        # No entry so we should post a record
        ic(i["resourceType"])
        data_file = entry["resource"]
        # remove imported id
        if "id" in data_file.keys():
            del data_file["id"]
        ic("Before attempting POST\n", data_file)
        status, response = call_fhir(data_file=data_file, calltype="POST")
        ic("result of POST\n", status)

    return status, response


def bundle_get_file(f):
    ic(f)
    with open(f, "r") as json_file:
        return json.load(json_file)


def bundle_load(f):
    # Read in bundle
    # get each resource
    # get identifier
    # search for resourceType and identifier in HAPI
    # PUT or POST record
    # return resource/identifier
    ic("bundle:f", f)
    list_entry = []
    if check_field(f, "entry"):
        entries = f["entry"]
        for e in entries:
            # get the resourceType and identifier
            ic(e)
            i = {"item": e['resource']['resourceType'] + "/" + e['resource']['identifier'][0]['value'],
                 "resourceType": e['resource']['resourceType'],
                 "identifier":  e['resource']['identifier'][0]['value'],
                 "source": f}
            if check_field(e['resource'], field="active"):
                if e['resource']['active']:
                    i['deleted'] = False
                else:
                    i['deleted'] = True
            if check_field(e['resource'], field="meta"):
                if check_field(e['resource']['meta'], field="lastUpdated"):
                    i['date'] = e['resource']['meta']['lastUpdated']
            i['entry'] = e

            list_entry.append(i)
    return list_entry


def resource_get(data, calltype="GET", query=""):
    resource = data["resourceType"]
    status, response = call_fhir(data_file=data,
                                 calltype="GET",
                                 query=query,
                                 get_token=TOKEN_REQUIRED)
    # ic("resource_get", status, response['entry'][0]['fullUrl'])
    ic("resource_get", status, response)
    return status, response


def org_from_bundle(bundle):
    # Get the Organization record from the bundle.
    organization = resource_from_source(bundle, resourcetype="Organization")
    return organization


def endpoint_from_bundle(bundle):
    # Get the endpoint record from the bundle.
    endpoint = resource_from_source(bundle, resourcetype="Endpoint")
    return endpoint


def resource_from_source(bundle, resourcetype=""):
    if "entry" in bundle.keys():
        for e in bundle['entry']:
            ic(resourcetype, e['fullUrl'])
            if e['resource']['resourceType'] == resourcetype:
                return e
    return


def get_resource_fhir_id(resp, rt="Organization"):
    # find the FHIR id for ResourceType (rt) in response
    if "entry" in resp.keys():

        fhir_id = resp['entry'][0]['resource']['id']
    elif resp['resourceType'] == rt:
        fhir_id = resp['id']
    else:
        fhir_id = None
    return fhir_id


def update_org_id(endpoint, org_fhir_id):
    # replace imported org id with loaded org fhir id
    ic("pre-update", endpoint['fullUrl'])
    #if "managingOrganization" in endpoint['resource'].keys():
    endpoint['resource']['managingOrganization']['reference'] = "Organization/" + org_fhir_id

    return endpoint


def list_get():
    # search for list in HAPI
    resource = "List"
    data = {"resourceType": resource,
            "id": DEFAULT_LIST_ID}
    status, response = call_fhir(data_file=data,
                                 calltype="GET",
                                 query=FHIR_BASE_URI + "/" + resource + "/" + DEFAULT_LIST_ID,
                                 get_token=TOKEN_REQUIRED)
    ic(status, response)
    if status == "404":
        # No task found
        list_data = TEMPLATE_LIST
    else:
        list_data = response

    return list_data


def list_update(payer, entry):
    matched = False
    for e in entry:
        if payer["item"] == e["item"]:
            matched = True
            if payer['deleted'] == e['deleted']:
                return entry
            else:
                entry[e] = payer
                return entry
        else:
            pass
    entry.append(payer)
    return entry


def list_put(list_data):
    data = list_data
    status, response = call_fhir(data_file=data,
                                 calltype="PUT",
                                 query="",
                                 get_token=TOKEN_REQUIRED)
    ic(status, response)
    return status


def check_field(target, field=""):
    if field in target.keys():
        return True
    return False


def remove_dead_records(bundle_fhir_values={"Organization":[], "Endpoint":[]}):
    # check records in HAPI match bundle
    kill_result = {"Endpoint": [],
                   "Organization": []}
    for r in ["Endpoint", "Organization"]:
        resource = r
        data_file = {"resourceType": resource}
        query = FHIR_BASE_URI + "/" + resource + "/?_summary=true"
        # gather list of records to DELETE
        to_delete = search_records(data_file, query, bundle_fhir_values, match_field="id", mode="EXCLUDE")
        ic(resource, kill_result, to_delete)
        if to_delete:
            actioned = kill_records(resource, to_delete[resource])
            ic(actioned)
            kill_result[r].extend(actioned)
    return kill_result


def search_records(data, query, bundle_fhir_values, match_field="id", mode="EXCLUDE"):
    # check if Resource/id is in bundle_fhir_ids[resource]
    resource = data['resourceType']
    records_to_action = {resource: []}
    next_batch = True
    while next_batch:
        status, resp = call_fhir(data_file=data, calltype="GET", query=query,get_token=TOKEN_REQUIRED)
        if 'entry' in resp.keys():
            for p in resp['entry']:
                ic("Search Step1:", p["resource"]['resourceType'], p['resource']['id'], match_field, bundle_fhir_values)
                if resource in bundle_fhir_values.keys():
                    if match_field in p['resource'].keys():
                        ic("Search Step2", bundle_fhir_values, p['resource'][match_field])
                        if mode == "EXCLUDE":
                            if p['resource'][match_field] not in bundle_fhir_values[resource]:
                                records_to_action[resource].append(p['resource']['id'])
                        else:
                            if p['resource'][match_field] in bundle_fhir_values[resource]:
                                records_to_action[resource].append(p['resource']['id'])
            query = is_next(resp)
            if query:
                next_batch = True

            else:
                next_batch = False
    return records_to_action


def kill_records(resource, batch_to_kill=[]):
    kill_result = []
    for i in batch_to_kill:
        data_file={"resourceType": resource,
                   "id": i}
        status, resp = call_fhir(data_file=data_file,calltype="DELETE")
        ic(status,resp)
        kill_result.append(status)
    return kill_result


def add_ep_to_org(org_id, ep_id):
    # Get Org, Add Endpoint Ref. Put org
    data = {"resourceType": "Organization",
            "id": org_id}
    status, resp = call_fhir(data_file=data, calltype="GET", get_token=TOKEN_REQUIRED)
    ic("We got the Org record -  check for entry", status, resp)
    if "entry" in resp.keys():
        org = resp['entry'][0]['resource']
    else:
        org = resp
    org['endpoint'] = []
    org['endpoint'].append({'reference': "Endpoint/" + ep_id})
    status, resp = call_fhir(data_file=org, calltype="PUT", get_token=TOKEN_REQUIRED)
    ic("We PUT an updated Org record. Is there an endpoint reference?", status, resp)
    if status in [200, 201]:
        return True
    return