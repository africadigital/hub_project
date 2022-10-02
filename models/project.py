# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError

class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    @api.model
    def create(self, values):
        partner = False
        if values.get('partner_id'):
            partner = self.env['res.partner'].browse(values.get('partner_id'))
        analytic_id = self.env['account.analytic.account'].create({
            'name' : values.get('name'),
            'partner_id': partner and partner.id
        })
        values['analytic_account_id'] = analytic_id.id
        return super(Project, self).create(values)
