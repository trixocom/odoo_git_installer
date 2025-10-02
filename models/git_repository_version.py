# -*- coding: utf-8 -*-

from odoo import models, fields


class GitRepositoryVersion(models.Model):
    _name = 'git.repository.version'
    _description = 'Git Repository Version/Tag/Branch'
    _order = 'sequence, name desc'

    name = fields.Char(string='Version/Tag/Branch', required=True)
    display_name_full = fields.Char(string='Display Name', compute='_compute_display_name_full', store=True)
    repository_id = fields.Many2one('git.repository', string='Repository', required=True, ondelete='cascade')
    version_type = fields.Selection([
        ('tag', 'Tag'),
        ('branch', 'Branch')
    ], string='Type', default='tag', required=True)
    sequence = fields.Integer(string='Sequence', default=10, help='Order of display (tags first by default)')
    full_reference = fields.Char(string='Full Reference', compute='_compute_full_reference', store=True)

    @api.depends('version_type', 'name')
    def _compute_display_name_full(self):
        """Compute display name with icon"""
        for record in self:
            icon = '🏷️' if record.version_type == 'tag' else '🌿'
            record.display_name_full = f"{icon} {record.name}"

    @api.depends('version_type', 'name')
    def _compute_full_reference(self):
        """Compute full reference like 'tag:18.0.1.0.0' or 'branch:18.0'"""
        for record in self:
            record.full_reference = f"{record.version_type}:{record.name}"

    def name_get(self):
        """Override name_get to show icon in dropdown"""
        result = []
        for record in self:
            icon = '🏷️' if record.version_type == 'tag' else '🌿'
            name = f"{icon} {record.name}"
            result.append((record.id, name))
        return result
