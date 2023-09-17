{
    'name': "Real estate Management",
    'version': '1.0',
    'author': "Consultant Odoo",
    'depends': ['base'],
    'website': 'www.doosys.ma',
    'description': """
    Description of the real estate App
    """,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menu.xml',
    ]


}