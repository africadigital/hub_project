# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HubRefuseWizard(models.TransientModel):

    _name = "hub.project.refuse.wizard"
    _description = "Hub Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    hub_project_id = fields.Many2one('hub.project')

    @api.model
    def default_get(self, fields):
        res = super(HubRefuseWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id', [])
        # refuse_model = self.env.context.get('hr_expense_refuse_model')
        res.update({'hub_project_id': active_id,})

        return res

    def hub_refuse_reason(self):
        self.ensure_one()
        if self.hub_project_id:
            self.hub_project_id.action_cancel(self.reason)

        return {'type': 'ir.actions.act_window_close'}
