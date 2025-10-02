# Git Module Installer for Odoo

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Description

**Git Module Installer** is a powerful Odoo module that allows you to install and manage Odoo modules directly from GitHub or GitLab repositories. No more manual downloads and file transfers - manage everything from within Odoo's interface!

### Key Features

- 🔗 **Multiple Repository Sources**: Define unlimited GitHub and GitLab repository sources
- 🏷️ **Tag/Version Selection**: Browse and select specific tags/versions to install
- 📦 **Automatic Installation**: Clone modules directly to your addons path
- 🔄 **Auto-restart & Update**: Automatically restart Odoo and update the module list
- 👤 **Permission Management**: Automatically sets proper ownership for the Odoo user
- 📊 **Installation History**: Track all installed modules and their versions
- 🎯 **User-friendly Interface**: Intuitive wizard-based installation process

## Version Compatibility

This module is compatible with:
- ✅ Odoo 15.0 (Community & Enterprise)
- ✅ Odoo 16.0 (Community & Enterprise)
- ✅ Odoo 17.0 (Community & Enterprise)
- ✅ Odoo 18.0 (Community & Enterprise)

## Requirements

### System Requirements
- Git must be installed on the server
- Python 3.7 or higher
- Write permissions on the addons directory

### Python Dependencies
All dependencies are part of Python's standard library:
- `subprocess`
- `os`
- `shutil`
- `pwd`
- `urllib`

## Installation

### 1. Download the Module

Clone this repository to your Odoo addons directory:

```bash
cd /path/to/odoo/addons
git clone https://github.com/trixocom/odoo_git_installer.git
```

Or download and extract the ZIP file to your addons directory.

### 2. Update Apps List

In Odoo:
1. Go to **Apps**
2. Click **Update Apps List**
3. Search for "Git Module Installer"
4. Click **Install**

## Configuration

### 1. Set Clone Path (Optional)

By default, modules are cloned to `/mnt/extra-addons`. You can change this when creating a repository source.

### 2. Ensure Permissions

Make sure the Odoo user has write permissions on the clone path:

```bash
sudo chown -R odoo:odoo /mnt/extra-addons
sudo chmod -R 755 /mnt/extra-addons
```

## Usage

### Adding a Repository Source

1. Go to **Git Installer > Repositories**
2. Click **Create**
3. Fill in the details:
   - **Repository Name**: A friendly name (e.g., "OCA Web")
   - **Repository URL**: The full public repository URL (e.g., `https://github.com/OCA/web`)
   - **Clone Path**: Where to install modules (default: `/mnt/extra-addons`)
4. Click **Validate & Fetch Tags**

### Installing a Module

1. Open a validated repository
2. Click **Clone Tag**
3. Select the desired tag/version
4. Optionally adjust:
   - **Module Name**: Custom name for the installation directory
   - **Auto Update Module List**: Update Odoo's module list after cloning
   - **Auto Restart Odoo**: Restart Odoo automatically after installation
5. Click **Clone**

### Managing Installed Modules

In the repository form, the **Installed Modules** tab shows all modules cloned from this repository. You can:
- View installation path
- See installation date
- Remove modules (deletes the directory)

## Example Repositories

Here are some popular Odoo repositories you can use:

### OCA (Odoo Community Association)
- **Web**: `https://github.com/OCA/web`
- **Server Tools**: `https://github.com/OCA/server-tools`
- **Reporting Engine**: `https://github.com/OCA/reporting-engine`
- **Account Financial Tools**: `https://github.com/OCA/account-financial-tools`

### Other Sources
Any public GitHub or GitLab repository with Odoo modules can be used as long as:
- The repository is publicly accessible
- The repository has at least one tag/release

## How It Works

### Clone Process

1. **Validation**: The module validates the repository URL and fetches available tags using `git ls-remote`
2. **Tag Selection**: User selects a specific tag through a wizard
3. **Cloning**: The module clones only the selected tag using `git clone --depth 1 --branch <tag>`
4. **Permissions**: Ownership is set to the Odoo user using `chown`
5. **Module List Update**: Odoo's module list is refreshed using `update_list()`
6. **Restart** (optional): Odoo is restarted by sending SIGHUP signal

### Directory Structure

Cloned modules are named with the tag suffix to avoid conflicts:

```
/mnt/extra-addons/
├── module_name_15.0.1.0.0/
├── module_name_16.0.1.0.0/
└── another_module_14.0.2.1.5/
```

## Security

- Only users with **Administration / Settings** access can manage repositories
- All users can view repositories (read-only)
- Git operations are executed with proper timeout limits
- Input validation prevents injection attacks

## Troubleshooting

### "Git command not found"
Install git on your server:
```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL
sudo yum install git
```

### "Permission denied" when cloning
Ensure the Odoo user has write permissions:
```bash
sudo chown -R odoo:odoo /mnt/extra-addons
```

### "Cannot restart Odoo automatically"
This is normal in some deployment scenarios. Simply restart Odoo manually:
```bash
sudo systemctl restart odoo
```

### Tags not showing
Ensure:
- The repository URL is correct
- The repository is public
- The repository has at least one tag/release

## Development

### Module Structure

```
odoo_git_installer/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── git_repository.py
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── git_repository_views.xml
│   └── menu_views.xml
├── static/
│   └── description/
│       ├── icon.png
│       └── index.html
└── README.md
```

### Models

- **git.repository**: Main model for repository sources
- **git.installed.module**: Tracks installed modules
- **git.clone.wizard**: Wizard for tag selection and cloning

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [Create an issue](https://github.com/trixocom/odoo_git_installer/issues)
- **Email**: hectorquiroz@trixocom.com

## License

This module is licensed under the LGPL-3 License. See [LICENSE](LICENSE) file for details.

## Credits

### Authors
- TrixoCom

### Contributors
- Hector Quiroz <hectorquiroz@trixocom.com>

## Changelog

### Version 18.0.1.0.0 (2025-10-01)
- Initial release
- Support for GitHub and GitLab
- Tag selection and cloning
- Automatic module list update
- Automatic Odoo restart
- Permission management
- Installation history tracking