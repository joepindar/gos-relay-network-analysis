from neomodel import DateTimeProperty, StringProperty, IntegerProperty, StructuredRel

class Transaction(StructuredRel):
    # date_created = DateTimeProperty(default_now=True)
    date_created = StringProperty()
    tx_type = StringProperty()
    fee_amount = IntegerProperty()              # default=0
    fee_denom = StringProperty()                # default="STAKE"

class Propose(StructuredRel):
    # date_created = DateTimeProperty(default_now=True)
    date_created = StringProperty()
    tx_type = StringProperty()
