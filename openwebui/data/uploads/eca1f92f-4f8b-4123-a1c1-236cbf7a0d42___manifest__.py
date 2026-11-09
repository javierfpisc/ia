{
    'name': "Real Estate",
    'version': '1.0',
    'category': 'Tutorials/Real Estate',
    'summary': "Manage real estate properties, types, tags and offers",
    'description': """
        The Real Estate Advertisement module built during the bootcamp —
        complete Server Framework 101 build: models, relations, computed
        fields, onchange, action buttons, security, polished views and menus.
    """,
    'depends': ['base', 'mail'],
    # Order matters: security first, then actions/views, then the menus that use them.
    'data': [
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'views/estate_make_offer_wizard_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_amenity_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml',
        'data/estate_data.xml',
        'data/estate_amenities.xml',
        'data/estate_cron.xml',
        'report/estate_property_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'estate/static/src/scss/estate_kanban.scss',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
