# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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
    group_id = fields.Many2one(
        "res.partner",
        "Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )
    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_id_domain = fields.Char(
        compute="_compute_applicant_id_domain",
        readonly=True,
        store=False,
    )
    applicant_phone = fields.Char()
    state = fields.Selection(
        [
            ("Draft", "Draft"),
            ("Fetched", "Fetched"),
            ("Imported", "Imported"),
            ("Cancelled", "Cancelled"),
        ],
        default="Draft",
    )
    cr_id = fields.Many2one("spp.change.request")

    @api.depends("group_id")
    def _compute_applicant_id_domain(self):
        """
        Called whenever registrant_id field is changed

        This method is used for dynamic domain of applicant_id field
        """
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.group_id:
                # TODO: Use the is_ended field to filter
                # Get only the members with non-expired membership
                group_memberships = rec.group_id.group_membership_ids.filtered(
                    lambda a: not a.ended_date or a.ended_date > fields.Datetime.now()
                )
                if group_memberships:
                    group_membership_ids = group_memberships.mapped("individual.id")
                    domain = [("id", "in", group_membership_ids)]
            rec.applicant_id_domain = json.dumps(domain)

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
            if rec.group_id and rec.applicant_id and rec.applicant_phone:
                cr_vals = {
                    "request_type": "spp.opencrvs.cr.add.child",
                    "applicant_id": rec.applicant_id.id,
                    "registrant_id": rec.group_id.id,
                    "applicant_phone": rec.applicant_phone,
                }

                cr_id = self.env["spp.change.request"].create(cr_vals)
                cr_id.create_request_detail()
                rec.cr_id = cr_id.id
                cr_add_child_vals = {
                    "given_name": rec.first_name or None,
                    "family_name": rec.family_name or None,
                    "birthdate": rec.date_of_birth or None,
                }
                cr_id.request_type_ref_id.update(cr_add_child_vals)
                rec.state = "Imported"
            else:
                raise UserError(
                    _("Group, Applicant and Applicant Phone Number are required")
                )

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
