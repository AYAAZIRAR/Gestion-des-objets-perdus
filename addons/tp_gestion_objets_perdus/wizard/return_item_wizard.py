from odoo import models, fields

class TpObjetReturnWizard(models.TransientModel):
    _name = 'tp.objet.return.wizard'
    _description = 'Assistant de restitution'

    objet_id = fields.Many2one('tp.objet', string="Objet", required=True)
    return_date = fields.Date(string="Date de restitution", default=fields.Date.context_today, required=True)
    returned_to = fields.Char(string="Restitué à", required=True)

    def action_confirm_return(self):
        self.ensure_one()
        self.objet_id.write({
            'statut': 'returned',
            'return_date': self.return_date,
            'returned_to': self.returned_to
        })
        return {'type': 'ir.actions.act_window_close'}
