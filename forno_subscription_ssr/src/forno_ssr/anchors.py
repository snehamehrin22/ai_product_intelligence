"""
Likert scale anchor statements for subscription intent.

Two sets of reference statements (Set 0 and Set 1) to average over,
following Maier et al. (2025) methodology for robustness.

Each set contains 5 statements corresponding to ratings 1-5 on the Likert scale.
"""

from .schemas import LikertAnchor


# Anchor Set 0 - First variation
ANCHOR_SET_0 = [
    LikertAnchor(
        rating=1,
        statement="I would almost certainly never subscribe to this. It doesn't fit my routine or budget at all.",
        anchor_set_id=0
    ),
    LikertAnchor(
        rating=2,
        statement="I probably wouldn't subscribe. It seems too expensive or inconvenient for my current situation.",
        anchor_set_id=0
    ),
    LikertAnchor(
        rating=3,
        statement="I might try it once to see if I like it, but I'm not sure it would stick as a regular habit.",
        anchor_set_id=0
    ),
    LikertAnchor(
        rating=4,
        statement="I'd likely subscribe. It fits my visits to Forno and seems worth trying for at least a few months.",
        anchor_set_id=0
    ),
    LikertAnchor(
        rating=5,
        statement="This fits perfectly into my weekly King Street routine. I can absolutely see myself keeping this subscription for many months.",
        anchor_set_id=0
    ),
]


# Anchor Set 1 - Second variation (different wording, same intent levels)
ANCHOR_SET_1 = [
    LikertAnchor(
        rating=1,
        statement="This subscription isn't for me. My visit frequency and budget make this unrealistic.",
        anchor_set_id=1
    ),
    LikertAnchor(
        rating=2,
        statement="It's unlikely I'd commit to this. The price or structure doesn't work for how I use Forno currently.",
        anchor_set_id=1
    ),
    LikertAnchor(
        rating=3,
        statement="I'm on the fence. I could see myself trying it for a month, but I'm uncertain about long-term commitment.",
        anchor_set_id=1
    ),
    LikertAnchor(
        rating=4,
        statement="This makes sense for me. Given how often I'm at Forno, I'd probably subscribe and use it consistently.",
        anchor_set_id=1
    ),
    LikertAnchor(
        rating=5,
        statement="This is exactly what I need. I visit regularly enough that this would definitely save me money and time.",
        anchor_set_id=1
    ),
]


# Combined list of all anchor sets
ALL_ANCHOR_SETS = [ANCHOR_SET_0, ANCHOR_SET_1]


def get_anchor_set(anchor_set_id: int) -> list[LikertAnchor]:
    """
    Get all anchors for a specific set.

    Args:
        anchor_set_id: 0 or 1

    Returns:
        List of 5 LikertAnchor objects for that set
    """
    if anchor_set_id == 0:
        return ANCHOR_SET_0
    elif anchor_set_id == 1:
        return ANCHOR_SET_1
    else:
        raise ValueError(f"Invalid anchor_set_id: {anchor_set_id}. Must be 0 or 1.")


def get_all_anchor_sets() -> list[list[LikertAnchor]]:
    """Get all anchor sets."""
    return ALL_ANCHOR_SETS


def get_anchor_by_rating(rating: int, anchor_set_id: int) -> LikertAnchor:
    """
    Get a specific anchor by rating and set.

    Args:
        rating: 1-5
        anchor_set_id: 0 or 1

    Returns:
        LikertAnchor object
    """
    anchor_set = get_anchor_set(anchor_set_id)
    for anchor in anchor_set:
        if anchor.rating == rating:
            return anchor
    raise ValueError(f"No anchor found for rating {rating} in set {anchor_set_id}")
