from odoo import models, fields, api
from datetime import date

class TpObjet(models.Model):
    _name = 'tp.objet'
    _description = 'Objet Perdu/Trouvé'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'declaration_date desc'

    name = fields.Char(string='Nom de l\'objet', required=True, tracking=True)
    description = fields.Text(string='Description')
    declaration_date = fields.Date(string='Date Déclaration', default=fields.Date.context_today)
    
    item_type = fields.Selection([
        ('lost', 'Perdu'),
        ('found', 'Trouvé')
    ], string='Type', required=True, default='lost', tracking=True)
    
    statut = fields.Selection([
        ('declared', 'Déclaré'),
        ('in_progress', 'En cours'),
        ('returned', 'Restitué')
    ], string='Statut', default='declared', tracking=True)
    
    location = fields.Char(string='Lieu')
    category_id = fields.Many2one('tp.objet.category', string='Catégorie', tracking=True)
    image = fields.Binary(string='Image')
    
    responsable = fields.Char(string='Responsable', default=lambda self: self.env.user.name)
    
    partner_id = fields.Many2one('res.partner', string='Contact/Propriétaire', tracking=True)
    contact_email = fields.Char(string='Email contact', related='partner_id.email', readonly=False, store=True)
    contact_phone = fields.Char(string='Téléphone contact', related='partner_id.phone', readonly=False, store=True)
    
    return_date = fields.Date(string='Date de restitution')
    returned_to = fields.Char(string='Restitué à')
    
    days_since_declaration = fields.Integer(string='Jours depuis la déclaration', compute='_compute_days', store=False)
    match_count = fields.Integer(string='Matchs Potentiels', compute='_compute_match_count')


    @api.model_create_multi
    def create(self, vals_list):
        records = super(TpObjet, self).create(vals_list)
        for record in records:
            if record.item_type == 'found':
                # Message in chatter
                record.message_post(
                    body="🌟 <strong>Nouvel objet trouvé !</strong> : %s a été déclaré à %s." % (record.name, record.location),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
            # Automatic matching
            record._check_matches()
        return records

    def write(self, vals):
        # Check if status is changing to 'returned'
        records_to_notify = self.env['tp.objet']
        if 'statut' in vals and vals['statut'] == 'returned':
            for record in self:
                if record.statut != 'returned':
                    records_to_notify |= record
        
        res = super(TpObjet, self).write(vals)
        
        # Send notifications after successful write
        for record in records_to_notify:
            record._send_restitution_email()
            
        return res

    def _compute_match_count(self):
        for record in self:
            if record.statut == 'returned' or not record.category_id:
                record.match_count = 0
                continue
            
            oppsite_type = 'found' if record.item_type == 'lost' else 'lost'
            domain = [
                ('item_type', '=', oppsite_type),
                ('category_id', '=', record.category_id.id),
                ('statut', '!=', 'returned'),
                ('id', '!=', record.id)
            ]
            matches = self.env['tp.objet'].search(domain)
            # Robust fuzzy filter
            if record.name:
                potential_matches = matches.filtered(lambda r: r.name and (record.name.lower() in r.name.lower() or r.name.lower() in record.name.lower()))
                record.match_count = len(potential_matches)
            else:
                record.match_count = 0

    def _check_matches(self):
        """ Trouve des objets correspondants et envoie des notifications. """
        self.ensure_one()
        if self.statut == 'returned':
            return

        oppsite_type = 'found' if self.item_type == 'lost' else 'lost'
        
        # Simple match on category and name (basic search)
        domain = [
            ('item_type', '=', oppsite_type),
            ('category_id', '=', self.category_id.id),
            ('statut', '!=', 'returned'),
            ('id', '!=', self.id)
        ]
        
        matches = self.search(domain)
        
        # Filter by name similarity (robust)
        if self.name:
            potential_matches = matches.filtered(lambda r: r.name and (self.name.lower() in r.name.lower() or r.name.lower() in self.name.lower()))
            
            for match in potential_matches:
                # Post matching notification in chatter for both
                msg = "🔍 <strong>Match potentiel trouvé !</strong><br/>"
                msg += "L'objet <strong>%s</strong> correspond à la description de <strong>%s</strong>." % (self.name, match.name)
                
                self.message_post(body=msg)
                match.message_post(body=msg)
                
                # If we found a 'found' item for a 'lost' item, notify the owner of the lost item
                if self.item_type == 'lost' and self.contact_email:
                    self._send_match_email()
                elif match.item_type == 'lost' and match.contact_email:
                    match._send_match_email()

    def _send_match_email(self):
        self.ensure_one()
        template = self.env.ref('tp_gestion_objets_perdus.email_template_match_found', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_restitution_email(self):
        self.ensure_one()
        template = self.env.ref('tp_gestion_objets_perdus.email_template_restitution_success', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    @api.depends('declaration_date')
    def _compute_days(self):
        for record in self:
            if record.declaration_date:
                delta = date.today() - record.declaration_date
                record.days_since_declaration = delta.days
            else:
                record.days_since_declaration = 0

    def action_start_progress(self):
        self.statut = 'in_progress'

    def action_return(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Restituer l\'objet',
            'res_model': 'tp.objet.return.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_objet_id': self.id}
        }
    
    def action_back_to_declared(self):
        self.statut = 'declared'

    def action_view_matches(self):
        self.ensure_one()
        oppsite_type = 'found' if self.item_type == 'lost' else 'lost'
        domain = [
            ('item_type', '=', oppsite_type),
            ('category_id', '=', self.category_id.id),
            ('statut', '!=', 'returned'),
            ('id', '!=', self.id)
        ]
        # On repasse par le filtrage par nom pour être cohérent avec le compute
        matches = self.env['tp.objet'].search(domain)
        potential_match_ids = []
        if self.name:
            potential_match_ids = matches.filtered(lambda r: r.name and (self.name.lower() in r.name.lower() or r.name.lower() in self.name.lower())).ids
        
        return {
            'name': 'Matchs Potentiels',
            'type': 'ir.actions.act_window',
            'res_model': 'tp.objet',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', potential_match_ids)],
            'context': {'create': False},
        }

