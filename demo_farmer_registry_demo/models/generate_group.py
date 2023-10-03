# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import hashlib
import logging
import math
import random

from dateutil.relativedelta import relativedelta
from faker import Faker

from odoo import api, models

_logger = logging.getLogger(__name__)


class G2PGenerateData(models.Model):
    _inherit = "spp.generate.data"

    def generate_sample_data(self):
        batches = math.ceil(self.num_groups / 1000)
        for _i in range(0, batches):
            self.with_delay()._generate_sample_data(res_id=self.id)

    @api.model
    def _generate_sample_data(self, **kwargs):
        """
        Generate sample data for testing
        Returns:

        """
        res_id = kwargs.get("res_id")
        res = self.browse(res_id)
        locales = [
            "cs_CZ",
            "en_US",
            "de_CH",
            "ar_AA",
            "de_DE",
            "en_GB",
            "en_IE",
            "en_TH",
            "es_ES",
            "es_MX",
            "fr_FR",
            "hi_IN",
            "hr_HR",
            "it_IT",
            "zh_CN",
        ]
        fake = Faker(locales)

        crop_grown_choices = [
            "rice",
            "corn",
            "wheat",
            "barley",
            "other",
        ]

        use_of_certified_seeds_choices = [
            "yes",
            "no",
        ]

        fertilizer_usage_choices = [
            "organic",
            "inorganic",
            "none",
        ]

        soil_type_choices = [
            "loamy",
            "sandy",
            "clayey",
            "silty",
            "peaty",
            "chalky",
        ]

        irrigation_availability_choices = [
            "yes",
            "no",
        ]

        source_of_irrigation_choices = [
            "river",
            "well",
            "rain-fed",
            "other",
        ]

        land_ownership_choices = [
            "owned",
            "leased",
            "shared",
        ]

        land_usage_choices = [
            "rotational_cropping",
            "permanent_crops",
            "fallow",
        ]

        types_of_machinery_owned_choices = [
            "tractors",
            "plows",
            "harvesters",
            "other",
        ]

        machinery_usage_choices = [
            "owned",
            "rented",
            "shared",
        ]

        insurance_coverage_choices = [
            "crop_insurance",
            "livestock_insurance",
            "equipment_insurance",
            "none",
        ]

        use_of_organic_farming_practices_choices = [
            "yes",
            "no",
        ]

        water_conservation_practices_choices = [
            "yes",
            "no",
        ]

        soil_conservation_practices_choices = [
            "yes",
            "no",
        ]

        use_of_digital_tools_choices = [
            "yes",
            "no",
        ]

        use_of_modern_farming_techniques_choices = [
            "yes",
            "no",
        ]

        # Get available gender field selections
        sex_choices = self.env["res.partner"]._fields["gender"].selection
        sex_choices = [sex[0] for sex in sex_choices]
        sex_choice_range = sex_choices * 50

        age_group_range = ["A", "C"] * 2 + ["E"]
        group_size_range = (
            list(range(1, 2)) * 2 + list(range(3, 5)) * 4 + list(range(6, 8))
        )

        group_membership_kind_head_id = self.env.ref(
            "g2p_registry_membership.group_membership_kind_head"
        ).id
        group_kind_household_id = self.env.ref(
            "g2p_registry_group.group_kind_household"
        ).id
        group_kind_family_id = self.env.ref("g2p_registry_group.group_kind_family").id

        num_groups = min(res.num_groups, 1000)
        for i in range(0, num_groups):
            locale = random.choice(locales)
            group_size = random.choice(group_size_range)
            last_name = fake[locale].last_name()

            registration_date = (
                fake[locale]
                .date_between_dates(
                    date_start=datetime.datetime.now() - relativedelta(weeks=4),
                    date_end=datetime.datetime.now(),
                )
                .isoformat()
            )

            head = res._generate_individual_data(
                fake[locale],
                last_name,
                sex_choice_range,
                age_group_range,
                registration_date,
            )

            head["is_head"] = True

            group_id = (
                "demo." + hashlib.md5(f"{last_name} {i}".encode("UTF-8")).hexdigest()
            )

            group_kind = random.choice([group_kind_household_id, group_kind_family_id])

            # random.choice(locales)
            group = {
                "id": group_id,
                "name": last_name,
                "is_group": True,
                "is_registrant": True,
                "registration_date": registration_date,
                "kind": group_kind,
                "grp_crop_grown": random.choice(crop_grown_choices),
                "grp_crop_grown_other": "Bread",
                "grp_arable_land_owned": 1.0,
                "grp_arable_land_farmed": 1.0,
                "grp_use_of_certified_seeds": random.choice(
                    use_of_certified_seeds_choices
                ),
                "grp_fertilizer_usage": random.choice(fertilizer_usage_choices),
                "grp_soil_type": random.choice(soil_type_choices),
                "grp_irrigation_availability": random.choice(
                    irrigation_availability_choices
                ),
                "grp_source_of_irrigation": random.choice(source_of_irrigation_choices),
                "grp_source_of_irrigation_other": "Water",
                "grp_land_ownership": random.choice(land_ownership_choices),
                "grp_land_usage": random.choice(land_usage_choices),
                "grp_types_of_machinery_owned": random.choice(
                    types_of_machinery_owned_choices
                ),
                "grp_types_of_machinery_owned_other": "SUV",
                "grp_machinery_usage": random.choice(machinery_usage_choices),
                "grp_family_labour": 5,
                "grp_hired_labour": 5,
                "grp_government_subsidies_received": 1.0,
                "grp_loans_and_credits": 1.0,
                "grp_insurance_coverage": random.choice(insurance_coverage_choices),
                "grp_use_of_organic_farming_practices": random.choice(
                    use_of_organic_farming_practices_choices
                ),
                "grp_water_conservation_practices": random.choice(
                    water_conservation_practices_choices
                ),
                "grp_soil_conservation_practices": random.choice(
                    soil_conservation_practices_choices
                ),
                "grp_agricultural_or_environmental_certifications": "Agricultural",
                "grp_use_of_digital_tools": random.choice(use_of_digital_tools_choices),
                "grp_use_of_modern_farming_techniques": random.choice(
                    use_of_modern_farming_techniques_choices
                ),
            }

            create_group_id = self.env["res.partner"].create(group)

            head["id"] = f"{group_id}-0"
            members = [head]

            for i in range(group_size - 1):
                data = res._generate_individual_data(
                    fake[locale],
                    last_name,
                    sex_choice_range,
                    age_group_range,
                    registration_date,
                )

                data["id"] = f"{group_id}-{i+1}"
                members.append(data)

            # add this on membership
            if random.randint(0, 2) == 0:
                members[0]["is_principal_recipient"] = True
            else:
                members[random.randint(0, group_size - 1)][
                    "is_principal_recipient"
                ] = True

            for member in members:
                is_head = True if (member and member.get("is_head")) else False
                is_principal_recipient = (
                    True if (member and member.get("is_principal_recipient")) else False
                )

                if is_head:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [
                                (
                                    4,
                                    group_membership_kind_head_id,
                                )
                            ],
                        }
                    )

                elif is_principal_recipient:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [],
                        }
                    )

                else:
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                        }
                    )

            if res.state == "draft":
                res.update({"state": "generate"})

        msg = "Task Queue called task: model [%s] and method [%s]." % (
            self._name,
            "_generate_sample_data",
        )
        _logger.info(msg)
        return {"result": msg, "res_model": self._name, "res_ids": [res_id]}
