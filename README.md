Vault Eagle

## The Vault Eagle Concept

- Provide easy visibility into the past and current state of OUSD.
- Provide an easy place to get data to make future predictions
- Have early detection when OUSD is becoming unsafe from a changing environment.
- Provide automated alerting when a problem happens.

## Setup

    # Let's create a new virtual environment
    python3 -m venv eagle-python
    source ./eagle-python/bin/activate
    pip install -r eagleproject/requirements.txt

## To run
    export PROVIDER_URL="https://CHANGEURLHERE"
    source ./eagle-python/bin/activate
    cd eagleproject
    python ./manage.py runserver

## Future

Data ingest:

- Oracle readings
- Vault holdings
- Vault supply
- Strategy holdings
- Actual exchange asset pricing
- OUSD and vault event logging
- [later] Compound events / state

Views:

- Holdings (current and historical)
- APR
- All Transactions
- [later] Oracle analysis
- [later] Compound health analysis
- [later] Flagged Transactions

Pushes:

- [later] To Discord
- [later]To a staticly rendered site for the public

