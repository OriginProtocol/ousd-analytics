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
    # edit eagleproject/.env and add in your provider URL (alchemy, for example)
    # run a postgresql db locally and setup DATABASE_URL in .env
    python manage.py migrate

## To run
    export PROVIDER_URL="https://CHANGEURLHERE"
    # Below line allows for multithreading from bash on macOS High Sierra
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    export ETHERSCAN_API_KEY="your api key here"
    source ./eagle-python/bin/activate
    python ./manage.py runserver
    # **IMPORTANT**
    # Start by visiting http://localhost:8000/snap to download blockchain snapshot (will take a few mins)
    # Otherwise, the root dashboard view will crash (with an IndexError)
    # Visit http://localhost:8000/reload to download blockchain data (data download starts from block 10884500)  
    # Otherwise, there will be no events shown for the contracts

## To deploy

    # push to stable branch
    git checkout stable
    git merge origin/master
    git push origin stable

## Additional Information

The app is based on Django and presents two main views - snapshot data and contract event data.  
Snapshot data view consists of total supply of OUSD, OUSD APY, Vault Holdings and allocations among other things  
Contract event data view consists of the latest events for OUSD, Vault, Governance, and other contracts   

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

