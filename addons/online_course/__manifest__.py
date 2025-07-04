{
    "name": "Online Course",
    "summary": "Addon for managing online courses.",
    "author": "Damián Čopík",
    "license": "AGPL-3",
    "version": "18.0.0.0.0",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        # Core Modules
        "base",
    ],
    "data": [
        # Categories
        "security/ir.module.category.xml",
        # Data
        "data/res_groups.xml",
        # Views
        "views/course.xml",
        "views/res_user.xml",
        # Security
        "security/ir.model.access.csv",
        "security/ir.rule.xml",
        # Actions
        "views/actions.xml",
        # Menu Items
        "views/menuitems.xml",
    ],
    "external_dependencies": {},
    "qweb": [],
    "images": [],
    "demo": [],
}
