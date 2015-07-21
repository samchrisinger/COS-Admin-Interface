import pymongo
import os

from modularodm import storage
from modularodm import fields
from modularodm.storedobject import StoredObject

import osf_settings
import utils

def get_mongo_client():
    """Create MongoDB client and authenticate database.
    """
    client = pymongo.MongoClient(osf_settings.DB_HOST, osf_settings.DB_PORT)

    db = client[osf_settings.DB_NAME]

    if osf_settings.DB_USER and osf_settings.DB_PASS:
        db.authenticate(osf_settings.DB_USER, osf_settings.DB_PASS)

    return client

client = get_mongo_client()    

def _get_current_database():
    """Getter for `database` proxy.
    """
    return client[osf_settings.DB_NAME]

db = _get_current_database()

print client
print db

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

DraftRegistration.set_storage(storage.MongoStorage(db, collection="draft_registration"))

all_drafts = DraftRegistration.find()

print all_drafts
print len(all_drafts)

serialized_drafts = {
	'drafts': [utils.serialize_draft_registration(d, auth) for d in all_drafts]
}

print serialized_drafts
