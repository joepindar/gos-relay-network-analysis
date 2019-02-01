# gos-relay-network-analysis

** Apologies for the roughness of the code - I am not a developer, I just do it answer my questions. **

#### Scope
POC to discover possible cartel relay network in Cosmos GOS 3 network.

#### Graph database
I used [GrapheneDB](https://www.graphenedb.com) as a graph database. There is a free Hobby instance, but you will likely have to pay for a Developer instance owing to the number of nodes required in the analysis.

* Security
Rename `security_creds-example.py` to `security_creds.py` and add in the GrapheneDB credentials.

#### Prepare the environment for development and testing
* Prepare the environment & install dependencies:
```bash
virtualenv -p /usr/local/bin/python3.7 venv
venv/bin/pip install -r requirements.txt
```

#### Run the processing code
* Prepare the environment & install dependencies:
```bash
venv/bin/python transaction_analysis.py
```

#### Investigate the graph
* Use the browser in your account on [GrapheneDB](https://www.graphenedb.com)
