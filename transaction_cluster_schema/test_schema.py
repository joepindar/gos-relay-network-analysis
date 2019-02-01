from pytest import raises
from neomodel import config, db, clear_neo4j_database
from .schema import *

# Set up the database connection
try:
    from os import environ
    graphenedb_uri = environ['GRAPHENEDB_URI']
    graphenedb_password = environ['GRAPHENEDB_PASSWORD']
    graphenedb_user = environ['GRAPHENEDB_USER']
except KeyError:
    from .security_creds import graphenedb_uri, graphenedb_user, graphenedb_password

graphenedb_uri = 'bolt://{user}:{password}@' + graphenedb_uri
print(graphenedb_uri)
config.DATABASE_URL = graphenedb_uri.format(user=graphenedb_user,
                                            password=graphenedb_password)

def test_schema():
    clear_neo4j_database(db)

    # Create the validator and assert that it has no connections
    validator = Validator(acc_address='cosmos1uwgyzw8mdsaxcmuy28lz79q3xznlnqmph227c7',
                        address='cosmosvaloper1uwgyzw8mdsaxcmuy28lz79q3xznlnqmpj77t5d',
                        cons_address='DD2CA4EF17A292E085C485C25D4B1855CEA9BE69',
                        moniker='loco.block3.community').save()
    assert validator
    # assert len(validator.tx) == 0
    # assert not validator.tx

# Add a block
    block = Block(height=1, proposer='DD2CA4EF17A292E085C485C25D4B1855CEA9BE69').save()
    assert block

    assert len(block.tx) == 0
    assert not block.tx

# Connect Validator to block
    validator.tx.connect(block)
    assert len(validator.tx) == 1
    assert validator.tx
    assert validator.tx.is_connected(block)
