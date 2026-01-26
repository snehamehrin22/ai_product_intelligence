# Tests - Perplexity → Obsidian → Replit Pipeline

This folder contains all testing for the case study generation workflow.

## Folder Structure

```
tests/
├── README.md                    # This file
├── perplexity/                  # Perplexity API testing
│   ├── test_connection.py       # Test API connection
│   ├── prompts/                 # Research prompts
│   │   └── business_origin.txt  # Business Origin prompt
│   └── responses/               # Saved API responses
│       ├── flo_health.json
│       ├── tiktok.json
│       └── spotify.json
├── obsidian/                    # Obsidian publishing testing
│   ├── test_markdown.py         # Test markdown generation
│   └── templates/               # Markdown templates
│       └── business_origin.md
├── replit/                      # Replit publishing testing
│   ├── test_publish.py          # Test Replit publishing
│   └── templates/               # HTML/CSS templates
│       ├── index.html
│       └── style.css
└── outputs/                     # Generated outputs for testing
    ├── flo_health/
    │   ├── perplexity_response.json
    │   ├── obsidian.md
    │   └── replit_url.txt
    ├── tiktok/
    └── spotify/
```

## Workflow

1. **Perplexity Research**: Get research from Perplexity Deep Research
2. **Obsidian Publishing**: Generate markdown and save to vault
3. **Replit Publishing**: Publish to public Replit site

## Test Apps

1. Flo Health
2. TikTok
3. Spotify
