import json
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomAddChildMember(models.Model):
    _inherit = "spp.opencrvs.cr.add.child"

    def _default_config_id(self):
        config_id = None
        config = self.env["spp.opencrvs.config"].search([("is_active", "=", True)])
        if config:
            config_id = config[0].id

        return config_id

    crvs_config_id = fields.Many2one(
        "spp.opencrvs.config",
        "OpenCRVS Config",
        required=True,
        default=_default_config_id,
    )

    brn = fields.Char("BRN")
    crvs_qr = fields.Text("Scanned QR")
    crvs_record_id = fields.Char("Record ID")

    certificate_details = fields.Text("Certificate Document")

    @api.onchange('certificate_details')
    def onchange_certificate_details(self):
        if self.certificate_details:
            try:
                details = json.loads(self.certificate_details)
            except json.decoder.JSONDecodeError as e:
                details = None
                _logger.error(e)
            if details:
                vals = {
                    "crvs_qr": details["qrcode"].strip()
                }
            self.update(vals)
        else:
            raise UserError(
                _("There are no data captured from the QR Code scanner.")
            )

    def fetch_data_from_opencrvs(self):
        for rec in self:
            if rec.crvs_config_id:
                data = {}
                rec.crvs_config_id.on_authenticate()
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "bearer {}".format(rec.crvs_config_id.auth_token),
                }
                if not rec.crvs_qr and not rec.crvs_record_id:
                    data = {
                        "operationName": "searchEvents",
                        "query": "query searchEvents($advancedSearchParameters: AdvancedSearchParametersInput!, $sort: String, $count: Int, $skip: Int) {\nsearchEvents(\n  advancedSearchParameters: $advancedSearchParameters\n  sort: $sort\n  count: $count\n  skip: $skip\n) {\n  totalItems\n  results {\n    id\n    type\n    registration {\n      status\n      contactNumber\n      trackingId\n      registrationNumber\n      registeredLocationId\n      duplicates\n      assignment {\n        userId\n        firstName\n        lastName\n        officeName\n        __typename\n      }\n      createdAt\n      modifiedAt\n      __typename\n    }\n    operationHistories {\n      operationType\n      operatedOn\n      operatorRole\n      operatorName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      operatorOfficeName\n      operatorOfficeAlias\n      notificationFacilityName\n      notificationFacilityAlias\n      rejectReason\n      rejectComment\n      __typename\n    }\n    ... on BirthEventSearchSet {\n      dateOfBirth\n      placeOfBirth    childGender   mothersFirstName         mothersLastName        fathersFirstName         fathersLastName        motherIdentifier       fatherIdentifier childName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    ... on DeathEventSearchSet {\n      dateOfDeath\n      deceasedName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}}",  # noqa: B950
                        "variables": {
                            "advancedSearchParameters": {"registrationNumber": rec.brn}
                        },
                    }

                else:
                    stripped_crvs_qr = rec.crvs_qr
                    rec.crvs_qr = stripped_crvs_qr.strip()

                    if rec.crvs_qr and not rec.crvs_record_id:
                        crvs_qr = rec.crvs_qr.rsplit("/", 1)[-1]
                        rec.crvs_record_id = crvs_qr

                    recordid = rec.crvs_record_id
                    data = {
                        "operationName": "searchEvents",
                        "query": "query searchEvents($advancedSearchParameters: AdvancedSearchParametersInput!, $sort: String, $count: Int, $skip: Int) {\nsearchEvents(\n  advancedSearchParameters: $advancedSearchParameters\n  sort: $sort\n  count: $count\n  skip: $skip\n) {\n  totalItems\n  results {\n    id\n    type\n    registration {\n      status\n      contactNumber\n      trackingId\n      registrationNumber\n      registeredLocationId\n      duplicates\n      assignment {\n        userId\n        firstName\n        lastName\n        officeName\n        __typename\n      }\n      createdAt\n      modifiedAt\n      __typename\n    }\n    operationHistories {\n      operationType\n      operatedOn\n      operatorRole\n      operatorName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      operatorOfficeName\n      operatorOfficeAlias\n      notificationFacilityName\n      notificationFacilityAlias\n      rejectReason\n      rejectComment\n      __typename\n    }\n    ... on BirthEventSearchSet {\n      dateOfBirth\n    placeOfBirth    childGender   mothersFirstName         mothersLastName        fathersFirstName         fathersLastName        motherIdentifier       fatherIdentifier   childName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    ... on DeathEventSearchSet {\n      dateOfDeath\n      deceasedName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}}",  # noqa: B950
                        "variables": {
                            "advancedSearchParameters": {"recordId": recordid}
                        },
                    }

                if data:
                    response = requests.post(
                        rec.crvs_config_id.domain,
                        data=json.dumps(data),
                        headers=headers,
                    )
                    if response.status_code == 200:
                        response_json = response.json()
                        response_json = response_json["data"]["searchEvents"][
                            "results"
                        ][0]

                        _logger.info(response_json)
                        rec.birthdate = response_json["dateOfBirth"]
                        rec.given_name = response_json["childName"][0]["firstNames"]
                        rec.family_name = response_json["childName"][0]["familyName"]
                        gender = response_json["childGender"]
                        if gender:
                            rec.gender = gender.title()
                        birth_place = response_json["placeOfBirth"]
                        if birth_place:
                            rec.birth_place = birth_place

                        mother_first_name = response_json["mothersFirstName"]
                        mother_last_name = response_json["mothersLastName"]

                        father_first_name = response_json["fathersFirstName"]
                        father_last_name = response_json["fathersLastName"]

                        parent_exists = self.check_if_parent_exists(
                            mother_first_name,
                            mother_last_name,
                            father_first_name,
                            father_last_name,
                        )
                        if parent_exists:
                            rec.action_submit()
                            user_validator = self.env.ref(
                                "spp_opencrvs_demo.demo_access_cr_validator_both"
                            )
                            stage = 1
                            while stage <= 2:
                                rec.with_user(user_validator.id).action_validate()
                                stage += 1

                        message = (
                                "Successfully fetched %s, %s with birthdate: %s."
                                % (
                                    rec.family_name,
                                    rec.given_name,
                                    rec.birthdate,
                                )
                            )
                        if rec.state == "applied":
                            message = (
                                "Successfully fetched %s, %s with birthdate: %s. and applied"
                                % (
                                    rec.family_name,
                                    rec.given_name,
                                    rec.birthdate,
                                )
                            )
                        kind = "success"
                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "title": _("OpenCRVS"),
                                "message": message,
                                "sticky": False,
                                "type": kind,
                                "next": {
                                    "type": "ir.actions.act_window_close",
                                },
                            },
                        }

    def check_if_parent_exists(
        self, mother_first, mother_last, father_first, father_last
    ):
        exists = False
        if mother_first and mother_last:
            mother_exists = self.check_if_individual_exists(mother_first, mother_last)
            if mother_exists:
                _logger.info("Mother EXISTS AS PARTNER")
                mother_group_exists = self.check_if_membership_exists(mother_exists)
                if mother_group_exists:
                    exists = True
                    _logger.info("Mother EXISTS AS MEMBER")

        if father_first and father_last:
            father_exists = self.check_if_individual_exists(father_first, father_last)
            if father_exists:
                _logger.info("Father EXISTS AS PARTNER")
                father_exists = self.check_if_membership_exists(father_exists)
                if father_exists:
                    exists = True
                    _logger.info("Father EXISTS AS MEMBER")

        return exists

    def check_if_individual_exists(self, individual_first, individual_last):
        individual_id = self.env["res.partner"].search(
            [
                ("given_name", "=", individual_first),
                ("family_name", "=", individual_last),
            ]
        )
        _logger.info("Individual %s", individual_id)
        _logger.info("Individual FIRST NAME: %s", individual_first)
        _logger.info("Individual LAST NAME: %s", individual_last)

        return individual_id

    def check_if_membership_exists(self, member):
        return self.env["g2p.group.membership"].search(
            [("group", "=", self.registrant_id.id), ("individual", "=", member.id)]
        )
