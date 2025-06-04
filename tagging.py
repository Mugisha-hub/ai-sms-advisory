import re

# List of common crop names
crop_tags = [
    "tomato", "maize", "beans", "cassava", "sweet potato", 
    "cabbage", "carrot", "onion", "rice", "banana", 
    "coffee", "tea", "sorghum", "wheat", "groundnut"
]

# Keywords linked to problems (mapped to tags)
tag_keywords = {
    "disease": ["blight", "wilt", "mosaic", "rot", "fungus", "virus"],
    "pest": ["aphid", "worm", "caterpillar", "beetle", "thrips", "mites", "grasshopper"],
    "fertilizer": ["yellow", "deficiency", "weak", "stunted", "slow growth", "nutrient"]
}

def extract_tags_from_message(message):
    """
    Takes an SMS message string and returns a list of relevant tags (crops and problems).
    """
    message = message.lower()
    tags = []

    # Crop tags: direct match
    for crop in crop_tags:
        if crop in message:
            tags.append(crop)

    # Problem tags: match based on keyword groups
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message):
                tags.append(tag)
                break  # Avoid multiple hits for same tag

    return list(set(tags))  # Remove duplicates
