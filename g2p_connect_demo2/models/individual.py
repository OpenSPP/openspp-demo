# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PIndividual(models.Model):
    _inherit = "res.partner"

    # Demo 1
    z_cst_indv_disability_level = fields.Integer("Disability level")  # 0-100
    z_cst_indv_receive_government_benefits = fields.Boolean(
        "Receive government benefits"
    )
    z_cst_indv_locust_aug_2022_lost_livestock = fields.Boolean(
        "Lost significant livestock during Locust Infestation Aug 2022"
    )
    z_cst_indv_locust_aug_2022_lost_primary_source_income = fields.Boolean(
        "Lost primary source income during Locust Infestation Aug 2022"
    )

    # Demo 2
    z_cst_indv_has_birth_certificate = fields.Boolean("Has birth certificate")
    z_cst_indv_pregnancy_start_date = fields.Date("Pregnancy Start Date")
