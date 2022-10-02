{
    'name': 'Hub Project',
    'version': '1.0',
    'summary': 'Fiche Projet',
    'description': "Fiche de projet HUB COTE D'IVOIRE",
    'category': 'Project',
    'author': 'Mor Tall Seck',
    'website': 'https://ivoirecode.ci/erp-odoo',
    'depends': ['base','project','hr','project_account_budget'],
    'data': [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'data/mail_data.xml',
            'views/seq.xml',
            'wizard/hub_refuse_reason.xml',
            'views/hub_project.xml',


            ],

    'installable': True,
    'auto_install': False
}