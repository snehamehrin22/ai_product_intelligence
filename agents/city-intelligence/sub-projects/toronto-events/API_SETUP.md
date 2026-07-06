# API Setup Guide

To extract events from all three sources, you need API keys.

## 1. Eventbrite API

**Documentation:** https://www.eventbrite.com/platform/docs/introduction

### Steps:
1. Go to https://www.eventbrite.com/account-settings/apps
2. Click "Create New App"
3. Fill in app details (name, description, URL)
4. Copy your **OAuth Token** (looks like `ABCDEFG123456789`)
5. Add to `.env`: `EVENTBRITE_TOKEN=your_token_here`

### Notes:
- You need an Eventbrite account (free)
- OAuth token gives read access to public events
- Rate limit: Check their docs for current limits

---

## 2. Luma API

**Documentation:** https://docs.luma.com/reference/getting-started-with-your-api

### Steps:
1. Go to https://lu.ma/settings/api (or similar - check their docs)
2. Generate an API key
3. Copy the key
4. Add to `.env`: `LUMA_API_KEY=your_key_here`

### Notes:
- API access may require specific account type (check docs)
- Base URL: `https://api.lu.ma` (verify in their docs)

---

## 3. Meetup GraphQL API

**Documentation:** https://www.meetup.com/graphql/

### Steps:
1. Go to https://secure.meetup.com/meetup_api/key/
2. Request an API key OR use OAuth
3. Copy your API key
4. Add to `.env`: `MEETUP_API_KEY=your_key_here`

### Notes:
- Meetup uses GraphQL (not REST)
- Explorer: https://www.meetup.com/graphql/
- Authentication: Bearer token in Authorization header

---

## Testing Your Setup

After adding all keys to `.env`, test each extractor:

```bash
# Test Eventbrite
python scripts/extract_eventbrite.py

# Test Luma
python scripts/extract_luma.py

# Test Meetup
python scripts/extract_meetup.py

# Extract from all sources
python scripts/extract_all.py
```

---

## Troubleshooting

### "EVENTBRITE_TOKEN not set"
- Make sure you created a `.env` file (copy from `.env.example`)
- Check the key name matches exactly: `EVENTBRITE_TOKEN=`

### "401 Unauthorized"
- Your API key is invalid or expired
- Regenerate the key from the platform

### "429 Too Many Requests"
- You hit the rate limit
- Wait a few minutes and try again
- Consider implementing retry logic with exponential backoff

### "GraphQL errors"
- Your Meetup query might be incorrect
- Check the GraphQL explorer for the correct schema
- The query in `extract_meetup.py` is a template - adjust based on actual schema

---

## API Costs

All three platforms offer free tiers:

- **Eventbrite**: Free for public event search
- **Luma**: Check their pricing page for API limits
- **Meetup**: Free tier available (check current limits)

If you exceed free tier limits, you'll need to upgrade or implement caching/batching.

---

## Next Steps

Once you have all three APIs working:

1. Run `python scripts/extract_all.py` to get 100+ events
2. Run `python scripts/3_analyze_patterns.py` to analyze
3. Check `patterns.md` for insights
