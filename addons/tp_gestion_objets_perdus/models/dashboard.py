from odoo import models, fields, api

class TpObjetDashboard(models.TransientModel):
    _name = 'tp.objet.dashboard'
    _description = 'Dashboard des Objets Perdus'

    total_objets = fields.Integer("Total", compute='_compute_kpis')
    objets_perdus = fields.Integer("Perdus", compute='_compute_kpis')
    objets_trouves = fields.Integer("Trouvés", compute='_compute_kpis')
    restitution_rate = fields.Float("Taux de Restitution", compute='_compute_kpis')
    user_id = fields.Many2one('res.users', string='Utilisateur', default=lambda self: self.env.user)
    
    def _compute_kpis(self):
        for record in self:
            record.total_objets = self.env['tp.objet'].search_count([])
            record.objets_perdus = self.env['tp.objet'].search_count([('item_type', '=', 'lost')])
            record.objets_trouves = self.env['tp.objet'].search_count([('item_type', '=', 'found')])
            
            objets_restitues = self.env['tp.objet'].search_count([('statut', '=', 'returned')])
            if record.total_objets > 0:
                record.restitution_rate = (objets_restitues / record.total_objets) * 100
            else:
                record.restitution_rate = 0

    def action_view_all(self):
        return self.env.ref('tp_gestion_objets_perdus.action_tp_objet_view').read()[0]

    def action_view_lost(self):
        return self.env.ref('tp_gestion_objets_perdus.action_tp_lost_items').read()[0]

    def action_view_found(self):
        return self.env.ref('tp_gestion_objets_perdus.action_tp_found_items').read()[0]
