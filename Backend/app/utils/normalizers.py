import re
import unicodedata


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

CITY_CANONICAL_MAP = {
    "b/quilla": "barranquilla",
    "barranquilla": "barranquilla",
    "bogota d.c.": "bogota",
    "bogota dc": "bogota",
    "bogota, d.c.": "bogota",
    "bogota": "bogota",
    "cartagena de indias": "cartagena",
    "cartagena": "cartagena",
    "santa marta": "santa marta",
    "santamarta": "santa marta",
    "san juan de pasto": "pasto",
    "pasto": "pasto",
    "monteria": "monteria",
    "soledad": "soledad",
    "medellin": "medellin",
    "bello": "bello",
    "itagui": "itagui",
    "envigado": "envigado",
    "rionegro": "rionegro",
    "pereira": "pereira",
    "manizales": "manizales",
    "cali": "cali",
    "bucaramanga": "bucaramanga",
}

MODEL_CANONICAL_MAP = {
    "nkd 125": "akt nkd 125",
    "nkd": "akt nkd 125",
    "pulsar ns 200": "bajaj pulsar ns 200",
    "ns 200": "bajaj pulsar ns 200",
    "pulsar 200": "bajaj pulsar ns 200",
    "pulsar ns 160": "bajaj pulsar ns 160",
    "ns 160": "bajaj pulsar ns 160",
    "xpulse 200": "hero xpulse 200",
    "xpulse": "hero xpulse 200",
    "honda xr 150l": "honda xr 150l",
    "xr 150l": "honda xr 150l",
    "xr 150": "honda xr 150l",
    "dio": "honda dio",
    "honda dio": "honda dio",
    "gixxer 150": "suzuki gixxer 150",
    "gixxer": "suzuki gixxer 150",
    "nmax": "yamaha nmax 155",
    "nmax 155": "yamaha nmax 155",
    "sz-rr": "yamaha sz-rr",
    "ttr 125": "akt ttr 125",
    "eco deluxe": "hero eco deluxe",
}


def strip_accents(text: str) -> str:
    """Removes diacritics and accents using Unicode NFKD normalization."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def normalize_phone_e164(value: str | None) -> str | None:
    """
    Normalizes a phone string to Colombian E.164 format (+573XXXXXXXXX).
    Returns None if the phone is not a valid Colombian mobile number.
    """
    if not value:
        return None

    cleaned = value.strip()
    if not cleaned or cleaned.lower() == "nan":
        return None

    digits = re.sub(r"\D", "", cleaned)

    if len(digits) == 10 and digits.startswith("3"):
        return f"+57{digits}"

    if len(digits) == 12 and digits.startswith("57"):
        national = digits[2:]
        if national.startswith("3"):
            return f"+{digits}"

    return None


def normalize_email(value: str | None) -> str | None:
    """
    Normalizes an email address (trims, lowercases, validates basic structure).
    Returns None if missing or invalid format.
    """
    if not value:
        return None

    cleaned = " ".join(value.strip().split()).lower()
    if not cleaned or len(cleaned) > 320:
        return None

    if not EMAIL_PATTERN.fullmatch(cleaned):
        return None

    return cleaned


def normalize_person_name(value: str | None) -> str | None:
    """
    Normalizes a person's name by stripping accents, converting to lowercase,
    removing punctuation and collapsing whitespace.
    """
    if not value:
        return None

    cleaned = strip_accents(value).lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    tokens = [t for t in cleaned.split() if t]
    if not tokens:
        return None

    return " ".join(tokens)


def token_similarity(name_a: str | None, name_b: str | None) -> float:
    """
    Computes a deterministic similarity score between two normalized names
    based on token overlap (Jaccard and containment).
    """
    norm_a = normalize_person_name(name_a)
    norm_b = normalize_person_name(name_b)

    if not norm_a or not norm_b:
        return 0.0

    if norm_a == norm_b:
        return 1.0

    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b

    jaccard = len(intersection) / len(union)

    # If one name's tokens are entirely contained in the other (e.g. 'luz marina jimenez' in 'luz marina jimenez ospina')
    min_len = min(len(tokens_a), len(tokens_b))
    containment = len(intersection) / min_len if min_len > 0 else 0.0

    # Weight combination: 60% containment, 40% jaccard
    return round(0.6 * containment + 0.4 * jaccard, 4)


def normalize_city(value: str | None) -> str | None:
    """
    Normalizes Colombian city names to a canonical standard form.
    """
    if not value:
        return None

    cleaned = strip_accents(value).lower()
    cleaned = " ".join(cleaned.split())

    if cleaned in CITY_CANONICAL_MAP:
        return CITY_CANONICAL_MAP[cleaned]

    # Remove trailing ' d.c.' or ' dc'
    cleaned = re.sub(r"\b(d\.c\.|dc)\b", "", cleaned).strip()
    return CITY_CANONICAL_MAP.get(cleaned, cleaned)


def normalize_model_text(value: str | None) -> str | None:
    """
    Normalizes vehicle model reference or interest text.
    """
    if not value:
        return None

    cleaned = strip_accents(value).lower()
    # Remove year numbers like 2024, 2025, 2026
    cleaned = re.sub(r"\b202\d\b", "", cleaned)
    cleaned = " ".join(cleaned.split())

    for key, canonical in MODEL_CANONICAL_MAP.items():
        if key in cleaned:
            return canonical

    return cleaned
