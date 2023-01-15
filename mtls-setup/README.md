# mTLS Server and Client Setup

## Overview

This document documents the steps necessary to enable mTLS connectivity between Payers that are members of a Payer-to-Payer Trust Framework.
The steps that have been defined are based upon an explanation for Server and Client configuration found here: 
[https://www.golinuxcloud.com/mutual-tls-authentication-mtls/](https://www.golinuxcloud.com/mutual-tls-authentication-mtls/)

## Payer-to-Payer Trust Framework

A Payer-to-Payer Trust Framework will:
- Identify that a participant is a HIPAA covered entity or business associate operating on behalf of a Payer Covered Entity.
- Define the requirements for collecting and sharing member consent for the exchange of member health information via an opt-in process.

## Core Concepts for mTLS setup

Entities that are part of the Payer-to-Payer Trust Framework will create server and client certificates that are generated from a 
Certificate Authority that is recognized as a manager of the Payer-Payer Repository. This will ensure that the certificate chain 
will confirm that a party is a legitimate participant in the Trust Framework and that a secure mTLS connection can be established.

## Server Setup

There are two parts to the setup for mTLS on a server:

1. establish the Certificate Authority (CA) bundle together with a server certificate and key that is tied to the published mTLS endpoint.
2. Publish the Organization and Endpoint records as a bundle, per the PDex STU2 IG Specification.

### Server Configuration

1. Obtain CA Intermediate Certificate in .PEM or .CRT format.
2. Combine with other necessary CA Intermediate certificates to create a CA Bundle file.
3. Create a Certificate Signing Request (CSR).
4. Create Server Certificate with mTLS url endpoint that will be declared in the FHIR ndhendpoint profile.
5. Create Server Private Key.
6. Configure Gateway or web server endpoint with CA Bundle, Server Certificate and Server Key.
7. Setup Gateway or Web Server to redirect authenticated connections to the Dynamic Client Registration Protocol endpoint of the OAuth2.0 Auth Server.
8. OAuth2.0 DCRP should only accept input from Gateway or Web Server configured with mTLS.
9. OAuth2.0 DCRP should create a system credential that has access to $membermatch operation
10. Publish Organization and Endpoint information as a bundle to Payer-Payer/bundles folder.
11. submit a pull request to add bundle to main branch


## Client Setup

The Client setup mimics the server setup in configuring a CA Bundle, Client Certificate and key. These elements (files) are 
submitted as part of a request to an mTLS endpoint that can be found in the Payer-Payer repository, or the National Directory, 
when the National Directory is established and operational.

### Client Configuration

1. Obtain CA Intermediate Certificate in .PEM or .CRT format.
2. Combine with other necessary CA Intermediate certificates to create a CA Bundle file.
3. Create a Certificate Signing Request (CSR).
4. Create Client Certificate
5. Create Client Private Key
6. Find target Payer-to-Payer connection from Payer-Payer repository, or National Directory. See get_endpoint utility in /bundle-import
7. Make request to mTLS Server endpoint using CA Bundle, Client Certificate and Client Private Key. See Client Curl sample below.

### Client curl sample

The code sample below gives an example call to an mTLS endpoint using the required CA Bundle, client public certificate
and client private key.

```bash
curl --cacert /root/certs/cacert.pem \
     --key /root/certs/client.key.pem \
     --cert /root/certs/client.cert.pem \
     https://p2p.diamondonyx.example.com/mtlsendpoint

```
