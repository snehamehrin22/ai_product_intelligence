"""Label third-party hosts with a vendor and category (tech-stack fingerprinting).

Pure functions, no I/O. Complements vendors.py, which only covers analytics requests.
Hosts that match nothing are returned as unknown so a human/LLM can research them.
"""
import re
from typing import List, Optional, Tuple

# (vendor, category, host regex)
HOST_LABELS: List[Tuple[str, str, str]] = [
    ("Webflow", "website", r"(^|\.)(website-files\.com|webflow\.com|webflow\.io)$"),
    ("Shopify", "ecommerce", r"(^|\.)(shopify\.com|myshopify\.com|shopifycdn\.com|shopifysvc\.com)$"),
    ("Squarespace", "website", r"(^|\.)(squarespace\.com|sqspcdn\.com)$"),
    ("Wix", "website", r"(^|\.)(wixstatic\.com|parastorage\.com)$"),
    ("Mariana Tek", "booking", r"(^|\.)(marianatek\.com|marianaiframes\.com|mtproduction-files\.s3\.amazonaws\.com)$"),
    ("Mindbody", "booking", r"(^|\.)(mindbodyonline\.com|mindbody\.io|healcode\.com)$"),
    ("Xplor", "forms/crm", r"(^|\.)xplorcs\.com$"),
    ("Vidzflow", "video", r"(^|\.)vidzflow\.com$"),
    ("Embedly", "video", r"(^|\.)embed\.ly$"),
    ("Video.js", "video", r"(^|\.)zencdn\.net$"),
    ("Wistia", "video", r"(^|\.)wistia\.(com|net)$"),
    ("Vimeo", "video", r"(^|\.)(vimeo\.com|vimeocdn\.com)$"),
    ("Cloudflare", "security/perf", r"(^|\.)(cloudflare\.com|cloudflareinsights\.com)$"),
    ("accessiBe", "accessibility", r"(^|\.)acsbapp\.com$"),
    ("Heybrio", "chat", r"(^|\.)heybrio\.ai$"),
    ("Intercom", "chat", r"(^|\.)(intercom\.io|intercomcdn\.com)$"),
    ("Drift", "chat", r"(^|\.)drift\.com$"),
    ("EmbedReach", "marketing/identity", r"(^|\.)embedreach\.com$"),
    ("Booko", "dynamic pricing", r"(^|\.)bookoapp\.com$"),
    ("OpenAI pixel", "ads/measurement", r"(^|\.)(bzr\.openai\.com|bzrcdn\.openai\.com)$"),
    ("Google Tag Manager", "tag manager", r"(^|\.)googletagmanager\.com$"),
    ("Google Analytics/Ads", "analytics/ads", r"(^|\.)(google-analytics\.com|analytics\.google\.com|doubleclick\.net|googleadservices\.com|googlesyndication\.com)$"),
    ("Meta pixel", "ads", r"(^|\.)(facebook\.net|facebook\.com)$"),
    ("LinkedIn", "ads", r"(^|\.)(linkedin\.com|licdn\.com)$"),
    ("TikTok", "ads", r"(^|\.)tiktok\.com$"),
    ("Pinterest", "ads", r"(^|\.)pinterest\.com$"),
    ("Microsoft Clarity", "session replay", r"(^|\.)clarity\.ms$"),
    ("Hotjar", "session replay", r"(^|\.)hotjar\.(com|io)$"),
    ("FullStory", "session replay", r"(^|\.)fullstory\.com$"),
    ("PostHog", "analytics", r"(^|\.)posthog\.com$"),
    ("Segment", "analytics", r"(^|\.)segment\.(io|com)$"),
    ("Klaviyo", "email/sms", r"(^|\.)klaviyo\.com$"),
    ("HubSpot", "crm/marketing", r"(^|\.)(hubspot\.com|hs-scripts\.com|hsforms\.com|hs-analytics\.net)$"),
    ("Stripe", "payments", r"(^|\.)stripe\.com$"),
    ("PayPal", "payments", r"(^|\.)paypal(objects)?\.com$"),
    ("Sentry", "errors", r"(^|\.)sentry\.io$"),
    ("Perkville", "loyalty", r"(^|\.)perkville\.com$"),
    ("jsDelivr", "cdn", r"(^|\.)jsdelivr\.net$"),
    ("cdnjs", "cdn", r"(^|\.)cdnjs\.cloudflare\.com$"),
    ("Google Fonts", "cdn", r"(^|\.)(fonts\.googleapis\.com|fonts\.gstatic\.com)$"),
]

_COMPILED = [(v, c, re.compile(p)) for v, c, p in HOST_LABELS]

# Third-party JS that mentions form fields AND submit handling may read what people type.
_FIELD_RE = re.compile(r"(?i)(type=.?email|\[name=.?\w*email|bb_email|captureFields|input\[type)")
_SUBMIT_RE = re.compile(r"(?i)(submit|addEventListener\(.?click)")


def label_host(host: str) -> Optional[Tuple[str, str]]:
    """Return (vendor, category) for a host, or None if unrecognised."""
    for vendor, category, pattern in _COMPILED:
        if pattern.search(host or ""):
            return vendor, category
    return None


def is_first_party(host: str, site_host: str) -> bool:
    """True if host shares the site's registrable-ish domain (last two labels)."""
    base = ".".join(site_host.split(".")[-2:])
    return host == site_host or host.endswith("." + base) or host == base


def may_read_form_fields(script_text: str) -> bool:
    """Heuristic: script references email/form-field selectors and submit handling.

    A prompt to read the script, not proof. False positives are expected.
    """
    return bool(_FIELD_RE.search(script_text) and _SUBMIT_RE.search(script_text))
