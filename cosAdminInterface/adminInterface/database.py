import pymongo
import os

from modularodm import Q

# importing from the osf.io submodule
import sys
sys.path.insert(0, '/Users/laurenbarker/GitHub/COS-Admin-Interface/cosAdminInterface/adminInterface/osf.io/')
from website.project.model import MetaSchema, DraftRegistration
#from osf_models import DraftRegistration, MetaSchema

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

def get_all_drafts():
	# set the collection to retrieve data from
	draftCollection = db['draftregistration']

	# TODO 
	# add query parameters to only retrieve submitted drafts
	all_drafts = draftCollection.find()

	auth = None

	serialized_drafts = {
		'drafts': [utils.serialize_draft_registration(d, auth) for d in all_drafts]
	}
	return serialized_drafts

# User.set_storage(storage.MongoStorage(db, collection="user"))
# use class for draft (should be the same as what is already created)
# create new instance of a class and then use .save to update db
# DraftRegistration.set_storage(storage.MongoStorage(db, collection=draftCollection))

get_schema_or_fail = lambda query: get_or_http_error(MetaSchema, query)

def get_metaschema(schema_name, schema_version=1, *args, **kwargs):
    meta_schema = get_schema_or_fail(
        Q('name', 'eq', schema_name) &
        Q('schema_version', 'eq', schema_version)
    )
    return serialize_meta_schema(meta_schema), http.OK
