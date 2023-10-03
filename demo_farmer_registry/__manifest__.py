# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
{
    "name": "Demo Group Registry: Farmer ",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-demo",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "g2p_registry_base",
        "g2p_registry_group",
        "g2p_registry_individual",
        "base_geolocalize",
    ],
    "data": [
        "data/group_kinds.xml",
        "template/template.xml",
        "views/group_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/demo_farmer_registry/static/src/scss/map_field_widget.scss",
            "/demo_farmer_registry/static/src/js/map_field_widget.js",
        ],
        "web.assets_qweb": [
            "/demo_farmer_registry/static/src/xml/map_field_widget.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
