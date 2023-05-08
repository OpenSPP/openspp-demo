import json
import logging

import requests

from odoo import _, fields, models

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

                        message = "Successfully fetched %s, %s with birthdate: %s." % (
                            rec.family_name,
                            rec.given_name,
                            rec.birthdate,
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
