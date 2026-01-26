# PRD: Phase 1 - Business Origin Section (End-to-End)

**Version**: 1.0
**Date**: 2026-01-26
**Status**: Draft
**Owner**: Product Intelligence Team

---

## Executive Summary

Build an end-to-end system to research, structure, and publish the **Business Origin** section for 5 apps. This is the MVP to validate the entire workflow before scaling to all 6 sections.

**Timeline**: 3-4 days
**Apps to Test**: Flo Health, TikTok, Spotify, Airbnb, Uber
**Deliverables**: 5 case studies with Business Origin section published on Replit + Obsidian

---

## Goals & Non-Goals

### Goals
- ✅ Validate end-to-end workflow with ONE section before scaling
- ✅ Prove Research Agent can gather accurate data
- ✅ Prove Structuring Agent can format data correctly
- ✅ Prove Markdown Agent can create quality narratives
- ✅ Prove Publish Agent can deploy to Replit + Obsidian
- ✅ Complete 5 case studies to test variety

### Non-Goals
- ❌ Not building all 6 sections (just Business Origin)
- ❌ Not building Synthesis Agent yet (Phase 7)
- ❌ Not building Knowledge Brain connections yet
- ❌ Not building pattern detection yet
- ❌ Not optimizing for speed (quality over speed)

---

## Phase Overview

```
INPUT: App Name ("Flo Health")
    ↓
┌─────────────────────────────────────┐
│  1. RESEARCH AGENT                  │
│  - Deep web research                │
│  - Extract structured findings      │
│  - Cite all sources                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. STRUCTURING AGENT               │
│  - Convert to database schema       │
│  - Validate data quality            │
│  - Store in Supabase                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. MARKDOWN AGENT                  │
│  - Generate narrative markdown      │
│  - Add context & analysis           │
│  - Save locally                     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. PUBLISH AGENT                   │
│  - Publish to Replit (public site)  │
│  - Publish to Obsidian (vault)      │
└─────────────────────────────────────┘
    ↓
OUTPUT:
✅ Structured data in Supabase
✅ Markdown file locally
✅ Public Replit site
✅ Obsidian vault entry
```

---

## 1. Research Agent (Section 1: Business Origin)

### Purpose
Deep research on Business Origin for a given app.

### Input
- App name (e.g., "Flo Health")

### Output
Structured findings JSON:

```json
{
  "app_name": "Flo Health",
  "section": "business_origin",
  "findings": {
    "founders": {
      "names": ["Dmitry Gurski", "Yuri Gurski"],
      "backgrounds": ["Tech entrepreneur", "Tech entrepreneur"],
      "source": "https://techcrunch.com/..."
    },
    "founding_year": {
      "year": 2015,
      "source": "https://flo.health/about"
    },
    "founding_country": {
      "country": "Belarus",
      "source": "https://flo.health/about"
    },
    "problem_solved": {
      "description": "Women's health tracking gap - existing apps were generic, inaccurate, and not personalized",
      "source": "https://..."
    },
    "trends_capitalized_on": {
      "trends": [
        "AI/ML for personalization",
        "Growing focus on women's health",
        "Mobile-first approach",
        "Freemium SaaS model"
      ],
      "source": "https://..."
    },
    "initial_market": {
      "description": "Women aged 18-45 interested in health tracking",
      "size": "50M+ potential users",
      "source": "https://..."
    },
    "founding_story": {
      "narrative": "In 2015, brothers Dmitry and Yuri Gurski identified a significant gap in women's health tracking...",
      "source": "https://..."
    },
    "early_monetization": {
      "model": "Freemium",
      "description": "Free app with premium subscription ($49.99/year)",
      "source": "https://..."
    },
    "early_user_acquisition": {
      "strategies": [
        "App store optimization",
        "Word of mouth",
        "Social media (Instagram, TikTok)",
        "Community building"
      ],
      "source": "https://..."
    },
    "funding": {
      "rounds": [
        {
          "round": "Series A",
          "year": 2018,
          "amount": "$12M",
          "source": "https://..."
        }
      ]
    },
    "competitors": {
      "main_competitors": ["Clue", "Period Tracker", "Ovia"],
      "differentiation": "AI-powered predictions, comprehensive health insights",
      "source": "https://..."
    }
  }
}
```

### Research Process

For each app, the Research Agent will:

**1. Search for founder information**
- Google: "[App name] founder"
- Google: "[Founder name] biography"
- LinkedIn profiles
- Company blog posts
- News articles (TechCrunch, The Verge, etc.)

**2. Search for founding story**
- Google: "[App name] founding story"
- Google: "[App name] history"
- Medium articles
- Podcast interviews (search transcripts)
- YouTube interviews (search transcripts)
- Company "About" page

**3. Search for market context**
- Google: "[Industry] market [founding year]"
- Google: "[Problem] market opportunity"
- Industry reports (Gartner, CB Insights)
- News articles from founding year
- Academic papers (if relevant)

**4. Search for trends capitalized on**
- Google: "[App name] trends"
- Google: "[App name] AI/ML"
- Tech blogs (TechCrunch, Product Hunt)
- Industry analysis

**5. Search for early monetization**
- Google: "[App name] monetization"
- Google: "[App name] pricing history"
- App store pages (current + Wayback Machine)
- News articles

**6. Search for user acquisition**
- Google: "[App name] user acquisition"
- Google: "[App name] growth strategy"
- Product Hunt posts
- Early reviews

**7. Search for funding**
- Crunchbase
- PitchBook
- News articles
- Company announcements

**8. Search for competitors**
- Google: "[App name] competitors"
- App store similar apps
- Industry reports

### Implementation

**Agent Type**: Claude with web search capability (Perplexity or Tavily API)

**Prompt Template**:
```markdown
You are a research agent analyzing the Business Origin of {APP_NAME}.

Your task is to research and extract the following information:

1. **Founders**
   - Names
   - Backgrounds (education, previous companies)
   - LinkedIn profiles

2. **Founding Details**
   - Year founded
   - Country founded
   - Initial team size

3. **Problem Solved**
   - What problem did they identify?
   - Why was it important?
   - Who had this problem?

4. **Trends Capitalized On**
   - What market trends enabled this?
   - What technology trends enabled this?
   - What behavioral trends enabled this?

5. **Initial Market**
   - Who were the first users?
   - How big was the market?
   - Why this market?

6. **Founding Story**
   - How did founders come up with the idea?
   - What was the "aha moment"?
   - Why did they decide to build it?

7. **Early Monetization**
   - How did they plan to make money?
   - What was the pricing model?
   - When did they start charging?

8. **Early User Acquisition**
   - How did they get first 1000 users?
   - What channels did they use?
   - What worked / didn't work?

9. **Funding** (if applicable)
   - Did they raise funding?
   - How much? When?
   - Who invested?

10. **Competitors**
    - Who were the main competitors at launch?
    - How did they differentiate?

For EACH finding, you MUST include:
- The actual data
- The source URL
- Your confidence level (High/Medium/Low)

Use deep web search. Search multiple sources. Verify facts across sources.

Return structured JSON in this format:
{
  "app_name": "{APP_NAME}",
  "section": "business_origin",
  "findings": {
    "founders": {
      "names": [...],
      "backgrounds": [...],
      "source": "https://...",
      "confidence": "high"
    },
    ...
  }
}
```

---

## 2. Structuring Agent

### Purpose
Convert research findings JSON to structured format ready for Supabase.

### Input
Research findings JSON from Research Agent

### Output
Structured data ready for database:

```json
{
  "app_id": 1,
  "section_type": "business_origin",
  "data": {
    "founders": "Dmitry Gurski, Yuri Gurski",
    "founder_backgrounds": "Tech entrepreneur; Tech entrepreneur",
    "founded_year": 2015,
    "founded_country": "Belarus",
    "problem_solved": "Women's health tracking gap - existing apps were generic...",
    "trends_capitalized_on": "AI/ML for personalization; Growing focus on women's health; Mobile-first approach; Freemium SaaS model",
    "initial_market": "Women aged 18-45 interested in health tracking",
    "initial_market_size": "50M+ potential users",
    "founding_story": "In 2015, brothers Dmitry and Yuri Gurski identified...",
    "early_monetization": "Freemium - Free app with premium subscription ($49.99/year)",
    "early_user_acquisition": "App store optimization; Word of mouth; Social media (Instagram, TikTok); Community building",
    "funding_rounds": "Series A (2018, $12M)",
    "competitors": "Clue, Period Tracker, Ovia",
    "differentiation": "AI-powered predictions, comprehensive health insights",
    "sources": "https://...; https://...; https://..."
  }
}
```

### Implementation

**Agent Type**: Claude with JSON parsing

**Process**:
1. Parse research findings JSON
2. Extract key entities
3. Flatten nested structures
4. Standardize formats (dates, lists)
5. Validate required fields
6. Create database record

**Validation Rules**:
- `founders` must not be empty
- `founded_year` must be 1900-2026
- `founding_country` must be valid country
- `sources` must contain at least 3 URLs
- All text fields must be < 5000 characters

---

## 3. Markdown Agent

### Purpose
Create human-readable markdown narrative from structured data.

### Input
Structured data from Structuring Agent

### Output
Markdown file saved to `app_analyses/{app-name}/01-business-origin.md`:

```markdown
# Business Origin: Flo Health

**Founded**: 2015
**Founders**: Dmitry Gurski, Yuri Gurski
**Country**: Belarus
**Industry**: Health & Fitness

---

## Founders

**Dmitry Gurski** and **Yuri Gurski** are brothers and tech entrepreneurs who founded Flo Health in 2015.

**Backgrounds**:
- Both have backgrounds in technology and entrepreneurship
- [Add more details from research]

**LinkedIn**: [Links]

---

## The Problem They Solved

In 2015, the Gurski brothers identified a significant gap in women's health tracking:

**The Problem:**
- Existing apps were generic and inaccurate
- No personalization based on individual health data
- Lack of comprehensive health insights beyond cycle tracking
- Poor prediction accuracy

**Why It Mattered:**
- 50M+ women aged 18-45 needed better health tracking
- Women's health was significantly underserved in tech
- Existing solutions didn't leverage modern AI/ML

**Who Had This Problem:**
- Women aged 18-45
- Particularly those interested in fertility tracking
- Users frustrated with existing generic apps

---

## Trends They Capitalized On

Flo Health launched at the intersection of several major trends:

### 1. AI/ML for Personalization
- Machine learning models could predict cycles more accurately
- Personalization was becoming table stakes in consumer apps
- AI could provide insights impossible with manual tracking

### 2. Growing Focus on Women's Health
- Increased awareness of women's health issues
- Growing demand for women-specific health solutions
- Femtech emerging as a category

### 3. Mobile-First Approach
- Smartphone penetration reaching critical mass
- Users comfortable with health tracking apps
- Mobile-first user experience expectations

### 4. Freemium SaaS Model
- Proven model for consumer apps
- Low barrier to entry, high conversion potential
- Recurring revenue model

---

## The Initial Market

**Target Users**: Women aged 18-45 interested in health tracking

**Market Size**: 50M+ potential users

**Why This Market:**
- Large addressable market
- Underserved by existing solutions
- High engagement potential (daily use)
- Clear monetization path

---

## The Founding Story

In 2015, brothers Dmitry and Yuri Gurski identified a significant gap in women's health tracking. [Expand with narrative from research]

**The "Aha Moment":**
[Details from research]

**Why They Built It:**
[Details from research]

**Early Challenges:**
[Details from research]

---

## Early Monetization

**Model**: Freemium

**How It Worked:**
- **Free Tier**: Basic cycle tracking and predictions
- **Premium Tier** ($49.99/year): Advanced features and personalized insights
  - Detailed health reports
  - Premium content
  - Unlimited access to health assistant
  - No ads

**Conversion Strategy:**
- Free tier creates habit (daily logging)
- Premium offers meaningful upgrades
- Health insights drive conversion

---

## Early User Acquisition

### Strategies That Worked

**1. App Store Optimization**
- Optimized for "period tracker", "women's health" keywords
- High-quality screenshots and description
- Strong early reviews

**2. Word of Mouth**
- Viral growth through user recommendations
- Community features encouraged sharing
- High NPS from early users

**3. Social Media**
- Organic growth on Instagram and TikTok
- User-generated content
- Health influencer partnerships

**4. Community Building**
- Built forums and community features
- Created content around women's health
- Engaged with users directly

### First 1000 Users
[Details from research about how they got their first users]

---

## Funding

**Series A (2018)**
- **Amount**: $12M
- **Investors**: [Details]
- **Use of Funds**: [Details]

[Add more funding rounds if applicable]

---

## Competitors & Differentiation

### Main Competitors at Launch
1. **Clue** - European competitor
2. **Period Tracker** - Simple tracking app
3. **Ovia** - Fertility-focused app

### How Flo Differentiated
- **AI-Powered Predictions**: More accurate than rule-based competitors
- **Comprehensive Health Insights**: Beyond just cycle tracking
- **Modern UX**: Better design than competitors
- **Personalization**: Tailored to individual users

### Competitive Advantage
- Better prediction accuracy (AI/ML)
- More comprehensive health tracking
- Superior user experience
- Stronger community features

---

## Key Insights

1. **Market Timing**: Launched during femtech wave (2015-2018)
2. **Technology Advantage**: AI/ML created moat vs competitors
3. **Freemium Model**: Proved effective for health tracking apps
4. **Community**: Built strong user community early

---

## Sources

- [Source 1 - Company About Page](https://flo.health/about)
- [Source 2 - TechCrunch Article](https://...)
- [Source 3 - Founder Interview](https://...)
- [Source 4 - Funding Announcement](https://...)
- [Source 5 - Industry Report](https://...)

---

**Last Updated**: 2026-01-26
**Research Confidence**: High (verified across 5+ sources)
```

### Implementation

**Agent Type**: Claude with markdown generation

**Process**:
1. Read structured data from Supabase
2. Create narrative sections:
   - Start with overview (founders, year, country)
   - Expand problem solved with context
   - Explain trends with detail
   - Tell founding story as narrative
   - Describe monetization clearly
   - Detail user acquisition strategies
   - List competitors with differentiation
   - Add key insights
3. Add proper markdown formatting
4. Include all sources
5. Save to local file

**Quality Checks**:
- All sections present
- Narrative flows well
- Sources cited
- Markdown formatting correct
- File saved to correct location

---

## 4. Publish Agent

### Purpose
Publish markdown to Replit and Obsidian.

### Input
- Markdown file from Markdown Agent
- App metadata

### Output
- Replit URL (public case study site)
- Obsidian file (local vault)

### 4.1 Replit Publishing

**Process**:

1. **Create Replit Project**
   - Project name: `case-study-{app-slug}`
   - Template: HTML/CSS/JS
   - Public visibility

2. **Create File Structure**:
   ```
   /
   ├── index.html              # Main page
   ├── style.css               # Styling
   ├── script.js               # Optional JS
   ├── 01-business-origin.md   # Markdown content
   └── README.md               # Project info
   ```

3. **Generate index.html**:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>{App Name} - Business Origin</title>
       <link rel="stylesheet" href="style.css">
       <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
   </head>
   <body>
       <nav>
           <a href="/">← All Case Studies</a>
       </nav>

       <main>
           <div id="content"></div>
       </main>

       <script>
           // Load and render markdown
           fetch('01-business-origin.md')
               .then(response => response.text())
               .then(markdown => {
                   document.getElementById('content').innerHTML = marked.parse(markdown);
               });
       </script>
   </body>
   </html>
   ```

4. **Generate style.css**:
   ```css
   * {
       margin: 0;
       padding: 0;
       box-sizing: border-box;
   }

   body {
       font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
       line-height: 1.6;
       color: #333;
       max-width: 800px;
       margin: 0 auto;
       padding: 20px;
   }

   nav {
       margin-bottom: 30px;
       padding-bottom: 10px;
       border-bottom: 1px solid #eee;
   }

   nav a {
       color: #0066cc;
       text-decoration: none;
   }

   nav a:hover {
       text-decoration: underline;
   }

   h1 {
       font-size: 2.5em;
       margin-bottom: 0.5em;
       color: #000;
   }

   h2 {
       font-size: 1.8em;
       margin-top: 1.5em;
       margin-bottom: 0.5em;
       color: #222;
   }

   h3 {
       font-size: 1.3em;
       margin-top: 1.2em;
       margin-bottom: 0.4em;
       color: #444;
   }

   p {
       margin-bottom: 1em;
   }

   ul, ol {
       margin-left: 2em;
       margin-bottom: 1em;
   }

   code {
       background: #f4f4f4;
       padding: 2px 6px;
       border-radius: 3px;
       font-family: 'Monaco', 'Courier New', monospace;
   }

   pre {
       background: #f4f4f4;
       padding: 15px;
       border-radius: 5px;
       overflow-x: auto;
       margin-bottom: 1em;
   }

   blockquote {
       border-left: 4px solid #0066cc;
       padding-left: 15px;
       margin-left: 0;
       margin-bottom: 1em;
       color: #666;
   }

   a {
       color: #0066cc;
   }

   hr {
       border: none;
       border-top: 1px solid #eee;
       margin: 2em 0;
   }
   ```

5. **Upload Files**
   - Upload markdown file
   - Upload generated HTML/CSS
   - Set as public project

6. **Return URL**
   - Format: `https://{project-slug}.{username}.repl.co`

**Example Output**:
```
Replit URL: https://case-study-flo-health.yourusername.repl.co
```

### 4.2 Obsidian Publishing

**Process**:

1. **Create Vault Structure** (if doesn't exist):
   ```
   /case-studies/
   ├── _Index.md                    # Index of all case studies
   ├── _Templates/                  # Section templates
   │   └── business_origin.md
   ├── Flo Health/
   │   ├── 01_Business_Origin.md    # This file
   │   └── _metadata.json
   ├── TikTok/
   │   ├── 01_Business_Origin.md
   │   └── _metadata.json
   └── ...
   ```

2. **Save Markdown File**
   - Path: `/case-studies/{App Name}/01_Business_Origin.md`
   - Format: Standard markdown
   - Add Obsidian frontmatter

3. **Add Frontmatter**:
   ```yaml
   ---
   title: "Business Origin: Flo Health"
   app: "Flo Health"
   section: "Business Origin"
   section_number: 1
   status: "complete"
   created: "2026-01-26"
   updated: "2026-01-26"
   tags:
     - case-study
     - flo-health
     - business-origin
     - health-fitness
   replit_url: "https://case-study-flo-health.yourusername.repl.co"
   ---
   ```

4. **Create Metadata File**:
   ```json
   {
     "app_name": "Flo Health",
     "category": "Health & Fitness",
     "founded_year": 2015,
     "founders": ["Dmitry Gurski", "Yuri Gurski"],
     "sections_completed": ["business_origin"],
     "replit_url": "https://case-study-flo-health.yourusername.repl.co",
     "created_at": "2026-01-26",
     "updated_at": "2026-01-26"
   }
   ```

5. **Update Index File**:
   ```markdown
   # Case Studies Index

   ## Health & Fitness
   - [[Flo Health/01_Business_Origin|Flo Health - Business Origin]] ✅

   ## Social Media
   - [[TikTok/01_Business_Origin|TikTok - Business Origin]] ✅

   ## Music Streaming
   - [[Spotify/01_Business_Origin|Spotify - Business Origin]] ✅

   ## Travel & Hospitality
   - [[Airbnb/01_Business_Origin|Airbnb - Business Origin]] ✅

   ## Transportation
   - [[Uber/01_Business_Origin|Uber - Business Origin]] ✅
   ```

**Example Output**:
```
Obsidian Path: /case-studies/Flo Health/01_Business_Origin.md
```

---

## 5. Database Schema (Supabase)

### Tables for Phase 1

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Apps table (main entities)
CREATE TABLE apps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  category TEXT,
  website TEXT,
  founded_year INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- App sections table (flexible JSONB storage)
CREATE TABLE app_sections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
  section_type TEXT NOT NULL, -- 'business_origin', 'user_behavior', etc.
  section_number INTEGER NOT NULL,
  data JSONB NOT NULL, -- Flexible storage for section data
  markdown_path TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(app_id, section_type)
);

-- Case studies table (publishing metadata)
CREATE TABLE case_studies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
  section_type TEXT NOT NULL,
  markdown_path TEXT,
  replit_url TEXT,
  obsidian_path TEXT,
  status TEXT DEFAULT 'draft', -- draft, in_progress, complete, published
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(app_id, section_type)
);

-- Create indexes
CREATE INDEX app_sections_app_id_idx ON app_sections(app_id);
CREATE INDEX app_sections_type_idx ON app_sections(section_type);
CREATE INDEX case_studies_app_id_idx ON case_studies(app_id);
CREATE INDEX case_studies_status_idx ON case_studies(status);
```

### Example Data

```sql
-- Insert app
INSERT INTO apps (name, slug, category, website, founded_year)
VALUES ('Flo Health', 'flo-health', 'Health & Fitness', 'https://flo.health', 2015);

-- Insert section data
INSERT INTO app_sections (app_id, section_type, section_number, data, markdown_path)
VALUES (
  'flo-health-uuid',
  'business_origin',
  1,
  '{
    "founders": "Dmitry Gurski, Yuri Gurski",
    "founded_year": 2015,
    "founded_country": "Belarus",
    "problem_solved": "Women health tracking gap...",
    "trends_capitalized_on": "AI/ML for personalization; ...",
    "sources": "https://...; https://..."
  }'::jsonb,
  '/app_analyses/flo-health/01-business-origin.md'
);

-- Insert case study
INSERT INTO case_studies (app_id, section_type, markdown_path, replit_url, obsidian_path, status)
VALUES (
  'flo-health-uuid',
  'business_origin',
  '/app_analyses/flo-health/01-business-origin.md',
  'https://case-study-flo-health.yourusername.repl.co',
  '/case-studies/Flo Health/01_Business_Origin.md',
  'published'
);
```

---

## 6. API Design

### Endpoints

```bash
# 1. Start a new research
POST /api/research/business-origin
{
  "app_name": "Flo Health"
}
→ Response: {
    "case_study_id": "uuid",
    "status": "researching",
    "estimated_time": "2-3 minutes"
  }

# 2. Get research status
GET /api/research/{case_study_id}/status
→ Response: {
    "case_study_id": "uuid",
    "status": "complete",
    "progress": {
      "research": "complete",
      "structuring": "complete",
      "markdown": "complete",
      "publishing": "complete"
    },
    "replit_url": "https://...",
    "obsidian_path": "/case-studies/..."
  }

# 3. Get business origin data
GET /api/apps/{app_slug}/business-origin
→ Response: {
    "app_name": "Flo Health",
    "section": "business_origin",
    "data": { ... },
    "markdown_url": "https://...",
    "sources": [...]
  }

# 4. Get all case studies
GET /api/case-studies
→ Response: [
    {
      "app_name": "Flo Health",
      "slug": "flo-health",
      "sections_completed": ["business_origin"],
      "replit_url": "https://...",
      "created_at": "2026-01-26"
    },
    ...
  ]

# 5. Republish case study
POST /api/case-studies/{case_study_id}/republish
→ Response: {
    "status": "published",
    "replit_url": "https://...",
    "obsidian_path": "/case-studies/..."
  }
```

---

## 7. Implementation Steps

### Day 1: Setup & Research Agent (8 hours)

**Morning (4 hours)**
- [ ] Set up Supabase project
- [ ] Run schema.sql to create tables
- [ ] Set up project structure
- [ ] Install dependencies

**Afternoon (4 hours)**
- [ ] Build Research Agent
- [ ] Integrate web search API (Perplexity/Tavily)
- [ ] Test with Flo Health
- [ ] Iterate based on results
- [ ] Validate output quality

**Deliverable**: Research Agent that can research Flo Health

---

### Day 2: Structuring & Markdown Agents (8 hours)

**Morning (4 hours)**
- [ ] Build Structuring Agent
- [ ] Implement data validation
- [ ] Integrate with Supabase
- [ ] Test with Flo Health data
- [ ] Validate database records

**Afternoon (4 hours)**
- [ ] Build Markdown Agent
- [ ] Create markdown templates
- [ ] Test narrative generation
- [ ] Review output quality
- [ ] Iterate and improve

**Deliverable**: Structured data in Supabase + markdown file

---

### Day 3: Publishing Agent (8 hours)

**Morning (4 hours)**
- [ ] Build Replit publishing logic
- [ ] Create HTML/CSS templates
- [ ] Test with Flo Health
- [ ] Verify public URL works

**Afternoon (4 hours)**
- [ ] Build Obsidian publishing logic
- [ ] Create vault structure
- [ ] Test with Flo Health
- [ ] Update index file
- [ ] Verify file organization

**Deliverable**: Published case study on Replit + Obsidian

---

### Day 4: Scale to 5 Apps (8 hours)

**Morning (4 hours)**
- [ ] Research TikTok (end-to-end)
- [ ] Research Spotify (end-to-end)
- [ ] Fix any bugs discovered

**Afternoon (4 hours)**
- [ ] Research Airbnb (end-to-end)
- [ ] Research Uber (end-to-end)
- [ ] Validate all 5 case studies
- [ ] Polish and document

**Deliverable**: 5 complete case studies

---

## 8. Test Apps

### 1. Flo Health
- **Category**: Health & Fitness
- **Founded**: 2015
- **Why**: Well-documented, clear problem-solution, good founding story
- **Research Difficulty**: Easy

### 2. TikTok
- **Category**: Social Media
- **Founded**: 2016
- **Why**: Interesting international story (ByteDance), rapid growth
- **Research Difficulty**: Medium (lots of info, need to filter)

### 3. Spotify
- **Category**: Music Streaming
- **Founded**: 2006
- **Why**: Long history, interesting pivots, well-documented
- **Research Difficulty**: Easy (extensive documentation)

### 4. Airbnb
- **Category**: Travel & Hospitality
- **Founded**: 2008
- **Why**: Famous founding story (cereal boxes), clear narrative
- **Research Difficulty**: Easy (famous story)

### 5. Uber
- **Category**: Transportation
- **Founded**: 2009
- **Why**: Well-known, controversial, interesting competition
- **Research Difficulty**: Easy (extensive coverage)

**Why These 5?**
- Different industries (variety)
- Different founding years (2006-2016)
- Different business models
- All well-documented
- Mix of B2C and marketplace models

---

## 9. Success Criteria

### Phase 1 is Complete When:

**Quantitative**:
- [ ] 5 apps researched
- [ ] 5 Supabase records created
- [ ] 5 markdown files generated
- [ ] 5 Replit sites published
- [ ] 5 Obsidian files created
- [ ] 100% of required fields populated
- [ ] 0 manual interventions needed

**Qualitative**:
- [ ] Research is accurate (cross-verified sources)
- [ ] Structured data is complete
- [ ] Markdown narratives are well-written
- [ ] Replit sites are public and accessible
- [ ] Obsidian vault is well-organized
- [ ] All sources are properly cited

### Quality Thresholds:

**Research Quality**:
- ✅ 3+ sources per finding
- ✅ High confidence on 80%+ of findings
- ✅ All major facts verified

**Structured Data Quality**:
- ✅ All required fields present
- ✅ Data formatted correctly
- ✅ Valid values (years, countries, etc.)

**Markdown Quality**:
- ✅ Reads like professional case study
- ✅ Clear narrative flow
- ✅ Proper formatting
- ✅ All sections present

**Publishing Quality**:
- ✅ Replit sites load correctly
- ✅ Mobile responsive
- ✅ Clean, readable design
- ✅ Obsidian files organized properly

---

## 10. Deliverables

### By End of Day 4:

**1. Five Replit Sites**
- https://case-study-flo-health.yourusername.repl.co
- https://case-study-tiktok.yourusername.repl.co
- https://case-study-spotify.yourusername.repl.co
- https://case-study-airbnb.yourusername.repl.co
- https://case-study-uber.yourusername.repl.co

**2. Obsidian Vault**
```
/case-studies/
├── _Index.md
├── Flo Health/
│   ├── 01_Business_Origin.md
│   └── _metadata.json
├── TikTok/
│   ├── 01_Business_Origin.md
│   └── _metadata.json
├── Spotify/
│   ├── 01_Business_Origin.md
│   └── _metadata.json
├── Airbnb/
│   ├── 01_Business_Origin.md
│   └── _metadata.json
└── Uber/
    ├── 01_Business_Origin.md
    └── _metadata.json
```

**3. Supabase Database**
- 5 records in `apps` table
- 5 records in `app_sections` table
- 5 records in `case_studies` table

**4. Documentation**
- Research methodology doc
- Agent prompts and configs
- Data quality report
- Lessons learned doc
- Next steps plan (for Section 2)

---

## 11. Success Metrics

### Quantitative Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Apps researched | 5 | Count in database |
| Average research time | < 3 min | Time per app |
| Data accuracy | > 90% | Manual spot-check |
| Sources per finding | ≥ 3 | Count in structured data |
| Publishing success rate | 100% | All sites accessible |
| Manual interventions | 0 | Track during execution |

### Qualitative Metrics

| Metric | Assessment |
|--------|------------|
| Research quality | Manual review - comprehensive & accurate? |
| Narrative quality | Manual review - reads well? |
| Site design | Manual review - professional? |
| Obsidian organization | Manual review - easy to navigate? |

---

## 12. Next Steps After Phase 1

### If Phase 1 Succeeds:

**Immediate (Week 2)**:
- Build Section 2: User Behavior
- Use same 5 apps
- Validate workflow works for different section type

**Short-term (Weeks 3-4)**:
- Build Section 3: Growth Loops (Inception)
- Build Section 4: UX Analysis
- Continue with same 5 apps

**Medium-term (Weeks 5-6)**:
- Build Section 5: Voice of Customer
- Build Section 6: Growth Loops (Post-AI)
- Now have 5 complete case studies (all 6 sections)

**Long-term (Weeks 7-8)**:
- Build Synthesis Agent
- Extract frameworks and patterns
- Connect to Knowledge Brain

### If Phase 1 Fails:

**Diagnose Issues**:
- Research accuracy low? → Improve search strategy
- Structuring errors? → Refine data model
- Markdown quality poor? → Improve templates
- Publishing failures? → Fix deployment logic

**Iterate**:
- Fix identified issues
- Test with 1-2 apps
- Re-run Phase 1

---

## 13. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Research inaccuracy** | High | Medium | Use multiple sources, verify facts, human review |
| **API failures** (web search) | High | Low | Implement retry logic, fallback to manual |
| **Replit publishing failures** | Medium | Medium | Test early, have manual backup, save markdown locally |
| **Data quality issues** | High | Medium | Validate before storing, manual spot-checks |
| **Time overruns** | Low | High | Focus on 1 app first, cut scope if needed |
| **Source URLs broken** | Low | Low | Use Wayback Machine, multiple sources |
| **Markdown formatting issues** | Low | Low | Test templates early, validate output |

---

## 14. Open Questions

### Technical
1. ✅ Which web search API? (Perplexity vs Tavily vs Google Custom Search)
2. Should we store raw research findings or just structured data?
3. Should we cache research results to avoid re-searching?
4. Should we version control case studies?

### Quality
5. Should we manually verify research before publishing?
6. What's acceptable accuracy threshold? (90%? 95%?)
7. Should we flag low-confidence findings in markdown?
8. Should we include confidence scores in published sites?

### Publishing
9. Should we publish all case studies or just manually approved ones?
10. Should we add images/screenshots to markdown?
11. Should we create a gallery/index page on Replit?
12. Should we enable comments on Replit sites?

### Data
13. Should we include financial data (revenue, valuation)?
14. Should we track competitor data in detail?
15. Should we include founder social media links?
16. Should we track founding team size over time?

**Recommend**: Answer these before Day 1 kickoff

---

## 15. Dependencies

### External Services
- **Supabase**: Database hosting
- **Web Search API**: Perplexity or Tavily (decide before Day 1)
- **Replit**: Case study hosting
- **OpenAI**: For Research/Structuring/Markdown agents

### Internal
- Knowledge Brain system (won't integrate until Phase 7)
- Obsidian vault (create before Day 1)

### Tools
- Claude API access
- Replit account
- Supabase project
- Web search API key

---

## 16. Budget Estimate

### API Costs (per app)
- Web search API: ~$0.50/app (assuming 20 searches)
- Claude API: ~$0.30/app (research + structuring + markdown)
- **Total per app**: ~$0.80

### Total Phase 1 Cost
- 5 apps × $0.80 = **~$4**

### Hosting
- Supabase: Free tier (sufficient for Phase 1)
- Replit: Free tier (sufficient for 5 sites)
- **Total hosting**: **$0**

**Phase 1 Total Budget**: ~$4

---

## 17. Team & Roles

**For Phase 1 (Solo)**:
- You build all 4 agents
- You validate quality
- You publish case studies
- You document learnings

**For Future Phases**:
- Consider splitting into specialist roles:
  - Research specialist
  - Markdown/writing specialist
  - Publishing/design specialist
  - Quality assurance

---

## Approval & Sign-off

**Approved By**: [Your Name]
**Date**: 2026-01-26
**Status**: Ready to Execute

**Next Step**: Begin Day 1 - Setup & Research Agent

---

**END OF PRD**
