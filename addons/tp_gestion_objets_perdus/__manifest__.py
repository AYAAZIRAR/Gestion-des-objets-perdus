{
    "name": "TP - Gestion des Objets Perdus",
    "version": "2.10.0",
    "summary": "Module de Gestion des Objets Perdus et Trouvés",
    "category": "Training",
    "author": "EMSI",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/objet_perdu_views.xml",
        "views/dashboard_views.xml",
        "wizard/return_item_wizard_views.xml",
    ],
    "installable": True,
    "application": True,
}
