from odoo import models, fields, api

class LostFoundDashboard(models.TransientModel):
    _name = 'lost.found.dashboard'
    _description = 'Dashboard Objets Perdus'

    total_items = fields.Integer(compute='_compute_kpis')
    lost_items = fields.Integer(compute='_compute_kpis')
    found_items = fields.Integer(compute='_compute_kpis')
    
    recent_items_ids = fields.Many2many('lost.found.item', compute='_compute_recent_items')

    def _compute_kpis(self):
        for record in self:
            record.total_items = self.env['lost.found.item'].search_count([])
            record.lost_items = self.env['lost.found.item'].search_count([('item_type', '=', 'lost')])
            record.found_items = self.env['lost.found.item'].search_count([('item_type', '=', 'found')])

    def _compute_recent_items(self):
        for record in self:
            record.recent_items_ids = self.env['lost.found.item'].search([], order='create_date desc', limit=10)

    @api.model
    def action_open_dashboard(self):
        dashboard = self.create({})
        return {
            'name': 'Tableau de Bord',
            'type': 'ir.actions.act_window',
            'res_model': 'lost.found.dashboard',
            'res_id': dashboard.id,
            'view_mode': 'form',
            'target': 'current',
        }
