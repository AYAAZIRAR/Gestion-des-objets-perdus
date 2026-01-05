from odoo import models, fields

class TpObjetCategory(models.Model):
    _name = 'tp.objet.category'
    _description = 'Catégorie d\'objet'
    
    name = fields.Char('Nom', required=True)
    sequence = fields.Integer('Séquence', default=10)
