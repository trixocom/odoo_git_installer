# -*- coding: utf-8 -*-
{
    'name': 'Git Module Installer',
    'version': '18.0.1.2.0',
    'category': 'Technical',
    'summary': 'Install Odoo modules directly from GitHub/GitLab repositories - supports tags and branches',
    'description': """
Git Module Installer
====================
This module allows you to:
* Define multiple GitHub or GitLab repository sources
* Browse available tags AND branches from repositories
* Clone specific module versions to your addons path
* Automatically restart Odoo and update module list
* Manage permissions for proper Odoo user ownership

Compatible with repositories that use tags (OCA) and branches (ADHOC)

Designed for Odoo 18.0 (CE and EE)
    """,
    'author': 'Trixocom',
    'website': 'https://www.trixocom.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
