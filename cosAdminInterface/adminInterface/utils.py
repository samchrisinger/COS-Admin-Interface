import osf_settings

# def serialize_draft_registration(draft, auth=None):
#     import ipdb; ipdb.set_trace()
#     import sys
#     sys.path.insert(0, '/Users/laurenbarker/GitHub/COS-Admin-Interface/cosAdminInterface/adminInterface/osf.io/')
#     from website.profile.utils import serialize_user  # noqa
#     #from website.project.utils import serialize_node  # noqa

#     node = draft.branched_from

#     return {
#         'pk': draft._id,
#         #'branched_from': serialize_node(draft.branched_from, auth),
#         'initiator': serialize_user(draft.initiator, full=True),
#         'registration_metadata': draft.registration_metadata,
#         'registration_schema': serialize_meta_schema(draft.registration_schema),
#         'initiated': str(draft.datetime_initiated),
#         'updated': str(draft.datetime_updated),
#         'config': draft.config or {},
#         'flags': draft.flags,
#         # 'urls': {
#         #     'edit': node.web_url_for('edit_draft_registration_page', draft_id=draft._id),
#         #     'before_register': node.api_url_for('project_before_register'),
#         #     'register': node.api_url_for('register_draft_registration', draft_id=draft._id),
#         #     'register_page': node.web_url_for('draft_before_register_page', draft_id=draft._id),
#         #     'registrations': node.web_url_for('node_registrations')
#         # }
#     }

def serialize_draft_registration(draft, auth=None):
    node = draft["branched_from"]
    #import ipdb; ipdb.set_trace()

    return {
        'pk': draft["_id"],
        'branched_from': draft["branched_from"],
        'initiator': draft["initiator"],
        'registration_metadata': draft["registration_metadata"],
        'registration_schema': draft["registration_schema"],
        'initiated': str(draft["datetime_initiated"]),
        'updated': str(draft["datetime_updated"]),
        'registered': draft["registered_node"],
        'config': draft["config"] or {},
        'flags': draft["flags"],
        # 'urls': {
        #     'edit': node.web_url_for('edit_draft_registration', draft_id=draft._id),
        #     'before_register': node.api_url_for('draft_before_register', draft_id=draft._id),
        #     'register': node.api_url_for('register_draft_registration', draft_id=draft._id),
        #     'register_page': node.web_url_for('draft_before_register_page', draft_id=draft._id),
        #     'registrations': node.web_url_for('node_registrations')
        # }
    }

def serialize_node(node, auth, primary=False):
    """Build a JSON object containing everything needed to render
    project.view.mako.
    """
    user = auth.user

    parent = node.parent_node
    if user:
        dashboard = find_dashboard(user)
        dashboard_id = dashboard._id
        in_dashboard = dashboard.pointing_at(node._primary_key) is not None
    else:
        in_dashboard = False
        dashboard_id = ''
    view_only_link = auth.private_key or request.args.get('view_only', '').strip('/')
    anonymous = has_anonymous_link(node, auth)
    widgets, configs, js, css = _render_addon(node)
    redirect_url = node.url + '?view_only=None'

    # Before page load callback; skip if not primary call
    if primary:
        for addon in node.get_addons():
            messages = addon.before_page_load(node, user) or []
            for message in messages:
                status.push_status_message(message, 'info', dismissible=False)
    data = {
        'node': {
            'id': node._primary_key,
            'title': node.title,
            'category': node.category_display,
            'category_short': node.category,
            'node_type': node.project_or_component,
            'description': node.description or '',
            'url': node.url,
            'api_url': node.api_url,
            'absolute_url': node.absolute_url,
            'redirect_url': redirect_url,
            'display_absolute_url': node.display_absolute_url,
            'update_url': node.api_url_for('update_node'),
            'in_dashboard': in_dashboard,
            'is_public': node.is_public,
            'is_archiving': node.archiving,
            'date_created': iso8601format(node.date_created),
            'date_modified': iso8601format(node.logs[-1].date) if node.logs else '',
            'tags': [tag._primary_key for tag in node.tags],
            'children': bool(node.nodes),
            'is_registration': node.is_registration,
            'is_retracted': node.is_retracted,
            'pending_retraction': node.pending_retraction,
            'retracted_justification': getattr(node.retraction, 'justification', None),
            'embargo_end_date': node.embargo_end_date.strftime("%A, %b. %d, %Y") if node.embargo_end_date else False,
            'pending_embargo': node.pending_embargo,
            'registered_from_url': node.registered_from.url if node.is_registration else '',
            'registered_date': iso8601format(node.registered_date) if node.is_registration else '',
            'root_id': node.root._id,
            'registered_meta': node.registered_meta,
            'registered_schema': serialize_meta_schema(node.registered_schema),
            'registration_count': len(node.node__registrations),
            'is_fork': node.is_fork,
            'forked_from_id': node.forked_from._primary_key if node.is_fork else '',
            'forked_from_display_absolute_url': node.forked_from.display_absolute_url if node.is_fork else '',
            'forked_date': iso8601format(node.forked_date) if node.is_fork else '',
            'fork_count': len(node.forks),
            'templated_count': len(node.templated_list),
            'watched_count': len(node.watchconfig__watched),
            'private_links': [x.to_json() for x in node.private_links_active],
            'link': view_only_link,
            'anonymous': anonymous,
            'points': len(node.get_points(deleted=False, folders=False)),
            'piwik_site_id': node.piwik_site_id,
            'comment_level': node.comment_level,
            'has_comments': bool(getattr(node, 'commented', [])),
            'has_children': bool(getattr(node, 'commented', False)),
            'identifiers': {
                'doi': node.get_identifier_value('doi'),
                'ark': node.get_identifier_value('ark'),
            },
        },
        'parent_node': {
            'exists': parent is not None,
            'id': parent._primary_key if parent else '',
            'title': parent.title if parent else '',
            'category': parent.category_display if parent else '',
            'url': parent.url if parent else '',
            'api_url': parent.api_url if parent else '',
            'absolute_url': parent.absolute_url if parent else '',
            'registrations_url': parent.web_url_for('node_registrations') if parent else '',
            'is_public': parent.is_public if parent else '',
            'is_contributor': parent.is_contributor(user) if parent else '',
            'can_view': parent.can_view(auth) if parent else False
        },
        'user': {
            'is_contributor': node.is_contributor(user),
            'is_admin_parent': parent.is_admin_parent(user) if parent else False,
            'can_edit': (node.can_edit(auth)
                         and not node.is_registration),
            'has_read_permissions': node.has_permission(user, 'read'),
            'permissions': node.get_permissions(user) if user else [],
            'is_watching': user.is_watching(node) if user else False,
            'piwik_token': user.piwik_token if user else '',
            'id': user._id if user else None,
            'username': user.username if user else None,
            'fullname': user.fullname if user else '',
            'can_comment': node.can_comment(auth),
            'show_wiki_widget': _should_show_wiki_widget(node, user),
            'dashboard_id': dashboard_id,
        },
        'badges': _get_badge(user),
        # TODO: Namespace with nested dicts
        'addons_enabled': node.get_addon_names(),
        'addons': configs,
        'addon_widgets': widgets,
        'addon_widget_js': js,
        'addon_widget_css': css,
        'node_categories': Node.CATEGORY_MAP,
    }
    return data
