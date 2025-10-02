# -*- coding: utf-8 -*-
{
    'name': 'Git Module Installer',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Install Odoo modules directly from GitHub/GitLab repositories',
    'description': """
Git Module Installer
====================
This module allows you to:
* Define multiple GitHub or GitLab repository sources
* Browse available tags/versions from repositories
* Clone specific module versions to your addons path
* Automatically restart Odoo and update module list
* Manage permissions for proper Odoo user ownership

Compatible with Odoo versions 15.0, 16.0, 17.0, and 18.0 (CE and EE)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
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