"""
38 disease/condition classes from PlantVillage dataset.
Each entry: internal_key → { display names per language, crop, severity_default }
"""

DISEASE_CLASSES = {
    "apple_scab": {
        "en": "Apple Scab",
        "fr": "Tavelure du pommier",
        "sw": "Ugonjwa wa tufaha",
        "kin": "Indwara y'intofanyi",
        "crop": "apple",
        "severity": "medium",
    },
    "apple_black_rot": {
        "en": "Apple Black Rot",
        "fr": "Pourriture noire du pommier",
        "sw": "Kuoza kwa tufaha",
        "kin": "Ubunyota bw'intofanyi",
        "crop": "apple",
        "severity": "high",
    },
    "corn_gray_leaf_spot": {
        "en": "Corn Gray Leaf Spot",
        "fr": "Tache grise du maïs",
        "sw": "Madoa ya kijivu ya mahindi",
        "kin": "Inganda zirabura ku ibigori",
        "crop": "corn",
        "severity": "medium",
    },
    "corn_common_rust": {
        "en": "Corn Common Rust",
        "fr": "Rouille commune du maïs",
        "sw": "Kutu ya mahindi",
        "kin": "Inganda zitukura ku ibigori",
        "crop": "corn",
        "severity": "medium",
    },
    "corn_northern_leaf_blight": {
        "en": "Northern Leaf Blight",
        "fr": "Brûlure nordique des feuilles",
        "sw": "Ugonjwa wa majani ya kaskazini",
        "kin": "Indwara y'amababi y'ibigori",
        "crop": "corn",
        "severity": "high",
    },
    "potato_early_blight": {
        "en": "Potato Early Blight",
        "fr": "Alternariose de la pomme de terre",
        "sw": "Ugonjwa wa mapema wa viazi",
        "kin": "Indwara y'ibirayi yaje kare",
        "crop": "potato",
        "severity": "medium",
    },
    "potato_late_blight": {
        "en": "Potato Late Blight",
        "fr": "Mildiou de la pomme de terre",
        "sw": "Ugonjwa wa marehemu wa viazi",
        "kin": "Indwara y'ibirayi irengeje igihe",
        "crop": "potato",
        "severity": "critical",
    },
    "tomato_bacterial_spot": {
        "en": "Tomato Bacterial Spot",
        "fr": "Tache bactérienne de la tomate",
        "sw": "Madoa ya bakteria ya nyanya",
        "kin": "Indwara ya nyanya ituruka ku binyabuzima",
        "crop": "tomato",
        "severity": "high",
    },
    "tomato_early_blight": {
        "en": "Tomato Early Blight",
        "fr": "Alternariose de la tomate",
        "sw": "Ugonjwa wa mapema wa nyanya",
        "kin": "Indwara y'inyanya yaje kare",
        "crop": "tomato",
        "severity": "medium",
    },
    "tomato_late_blight": {
        "en": "Tomato Late Blight",
        "fr": "Mildiou de la tomate",
        "sw": "Ugonjwa wa marehemu wa nyanya",
        "kin": "Indwara y'inyanya irengeje igihe",
        "crop": "tomato",
        "severity": "critical",
    },
    "tomato_leaf_mold": {
        "en": "Tomato Leaf Mold",
        "fr": "Moisissure des feuilles de tomate",
        "sw": "Ukungu wa majani ya nyanya",
        "kin": "Ubunyota bw'amababi y'inyanya",
        "crop": "tomato",
        "severity": "medium",
    },
    "tomato_septoria_leaf_spot": {
        "en": "Septoria Leaf Spot",
        "fr": "Septoriose de la tomate",
        "sw": "Madoa ya Septoria",
        "kin": "Indwara ya Septoria",
        "crop": "tomato",
        "severity": "medium",
    },
    "tomato_spider_mites": {
        "en": "Spider Mites (Two-spotted)",
        "fr": "Acariens (Tétranyque)",
        "sw": "Utitiri wa buibui",
        "kin": "Ibibumba bisimbuye",
        "crop": "tomato",
        "severity": "medium",
    },
    "tomato_target_spot": {
        "en": "Tomato Target Spot",
        "fr": "Tache cible de la tomate",
        "sw": "Madoa ya shabaha ya nyanya",
        "kin": "Indwara y'inyanya ifite igishusho cy'intego",
        "crop": "tomato",
        "severity": "high",
    },
    "tomato_yellow_leaf_curl": {
        "en": "Tomato Yellow Leaf Curl Virus",
        "fr": "Virus de l'enroulement jaune",
        "sw": "Virusi ya kujikunja kwa majani ya nyanya",
        "kin": "Virusi y'amababi y'inyanya akurika",
        "crop": "tomato",
        "severity": "critical",
    },
    "tomato_mosaic_virus": {
        "en": "Tomato Mosaic Virus",
        "fr": "Virus de la mosaïque de la tomate",
        "sw": "Virusi ya mosaic ya nyanya",
        "kin": "Virusi ya mosayike y'inyanya",
        "crop": "tomato",
        "severity": "high",
    },
    "healthy": {
        "en": "Healthy Plant",
        "fr": "Plante saine",
        "sw": "Mmea mzima",
        "kin": "Umusaruro muzima",
        "crop": "any",
        "severity": "none",
    },
}

CLASS_LABELS = list(DISEASE_CLASSES.keys())


def get_disease_info(key: str, language: str = "en") -> dict:
    info = DISEASE_CLASSES.get(key, DISEASE_CLASSES["healthy"])
    return {
        "key": key,
        "display_name": info.get(language, info.get("en", key)),
        "crop": info.get("crop", "unknown"),
        "severity": info.get("severity", "unknown"),
    }
