# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenG2P Connect Demo",
    "category": "OpenG2P",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-demo",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_base_demo",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "g2p_programs",
        "g2p_bank",
        "spp_custom_field",
        "g2p_entitlement_cash",
        # "spp_dashboard",
        # "spp_idpass",
        # "spp_helpdesk",
        "spp_area",
        "theme_openspp",
        # "spp_photo",
        # "spp_pos",
        # "spp_sms",
        "queue_job",
    ],
    "external_dependencies": {"python": ["faker"]},
    "data": [
        "security/ir.model.access.csv",
        "views/generate_data_view.xml",
        "views/groups_view.xml",
        "views/individuals_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
