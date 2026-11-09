{
    'name': "Estate Accounts",
    'version': '1.0',
    'category': 'Tutorials/Real Estate',
    'summary': "Bills the buyer when a property is sold (links Real Estate to Invoicing)",
    # Depends on 'account' so we can create customer invoices (account.move).
    'depends': ['estate', 'account'],
    'data': [
        "views/estate_property_views.xml",
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
