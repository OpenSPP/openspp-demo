# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP OpenCRVS Demo",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-demo",
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
    ],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/import_view.xml",
        "views/configuration_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
