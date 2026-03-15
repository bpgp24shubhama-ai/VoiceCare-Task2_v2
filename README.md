# VoiceCare.ai - AI Growth Engine Agent

An AI-powered growth hacking agent that uses **OpenAI GPT-5 with web search and reasoning** to grow VoiceCare.ai's LinkedIn presence from 2,900 to 10,000 followers in 3 months and boost visibility on AI engines (ChatGPT, Perplexity, Gemini, etc.).

## Architecture

```
agent/
├── core.py                  # GPT-5 engine with web search (Responses API)
├── orchestrator.py          # Central coordinator for all modules
├── modules/
│   ├── competitor_analyzer.py   # Real-time competitive intelligence
│   ├── linkedin_growth.py       # LinkedIn content & engagement strategies
│   ├── ai_visibility.py         # GEO - Generative Engine Optimization
│   ├── content_generator.py     # Multi-format content generation
│   ├── growth_hacks.py          # Growth hacking frameworks & playbooks
│   └── analytics.py             # Tracking, reporting & recommendations
├── strategies/              # Strategy templates
└── templates/               # Content templates
```

## Key Features

- **GPT-5 with Web Search**: Every query uses real-time web search for current data, competitor moves, and trending topics
- **Competitive Intelligence**: Live analysis of Observe.AI, CallMiner, Gong, Level AI, Balto and others
- **GEO (Generative Engine Optimization)**: Optimize visibility on ChatGPT, Perplexity, Gemini, Claude, Copilot
- **Content Factory**: Generate ready-to-post LinkedIn content (posts, carousels, polls, newsletters)
- **12-Week Growth Playbook**: Phased plan with weekly milestones and tactics
- **Weekly Cycles**: Automated weekly reporting, trend scanning, and content calendar generation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Agent

#### Generate Initial Strategy (run first)
```bash
python run.py strategy
```
This generates: competitive analysis, GEO audit, 12-week playbook, algorithm guide, and Week 1 content.

#### Weekly Growth Cycle
```bash
python run.py weekly 1 3100 --posts 7 --impressions 15000 --engagement 250
```

#### Generate Content On-Demand
```bash
python run.py content post "Why 73% of contact centers are failing at QA"
python run.py content carousel "The future of voice AI in customer service"
python run.py content poll "AI vs human quality assurance"
python run.py content thought_leadership "The death of traditional IVR" --exec-name "John Smith" --exec-role "CEO"
python run.py content data_post "Contact center AI adoption statistics 2026"
```

#### GEO Optimization (AI Engine Visibility)
```bash
python run.py geo
```

#### Growth Hacks
```bash
python run.py growth-hacks
```

#### Competitor Deep-Dive
```bash
python run.py competitor "Observe.AI"
```

#### Audit AI Visibility for a Query
```bash
python run.py audit "best voice analytics software"
```

#### Ask Any Question
```bash
python run.py ask "What LinkedIn content formats are getting the most reach in 2026?"
```

#### Interactive Mode
```bash
python run.py interactive
```

## How It Works

### GPT-5 Web Search Integration
The agent uses OpenAI's Responses API with `web_search_preview` tool, giving GPT-5 access to real-time web data. Every analysis, content piece, and strategy is informed by current information, not stale training data.

### The 3-Phase Growth Plan
- **Phase 1 (Weeks 1-4)**: Foundation - Profile optimization, content engine, engagement system → Target: 4,000 followers
- **Phase 2 (Weeks 5-8)**: Acceleration - Newsletter, events, influencer collabs, employee advocacy → Target: 6,500 followers
- **Phase 3 (Weeks 9-12)**: Viral Growth - Viral loops, community, PR push, partnerships → Target: 10,000 followers

### Generative Engine Optimization (GEO)
A new discipline that ensures VoiceCare.ai appears in AI-powered search responses:
- Audit current visibility across AI engines
- Create content AI engines cite (guides, data, comparisons)
- Build citation authority through third-party validation
- Optimize structured data and schema markup
- Monitor and improve AI mentions over time

## Configuration

Edit `config.yaml` to customize:
- Company details and targets
- Competitor list
- GPT-5 model settings and web search parameters
- LinkedIn content mix and posting schedule
- Hashtag strategy
- Target AI engines and search queries
- Growth hack modules to enable

## Output

All generated content and reports are saved to:
- `data/output/` - Generated content, strategies, and plans
- `data/reports/` - Weekly performance reports
