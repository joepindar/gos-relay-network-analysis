from neomodel import (DateTimeProperty, IntegerProperty, JSONProperty,
                    StringProperty, UniqueIdProperty, StructuredNode,
                    RelationshipFrom, RelationshipTo, ZeroOrMore)

from .relationships import (Transaction, Propose)

class Validator(StructuredNode):
    acc_address = StringProperty()                      # cosmos1 address
    address = StringProperty(unique_index=True)         # cosmosvaloper1 address
    moniker = StringProperty(default="unknown")         # Human readable name
    cons_address = StringProperty(unique_index=True)    # Hex address
    date_node_created = DateTimeProperty(default_now=True)
    uid = UniqueIdProperty()

    # traverse outgoing TX relations, inflate to Block objects
    tx = RelationshipTo('Block', 'TX',
                        model=Transaction,
                        cardinality=ZeroOrMore)
    proposal = RelationshipTo('Block', 'PROPOSAL',
                        model=Propose,
                        cardinality=ZeroOrMore)

class Block(StructuredNode):
    height = IntegerProperty(unique_index=True, required=True)  # Block height
    proposer = StringProperty(default="unknown")        # Proposer address for easy single node querying
    json_blob = JSONProperty()                          # raw data from the Stargazer API
    validator_misses = IntegerProperty()                # How many precommits are missing from the block
    uid = UniqueIdProperty()

    # traverse outgoing TX relations, inflate to Block objects
    tx = RelationshipFrom('Validator', 'TX',
                        model=Transaction,
                        cardinality=ZeroOrMore)

    proposal = RelationshipFrom('Validator', 'PROPOSAL',
                        model=Propose,
                        cardinality=ZeroOrMore)
