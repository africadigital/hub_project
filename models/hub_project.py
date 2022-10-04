# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError



class HubProject (models.Model):
    _name = 'hub.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fiche projet'

    name = fields.Char("N° Fiche projet", readonly=True)
    budget_id = fields.Many2one(comodel_name="crossovered.budget", string="Budget", required=False,readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one(comodel_name="project.project", string="Projet", required=True,readonly=True, states={'draft': [('readonly', False)]})
    supervisor_id = fields.Many2one(comodel_name="hr.employee", string="Superviseur", required=False,readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, required=True, index=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda x: x.env.company.currency_id)
    project_manager_id = fields.Many2one(comodel_name="hr.employee", string="Chef de projet", required=False,)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Client", required=False, related="project_id.partner_id")
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Compte analytique", required=False, related="project_id.analytic_account_id")
    worksite_id = fields.Many2one(comodel_name="hub.worksite", string="Chantier", required=False,readonly=True, states={'draft': [('readonly', False)]})
    locality_id = fields.Many2one(comodel_name="hub.locality", string="Localité", required=True,readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code", required=False, readonly=True, states={'draft': [('readonly', False)]})
    zone = fields.Char(string="CTR-ZONE", required=True,readonly=True, states={'draft': [('readonly', False)]})
    #url = fields.Char(string="url projet", required=False,readonly=True,copy=False, states={'draft': [('readonly', False)]})
    ticket = fields.Char(string="Ticket", required=False,)
    operation = fields.Char(string="Operation", required=True,readonly=True, states={'draft': [('readonly', False)]})
    motif = fields.Text(string="Motif/Objet", required=True,readonly=True, states={'draft': [('readonly', False)]})
    observation = fields.Text(string="Observation")
    date_start = fields.Date(string="Date debut", required=True,readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Date(string="Date fin", required=True,readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Datetime(string="Date etablissement", default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), required=True, readonly=True, states={'draft': [('readonly', False)]})
    hub_daf_id = fields.Many2one(comodel_name="res.users", string="DAF", readonly=True)
    date_daf = fields.Datetime(string="Date Validation", required=False, readonly=True ,copy=False)
    hub_pmo_id = fields.Many2one(comodel_name="res.users", string="PMO", required=False, readonly=True,copy=False )
    date_pmo = fields.Datetime(string="Date Validation", required=False, readonly=True,copy=False )
    hub_dsd_id = fields.Many2one(comodel_name="res.users", string="DBD", required=False, readonly=True,copy=False )
    date_dsd = fields.Datetime(string="Date Validation", required=False,  readonly=True,copy=False)
    hub_manager_id = fields.Many2one(comodel_name="res.users", string="Directeur Général", required=False, readonly=True,copy=False )
    date_manager = fields.Datetime(string="Date Approbation", required=False, readonly=True,copy=False)
    state = fields.Selection(string="Etat",
                             selection=[('draft', 'Nouveau'), ('pmo_state', 'PMO'), ('daf_state', 'DAF'),('dsd_state', 'DBD'),('dg_state', 'DG'),('cancel', 'Annulée'),('done', 'Demande Approuvée')],
                             default='draft',tracking=1, readonly=True )
    employee_ids = fields.One2many(comodel_name="hub.employee.line", inverse_name="hub_id", string="Personnel Intervenants", readonly=True, required=True,states={'draft': [('readonly', False)]},copy=True)
    materials_ids = fields.One2many(comodel_name="hub.materials.line", inverse_name="hub_id", string="Besoins maretiels", readonly=True, required=True,states={'draft': [('readonly', False)]},copy=True)
    supply_ids = fields.One2many(comodel_name="hub.supply.line", inverse_name="hub_id", string="Fournitures exterieures diverse", readonly=True, required=True,states={'draft': [('readonly', False)]},copy=True)
    amount_total_prime = fields.Monetary(compute="_compute_total",string="Prime Totale",  required=False,store=True)
    amount_total_materials = fields.Monetary(compute="_compute_total",string="Total Besoins Materiels",  required=False,store=True )
    amount_total_supply = fields.Monetary(compute="_compute_total",string="Total Fournitures exterieures divers",store=True,  required=False, )
    amount_total = fields.Monetary(compute="_compute_total",string="Total Général",store=True,  required=False, )

    #=======================================
     # ORM Method
    #=======================================
    @api.model
    def create(self, vals):
        # if not vals.get('employee_ids'):
        #     raise ValidationError("Veuillez renseigner le personnel intervenant ")
        #
        # if not vals.get('materials_ids'):
        #     raise ValidationError("Veuillez renseigner les besoins en materiels ")

        validators = self.env['hub.validator'].search([])
        if validators :
            for user in validators:
                if user.type == 'pmo':
                    vals['hub_pmo_id'] = user.user_id.id
                if user.type == 'daf':
                    vals['hub_daf_id'] = user.user_id.id
                if user.type == 'dsd':
                    vals['hub_dsd_id'] = user.user_id.id
                if user.type == 'dg':
                    vals['hub_manager_id'] = user.user_id.id

        vals['name'] = self.env['ir.sequence'].next_by_code('hub.project.seq')
        return super(HubProject, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Vous ne pouvez supprimer que les fiche de projet à l'etape Nouveau. ")
        return super(HubProject, self).unlink()

    # =======================================
    # Compute Function
    # =======================================

    @api.depends('employee_ids','materials_ids','supply_ids')
    def _compute_total(self):
        for rec in self:
            rec.amount_total_prime = rec.employee_ids and sum([x.subtotal for x in rec.employee_ids]) or 0.0
            rec.amount_total_materials = rec.materials_ids and  sum([x.subtotal for x in rec.materials_ids]) or 0.0
            rec.amount_total_supply = rec.supply_ids and sum([x.subtotal for x in rec.supply_ids]) or 0.0
            rec.amount_total =  rec.amount_total_supply + rec.amount_total_prime + rec.amount_total_materials

    def _analytic_move(self):
        for rec in self :
            self.env['account.analytic.line'].create({
                'name': rec.name + ' - ' + rec.project_id.name,
                'account_id': rec.analytic_account_id.id,
                'ref': rec.name,
                'amount': -1*rec.amount_total,
            })
    def send_email(self):
        email_template_obj = self.env['mail.template']
        template_ctx = {'action_url': "/web#id=%s&model=hub.project&view_type=form"%(self.id)}

        for p in self:
            if p.state == 'draft':
                # Send email Manager Project

                template_ids = self.env.ref('hub_project.email_template_pmo').id
                email_template_obj.browse(template_ids).with_context(**template_ctx).send_mail(self.id, force_send=True)
                p.state = "pmo_state"
            elif p.state == 'pmo_state':
                if p.hub_pmo_id.id != self._uid:
                    raise ValidationError("Vous n'êtes pas autorisé à valider cette fiche ! Merci de contacter l'Administrateur en cas d'erreur.")
                template_ids = self.env.ref('hub_project.email_template_daf').id
                email_template_obj.browse(template_ids).with_context(**template_ctx).send_mail(self.id, force_send=True)
                p.write({'state': 'daf_state', 'date_pmo': time.strftime('%Y-%m-%d %H:%M:%S')})

            elif p.state == 'daf_state':
                # Send email DAF
                if p.hub_daf_id.id != self._uid:
                    raise ValidationError(
                        "Vous n'êtes pas autorisé à valider cette fiche ! Merci de contacter l'Administrateur en cas d'erreur.")
                template_ids = self.env.ref('hub_project.email_template_dsd').id
                email_template_obj.browse(template_ids).with_context(**template_ctx).send_mail(self.id, force_send=True)
                p.write({'state': 'dsd_state', 'date_daf': time.strftime('%Y-%m-%d %H:%M:%S')})

            elif p.state == 'dsd_state':
                # Send email General Manager
                if p.hub_dsd_id.id != self._uid:
                    raise ValidationError(
                        "Vous n'êtes pas autorisé à valider cette fiche ! Merci de contacter l'Administrateur en cas d'erreur.")

                template_ids = self.env.ref('hub_project.email_template_dg').id
                email_template_obj.browse(template_ids).with_context(**template_ctx).send_mail(self.id, force_send=True)

                p.write({'state': 'dg_state', 'date_dsd': time.strftime('%Y-%m-%d %H:%M:%S')})

            elif p.state == 'dg_state':
                # Send email Applicant pay validate
                if p.hub_manager_id.id != self._uid:
                    raise ValidationError(
                        "Vous n'êtes pas autorisé à valider cette fiche ! Merci de contacter l'Administrateur en cas d'erreur.")
                # Move analytic budget
                p._analytic_move()
                template_ids = self.env.ref('hub_project.email_template_applicant').id
                email_template_obj.browse(template_ids).send_mail(self.id, force_send=True)
                p.write({'state': 'done', 'date_manager': time.strftime('%Y-%m-%d %H:%M:%S')})

        return True
    # =======================================
    # Workflow Function
    # =======================================



    def action_submit(self):
        return self.send_email()

    def action_cancel(self,reason):
        self.message_post_with_view('hub_project.template_refuse_reason',
                                    values={'reason': reason, 'name': self.name})
        return self.write({'state': 'cancel'})

    def action_draft(self):
        return self.write({'state': 'draft'})

class HubEmployeeLine(models.Model):
    _name = 'hub.employee.line'
    _description = 'Ligne du personnel intervenant'

    hub_id = fields.Many2one(comodel_name="hub.project", string="Fiche projet", required=True, ondelete="cascade" )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Nom et Prenom", required=True, )
    job_id = fields.Many2one(comodel_name="hr.job", string="Fonction", required=False,related="employee_id.job_id" )
    qty = fields.Float(string="Qte en jrs",default=1,  required=False, )
    price = fields.Monetary(string="Prime Jounaliere",  required=True, )
    subtotal = fields.Monetary(compute="_compute_subtotal",string="Prime Totale",  required=False,store=True )
    company_id = fields.Many2one('res.company', 'Company', readonly=True,related="hub_id.company_id")
    currency_id = fields.Many2one('res.currency', readonly=True,related="hub_id.currency_id")

    # =======================================
    #  Function API
    # =======================================

    @api.depends('qty', 'price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.price


class HubMaterialLine(models.Model):
    _name = 'hub.materials.line'
    _description = 'Ligne des besoins en materiels'

    hub_id = fields.Many2one(comodel_name="hub.project", string="Fiche projet", required=True, ondelete="cascade" )
    name = fields.Char(string="Designation", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Article", required=True, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Unite de mesure", required=False, )
    company_id = fields.Many2one('res.company', 'Company', readonly=True, related="hub_id.company_id")
    currency_id = fields.Many2one('res.currency', readonly=True, related="hub_id.currency_id")
    qty = fields.Float(string="Quantité", default=1,  required=False, )
    price = fields.Monetary(string="Prix Unitaire",  required=False, )
    subtotal = fields.Monetary(compute="_compute_subtotal",string="Prix Total",  required=False,store=True)

    # =======================================
    # Function API
    # =======================================

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.price = self.product_id.standard_price
            if not self.name:
                self.name = self.product_id.display_name

    @api.depends('qty','price')
    def _compute_subtotal(self):
        for rec in self :
            rec.subtotal = rec.qty*rec.price

class HubSupplyLine(models.Model):
    _name = 'hub.supply.line'
    _description = 'Ligne des fournitures exetrieures divers'

    hub_id = fields.Many2one(comodel_name="hub.project", string="Fiche projet", required=True, ondelete="cascade" )
    name = fields.Char(string="Designation", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Article", required=True, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Unite de mesure", required=False, )
    company_id = fields.Many2one('res.company', 'Company', readonly=True, related="hub_id.company_id")
    currency_id = fields.Many2one('res.currency', readonly=True, related="hub_id.currency_id")
    qty = fields.Float(string="Quantité",default=1,  required=True, )
    price = fields.Monetary(string="Prix Unitaire",  required=True, )
    subtotal = fields.Monetary(compute="_compute_subtotal",string="Prix Total",  required=False,store=True )

    # =======================================
    #  Function API
    # =======================================

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.price = self.product_id.standard_price
            if not self.name:
                self.name = self.product_id.display_name

    @api.depends('qty', 'price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.price