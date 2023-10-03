import json

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    grp_crop_grown = fields.Selection(
        [
            ("rice", "Rice"),
            ("corn", "Corn"),
            ("wheat", "Wheat"),
            ("barley", "Barley"),
            ("other", "Other"),
        ],
        string="Crop Grown",
        allow_filter=True,
    )
    grp_crop_grown_other = fields.Char(string="Specify Other Crop", allow_filter=True)
    grp_arable_land_owned = fields.Float(
        string="Arable Hectares of Land Owned", allow_filter=True
    )
    grp_arable_land_farmed = fields.Float(
        string="Arable Hectares of Land Farmed", allow_filter=True
    )
    grp_use_of_certified_seeds = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Use of Certified Seeds",
        allow_filter=True,
    )
    grp_fertilizer_usage = fields.Selection(
        [
            ("organic", "Organic"),
            ("inorganic", "Inorganic"),
            ("none", "None"),
        ],
        string="Fertilizer Usage",
        allow_filter=True,
    )
    grp_soil_type = fields.Selection(
        [
            ("loamy", "Loamy"),
            ("sandy", "Sandy"),
            ("clayey", "Clayey"),
            ("silty", "Silty"),
            ("peaty", "Peaty"),
            ("chalky", "Chalky"),
        ],
        string="Soil Type",
        allow_filter=True,
    )
    grp_irrigation_availability = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Irrigation Availability",
        allow_filter=True,
    )
    grp_source_of_irrigation = fields.Selection(
        [
            ("river", "River"),
            ("well", "Well"),
            ("rain-fed", "Rain-fed"),
            ("other", "Other"),
        ],
        string="Source of Irrigation",
        allow_filter=True,
    )
    grp_source_of_irrigation_other = fields.Char(
        string="Specify Other Source of Irrigation",
        allow_filter=True,
    )

    grp_land_ownership = fields.Selection(
        [
            ("owned", "Owned"),
            ("leased", "Leased"),
            ("shared", "Shared"),
        ],
        string="Land Ownership",
        allow_filter=True,
    )

    grp_land_usage = fields.Selection(
        [
            ("rotational_cropping", "Rotational Cropping"),
            ("permanent_crops", "Permanent Crops"),
            ("fallow", "Fallow"),
        ],
        string="Land Usage",
        allow_filter=True,
    )

    grp_types_of_machinery_owned = fields.Selection(
        [
            ("tractors", "Tractors"),
            ("plows", "Plows"),
            ("harvesters", "Harvesters"),
            ("other", "Other"),
        ],
        string="Types of Machinery Owned",
        allow_filter=True,
    )
    grp_types_of_machinery_owned_other = fields.Char(string="Specify Other Machinery")

    grp_machinery_usage = fields.Selection(
        [
            ("owned", "Owned"),
            ("rented", "Rented"),
            ("shared", "Shared"),
        ],
        string="Machinery Usage",
        allow_filter=True,
    )

    grp_family_labour = fields.Integer(string="Family Labour", allow_filter=True)

    grp_hired_labour = fields.Integer(string="Hired Labour", allow_filter=True)

    grp_government_subsidies_received = fields.Float(
        string="Government Subsidies Received",
        allow_filter=True,
    )

    grp_loans_and_credits = fields.Float(string="Loans and Credits", allow_filter=True)

    grp_insurance_coverage = fields.Selection(
        [
            ("crop_insurance", "Crop Insurance"),
            ("livestock_insurance", "Livestock Insurance"),
            ("equipment_insurance", "Equipment Insurance"),
            ("none", "None"),
        ],
        string="Insurance Coverage",
        allow_filter=True,
    )

    grp_use_of_organic_farming_practices = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Use of Organic Farming Practices",
        allow_filter=True,
    )

    grp_water_conservation_practices = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Water Conservation Practices",
        allow_filter=True,
    )

    grp_soil_conservation_practices = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Soil Conservation Practices",
        allow_filter=True,
    )

    grp_agricultural_or_environmental_certifications = fields.Char(
        string="Agricultural or Environmental Certifications Obtained",
        allow_filter=True,
    )

    grp_use_of_digital_tools = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Use of Digital Tools",
        allow_filter=True,
    )

    grp_use_of_modern_farming_techniques = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Use of Modern Farming Techniques",
        allow_filter=True,
    )

    # Geolocation
    longitude = fields.Float(digits=(16, 5), allow_filter=True)
    latitude = fields.Float(digits=(16, 5), allow_filter=True)

    geolocation_json = fields.Char(
        compute="_compute_geolocation_json",
        inverse="_inverse_geolocation_json",
        allow_filter=True,
    )

    @api.depends("latitude", "longitude")
    def _compute_geolocation_json(self):
        for rec in self:
            rec.geolocation_json = json.dumps(
                {"lat": round(rec.latitude, 5), "lng": round(rec.longitude, 5)},
                ensure_ascii=False,
            )

    def _inverse_geolocation_json(self):
        for rec in self:
            geolocation = json.loads(rec.geolocation_json)
            if rec.latitude != geolocation["lat"]:
                rec.latitude = geolocation["lat"]
            if rec.longitude != geolocation["lng"]:
                rec.longitude = geolocation["lng"]

    @api.model
    def _geo_localize(self, street="", zip_code="", city="", state="", country=""):
        geo_obj = self.env["base.geocoder"]
        search = geo_obj.geo_query_address(
            street=street, zip=zip_code, city=city, state=state, country=country
        )
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        for rec in self.with_context(lang="en_US"):
            street = "%s, %s" % (rec.street, rec.street2) if rec.street2 else rec.street
            result = self._geo_localize(
                street=street,
                zip_code=rec.zip,
                city=rec.city,
                state=rec.state_id.name,
                country=rec.country_id.name,
            )
            if result:
                rec.write({"latitude": result[0], "longitude": result[1]})
        return True
