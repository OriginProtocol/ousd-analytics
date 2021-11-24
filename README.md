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
    cd eagleproject
    cp eagleproject/.env.dev eagleproject/.env
    # edit eagleproject/.env and add in your provider URL
    python manage.py migrate

## To run
    export PROVIDER_URL="https://CHANGEURLHERE"
    # Below line allows for multithreading from bash on macOS High Sierra
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    export ETHERSCAN_API_KEY="your api key here"
    source ./eagle-python/bin/activate
    python ./manage.py runserver
    # **IMPORTANT**
    # Start by visiting http://localhost:8000/reload to download blockchain data
    # Otherwise, the root dashboard view will crash if there is no data

## To deploy

    # push to stable branch
    git checkout stable
    git merge origin/master
    git push origin stable

## Future

Data ingest:

- Oracle readings
- Actual exchange asset pricing
- Compound state

Views:

- Holdings (current and historical)
- [later] Oracle analysis
- [later] Compound health analysis
- [later] Flagged Transactions

Pushes:

- [later] To Discord

