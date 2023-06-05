from odoo.tests import TransactionCase


class TestCRVSAddChild(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_hh = self.env["res.partner"].create(
            {
                "name": "BARASA",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self._test_applicant = self.env["res.partner"].create(
            {
                "name": "NJERI, WAMBUI",
                "family_name": "Njeri",
                "given_name": "Wambui",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )

        # Add _test_applicant to _test_hh

        self.env["g2p.group.membership"].create(
            {"group": self._test_hh.id, "individual": self._test_applicant.id}
        )

        self._test_member = self.env["res.partner"].create(
            {
                "name": "NJERI, BARASA",
                "family_name": "Njeri",
                "given_name": "Barasa",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716912",
            }
        )

        # Add _test_member to _test_hh

        self.env["g2p.group.membership"].create(
            {"group": self._test_hh.id, "individual": self._test_member.id}
        )

        self._opencrvs_config = self.env["spp.opencrvs.config"].create(
            {
                "name": "OpenCRVS Test",
                "domain": "https://gateway.farajaland-demo.opencrvs.org/graphql",
                "client_id": "3408c5f0-e829-4488-a26c-72c72dc228f8",
                "client_secret": "d2b1d4b1-638a-452b-a6db-fd5b5598523a",
                "auth_token_url": "https://auth.farajaland-demo.opencrvs.org/authenticateSystemClient",
                "is_active": True,
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

    def test_01_fetch_from_opencrvs(self):
        change_request = self.create_mock_cr_with_reference()
        request_type = change_request.request_type_ref_id

        qr = "https://register.farajaland-demo.opencrvs.org/verify-certificate/a399e839-82a9-4f1c-b0b5-81fffcf2efd2"

        request_type.write(
            {
                "crvs_qr": qr,
                "crvs_config_id": self._opencrvs_config.id,
            }
        )
        request_type.fetch_data_from_opencrvs()

        self.assertEqual(
            request_type.crvs_record_id, "a399e839-82a9-4f1c-b0b5-81fffcf2efd2"
        )
        self.assertEqual(request_type.state, "applied")
