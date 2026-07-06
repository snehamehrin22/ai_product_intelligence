# Quick Setup Guide

## 1. Install Dependencies

```bash
cd /Users/snehamehrin/Desktop/ai_product_intelligence/agents/cafe-review-intelligence

# Create virtual environment
/usr/local/bin/python3.13 -m venv .venv

# Activate
source .venv/bin/activate

# Install
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your actual API keys
nano .env  # or use your preferred editor
```

Required API keys:
- `APIFY_API_TOKEN` - Get from https://console.apify.com/
- `OPENAI_API_KEY` - Get from https://platform.openai.com/

## 3. Test with a Real Cafe

```bash
# Run analysis for a cafe
python scripts/run_single_cafe.py "Quantum Coffee" "Toronto"

# Or run interactively
python scripts/run_single_cafe.py
```

## 4. Verify Output

You should see:
1. ✓ Reviews scraped from Google Maps
2. ✓ Behavioral signals detected
3. ✓ Insights generated and mapped to framework
4. ✓ Top 3 priority findings displayed
5. ✓ Results saved as JSON files in `data/` directory

Check the `data/` folder for 3 JSON files:
- `{cafe_name}_reviews_{timestamp}.json` - All reviews
- `{cafe_name}_signals_{timestamp}.json` - Detected behavioral signals
- `{cafe_name}_analysis_{timestamp}.json` - Complete framework analysis

## Troubleshooting

### "APIFY_API_TOKEN not found"
- Check that `.env` file exists and has the token
- Make sure you're running from the correct directory
- Try: `source .venv/bin/activate` again

### "No reviews found"
- Check cafe name spelling
- Try adding location: `python scripts/run_single_cafe.py "Cafe Name" "Toronto"`
- Verify the cafe exists on Google Maps

### "OpenAI error"
- Check OPENAI_API_KEY in `.env`
- Verify you have credits on OpenAI account
- Cost per cafe: ~$0.08 (very cheap)

## Next Steps

Once setup is working:

1. **Test on 3-5 cafes you know** - Verify insights match reality
2. **Run on your 30-cafe pilot list** - Build your dataset
3. **Use insights for reels** - Turn findings into content
4. **Track experiments** - See which cafes implement your suggestions

## Cost Estimate

For 30 cafes:
- Apify: Free tier covers ~100 requests (plenty for 30 cafes)
- OpenAI: ~$2.40 total ($0.08 per cafe with 50 reviews)

**Total: ~$2.50 for full 30-cafe analysis**

## Support

Questions? Check:
1. `README.md` - Full documentation
2. `CLAUDE.md` - Development notes and lessons learned
3. Code comments - Each module has usage examples

---

Ready to analyze cafes! 🚀
