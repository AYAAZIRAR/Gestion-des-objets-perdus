from odoo import models, fields, api

class LostFoundItem(models.Model):
    _name = 'lost.found.item'
    _description = 'Objet Perdu/Trouvé'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom de l\'objet', required=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    
    # FIX: Change string to avoid 'Type' keyword
    item_type = fields.Selection([
        ('lost', 'Perdu'),
        ('found', 'Trouvé')
    ], string='Nature de l\'objet', required=True, default='lost')
    
    state = fields.Selection([
        ('draft', 'Nouveau'),
        ('lost', 'Perdu'),
        ('found', 'Trouvé'),
        ('returned', 'Restitué')
    ], string='Statut', default='draft')
    
    def action_lost(self):
        self.state = 'lost'

    def action_found(self):
        self.state = 'found'

    def action_returned(self):
        self.state = 'returned'
