import json
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomAddChildMember(models.Model):
    _inherit = "spp.change.request.add.child"

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

    def fetch_data_from_opencrvs(self):
        for rec in self:
            if rec.crvs_config_id:
                data = {
                    "operationName": "searchEvents",
                    "query": "query searchEvents($advancedSearchParameters: AdvancedSearchParametersInput!, $sort: String, $count: Int, $skip: Int) {\nsearchEvents(\n  advancedSearchParameters: $advancedSearchParameters\n  sort: $sort\n  count: $count\n  skip: $skip\n) {\n  totalItems\n  results {\n    id\n    type\n    registration {\n      status\n      contactNumber\n      trackingId\n      registrationNumber\n      registeredLocationId\n      duplicates\n      assignment {\n        userId\n        firstName\n        lastName\n        officeName\n        __typename\n      }\n      createdAt\n      modifiedAt\n      __typename\n    }\n    operationHistories {\n      operationType\n      operatedOn\n      operatorRole\n      operatorName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      operatorOfficeName\n      operatorOfficeAlias\n      notificationFacilityName\n      notificationFacilityAlias\n      rejectReason\n      rejectComment\n      __typename\n    }\n    ... on BirthEventSearchSet {\n      dateOfBirth\n      childName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    ... on DeathEventSearchSet {\n      dateOfDeath\n      deceasedName {\n        firstNames\n        familyName\n        use\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}}",  # noqa: B950
                    "variables": {
                        "advancedSearchParameters": {"registrationNumber": rec.brn}
                    },
                }
                rec.crvs_config_id.on_authenticate()
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "bearer {}".format(rec.crvs_config_id.auth_token),
                }
                response = requests.post(
                    rec.crvs_config_id.domain,
                    data=json.dumps(data),
                    headers=headers,
                )
                if response.status_code == 200:
                    response_json = response.json()
                    response_json = response_json["data"]["searchEvents"]["results"][0]

                    _logger.info(response_json)
                    rec.birthdate = response_json["dateOfBirth"]
                    rec.given_name = response_json["childName"][0]["firstNames"]
                    rec.family_name = response_json["childName"][0]["familyName"]
