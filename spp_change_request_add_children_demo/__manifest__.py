{
    "name": "CR Demo: Add Child/Member",
    "category": "OpenSPP",
    "version": "15.0.1.0.14",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-demo",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_change_request",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_service_points",
    ],
    "data": [
        "security/change_request_security.xml",
        "security/ir.model.access.csv",
        "data/dms.xml",
        "data/change_request_stage.xml",
        "data/change_request_sequence.xml",
        "data/id_type.xml",
        "views/change_request_add_children_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
