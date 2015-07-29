from modularodm.storedobject import StoredObject
from modularodm import storage
from modularodm import fields

class AddonModelMixin(StoredObject):

    _meta = {
        'abstract': True,
    }

class DraftRegistration(AddonModelMixin, StoredObject):

    is_draft_registration = True

    _id = fields.StringField(primary=True, default=lambda: str(ObjectId()))

    datetime_initiated = fields.DateTimeField(auto_now_add=True)
    datetime_updated = fields.DateTimeField(auto_now=True)

    branched_from = fields.ForeignField('node')

    initiator = fields.ForeignField('user')

    # Dictionary field mapping question id to a question's comments and answer
    # {<qid>: { 'comments': [<Comment1>, <Comment2>], 'value': 'string answer }
    registration_metadata = fields.DictionaryField(default=dict)
    registration_schema = fields.ForeignField('metaschema')
    registered_node = fields.ForeignField('node')

    storage = fields.ForeignField('osfstoragenodesettings')

    # Dictionary field mapping
    # { 'requiresApproval': true, 'fulfills': [{ 'name': 'Prereg Prize', 'info': <infourl>  }]  }
    config = fields.DictionaryField()

    # Dictionary field mapping a draft's states during the review process to their value
    # { 'isApproved': false, 'isPendingReview': false, 'paymentSent': false }
    flags = fields.DictionaryField()

class MetaSchema(StoredObject):

    _id = fields.StringField(default=lambda: str(ObjectId()))
    name = fields.StringField()
    schema = fields.DictionaryField()
    category = fields.StringField()

    # Version of the Knockout metadata renderer to use (e.g. if data binds
    # change)
    metadata_version = fields.IntegerField()
    # Version of the schema to use (e.g. if questions, responses change)
    schema_version = fields.IntegerField()
