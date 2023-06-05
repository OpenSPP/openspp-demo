from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestCRAddChild(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_hh = self.env["res.partner"].create(
            {
                "name": "Renaud",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self._test_applicant = self.env["res.partner"].create(
            {
                "name": "Rufino Renaud",
                "family_name": "Renaud",
                "given_name": "Rufino",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )
        # Add _test_applicant to _test_hh

        self._test_group_membership = self.env["g2p.group.membership"].create(
            {"group": self._test_hh.id, "individual": self._test_applicant.id}
        )

        self._test_user_validator = self.env["res.users"].create(
            {
                "name": "CR Validator Local and HQ",
                "login": "cr_validator_both",
                "email": "cr_validator_both@yourorg.example.com",
                "password": "atMnSaWYymYD",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref(
                                "spp_change_request.group_spp_change_request_hq_validator"
                            ).id,
                            self.env.ref(
                                "spp_change_request.group_spp_change_request_local_validator"
                            ).id,
                            self.env.ref(
                                "spp_change_request.group_spp_change_request_validator"
                            ).id,
                            self.env.ref("g2p_registry_base.group_g2p_admin").id,
                        ],
                    )
                ],
            }
        )

    def create_mock_cr(self):
        vals = {
            "request_type": "spp.opencrvs.cr.add.child",
            "registrant_id": self._test_hh.id,
            "applicant_id": self._test_applicant.id,
            "applicant_phone": self._test_applicant.phone,
        }
        change_request = self.env["spp.change.request"].create(vals)

        return change_request

    def create_mock_cr_with_reference(self):
        change_request = self.create_mock_cr()
        change_request.create_request_detail()
        return change_request

    def test_01_check_full_name(self):
        change_request = self.create_mock_cr_with_reference()
        request_type = change_request.request_type_ref_id

        given_name = "Jordan"
        family_name = "Renauld"

        full_name = f"{given_name or ''} {family_name or ''}"

        request_type.write(
            {
                "given_name": given_name,
                "family_name": family_name,
            }
        )

        self.assertEqual(request_type.full_name, full_name)

    def test_02_validate_without_data(self):
        change_request = self.create_mock_cr_with_reference()
        request_type = change_request.request_type_ref_id

        request_type.write(
            {
                "given_name": False,
                "family_name": False,
            }
        )

        with self.assertRaises(ValidationError):
            request_type.validate_data()

    def test_03_validate_data(self):
        change_request = self.create_mock_cr_with_reference()
        request_type = change_request.request_type_ref_id

        request_type.write(
            {
                "given_name": "Jordan",
                "family_name": "Renauld",
                "birthdate": fields.Date.today(),
                "gender": "Male",
            }
        )

        request_type.action_submit()
        change_request.assign_to_user(self._test_user_validator)
        stage = 1
        while stage <= 2:
            request_type.with_user(self._test_user_validator).action_validate()
            stage += 1

        self.assertEqual(request_type.state, "applied")
