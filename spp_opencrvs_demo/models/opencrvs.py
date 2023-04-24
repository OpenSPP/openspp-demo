# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPOpenCRVSImport(models.Model):
    _name = "spp.opencrvs.import"

    def _default_config_id(self):
        config_id = None
        config = self.env["spp.opencrvs.config"].search([("is_active", "=", True)])
        if config:
            config_id = config[0].id

        return config_id

    name = fields.Char()
    import_by = fields.Selection(
        [("BRN", "BRN"), ("All", "All")], default="BRN", required=True
    )
    config_id = fields.Many2one(
        "spp.opencrvs.config", "Config", required=True, default=_default_config_id
    )

    # OpenCRVS Response Fields
    response = fields.Text()
    date_of_birth = fields.Date()
    first_name = fields.Char()
    family_name = fields.Char()
    state = fields.Selection(
        [
            ("Draft", "Draft"),
            ("Fetched", "Fetched"),
            ("Imported", "Imported"),
            ("Cancelled", "Cancelled"),
        ],
        default="Draft",
    )

    def fetch_data_opencrvs(self):
        for rec in self:
            if rec.config_id:
                if rec.import_by == "BRN" and rec.name:
                    data = {
                        "operationName": "searchEvents",
                        "query": "query searchEvents($advancedSearchParameters: AdvancedSearchParametersInput!, $sort: String, $count: Int, $skip: Int) {\nsearchEvents(\n  advancedSearchParameters: $advancedSearchParameters\n  sort: $sort\n  count: $count\n  skip: $skip\n) {\n  totalItems\n  results {\n    id\n    type\n    registration {\n      status\n      contactNumber\n      trackingId\n      registrationNumber\n      registeredLocationId\n      duplicates\n      assignment {\n        userId\n        firstName\n        lastName\n        officeName\n        __typename\n      }\n      createdAt\n      modifiedAt\n      __typename\n    }\n    operationHistories {\n      operationType\n      operatedOn\n      operatorRole\n      operatorName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      operatorOfficeName\n      operatorOfficeAlias\n      notificationFacilityName\n      notificationFacilityAlias\n      rejectReason\n      rejectComment\n      __typename\n    }\n    ... on BirthEventSearchSet {\n      dateOfBirth\n      childName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    ... on DeathEventSearchSet {\n      dateOfDeath\n      deceasedName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}}",  # noqa: B950
                        "variables": {
                            "advancedSearchParameters": {"registrationNumber": rec.name}
                        },
                    }
                    rec.config_id.on_authenticate()
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": "bearer {}".format(rec.config_id.auth_token),
                    }
                    response = requests.post(
                        rec.config_id.domain,
                        data=json.dumps(data),
                        headers=headers,
                    )
                    _logger.info(response.json())
                    if response.status_code == 200:
                        response_json = response.json()
                        response_json = response_json["data"]["searchEvents"][
                            "results"
                        ][0]
                        rec.response = response_json
                        rec.date_of_birth = response_json["dateOfBirth"]
                        rec.first_name = response_json["childName"][0]["firstNames"]
                        rec.family_name = response_json["childName"][0]["familyName"]
                        rec.state = "Fetched"

    def import_data(self):
        for rec in self:
            name = "{}, {}".format(rec.family_name, rec.first_name).upper()
            vals = {
                "is_registrant": True,
                "is_group": False,
                "given_name": rec.first_name,
                "family_name": rec.family_name,
                "birthdate": rec.date_of_birth,
                "name": name,
            }
            self.env["res.partner"].create(vals)
            rec.state = "Imported"

    def cancel_import(self):
        for rec in self:
            rec.state = "Cancelled"


class SPPOpenCRVSConfig(models.Model):
    _name = "spp.opencrvs.config"

    name = fields.Char("Config Name", required=True)
    domain = fields.Char(required=True)
    client_id = fields.Char("Client ID", required=True)
    client_secret = fields.Char(required=True)
    auth_token_url = fields.Char("Auth Token URL", required=True)
    auth_token = fields.Char()
    is_active = fields.Boolean("Active")

    def on_authenticate(self):
        for rec in self:
            if rec.auth_token_url and rec.client_id and rec.client_secret:
                data = {"client_id": rec.client_id, "client_secret": rec.client_secret}
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }

                response = requests.post(
                    rec.auth_token_url,
                    data=json.dumps(data),
                    headers=headers,
                )
                if response.status_code == 200:
                    response_json = response.json()
                    rec.auth_token = response_json["token"]
        return
