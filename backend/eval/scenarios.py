"""Fixed eval scenarios for Ava: a DOM state + a question + the expected behaviour.

`expect_selectors` is the set of acceptable highlight targets (the crew may pick the
root-cause element). `expect_keywords` are terms the answer should mention (empty = skip).
"""

_DOMAIN_PAGE = {
    "url": "/reglages/domaine",
    "title": "Lyvica — Domaine",
    "elements": [
        {"selector": "[data-ava=publish-btn]", "label": "Publier", "disabled": True},
        {
            "selector": "[data-ava=domain-input]",
            "label": "Domaine",
            "text": "mon site .com",
            "error": "Format de domaine invalide : retire les espaces (ex. monsite.com)",
        },
        {"selector": "[data-ava=connect-btn]", "label": "Connecter"},
    ],
}

_CREATE_PAGE = {
    "url": "/creer",
    "title": "Lyvica — Créer un site",
    "elements": [
        {"selector": "[data-ava=continue-btn]", "label": "Continuer", "disabled": True},
        {"selector": "[data-ava=template-card]", "label": "Choisir un template"},
    ],
}

_EDITOR_PAGE = {
    "url": "/editeur",
    "title": "Lyvica — Éditeur",
    "elements": [
        {"selector": "[data-ava=color-picker]", "label": "Couleur du texte"},
        {"selector": "[data-ava=save-btn]", "label": "Enregistrer"},
    ],
}

SCENARIOS = [
    {
        "name": "publish_blocked_by_domain",
        "question": "pourquoi je ne peux pas publier ?",
        "dom": _DOMAIN_PAGE,
        "expect_selectors": ["[data-ava=domain-input]", "[data-ava=publish-btn]"],
        "expect_keywords": ["domaine", "publier", "format"],
    },
    {
        "name": "domain_format_error",
        "question": "c'est quoi le souci avec mon domaine ?",
        "dom": _DOMAIN_PAGE,
        "expect_selectors": ["[data-ava=domain-input]"],
        "expect_keywords": ["domaine", "format", "espace"],
    },
    {
        "name": "create_continue_disabled",
        "question": "pourquoi le bouton continuer est grisé ?",
        "dom": _CREATE_PAGE,
        "expect_selectors": ["[data-ava=continue-btn]", "[data-ava=template-card]"],
        "expect_keywords": ["template", "continuer", "choisi", "sélection"],
    },
    {
        "name": "no_block_question",
        "question": "comment je change la couleur du texte ?",
        "dom": _EDITOR_PAGE,
        "expect_selectors": [None, "[data-ava=color-picker]"],
        "expect_keywords": ["couleur"],
    },
]
