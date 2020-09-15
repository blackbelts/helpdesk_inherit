# -*- coding: utf-8 -*-
{
    'name': "Help Desk BB",
    'summary': """HR Management & Operations""",
    'description': """Insurance Broker System """,
    'author': "Black Belts Egypt",
    'website': "www.blackbelts-egypt.com",
    'category': 'Policy',
    'version': '0.1',
    'license': 'AGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','helpdesk_lite',],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/help_desc.xml',
        'views/help_support_team.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
