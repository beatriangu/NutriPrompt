from __future__ import annotations

LOW_FODMAP_ALLOWED = {
    "rice",
    "potato",
    "chicken",
    "turkey",
    "eggs",
    "zucchini",
    "carrot",
    "spinach",
    "banana",
    "strawberries",
    "quinoa",
    "gluten-free bread",
    "gluten-free pasta",
    "lactose-free yogurt",
    "peanut butter",
    "oats",
    "tomato",
}

LOW_FODMAP_LIMITED = {
    "avocado": "max 30g",
    "oats": "moderate portion",
    "tomato": "moderate portion",
}

LOW_FODMAP_AVOID = {
    "onion",
    "garlic",
    "milk",
    "regular yogurt",
    "wheat pasta",
    "wheat bread",
}

CANONICAL_INGREDIENTS = {
    "huevo": "eggs",
    "huevos": "eggs",
    "yogur": "yogurt",
    "yogur sin lactosa": "lactose-free yogurt",
    "pan": "bread",
    "pan sin gluten": "gluten-free bread",
    "pasta": "pasta",
    "pasta sin gluten": "gluten-free pasta",
    "aguacate": "avocado",
    "tomate": "tomato",
    "avena": "oats",
    "pollo": "chicken",
    "pavo": "turkey",
    "ternera": "beef",
    "patata": "potato",
    "boniato": "sweet potato",
    "espinacas": "spinach",
    "zanahoria": "carrot",
    "arroz": "rice",
    "quinoa": "quinoa",
    "frutos rojos": "berries",
    "crema de cacahuete": "peanut butter",
    "bebida vegetal": "plant drink",
}

PROFILE_TAG_RULES = {
    "low_fodmap": {
        "avoid": LOW_FODMAP_AVOID,
        "limited": LOW_FODMAP_LIMITED,
    },
    "budget": {
        "prefer": {"eggs", "chicken", "turkey", "rice", "potato", "carrot", "zucchini"},
    },
    "quick": {
        "prefer_styles": {"bowl", "omelette", "traybake", "salad", "grill"},
    },
    "muscle_gain": {
        "prefer": {"eggs", "chicken", "turkey", "beef", "lactose-free yogurt"},
    },
    "energy": {
        "prefer": {"rice", "potato", "oats", "banana", "quinoa"},
    },
}