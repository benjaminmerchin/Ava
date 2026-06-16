# Connecter un domaine

1. Va dans **Réglages → Domaine**.
2. Saisis ton nom de domaine dans le champ **Domaine** (ex. `monsite.com`).
3. Clique sur **« Connecter »**.
4. Ajoute les enregistrements **DNS** indiqués chez ton registrar.
5. Reviens sur Lyvica et clique sur **« Vérifier »** — le statut passe à *Connecté* une fois le DNS propagé.

## Pourquoi le champ domaine est en erreur

Le champ **Domaine** affiche une erreur si le format est invalide (il faut un domaine de la forme `exemple.com`, sans `http://` ni espace).

## Pourquoi le statut reste « En attente »

Tant que les enregistrements DNS ne sont pas propagés, le statut reste **En attente**. La propagation peut prendre jusqu'à 24 h. Clique sur **Vérifier** pour rafraîchir.
