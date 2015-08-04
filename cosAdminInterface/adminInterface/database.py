import pymongo
import os
import httplib as http

from modularodm import Q
from modularodm import storage

# importing from the osf.io submodule
from utils import submodule_path
import sys
sys.path.insert(0, submodule_path('utils.py'))
from website.project.model import MetaSchema, DraftRegistration, Node
from framework.mongo.utils import get_or_http_error
from framework.auth.core import User
from framework.auth import Auth
from website.project.metadata.utils import serialize_meta_schema, serialize_draft_registration
from website.app import do_set_backends, init_addons
from website import settings as osf_settings

import utils

init_addons(osf_settings, routes=False)
do_set_backends(osf_settings)
adminUser = User.load('dsmpw')

# create new instance of a class and then use .save to update db

def get_all_drafts():
	# TODO 
	# add query parameters to only retrieve submitted drafts
	all_drafts = DraftRegistration.find()

	auth = Auth(adminUser)

	serialized_drafts = {
		'drafts': [utils.serialize_draft_registration(d, auth) for d in all_drafts]
	}
	return serialized_drafts

get_schema_or_fail = lambda query: get_or_http_error(MetaSchema, query)	

def get_draft(draft_pk):
	auth = Auth(adminUser)
	
	draft = DraftRegistration.find(
        Q('_id', 'eq', draft_pk)
    )

	return utils.serialize_draft_registration(draft[0], auth), http.OK

# TODO update so works in this context
def update_draft_registration(auth, node, draft_pk, *args, **kwargs):
    data = request.get_json()

    draft = get_draft_or_fail(draft_pk)

    schema_data = data.get('schema_data', {})

    schema_name = data.get('schema_name')
    schema_version = data.get('schema_version', 1)
    if schema_name:
        meta_schema = get_schema_or_fail(
            Q('name', 'eq', schema_name) &
            Q('schema_version', 'eq', schema_version)
        )
        existing_schema = draft.registration_schema
        if (existing_schema.name, existing_schema.schema_version) != (meta_schema.name, meta_schema.schema_version):
            draft.registration_schema = meta_schema

    try:
        draft.update_metadata(schema_data)
    except (NodeStateError):
        raise HTTPError(http.BAD_REQUEST)
    return serialize_draft_registration(draft, auth), http.OK

def get_schema():
	metaCollection = db['metaschema']
	all_schemas = metaCollection.find()
	serialized_schemas = {
		'schemas': [utils.serialize_meta_schema(s) for s in all_schemas]
	}
	return serialized_schemas

def get_metaschema(schema_name, schema_version=1):
    meta_schema = get_schema_or_fail(
        Q('name', 'eq', schema_name) &
        Q('schema_version', 'eq', schema_version)
    )
    return serialize_meta_schema(meta_schema), http.OK
