# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ChangeRequestSourceMixin(models.AbstractModel):
    _inherit = "spp.change.request.source.mixin"

    current_user_in_validation_group = fields.Boolean(
        related="change_request_id.current_user_in_validation_group",
    )
    date_requested = fields.Datetime(related="change_request_id.date_requested")
