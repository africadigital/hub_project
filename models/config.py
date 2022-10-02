# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError

class HubValidator(models.Model):
    _name = 'hub.validator'
    _description = 'Hub Validateurs'

    user_id = fields.Many2one(comodel_name="res.users", string="", required=True,)
    type = fields.Selection(string="Type validation", selection=[('pmo', 'PMO'),('daf', 'DAF'), ('dsd', 'DBD'),('dg', 'Directeur Général')], required=True, )
    email = fields.Char(string="Email", required=False,related="user_id.login")

    # =======================================
    # ORM Method
    # =======================================
    @api.model
    def create(self, vals):
        validators = self.search([])
        #raise ValidationError("%s et %s"%(validator.type,vals.get('type')))
        if validators:
            for validator in validators:
                if validator.type == vals.get('type'):
                    raise ValidationError('Vous ne pouvez pas definir le même niveau de validation [%s] une seconde fois de suite'%(validator.type))

        return super(HubValidator, self).create(vals)

class HubSite(models.Model):
    _name = 'hub.worksite'
    _description = 'Hub Chantier'

    name = fields.Char("Designation",required=True)

class HubLocality(models.Model):
    _name = 'hub.locality'
    _description = 'Hub Localité'

    name = fields.Char("Designation",required=True)