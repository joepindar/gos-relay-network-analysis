from datetime import datetime
from time import sleep
import requests as requests
import json
from neomodel import config, db, clear_neo4j_database
from transaction_cluster_schema.schema import *

import logging
# create logger with 'spam_application'
logger = logging.getLogger('gos_cluster_analysis')
logger.setLevel(logging.DEBUG)
console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_log.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(console_log)


# Set up the database connection
try:
    from os import environ
    graphenedb_uri = environ['GRAPHENEDB_URI']
    graphenedb_password = environ['GRAPHENEDB_PASSWORD']
    graphenedb_user = environ['GRAPHENEDB_USER']
except KeyError:
    from transaction_cluster_schema.security_creds import graphenedb_uri, graphenedb_user, graphenedb_password

graphenedb_uri = 'bolt://{user}:{password}@' + graphenedb_uri
logger.debug("graphenedb uri {}".format(graphenedb_uri))
config.DATABASE_URL = graphenedb_uri.format(user=graphenedb_user,
                                            password=graphenedb_password)

def _api_call(call_url, headers):
    logger.debug("calling url {}".format(call_url))
    logger.debug("sent headers {}".format(headers))

    r = requests.get(call_url, headers=headers)
    # logger.debug("response header size: {}".format(len(r.headers)))
    response = json.loads(r.text)
    return response

def get_ValidatorNames():
    call_url = 'https://sgapi.certus.one/state/validatorNames'
    headers = {'User-Agent': 'Hello-From-Block3-Community'}
    response = _api_call(call_url, headers)
    logger.debug("number of validator names returned: {}".format(len(response)))
    return response

def get_last50_blocks(offset):
    base_url = 'https://sgapi.certus.one/blocks?limit=50&afterBlock={offset}'
    call_url = base_url.format(offset=offset)
    headers = {'User-Agent': 'Hello-From-Block3-Community'}
    response = _api_call(call_url, headers)
    logger.debug("number of blocks returned: {}".format(len(response)))
    return response

def get_transactions(height):
    base_url = 'https://sgapi.certus.one/transactions?height={height}'
    call_url = base_url.format(height=height)
    headers = {'User-Agent': 'Hello-From-Block3-Community'}
    response = _api_call(call_url, headers)
    logger.debug("number of transactions returned: {}".format(len(response)))
    return response

# Discover hidden stuff
def analyse_gos(start_block, end_block):

    # Get Validator names from Stargazer
    validator_response = get_ValidatorNames()
    # Add the validator names to graphenedb
    for validator in validator_response:
        logger.debug("Creating validator node: {}".format(validator))
        Validator(address=validator['operator_address'],
                    cons_address=validator['cons_address'],
                    moniker=validator['moniker']).save()

        sleep(0.2)     # be nice to graphenedb

    # Create the send_sync validator node
    Validator(address='send_sync', cons_address='send_sync', moniker='send_sync').save()

    # Get some blocks from Stargazer & set the proposer
    for offset in range(end_block, start_block, -50):
        blocks_response = get_last50_blocks(offset)
        # Add blocks to graphenedb
        for block in blocks_response:
            # ensure only processing blocks within the range...
            if block['height'] < start_block or block['height'] > end_block:
                continue

            sleep(0.2)     # be nice to graphenedb
            logger.debug("Creating block node: {}".format(block))
            cur_block = Block(height=block['height'],
                proposer=block['proposer'],
                json_blob=block,
                validator_misses=block['num_misses']).save()

            # Get the Validator node related to this proposal
            proposer_node = Validator.nodes.get(cons_address=block['proposer'])
            # Connect them
            # TODO: Change this to use neo4j datatime objects - currently issues with the string format -> datatime object
            rel = cur_block.proposal.connect(proposer_node,
                                    {'date_created': block['time'],
                                    'tx_type': 'propose'}).save()
            logger.debug("Validator {} proposed block {} @ height {}".format(proposer_node.cons_address,
                                                                    cur_block.uid,
                                                                    cur_block.height))

            if block['numTx'] > 0:
                # Get some transactions within the blocks...
                block_tx = get_transactions(block['height'])
                # Connect block tx senders to vlidators
                for tx in block_tx:

                    if len(tx['Messages']) > 1:
                        logger.debug("Found {} sub-transactions".format(len(tx['Messages'])))
                    for idx in range(len(tx['Messages'])):
                        sleep(0.05)
                        #ignore 'send' transactions for the moment...
                        if tx['Messages'][idx]['type'] == 'send':
                            logger.debug("Ignoring send message @ block {}".format(tx['Height']))
                            tx['Messages'][idx]['data']['validator_addr'] = 'send_sync'
                        elif tx['Messages'][idx]['type'] == 'withdraw_delegation_rewards_all':
                            logger.debug("Ignoring withdraw_delegation_rewards_all message @ block {}".format(tx['Height']))
                            continue
                        elif tx['Messages'][idx]['type'] == 'unjail':
                            logger.debug("Ignoring unjail message @ block {}".format(tx['Height']))
                            continue

                        # TODO: change this into a MERGE??
                        # Get the Validator node related to this transaction
                        tx_validator = Validator.nodes.get(address=tx['Messages'][idx]['data']['validator_addr'])

                        # Connect with relationship
                        rel = cur_block.tx.connect(tx_validator,
                                                {'tx_type': tx['Messages'][idx]['type'],
                                                'fee_denom': tx['Fee']['amount'][0]['denom'],
                                                'fee_amount': tx['Fee']['amount'][0]['amount']}).save()

                        logger.debug("Connected validator {} to block {} with transaction type {}".format(tx_validator.address,
                                                                                cur_block.uid,
                                                                                rel.tx_type))

if __name__ == "__main__":
    # Discover hidden stuff
    clear_neo4j_database(db)
    logger.debug("Clearing the graphenedb database...")
    analyse_gos(337000, 339000)
