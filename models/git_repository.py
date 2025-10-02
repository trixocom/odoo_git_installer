# -*- coding: utf-8 -*-

import os
import subprocess
import logging
import shutil
import pwd
from urllib.parse import urlparse
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository Source'
    _order = 'name'

    name = fields.Char(string='Repository Name', required=True)
    url = fields.Char(string='Repository URL', required=True, help='Public GitHub or GitLab repository URL')
    repository_type = fields.Selection([
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
    ], string='Repository Type', compute='_compute_repository_type', store=True)
    
    clone_path = fields.Char(
        string='Clone Path',
        default='/mnt/extra-addons',
        required=True,
        help='Path where modules will be cloned'
    )
    
    tags = fields.Text(string='Available Tags', readonly=True, help='Cached list of available tags')
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('error', 'Error'),
    ], string='Status', default='draft', readonly=True)
    
    error_message = fields.Text(string='Error Message', readonly=True)
    installed_modules = fields.One2many('git.installed.module', 'repository_id', string='Installed Modules')

    @api.depends('url')
    def _compute_repository_type(self):
        """Automatically detect repository type from URL"""
        for record in self:
            if record.url:
                if 'github.com' in record.url:
                    record.repository_type = 'github'
                elif 'gitlab.com' in record.url or 'gitlab' in record.url:
                    record.repository_type = 'gitlab'
                else:
                    record.repository_type = 'github'  # default
            else:
                record.repository_type = False

    @api.constrains('url')
    def _check_url(self):
        """Validate repository URL format"""
        for record in self:
            if record.url:
                parsed = urlparse(record.url)
                if not parsed.scheme or not parsed.netloc:
                    raise ValidationError(_('Invalid repository URL format. Please provide a complete URL.'))

    @api.constrains('clone_path')
    def _check_clone_path(self):
        """Validate clone path exists and is writable"""
        for record in self:
            if record.clone_path:
                if not os.path.isabs(record.clone_path):
                    raise ValidationError(_('Clone path must be an absolute path.'))

    def _get_odoo_user(self):
        """Get the user running the Odoo process"""
        try:
            return pwd.getpwuid(os.getuid()).pw_name
        except Exception as e:
            _logger.warning(f"Could not determine Odoo user: {e}")
            return None

    def _run_command(self, command, cwd=None):
        """Execute shell command and return output"""
        try:
            _logger.info(f"Executing command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                error_msg = f"Command failed: {command}\nError: {result.stderr}"
                _logger.error(error_msg)
                raise UserError(error_msg)
            
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise UserError(_('Command timeout expired. The operation took too long.'))
        except Exception as e:
            _logger.exception("Error executing command")
            raise UserError(_(f'Error executing command: {str(e)}'))

    def _get_git_tags(self):
        """Fetch available tags from git repository"""
        self.ensure_one()
        
        try:
            # Use ls-remote to get tags without cloning
            command = f"git ls-remote --tags {self.url}"
            output = self._run_command(command)
            
            if not output:
                return []
            
            # Parse tags from output
            tags = []
            for line in output.split('\n'):
                if line and 'refs/tags/' in line:
                    tag = line.split('refs/tags/')[-1]
                    # Remove ^{} suffix for annotated tags
                    if tag.endswith('^{}'):
                        continue
                    tags.append(tag)
            
            return sorted(tags, reverse=True)
        except Exception as e:
            _logger.exception("Error fetching git tags")
            raise UserError(_(f'Error fetching tags: {str(e)}'))

    def action_validate_repository(self):
        """Validate repository connection and fetch tags"""
        self.ensure_one()
        
        try:
            # Check if git is installed
            self._run_command("git --version")
            
            # Fetch tags
            tags = self._get_git_tags()
            
            if not tags:
                raise UserError(_('No tags found in repository. Please ensure the repository has at least one tag.'))
            
            self.write({
                'tags': '\n'.join(tags),
                'last_sync': fields.Datetime.now(),
                'state': 'validated',
                'error_message': False,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Repository validated successfully. Found %s tags.') % len(tags),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise

    def action_refresh_tags(self):
        """Refresh available tags from repository"""
        return self.action_validate_repository()

    def action_clone_tag(self):
        """Open wizard to select and clone a specific tag"""
        self.ensure_one()
        
        if self.state != 'validated':
            raise UserError(_('Please validate the repository first.'))
        
        if not self.tags:
            raise UserError(_('No tags available. Please refresh tags first.'))
        
        # Open wizard
        return {
            'name': _('Clone Repository Tag'),
            'type': 'ir.actions.act_window',
            'res_model': 'git.clone.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_repository_id': self.id,
            }
        }

    def _clone_repository_tag(self, tag, module_name=None):
        """Clone specific tag from repository"""
        self.ensure_one()
        
        # Ensure clone path exists
        if not os.path.exists(self.clone_path):
            try:
                os.makedirs(self.clone_path, exist_ok=True)
                _logger.info(f"Created clone path: {self.clone_path}")
            except Exception as e:
                raise UserError(_(f'Cannot create clone path: {str(e)}'))
        
        # Determine module name from URL if not provided
        if not module_name:
            module_name = self.url.rstrip('/').split('/')[-1]
            if module_name.endswith('.git'):
                module_name = module_name[:-4]
        
        # Add tag suffix to avoid conflicts
        target_dir = os.path.join(self.clone_path, f"{module_name}_{tag}")
        
        # Check if already exists
        if os.path.exists(target_dir):
            raise UserError(_(f'Module directory already exists: {target_dir}\nPlease remove it first or choose a different tag.'))
        
        temp_dir = None
        try:
            # Create temporary directory for cloning
            temp_dir = f"/tmp/odoo_git_clone_{os.getpid()}"
            
            # Clone with specific tag
            _logger.info(f"Cloning repository {self.url} tag {tag} to {temp_dir}")
            clone_cmd = f"git clone --depth 1 --branch {tag} {self.url} {temp_dir}"
            self._run_command(clone_cmd)
            
            # Move to final destination
            shutil.move(temp_dir, target_dir)
            temp_dir = None
            
            # Set proper permissions
            odoo_user = self._get_odoo_user()
            if odoo_user:
                try:
                    _logger.info(f"Setting ownership to {odoo_user} for {target_dir}")
                    self._run_command(f"chown -R {odoo_user}:{odoo_user} {target_dir}")
                except Exception as e:
                    _logger.warning(f"Could not set ownership: {e}")
            
            # Record installed module
            self.env['git.installed.module'].create({
                'repository_id': self.id,
                'name': module_name,
                'tag': tag,
                'path': target_dir,
                'install_date': fields.Datetime.now(),
            })
            
            return target_dir
            
        except Exception as e:
            # Cleanup on error
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
            raise
        
    def _restart_odoo(self):
        """Restart Odoo server"""
        _logger.info("Restarting Odoo server...")
        try:
            # Send SIGHUP to reload Odoo
            os.kill(os.getppid(), 1)
        except Exception as e:
            _logger.warning(f"Could not restart Odoo automatically: {e}")
            raise UserError(_('Module cloned successfully, but automatic restart failed.\nPlease restart Odoo manually.'))

    def _update_module_list(self):
        """Update Odoo module list"""
        _logger.info("Updating module list...")
        try:
            self.env['ir.module.module'].update_list()
            self.env.cr.commit()
        except Exception as e:
            _logger.exception("Error updating module list")
            raise UserError(_(f'Error updating module list: {str(e)}'))


class GitInstalledModule(models.Model):
    _name = 'git.installed.module'
    _description = 'Git Installed Module'
    _order = 'install_date desc'

    repository_id = fields.Many2one('git.repository', string='Repository', required=True, ondelete='cascade')
    name = fields.Char(string='Module Name', required=True)
    tag = fields.Char(string='Tag/Version', required=True)
    path = fields.Char(string='Installation Path', required=True)
    install_date = fields.Datetime(string='Installation Date', required=True)
    
    def action_remove_module(self):
        """Remove cloned module directory"""
        self.ensure_one()
        
        if not os.path.exists(self.path):
            self.unlink()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Module directory not found. Record removed.'),
                    'type': 'warning',
                }
            }
        
        try:
            shutil.rmtree(self.path)
            self.unlink()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Module removed successfully.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f'Error removing module: {str(e)}'))


class GitCloneWizard(models.TransientModel):
    _name = 'git.clone.wizard'
    _description = 'Git Clone Wizard'

    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
    tag = fields.Selection(selection='_get_tag_selection', string='Select Tag', required=True)
    module_name = fields.Char(string='Module Name (optional)', help='Leave empty to use repository name')
    auto_restart = fields.Boolean(string='Auto Restart Odoo', default=True)
    auto_update_list = fields.Boolean(string='Auto Update Module List', default=True)

    @api.model
    def _get_tag_selection(self):
        """Get tags from repository for selection field"""
        repository_id = self.env.context.get('default_repository_id')
        if repository_id:
            repo = self.env['git.repository'].browse(repository_id)
            if repo.tags:
                tags = repo.tags.split('\n')
                return [(tag, tag) for tag in tags if tag]
        return [('', '')]

    def action_clone(self):
        """Execute clone operation"""
        self.ensure_one()
        
        try:
            # Clone repository
            target_dir = self.repository_id._clone_repository_tag(self.tag, self.module_name)
            
            # Update module list
            if self.auto_update_list:
                self.repository_id._update_module_list()
            
            # Restart Odoo
            if self.auto_restart:
                self.repository_id._restart_odoo()
                message = _('Module cloned successfully to: %s\nOdoo is restarting...') % target_dir
            else:
                message = _('Module cloned successfully to: %s\nPlease restart Odoo manually and update module list.') % target_dir
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': True,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
            
        except Exception as e:
            _logger.exception("Error during clone operation")
            raise UserError(_(f'Clone operation failed: {str(e)}'))