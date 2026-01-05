# Create Categories
categories = ['Électronique', 'Vêtements', 'Documents', 'Clés', 'Autres']
cat_ids = {}
for cat_name in categories:
    cat_id = env['tp.objet.category'].create({'name': cat_name})
    cat_ids[cat_name] = cat_id.id
print(f"Categories created: {categories}")

# Create Sample Objects
items = [
    {
        'name': 'iPhone 13 Noir',
        'description': 'Trouvé près de la cafétéria',
        'item_type': 'found',
        'statut': 'declared',
        'location': 'Cafétéria',
        'category_id': cat_ids['Électronique'],
    },
    {
        'name': 'Portefeuille en cuir',
        'description': 'Perdu dans le couloir B',
        'item_type': 'lost',
        'statut': 'in_progress',
        'location': 'Couloir B',
        'category_id': cat_ids['Autres'],
    },
    {
        'name': 'Carte Étudiant - Amal Bennani',
        'description': 'Trouvé à la bibliothèque',
        'item_type': 'found',
        'statut': 'returned',
        'location': 'Bibliothèque',
        'category_id': cat_ids['Documents'],
        'return_date': '2025-12-30',
        'returned_to': 'Amal Bennani',
    },
    {
        'name': 'Clés de voiture (Renault)',
        'description': 'Perdues sur le parking',
        'item_type': 'lost',
        'statut': 'declared',
        'location': 'Parking P1',
        'category_id': cat_ids['Clés'],
    },
    {
        'name': 'Ordinateur Portable Dell',
        'description': 'Oublié en salle 102',
        'item_type': 'found',
        'statut': 'in_progress',
        'location': 'Salle 102',
        'category_id': cat_ids['Électronique'],
    }
]

for item in items:
    obj = env['tp.objet'].create(item)
    print(f"Created item: {obj.name}")

env.cr.commit()
