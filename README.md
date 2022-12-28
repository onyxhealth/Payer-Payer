# Payer-to-Payer mTLS Discovery

This repository supports the [HL7 Da Vinci Payer Data Exchange STU2 Implementation Guide](http://hl7.org/fhir/us/davinci-pdex/2022May/)
 (IG) for Payer-to-Payer exchange.

In order for an automated exchange of Member data to be accomplished between two Payers (HIPAA Covered Entities) 
four steps need to happen:

1. Payers can discover the FHIR Endpoint for other trusted Payers
2. Payers can apply for an access token
3. Payers can submit information to enable a member to be matched
4. Payers can obtain an access token to retrieve the health information of the matched member.

In the absence of a National Directory that enables other Payer's FHIR endpoints to be discovered, an alternative
discovery mechanism is required. This repository is a test version of that discovery mechanism. for a production
implementation a trusted Certificate Authority would post certified bundles to the *bundles* folder. Each payer that
wants to perform Payer-to-Payer exchange with another Payer would submit a bundle to the repository.
Each bundle would contain an Organization and Endpoint record that details the necessary
mTLS connectivity information with supporting Public Certificate. 

Payers clone this repository and use the content of the */bundles* folder to setup mTLS connections
with other Payers.

The automated work flow for Payer-to-Payer Exchange is documented in the PDex IG on the
[Payer-to-Payer Exchange](http://hl7.org/fhir/us/davinci-pdex/2022May/PayerToPayerExchange.html) page.

The mTLS bundles are located in the /bundles directory of this repository.

A dockerized HAPI instance can be run by following the instructions in the /hapi-docker directory.

A set of Python scripts to load the bundles to the dockerized hapi server can be found in the /bundle-import directory. 


