# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PIndividual(models.Model):
    _inherit = "res.partner"

    z_cst_indv_medical_condition = fields.Integer(
        "chronic illness/medical conditions level"
    )  # 0-100
    z_cst_indv_disability_level = fields.Integer("Disability level")  # 0-100
    z_cst_indv_pregnancy_start = fields.Date(
        "Pregnancy start"
    )  # We set a date to be able to clean it later
    z_cst_indv_pregnancy_end = fields.Date(
        "Pregnancy end"
    )  # We set a date to be able to clean it later

    # Maternal and neonatal outcomes
    z_cst_indv_pregnancy_maternal_outcome = fields.Selection(
        [
            ("normal", "Normal"),
            ("preterm", "Preterm birth"),
            ("stillbirth", "Stillbirth"),
        ],
        "Maternal outcome",
    )
    z_cst_indv_pregnancy_neonatal_outcome = fields.Selection(
        [
            ("normal", "Neonatal death"),
            ("conanomalies", "Congenital anomalies"),
            ("infections", "Neonatal infections"),
            ("loweight", "Low birth weight"),
            ("small", "Small for gestational age"),
            ("respiratory", "Respiratory distress"),
            ("thrive", "Failure to thrive"),
            ("seizures", "Neonatal seizures"),
            ("neurodevdelay", "Neurodevelopmental delay"),
        ],
        "Neonatal outcome",
    )
