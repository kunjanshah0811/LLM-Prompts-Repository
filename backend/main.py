from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import databases
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, JSON
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://promptuser:promptpass@localhost:5432/promptdb")

#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://llm_prompts_db_user:W0TGzcdGlz41K8qjToErNhG9A8Dy5P1Z@dpg-d61pbcvgi27c73esnov0-a/llm_prompts_db")

database = databases.Database(DATABASE_URL)
metadata = MetaData()

# Define prompts table
prompts = Table(
    "prompts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("prompt_text", Text, nullable=False),
    Column("category", String(100), nullable=False),
    Column("tags", JSON, default=[]),
    Column("source", String(255), nullable=True),
    Column("views", Integer, default=0),
    Column("created_at", DateTime, default=datetime.utcnow),
)

# Create engine and tables
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# FastAPI app
app = FastAPI(
    title="LLM Prompts Repository API",
    description="API for sharing and discovering LLM prompts for social science research",
    version="1.0.0"
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PromptCreate(BaseModel):
    title: str
    prompt_text: str
    category: str
    tags: List[str] = []
    source: Optional[str] = None

class PromptResponse(BaseModel):
    id: int
    title: str
    prompt_text: str
    category: str
    tags: List[str]
    source: Optional[str]
    views: int
    created_at: datetime

class PromptStats(BaseModel):
    total_prompts: int
    categories: dict

# Database connection events
@app.on_event("startup")
async def startup():
    await database.connect()
    # Seed database with example prompts
    await seed_database()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "LLM Prompts Repository API",
        "version": "1.0.0",
        "endpoints": {
            "prompts": "/api/prompts",
            "stats": "/api/stats"
        }
    }

@app.post("/api/prompts", response_model=PromptResponse)
async def create_prompt(prompt: PromptCreate):

    """Create a new prompt"""
    query = prompts.insert().values(
        title=prompt.title,
        prompt_text=prompt.prompt_text,
        category=prompt.category,
        tags=prompt.tags,
        source=prompt.source,
        views=0,
        created_at=datetime.utcnow()
    )
    last_record_id = await database.execute(query)
    
    # Fetch and return the created prompt
    select_query = prompts.select().where(prompts.c.id == last_record_id)
    result = await database.fetch_one(select_query)
    return dict(result)

@app.get("/api/prompts", response_model=List[PromptResponse])
async def get_prompts(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query("date", regex="^(date|popularity)$"),
    limit: int = Query(100, le=500),
    offset: int = 0
):
    """
    Get all prompts with optional filtering and sorting
    - category: Filter by category
    - search: Search in title, tags, and prompt_text
    - sort: Sort by 'date' (newest first) or 'popularity' (most views)
    - limit: Maximum number of results (max 500)
    - offset: Pagination offset
    """
    query = prompts.select()
    
    # Apply category filter
    if category:
        query = query.where(prompts.c.category == category)
    
    # Apply search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            sqlalchemy.or_(
                prompts.c.title.ilike(search_term),
                prompts.c.prompt_text.ilike(search_term),
                sqlalchemy.cast(prompts.c.tags, String).ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort == "popularity":
        query = query.order_by(prompts.c.views.desc())
    else:  # date
        query = query.order_by(prompts.c.created_at.desc())
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    results = await database.fetch_all(query)
    return [dict(row) for row in results]

@app.get("/api/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int):
    """Get a single prompt by ID and increment view count"""
    query = prompts.select().where(prompts.c.id == prompt_id)
    result = await database.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Increment view count
    update_query = (
        prompts.update()
        .where(prompts.c.id == prompt_id)
        .values(views=prompts.c.views + 1)
    )
    await database.execute(update_query)
    
    # Fetch the updated prompt with new view count
    updated_result = await database.fetch_one(query)
    
    return dict(updated_result)

@app.get("/api/categories")
async def get_categories():
    """Get all unique categories"""
    query = sqlalchemy.select(prompts.c.category).distinct()
    results = await database.fetch_all(query)
    categories = sorted([row["category"] for row in results])
    return {"categories": categories}

@app.get("/api/stats", response_model=PromptStats)
async def get_stats():
    """Get statistics about prompts"""
    # Total count
    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(prompts)
    total = await database.fetch_val(count_query)
    
    # Count by category
    category_query = (
        sqlalchemy.select(
            prompts.c.category,
            sqlalchemy.func.count().label("count")
        )
        .group_by(prompts.c.category)
    )
    category_results = await database.fetch_all(category_query)
    categories_dict = dict(sorted((row["category"], row["count"]) for row in category_results))
    
    return {
        "total_prompts": total,
        "categories": categories_dict
    }

# Seed database with social science research prompts
async def seed_database():
    """Populate database with example prompts if empty"""
    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(prompts)
    count = await database.fetch_val(count_query)
    
    if count > 0:
        return  # Database already has data
    
    example_prompts = [
        # ============================================
        # 1. DATA COLLECTION
        # ============================================
        
        # Data Extraction & APIs (3 prompts)
        {
            "title": "Twitter API Data Collection",
            "prompt_text": """Extract tweets about {topic} from the past {timeframe}.

Requirements:
- Include: tweet text, author, timestamp, engagement metrics
- Filter: {language}, exclude retweets
- Sample size: {n} tweets

Provide the data in CSV format with these columns: tweet_id, text, author, likes, retweets, timestamp.

---EXAMPLE---

Topic: climate change
Timeframe: 7 days
Language: English
N: 100

Output (CSV format):
tweet_id,text,author,likes,retweets,timestamp
1234567890,"New climate report shows...",@scientist_jane,245,89,2024-02-01 14:23:00
1234567891,"Government announces climate policy...",@news_source,1032,456,2024-02-01 15:45:00
...(98 more rows)""",
            "category": "Data Collection > Data Extraction & APIs",
            "tags": ["twitter", "api", "social-media", "data-collection"],
            "source": "Custom"
        },
        {
            "title": "Reddit Comments Scraper",
            "prompt_text": """Extract top comments from r/{subreddit} posts about {topic}.

Filters:
- Post score: minimum {min_score} upvotes
- Comment depth: top-level only
- Time period: {timeframe}

Return: post_title, comment_text, score, author, timestamp.

---EXAMPLE---

Subreddit: AskSocialScience
Topic: research methods
Min_score: 50
Timeframe: past month

Output:
Post: "What's the best way to analyze interview data?"
├─ Comment 1: "I recommend thematic analysis. Start by reading all transcripts..." (Score: 127, Author: researcher_23)
├─ Comment 2: "Grounded theory works well for exploratory studies..." (Score: 89, Author: prof_methods)
├─ Comment 3: "Consider using NVivo or Atlas.ti for coding..." (Score: 64, Author: qual_expert)""",
            "category": "Data Collection > Data Extraction & APIs",
            "tags": ["reddit", "web-scraping", "comments", "social-media"],
            "source": "Custom"
        },
        {
            "title": "Survey API Data Export",
            "prompt_text": """Export survey responses from {platform} for survey ID: {survey_id}.

Include:
- All responses (complete and partial)
- Response metadata (start time, completion time, IP location)
- Custom variables

Format: JSON with nested structure for matrix questions.

---EXAMPLE---

Platform: Qualtrics
Survey_ID: SV_abc123xyz

Output (JSON):
{
  "responses": [
    {
      "response_id": "R_xyz789",
      "status": "complete",
      "start_date": "2024-02-01 10:30:00",
      "end_date": "2024-02-01 10:45:00",
      "answers": {
        "Q1_age": 28,
        "Q2_gender": "Female",
        "Q3_satisfaction": 4
      }
    }
  ],
  "total_responses": 456
}""",
            "category": "Data Collection > Data Extraction & APIs",
            "tags": ["survey", "qualtrics", "api", "export"],
            "source": "Custom"
        },
        
        # Interview Protocols (3 prompts)
        {
            "title": "Mock Job Interview Practice",
            "prompt_text": """Act as a mock interviewer for a {job_title} position at {organization}.

Conduct a {duration}-minute {interview_type} interview. Ask relevant questions, wait for my responses, then provide constructive feedback.

Start with: "Tell me about yourself and why you're interested in this position."

---EXAMPLE---

Job: Project Manager
Organization: Tech startup
Duration: 15 minutes
Type: Behavioral

Interviewer: "Tell me about yourself and why you're interested in this position."

[Candidate responds]

Interviewer: "Good background. Now, tell me about a time when you managed a project that went off track. How did you handle it?"

[Candidate responds]

Interviewer: "That's a solid example. I noticed you emphasized communication. Can you be more specific about the tools or frameworks you used?"

Feedback: Your STAR structure was clear, but consider quantifying the impact more. For example, "reduced delays by 2 weeks" is stronger than "got back on track."

Next question: "Describe your experience with Agile methodologies..."

[Interview continues with 3-5 questions total, feedback after each]""",
            "category": "Data Collection > Interview Protocols",
            "tags": ["interview", "job-prep", "mock-interview", "career"],
            "source": "Adapted from Wolfram PromptRepository - MockInterviewer"
        },
        {
            "title": "Research Interview Guide Generator",
            "prompt_text": """Create a semi-structured interview guide for researching: {research_question}

Target participants: {population}
Interview length: {duration} minutes

Include:
1. Opening (rapport-building)
2. 5-7 main questions with probes
3. Closing questions

---EXAMPLE---

Research question: How do remote workers maintain work-life balance?
Population: Remote employees (2+ years experience)
Duration: 45 minutes

INTERVIEW GUIDE

Opening (5 min):
- Thanks for participating. This interview is confidential.
- Tell me about your current remote work setup.
- How long have you been working remotely?

Main Questions (30 min):

1. Daily Routines
   Q: "Walk me through a typical workday from start to finish."
   Probes: What time do you start? Where do you work? When do you stop?

2. Boundaries
   Q: "How do you separate work time from personal time?"
   Probes: Physical spaces? Time-based rules? Digital boundaries?

3. Challenges
   Q: "What's the hardest part about maintaining balance?"
   Probes: Can you give a specific example? How did you handle it?

4. Strategies
   Q: "What strategies have worked best for you?"
   Probes: How did you discover this? Would you recommend it to others?

5. Support Systems
   Q: "Who or what helps you maintain balance?"
   Probes: Family? Employer policies? Technology?

Closing (10 min):
- Is there anything we haven't covered that you think is important?
- Any advice for new remote workers?
- Thank you for your time.""",
            "category": "Data Collection > Interview Protocols",
            "tags": ["interview-guide", "qualitative", "semi-structured", "research"],
            "source": "Custom"
        },
        {
            "title": "Focus Group Discussion Protocol",
            "prompt_text": """Design a focus group protocol for: {topic}

Participants: {n} people, {demographics}
Duration: {duration} minutes

Include: introduction, ice-breaker, discussion questions, closing.

---EXAMPLE---

Topic: Student perceptions of online learning
Participants: 6-8 undergraduate students
Duration: 90 minutes

FOCUS GROUP PROTOCOL

Introduction (10 min):
"Welcome! Today we're discussing online learning experiences. There are no right or wrong answers. Please speak openly, and it's okay to disagree with each other."

Ground rules: One person speaks at a time, respect all opinions, phones on silent.

Ice-breaker (10 min):
"Let's go around the room. Share your name, major, and one word that describes your online learning experience this semester."

Discussion Questions (60 min):

1. Overall Experience (15 min)
"Think back to your first online class. What surprised you most?"
- Follow-up: How has your view changed since then?

2. Engagement (15 min)
"Some students say they feel disconnected in online classes. Does this resonate with you? Why or why not?"
- Probe: What makes you feel connected/disconnected?

3. Learning Effectiveness (15 min)
"Do you feel you learn as well online as in-person? What makes the difference?"
- Probe: Specific examples?

4. Improvements (15 min)
"If you could change one thing about online learning, what would it be?"
- Have participants vote on top suggestions

Closing (10 min):
"Any final thoughts? Thank you for participating. Your insights are valuable."

Moderator notes: Watch for quiet participants and invite them in. Manage dominant speakers politely.""",
            "category": "Data Collection > Interview Protocols",
            "tags": ["focus-group", "qualitative", "discussion", "protocol"],
            "source": "Custom"
        },
        
        # ============================================
        # 2. DATA PREPARATION
        # ============================================
        
        # Text Preprocessing (2 prompts)
        {
            "title": "Social Media Text Cleaner",
            "prompt_text": """Clean this social media text for analysis:

Text: {raw_text}

Remove: URLs, @mentions, hashtags, emojis
Fix: Abbreviations (e.g., "u" → "you"), typos
Preserve: Negations, capitalization for emphasis

Return cleaned text.

---EXAMPLE---

Input: "OMG!!! I can't believe this happened 😭 Check out http://example.com #shocking @friend u won't believe it"

Output:
"Oh my god I cannot believe this happened check out [URL] [hashtag: shocking] [mention] you will not believe it"

Transformations applied:
- OMG → Oh my god
- !!! → ! (normalized punctuation)
- 😭 → [emoji: crying face]
- URLs → [URL]
- @mentions → [mention]
- #hashtags → [hashtag: shocking]
- u → you
- Preserved "can't" negation""",
            "category": "Data Preparation > Text Preprocessing",
            "tags": ["text-cleaning", "social-media", "nlp", "preprocessing"],
            "source": "Custom"
        },
        {
            "title": "Remove Stopwords (Smart)",
            "prompt_text": """Remove stopwords from: {text}

Language: {language}
Keep: Negations (not, no, never), domain terms in {keep_words}

Return: processed text, word count before/after.

---EXAMPLE---

Text: "The patient is not feeling very well today and does not want to eat anything"
Language: English
Keep_words: ["patient"]

Output:
Processed: "patient not feeling well today not want eat"

Details:
- Removed: the, is, very, and, does, to, anything (7 words)
- Kept: not (negation), patient (domain term)
- Before: 14 words → After: 7 words (50% reduction)""",
            "category": "Data Preparation > Text Preprocessing",
            "tags": ["stopwords", "nlp", "text-processing"],
            "source": "Custom"
        },
        
        # Data Cleaning (2 prompts)
        {
            "title": "Survey Data Quality Check",
            "prompt_text": """Validate survey data: {n} responses

Check for:
- Speeders (completion time < {min_seconds} seconds)
- Straight-liners (same answer to all questions)
- Missing data patterns
- Duplicate IPs

Provide: exclusion report, final sample size.

---EXAMPLE---

Survey: Customer satisfaction (20 questions)
Responses: 500
Min_time: 120 seconds

QUALITY REPORT:

Issues Found:
1. Speeders: 23 responses (<120 sec)
   - Fastest: 45 seconds (Response ID: R_123)
   - Action: Exclude

2. Straight-liners: 8 responses (all "5" ratings)
   - Example: R_456 (answered 5 to all 20 questions)
   - Action: Exclude

3. Duplicate IPs: 12 responses (6 IP addresses)
   - IP 192.168.1.1: 3 responses
   - Action: Keep only first response per IP

4. Missing data: 34 responses incomplete
   - <50% complete: 12 (exclude)
   - 50-90% complete: 22 (keep with flagging)

RECOMMENDATIONS:
- Total exclusions: 23 + 8 + 6 + 12 = 49 responses
- Final sample: 451 valid responses
- Response rate: 90.2% (451/500)

Proceed with analysis? Yes, with noted limitations in methodology section.""",
            "category": "Data Preparation > Data Cleaning",
            "tags": ["survey", "data-quality", "validation", "cleaning"],
            "source": "Custom"
        },
        {
            "title": "Remove Duplicate Records",
            "prompt_text": """Find and remove duplicates in dataset with {n} records.

Match criteria: {fields}
Resolution: Keep {keep_strategy}

Return: deduplicated data, duplicate log.

---EXAMPLE---

Records: 1,200 participants
Fields: email, name
Strategy: Keep first occurrence

DEDUPLICATION REPORT:

Duplicates Found: 45 records

Examples:
1. email: john.doe@email.com
   - Record 1 (ID: 001, Date: 2024-01-15) ← KEPT
   - Record 2 (ID: 756, Date: 2024-02-01) ← REMOVED

2. name: Jane Smith (different emails)
   - Record 1 (jane.smith@email.com, ID: 034) ← KEPT
   - Record 2 (j.smith@work.com, ID: 892) ← REMOVED (likely same person)

Actions Taken:
- Removed: 45 duplicate records
- Final dataset: 1,155 unique records
- Duplicate rate: 3.75%

Exported:
- Clean data: participants_clean.csv (1,155 rows)
- Duplicates log: duplicates_removed.csv (45 rows with both IDs)""",
            "category": "Data Preparation > Data Cleaning",
            "tags": ["duplicates", "data-cleaning", "deduplication"],
            "source": "Custom"
        },
        
        # Data Formatting (2 prompts)
        {
            "title": "Long to Wide Format Converter",
            "prompt_text": """Convert survey data from long to wide format.

Variables: {variables}
Time points: {time_points}
ID variable: {id_var}

Return: restructured data.

---EXAMPLE---

Variables: stress_score, sleep_hours
Time: T1, T2, T3
ID: participant_id

INPUT (Long format):
participant_id | time | stress_score | sleep_hours
001           | T1   | 7           | 6
001           | T2   | 5           | 7
001           | T3   | 4           | 8
002           | T1   | 8           | 5
002           | T2   | 8           | 5
002           | T3   | 6           | 6

OUTPUT (Wide format):
participant_id | stress_T1 | stress_T2 | stress_T3 | sleep_T1 | sleep_T2 | sleep_T3
001           | 7         | 5         | 4         | 6        | 7        | 8
002           | 8         | 8         | 6         | 5        | 5        | 6

Benefits:
- Ready for repeated measures ANOVA
- Easier visualization of individual trajectories
- Compatible with most statistical software""",
            "category": "Data Preparation > Data Formatting",
            "tags": ["data-transformation", "longitudinal", "reshape"],
            "source": "Custom"
        },
        {
            "title": "Transcript Formatter for Coding",
            "prompt_text": """Format interview transcript for qualitative coding.

Raw transcript: {transcript}
Speaker labels: {speakers}

Add: Line numbers, timestamps, speaker tags.

---EXAMPLE---

Raw transcript:
"So tell me about your experience. Well, I started working remotely in 2020 and it was challenging at first. What made it challenging? The isolation mainly."

Speakers: Interviewer (I), Participant (P)

FORMATTED:

[00:00:15]
001 I: So tell me about your experience.
002 
003 P: Well, I started working remotely in 2020 and it was challenging at 
004 first.
005
[00:00:28]
006 I: What made it challenging?
007
008 P: The isolation mainly.
009

Format notes:
- Line numbers every line (for coding reference)
- Timestamps every 30 seconds
- Speaker tags (I/P) before each turn
- Blank lines between speakers
- Text wrapped at 80 characters

Ready for: NVivo, Atlas.ti, manual coding""",
            "category": "Data Preparation > Data Formatting",
            "tags": ["transcription", "qualitative", "formatting", "coding"],
            "source": "Custom"
        },
        
        # ============================================
        # 3. TEXT ANALYSIS
        # ============================================
        
        # Text Summarization (3 prompts)
        {
            "title": "Academic Article Summarizer",
            "prompt_text": """Summarize this research article in structured format.

Article: {article_text}

Include: Research question, method, key findings (3-5 points), implications.

---EXAMPLE---

Article: [Paste full article text about social media and mental health]

SUMMARY:

Research Question:
Does passive social media use predict depression in adolescents?

Method:
Longitudinal survey; n=1,247 teens (ages 13-17); 2-year follow-up; measured social media habits and depressive symptoms at 3 time points.

Key Findings:
1. Passive scrolling linked to 23% increase in depressive symptoms (β=.23, p<.001)
2. Active engagement (posting, commenting) showed no negative effects
3. Effect stronger for girls and younger adolescents
4. Social comparison fully mediated the relationship
5. Results held after controlling for baseline mental health

Implications:
- Interventions should target passive use specifically, not overall screen time
- Focus on reducing upward social comparisons
- Age and gender matter - tailor approaches accordingly

Study Limitations: Self-report measures, limited to Instagram users

Citation: [Author et al., 2023, Journal of Adolescent Psychology]""",
            "category": "Text Analysis > Text Summarization",
            "tags": ["summarization", "academic", "research"],
            "source": "Adapted from Wolfram PromptRepository - SummarizeContent"
        },
        {
            "title": "Web Article Research Summarizer",
            "prompt_text": """Summarize this web article for research purposes.

URL: {url}

Extract: Main argument, key data/statistics, author credibility, bias indicators, useful quotes.

---EXAMPLE---

URL: https://writings.stephenwolfram.com/2023/05/the-new-world-of-llm-functions/

RESEARCH SUMMARY:

Main Argument:
LLMs can be integrated as computational functions, enabling new ways to combine natural language processing with traditional programming and computation.

Key Points:
1. LLM functions treat language models as callable functions within code
2. Enables "prompt engineering" at the programming level
3. Combines symbolic computation with neural networks
4. Opens possibilities for hybrid AI systems

Data/Statistics:
- Example: Function calls reduce prompt complexity by 60%
- Performance: 10x faster than traditional NLP pipelines for certain tasks

Author Credibility:
- Stephen Wolfram (creator of Mathematica, Wolfram Alpha)
- Published: May 2023
- Highly technical, first-person account of implementation

Bias Indicators:
- Promotes Wolfram Language specifically
- Author has commercial interest (Wolfram Research)
- Balanced: acknowledges limitations and challenges

Useful Quotes:
"The integration of LLMs into computational workflows represents a fundamental shift in how we think about programming" (para. 3)

"Not about replacing programmers, but augmenting what's computable" (para. 12)

Relevance: High for AI + research methods, programming, computational social science

Source Type: Technical blog post by domain expert""",
            "category": "Text Analysis > Text Summarization",
            "tags": ["web-summary", "url", "research"],
            "source": "Adapted from Wolfram PromptRepository - SummarizeContent (URL version)"
        },
        {
            "title": "Multi-Document Literature Synthesis",
            "prompt_text": """Synthesize findings from these {n} articles on: {topic}

Articles: {article_list}

Create: Narrative synthesis identifying themes, contradictions, gaps, chronological development.

---EXAMPLE---

Topic: Remote work and productivity
Articles: 5 studies (2020-2023)

LITERATURE SYNTHESIS:

Theme 1: Productivity Effects (Mixed Evidence)
Early pandemic studies (Smith, 2020; Jones, 2020) reported productivity gains of 10-15%, primarily attributed to reduced commute time and fewer office distractions. However, more recent research (Chen, 2022; Williams, 2023) found these effects diminished over time, with productivity returning to baseline after 12-18 months. Martinez (2023) suggests this decline correlates with "Zoom fatigue" and erosion of work-life boundaries.

Theme 2: Individual Differences Matter
Across all studies, effects varied significantly by: job type (knowledge work vs. manual), personality (introversion/extroversion), home environment (dedicated office vs. shared spaces), and caregiving responsibilities. Chen (2022) found a 30% productivity gap between workers with and without dependent care duties.

Theme 3: Organizational Support Critical
Williams (2023) and Martinez (2023) both emphasize that productivity outcomes depend heavily on managerial practices. Organizations with clear communication protocols, regular check-ins, and investment in technology saw better outcomes.

Contradictions:
- Smith (2020): 13% productivity increase
- Chen (2022): No significant change
- Possible explanation: Smith measured short-term (3 months), Chen long-term (2 years)

Research Gaps:
1. Limited longitudinal studies beyond 2 years
2. Underrepresented populations (non-desk workers, Global South)
3. Mental health mediators understudied
4. Few experimental designs (mostly correlational)

Chronological Development:
2020: Initial optimism about productivity gains
2021-2022: More nuanced findings emerge
2023: Recognition of complexity, individual differences

Theoretical Integration:
Job Demands-Resources theory (Bakker & Demerouti) best explains observed patterns - remote work simultaneously increases resources (autonomy) and demands (boundary management).""",
            "category": "Text Analysis > Text Summarization",
            "tags": ["literature-review", "synthesis", "meta-analysis"],
            "source": "Custom"
        },
        
        # Text Classification (2 prompts)
        {
            "title": "Social Media Post Classifier",
            "prompt_text": """Classify these social media posts into categories.

Posts: {posts}
Categories: {category_list}
Allow multiple labels: {yes/no}

For each post provide: primary category, confidence %, key phrases.

---EXAMPLE---

Posts: 3 tweets
Categories: Political, News, Personal, Marketing, Educational
Multiple labels: Yes

CLASSIFICATION RESULTS:

Post 1: "Just voted! Make your voice heard 🗳️ #Election2024"
Primary: Political (95%)
Secondary: Personal (60%)
Key phrases: "voted", "#Election2024"
Reasoning: Clear political content + personal experience

Post 2: "New study shows coffee may reduce heart disease risk by 15%"
Primary: News (90%)
Secondary: Educational (75%)
Key phrases: "new study", "reduce heart disease"
Reasoning: Reports research finding, educational value

Post 3: "Excited to share our new product launch! Limited time offer 50% off"
Primary: Marketing (98%)
Secondary: None
Key phrases: "product launch", "50% off", "limited time"
Reasoning: Explicit promotional content

Summary Statistics:
- Political: 1 (33%)
- News: 1 (33%)
- Marketing: 1 (33%)
- Personal: 1 secondary (33%)
- Educational: 1 secondary (33%)

Confidence: Average 94% (high reliability)""",
            "category": "Text Analysis > Text Classification",
            "tags": ["classification", "social-media", "content-analysis"],
            "source": "Custom"
        },
        {
            "title": "Survey Open-Ended Response Categorizer",
            "prompt_text": """Categorize open-ended survey responses.

Question: {survey_question}
Responses: {responses} (n={count})

Create 5-8 categories, code all responses, provide frequency distribution.

---EXAMPLE---

Question: "What is your biggest challenge working from home?"
Responses: 50 responses

CATEGORY DEVELOPMENT:

Categories Created:
1. Isolation/Loneliness (mentions feeling disconnected, missing colleagues)
2. Distractions (family, household tasks, pets)
3. Technology Issues (internet, software, equipment)
4. Work-Life Boundaries (difficulty "switching off", always available)
5. Communication Challenges (misunderstandings, lack of informal chat)
6. Workspace/Ergonomics (no dedicated office, uncomfortable setup)
7. Other

CODING RESULTS:

Category 1 (Isolation): n=18 (36%)
- "Missing the social interaction with coworkers"
- "Feel disconnected from the team"
- "Loneliness is a real issue"

Category 2 (Distractions): n=12 (24%)
- "Kids interrupting Zoom calls"
- "Household chores calling my name"
- "My dog barks during meetings"

Category 3 (Technology): n=7 (14%)
- "Slow internet connection"
- "VPN always disconnecting"
- "Don't have proper equipment"

Category 4 (Boundaries): n=8 (16%)
- "Never truly log off anymore"
- "Working evenings and weekends"
- "Hard to separate work from home"

Category 5 (Communication): n=3 (6%)
- "Email miscommunications"
- "Miss hallway conversations"

Category 6 (Workspace): n=2 (4%)
- "Working from my couch hurts my back"

FREQUENCY DISTRIBUTION:
Isolation: 36% ████████████████
Distractions: 24% ██████████
Work-Life: 16% ███████
Technology: 14% ██████
Communication: 6% ███
Workspace: 4% ██

Primary Finding: Isolation/loneliness is the dominant challenge (36%), followed by distractions (24%).""",
            "category": "Text Analysis > Text Classification",
            "tags": ["survey", "open-ended", "categorization", "coding"],
            "source": "Custom"
        },
        
        # Sentiment Analysis (3 prompts)
        {
            "title": "Sentiment Analyzer (Contextual)",
            "prompt_text": """Analyze sentiment of this text with full context.

Text: {text}

Provide: Overall sentiment, score (-1 to +1), confidence %, key phrases, emotions, sarcasm check.

---EXAMPLE---

Text: "Halloween is most likely the greatest holiday of them all. It hits all the high notes for me! Although, I don't like having my doorbell rung every 5 minutes."

SENTIMENT ANALYSIS:

Overall Sentiment: Mixed (Leaning Positive)
Sentiment Score: +0.6 (on scale of -1 to +1)
Confidence: 85%

Breakdown by Section:
1. "Halloween is most likely the greatest holiday" 
   → Very Positive (+0.9)
   
2. "It hits all the high notes for me!"
   → Positive (+0.8)
   
3. "Although, I don't like having my doorbell rung every 5 minutes"
   → Negative (-0.4)

Key Sentiment Phrases:
Positive: "greatest holiday", "hits all the high notes"
Negative: "don't like", "every 5 minutes" (implies annoyance)

Emotional Dimensions:
- Joy: High (enthusiasm about holiday)
- Annoyance: Moderate (doorbell interruptions)
- Satisfaction: High (overall positive experience)

Contextual Modifiers:
- "Although" signals contrast/caveat
- "every 5 minutes" is hyperbole indicating frustration
- Exclamation mark reinforces positive emotion

Sarcasm Detection: Not detected (genuine sentiment)

Interpretation:
Speaker loves Halloween overall but has a specific frustration with frequent trick-or-treaters. The positive sentiment (love of holiday) outweighs the negative (doorbell annoyance), resulting in net positive score.

Use Case: Product/service feedback analysis, social listening""",
            "category": "Text Analysis > Sentiment Analysis",
            "tags": ["sentiment", "emotion", "nlp"],
            "source": "Adapted from Wolfram PromptRepository - SentimentAnalyze"
        },
        {
            "title": "Comparative Sentiment Over Time",
            "prompt_text": """Analyze sentiment trends across time periods.

Text data: {texts_by_period}
Periods: {period_labels}

For each period: average sentiment, distribution, top themes, significant shifts.

---EXAMPLE---

Data: Customer reviews
Periods: Q1 2023, Q2 2023, Q3 2023

SENTIMENT TREND ANALYSIS:

Period 1 (Q1 2023): n=450 reviews
Average Sentiment: +0.52 (Positive)
Distribution: 68% positive, 20% neutral, 12% negative
Top Positive Theme: "fast delivery" (mentioned 156 times)
Top Negative Theme: "customer service delays" (mentioned 34 times)

Period 2 (Q2 2023): n=523 reviews
Average Sentiment: +0.38 (Mildly Positive)
Distribution: 58% positive, 25% neutral, 17% negative
Top Positive Theme: "product quality" (mentioned 187 times)
Top Negative Theme: "price increases" (mentioned 67 times)
⚠️ SHIFT: Sentiment declined by 0.14 points (p=0.003, significant)

Period 3 (Q3 2023): n=489 reviews
Average Sentiment: +0.61 (Positive)
Distribution: 71% positive, 18% neutral, 11% negative
Top Positive Theme: "new features" (mentioned 201 times)
Top Negative Theme: "occasional bugs" (mentioned 28 times)
✓ IMPROVEMENT: Sentiment recovered to above Q1 levels

TREND VISUALIZATION:
Q1: +0.52 ████████████
Q2: +0.38 ████████ (↓ 27% decline)
Q3: +0.61 ██████████████ (↑ 61% improvement)

Key Findings:
1. Q2 dip correlates with price increase announcement (external event)
2. Q3 recovery linked to new feature release
3. Product quality consistently praised across all periods
4. Customer service mentioned less frequently in Q3 (may indicate improvement)

Statistical Tests:
- Q1 vs Q2: t=-2.89, p=0.003 (significant decrease)
- Q2 vs Q3: t=4.12, p<0.001 (significant increase)
- Overall trend: Positive (recovered and exceeded baseline)

Recommendation: Monitor price sensitivity; new features boost sentiment.""",
            "category": "Text Analysis > Sentiment Analysis",
            "tags": ["sentiment", "trend-analysis", "longitudinal"],
            "source": "Custom"
        },
        {
            "title": "Aspect-Based Sentiment Analysis",
            "prompt_text": """Analyze sentiment for specific aspects/features.

Text: {review_text}
Aspects: {aspect_list}

For each aspect: sentiment score, supporting quotes.

---EXAMPLE---

Text: "The hotel room was spacious and clean, which I loved. However, the staff were quite rude when I asked for extra towels. The location is perfect - right downtown. But the Wi-Fi barely worked and kept disconnecting."

Aspects: Room, Staff, Location, Amenities

ASPECT-BASED SENTIMENT:

Aspect 1: Room
Sentiment: Positive (+0.8)
Score Breakdown:
- Size: Positive ("spacious")
- Cleanliness: Positive ("clean")
Supporting Quote: "The hotel room was spacious and clean, which I loved."
Overall: Strongly positive experience

Aspect 2: Staff
Sentiment: Negative (-0.7)
Score Breakdown:
- Helpfulness: Negative ("quite rude")
- Responsiveness: Negative (implied by context)
Supporting Quote: "the staff were quite rude when I asked for extra towels"
Overall: Poor service experience

Aspect 3: Location
Sentiment: Very Positive (+0.9)
Score Breakdown:
- Convenience: Positive ("perfect", "right downtown")
Supporting Quote: "The location is perfect - right downtown."
Overall: Excellent location

Aspect 4: Amenities
Sentiment: Negative (-0.6)
Score Breakdown:
- Wi-Fi: Very Negative ("barely worked", "kept disconnecting")
Supporting Quote: "the Wi-Fi barely worked and kept disconnecting"
Overall: Technology issues

SUMMARY MATRIX:
Aspect    | Sentiment | Score | Impact
----------|-----------|-------|--------
Room      | Positive  | +0.8  | High
Staff     | Negative  | -0.7  | High
Location  | Positive  | +0.9  | High
Amenities | Negative  | -0.6  | Medium

Overall Rating Prediction: 3.2/5 stars
(Positive room + location offset by negative staff + Wi-Fi)

Actionable Insights:
1. URGENT: Address staff training (highest negative impact)
2. Fix Wi-Fi infrastructure
3. Maintain room quality standards (strength)
4. Leverage location in marketing (strength)""",
            "category": "Text Analysis > Sentiment Analysis",
            "tags": ["aspect-sentiment", "reviews", "detailed-analysis"],
            "source": "Custom"
        },
        
        # Word Frequency & Patterns (2 prompts)
        {
            "title": "Word Frequency Analysis",
            "prompt_text": """Analyze word frequencies in corpus.

Text: {corpus}
Size: {n_words} words

Generate: Top 30 words, top 20 bigrams, top 10 trigrams (exclude stopwords).

---EXAMPLE---

Corpus: Research articles on climate change (n=50,000 words)

FREQUENCY ANALYSIS:

Top 30 Words:
1. climate (n=892, 1.78%)
2. change (n=834, 1.67%)
3. temperature (n=456, 0.91%)
4. emissions (n=398, 0.80%)
5. carbon (n=367, 0.73%)
6. global (n=334, 0.67%)
7. warming (n=312, 0.62%)
8. data (n=289, 0.58%)
9. research (n=276, 0.55%)
10. study (n=245, 0.49%)
...(20 more)

Top 20 Bigrams:
1. "climate change" (n=567)
2. "global warming" (n=234)
3. "greenhouse gas" (n=198)
4. "carbon emissions" (n=187)
5. "temperature rise" (n=156)
6. "sea level" (n=142)
7. "climate model" (n=128)
8. "fossil fuel" (n=119)
9. "renewable energy" (n=107)
10. "climate crisis" (n=98)
...(10 more)

Top 10 Trigrams:
1. "greenhouse gas emissions" (n=89)
2. "global temperature rise" (n=67)
3. "renewable energy sources" (n=54)
4. "climate change impacts" (n=48)
5. "carbon dioxide levels" (n=43)
6. "sea level rise" (n=41)
7. "climate change mitigation" (n=38)
8. "fossil fuel consumption" (n=35)
9. "global climate model" (n=31)
10. "extreme weather events" (n=29)

INSIGHTS:
- "Climate change" used 5.7x more than "global warming" (terminology shift)
- Technical terms dominate (emissions, carbon, data)
- Solution-oriented terms emerging (renewable energy, mitigation)
- Zipf's law observed (frequency follows power law distribution)

Contextual Usage (KWIC for "climate"):
"...address **climate** change urgently..."
"...predict future **climate** patterns..."
"...global **climate** negotiations..."

Most common context: policy/action (43%), science/research (38%), impacts (19%)""",
            "category": "Text Analysis > Word Frequency & Patterns",
            "tags": ["frequency", "corpus-analysis", "text-mining"],
            "source": "Custom"
        },
        {
            "title": "Collocation Analysis",
            "prompt_text": """Identify collocations (words that frequently appear together).

Corpus: {text}
Target word: {keyword}
Window: ±{n} words

Provide: Top collocates, statistical significance, semantic patterns.

---EXAMPLE---

Corpus: News articles (1 million words)
Target: "vaccine"
Window: ±5 words

COLLOCATION ANALYSIS for "vaccine":

Top 10 Collocates (statistical strength):
1. "COVID" (PMI: 9.2, t-score: 67.3) - appears 89% of time
2. "efficacy" (PMI: 8.7, t-score: 45.1) - appears 67% of time
3. "doses" (PMI: 8.1, t-score: 38.9)
4. "rollout" (PMI: 7.9, t-score: 34.2)
5. "mandate" (PMI: 7.6, t-score: 29.8)
6. "hesitancy" (PMI: 7.4, t-score: 27.5)
7. "approval" (PMI: 7.1, t-score: 25.3)
8. "Pfizer" (PMI: 6.9, t-score: 23.1)
9. "booster" (PMI: 6.7, t-score: 21.8)
10. "trial" (PMI: 6.4, t-score: 19.4)

Positional Preferences:
Before "vaccine": COVID (52%), new (18%), approved (12%)
After "vaccine": doses (34%), rollout (28%), efficacy (21%)

Semantic Clusters:
1. Policy/Distribution: rollout, mandate, doses (38%)
2. Scientific: efficacy, trial, approval (31%)
3. Brands: Pfizer, Moderna, J&J (18%)
4. Social: hesitancy, misinformation (13%)

Temporal Trends:
2020-2021: "trial", "development" dominant
2022-2023: "booster", "mandate" increasing

Example Sentences:
"The **COVID vaccine** rollout begins next week"
"**Vaccine efficacy** data shows 95% protection"
"New **vaccine mandates** announced for healthcare workers"

Insight: Discourse shifted from development phase to implementation and public health policy.""",
            "category": "Text Analysis > Word Frequency & Patterns",
            "tags": ["collocation", "corpus-linguistics", "text-patterns"],
            "source": "Custom"
        },
        
        # ============================================
        # 4. ACADEMIC WRITING
        # ============================================
        
        # Literature Review (2 prompts)
        {
            "title": "Literature Review Section Writer",
            "prompt_text": """Write a literature review section on: {topic}

Key studies: {study_list}
Themes: {themes}
Word count: {words}

Structure: Opening, thematic organization, gaps, transition to current study.

---EXAMPLE---

Topic: Social media and adolescent mental health
Studies: 5 key papers
Themes: Usage patterns, mechanisms, moderators
Words: 500

LITERATURE REVIEW:

The relationship between social media use and adolescent mental health has garnered substantial research attention in recent years, with scholars examining multiple dimensions of this complex association (Twenge & Campbell, 2022; Odgers & Jensen, 2020). This review synthesizes current evidence, organizing findings around three key themes: usage patterns, underlying mechanisms, and moderating factors.

Usage Patterns and Mental Health Outcomes

Research distinguishes between passive consumption (scrolling without engaging) and active use (posting, commenting), with differential effects on wellbeing. Verduyn et al. (2021) found that passive Facebook use predicted decreased wellbeing, while active use showed no such relationship. Similarly, Escobar-Viera et al. (2022) reported that passive Instagram scrolling correlated with depressive symptoms (r=.31, p<.001), whereas active engagement did not. These findings align with earlier work by Shakya and Christakis (2017), who demonstrated that clicking "likes" predicted worse mental health outcomes than direct social interaction online.

Psychological Mechanisms

Social comparison theory provides the predominant explanatory framework for observed effects (Vogel et al., 2021). Longitudinal evidence indicates that upward social comparison—comparing oneself unfavorably to idealized online presentations—mediates the relationship between passive social media use and depression (Burnell et al., 2022). Additionally, fear of missing out (FOMO) has emerged as a significant pathway, with Franchina et al. (2020) finding that FOMO partially explained the link between social media intensity and anxiety.

Moderating Factors

Effects vary considerably across demographic and individual difference variables. Age appears critical, with younger adolescents (ages 13-15) showing greater vulnerability than older teens (Nesi et al., 2021). Gender differences are consistently reported, with girls experiencing more negative impacts than boys, potentially due to higher engagement with appearance-focused platforms (Kelly et al., 2022). Individual factors such as self-esteem and pre-existing mental health conditions also moderate outcomes.

Research Gaps and Current Study

Despite these advances, several limitations warrant attention. Most studies rely on cross-sectional designs, limiting causal inference. Few investigations examine mechanisms beyond social comparison. Additionally, the rapid evolution of platforms means findings may not generalize across contexts. The current study addresses these gaps by employing a longitudinal design, testing multiple mediating pathways, and examining effects across diverse platforms.

[Word count: 498]""",
            "category": "Academic Writing > Literature Review",
            "tags": ["literature-review", "academic-writing", "research-paper"],
            "source": "Custom"
        },
        {
            "title": "Research Gap Identifier",
            "prompt_text": """Identify research gaps in this literature on: {topic}

Review: {literature_summary}

List: 5-7 specific gaps with justification and suggested next steps.

---EXAMPLE---

Topic: Remote work productivity
Literature: 15 studies reviewed (2019-2023)

RESEARCH GAPS IDENTIFIED:

Gap 1: Longitudinal Effects Beyond 2 Years
Current state: Most studies examine short-term effects (3-12 months)
Evidence: Only 2 of 15 studies exceed 18-month follow-up
Why it matters: Productivity effects may change as remote work becomes normalized
Suggested study: 5-year panel study tracking same workers across transition

Gap 2: Non-Knowledge Workers Underrepresented
Current state: 87% of studies focus on office/knowledge workers
Missing: Manufacturing supervisors, healthcare admin, retail management
Why it matters: Generalizability limited; different job types may show different patterns
Suggested study: Comparative study across job sectors

Gap 3: Mental Health as Mediator Understudied
Current state: Only 3 studies examine psychological mechanisms
Evidence: Productivity often measured without considering wellbeing pathways
Why it matters: May miss important explanatory variables (burnout, work-life conflict)
Suggested study: Mediation analysis with mental health indicators

Gap 4: Experimental Designs Absent
Current state: All 15 studies are correlational/observational
Limitation: Cannot establish causation
Why it matters: Policy decisions require stronger causal evidence
Suggested study: Randomized trial with matched control group

Gap 5: Cultural Context Neglected
Current state: 93% of studies from US/Western Europe
Missing: Asia, Africa, Latin America perspectives
Why it matters: Cultural norms around work may moderate effects
Suggested study: Cross-cultural comparison study

Gap 6: Team-Level Outcomes Overlooked
Current state: Focus almost exclusively on individual productivity
Missing: Team cohesion, collaboration quality, innovation
Why it matters: Remote work impacts group processes differently
Suggested study: Multi-level analysis (individual + team outcomes)

Gap 7: Technology Infrastructure Assumed
Current state: Studies assume reliable internet, equipment access
Reality: Digital divide may affect who can work remotely productively
Why it matters: Equity concerns, sample bias
Suggested study: Stratified analysis by technology access levels

PRIORITY RANKING:
High Priority: Gaps 1, 4, 6 (methodological improvements needed)
Medium Priority: Gaps 2, 5 (generalizability concerns)
Lower Priority: Gaps 3, 7 (important but can build on existing frameworks)

Recommendation: Address Gap 1 (longitudinal) + Gap 4 (experimental) in next study to provide strongest evidence base for policy.""",
            "category": "Academic Writing > Literature Review",
            "tags": ["research-gaps", "literature-review", "academic"],
            "source": "Custom"
        },
        
        # Research Papers (2 prompts)
        {
            "title": "Abstract Generator (Structured)",
            "prompt_text": """Create a structured abstract for: {study_title}

Study details:
- Research question: {RQ}
- Method: {method}
- Sample: {sample}
- Key findings: {findings}
- Implications: {implications}

Format: Background, Methods, Results, Conclusions (250 words max).

---EXAMPLE---

Study: Social Media Use and Sleep Quality in College Students

RQ: Does evening social media use predict poor sleep quality?
Method: Survey + 7-day sleep diary
Sample: 342 undergraduates, ages 18-22
Findings: Evening use (9pm-midnight) linked to 45-min later sleep onset, lower quality
Implications: Targeted interventions needed

ABSTRACT:

Background: Social media use among college students is ubiquitous, yet its effects on sleep remain poorly understood. This study examined whether evening social media engagement predicts sleep onset latency and subjective sleep quality.

Methods: A sample of 342 undergraduate students (M age=19.7, SD=1.2; 68% female) completed baseline surveys assessing social media habits and demographics, followed by 7-day sleep diaries documenting nightly social media use, sleep onset time, and sleep quality ratings. Linear mixed models tested associations between evening social media use (9pm-midnight) and sleep outcomes, controlling for caffeine intake and baseline sleep patterns.

Results: Evening social media use significantly predicted later sleep onset (β=6.3 min per 30-min use, p<.001) and lower sleep quality (β=-.28, p<.001). Students using social media for 90+ minutes after 9pm experienced sleep onset delays averaging 45 minutes compared to minimal users. Effects were strongest for interactive platforms (Instagram, TikTok) versus passive consumption (YouTube). Academic performance concerns partially mediated the relationship (indirect effect=.12, 95% CI [.07, .18]).

Conclusions: Evening social media use substantially disrupts college student sleep patterns, with implications for academic performance and wellbeing. Interventions targeting specific platforms and time windows may prove more effective than generic "screen time" recommendations. Universities should consider incorporating sleep hygiene education that addresses social media use specifically.

Keywords: social media, sleep quality, college students, screen time, wellbeing

[Word count: 248]""",
            "category": "Academic Writing > Research Papers",
            "tags": ["abstract", "academic-writing", "publication"],
            "source": "Custom"
        },
        {
            "title": "Methods Section Writer",
            "prompt_text": """Write the Methods section for this study.

Study type: {design}
Participants: {sample_details}
Measures: {measures_list}
Procedure: {procedure}
Analysis: {analysis_plan}

Include: Participants, measures, procedure, analysis (APA style).

---EXAMPLE---

Design: Cross-sectional survey
Participants: 500 adults, online recruitment, age 25-65
Measures: Remote work experience scale, work-life balance inventory, burnout measure
Procedure: Online survey via Qualtrics, 20 minutes
Analysis: Correlations, multiple regression

METHODS SECTION:

Participants

A total of 500 adults (M age = 42.3, SD = 11.2; 52% female, 47% male, 1% non-binary) were recruited through Prolific, an online crowdsourcing platform. Inclusion criteria required participants to: (a) be currently employed full-time, (b) have remote work experience of at least 6 months, and (c) reside in the United States. The sample was racially diverse (68% White, 14% Black, 10% Hispanic, 5% Asian, 3% other) and represented various industries (technology 28%, education 19%, healthcare 15%, finance 12%, other 26%). Participants were compensated $4.50 for their time.

Measures

Remote Work Experience Scale (RWES; Gajendran & Harrison, 2021). This 8-item measure assesses frequency and intensity of remote work (e.g., "I work remotely ___ days per week"). Items use 5-point scales, with higher scores indicating greater remote work intensity. The scale demonstrates good internal consistency (α = .87 in validation sample; α = .89 in current study).

Work-Life Balance Inventory (WLBI; Fisher et al., 2019). The WLBI consists of 12 items measuring perceived balance between work and personal life domains (e.g., "I maintain healthy boundaries between work and home"). Responses range from 1 (strongly disagree) to 7 (strongly agree). Internal consistency was excellent (α = .92).

Maslach Burnout Inventory (MBI; Maslach & Jackson, 1981). We administered the 22-item MBI assessing three dimensions: emotional exhaustion (9 items), depersonalization (5 items), and personal accomplishment (8 items). The MBI is widely used and psychometrically sound (α = .88-.94 across subscales in current study).

Demographic Variables. Participants reported age, gender, race/ethnicity, industry, and years of remote work experience.

Procedure

Following institutional review board approval, participants accessed the study via a Qualtrics link distributed through Prolific. After providing informed consent, participants completed the measures in counterbalanced order to control for potential order effects. The survey required approximately 20 minutes. Attention check items (n = 3) were embedded throughout; participants failing 2+ checks were excluded (n = 23, 4.4% of initial sample), resulting in the final sample of 500.

Data Analysis

Descriptive statistics and bivariate correlations were computed using SPSS 28.0. Hierarchical multiple regression tested whether remote work intensity predicted burnout dimensions beyond demographic controls. Model 1 included age, gender, and industry; Model 2 added remote work intensity; Model 3 added work-life balance to test mediation. Assumptions were evaluated and met: linearity (scatterplot inspection), homoscedasticity (Breusch-Pagan test, p = .23), multicollinearity (VIF < 2.1 for all predictors), and normality of residuals (Shapiro-Wilk test, p = .19). Alpha was set at .05 for all tests.

[Formatted in APA 7th edition style]""",
            "category": "Academic Writing > Research Papers",
            "tags": ["methods", "academic-writing", "apa-style"],
            "source": "Custom"
        },
        
        # Reports & Presentations (1 prompt)
        {
            "title": "Executive Summary Generator",
            "prompt_text": """Create an executive summary for report: {report_title}

Key findings: {findings}
Recommendations: {recommendations}
Target audience: {audience}

Length: 1-2 pages, no jargon, action-oriented.

---EXAMPLE---

Report: Employee Engagement Survey Results 2024
Findings: Engagement down 12%, top issues are workload, communication, growth opportunities
Recommendations: Reduce meeting time, improve manager training, create career pathways
Audience: C-suite executives

EXECUTIVE SUMMARY: Employee Engagement Survey 2024

Key Findings

Our annual engagement survey reveals a concerning 12-percentage-point decline in overall employee engagement (from 73% to 61%), the lowest in five years. This decline affects retention, productivity, and organizational culture.

Three Critical Issues Identified:

1. Workload Intensity (flagged by 68% of employees)
Employees report working 8+ hours beyond contracted time weekly. Meeting overload is the primary culprit, with staff spending average 18 hours/week in meetings—up from 12 hours in 2023.

Impact: 34% of respondents actively considering leaving due to unsustainable workload.

2. Communication Breakdown (58% dissatisfied)
Information silos between departments are worsening. 71% report learning about major decisions "through the grapevine" rather than official channels. Manager communication quality rated 4.2/10 (down from 6.8/10 in 2023).

Impact: Decreased trust in leadership, slower decision-making, duplicated efforts.

3. Limited Growth Opportunities (52% see no clear path)
Career advancement feels opaque. Only 23% understand promotion criteria. Internal mobility stagnated—just 8% of positions filled internally vs. 34% external hires.

Impact: Top talent seeking external opportunities, loss of institutional knowledge.

Urgent Recommendations

We recommend four immediate actions to reverse this trend:

1. Reduce Meeting Load (Target: 30% reduction)
   - Implement "No Meeting Fridays"
   - Require meeting agendas; cancel without clear purpose
   - Default to 25-minute (not 30) and 50-minute (not 60) meetings
   - Expected impact: 5+ hours returned to employees weekly

2. Strengthen Manager Capabilities (Start Q2 2024)
   - Mandatory communication training for all managers
   - Monthly skip-level meetings for transparency
   - Manager effectiveness tied to 360 feedback
   - Expected impact: Communication scores improve to 7/10 within 6 months

3. Create Transparent Career Pathways (Launch Q2 2024)
   - Publish competency frameworks for all role levels
   - Quarterly "career conversation" between employees and managers
   - Internal candidate preference policy (interview all qualified internals)
   - Expected impact: 50% of positions filled internally by Q4 2024

4. Quick Wins for Morale (Immediate)
   - Recognize high performers publicly (monthly awards)
   - Flexible work arrangements formalized
   - Mental health days added to PTO
   - Expected impact: Visible commitment to employee wellbeing

Cost-Benefit Analysis

Inaction costs: Conservative estimate of $2.4M annually (recruitment, training, lost productivity from 34% potential attrition).

Investment required: $180K (training programs, internal mobility platform).

ROI: 13:1 if we retain even 15% of at-risk employees.

Next Steps

We propose forming a cross-functional task force by March 1st to implement these recommendations. Monthly progress reports will track metrics: engagement scores, meeting hours, internal mobility rates, and voluntary turnover.

The window for intervention is narrow. Addressing these issues now protects our talent, culture, and bottom line.

Contact: People Analytics Team | engagement@company.com

[Format: Clear headers, bullet points, data callouts, action-oriented language]""",
            "category": "Academic Writing > Reports & Presentations",
            "tags": ["executive-summary", "report", "business-writing"],
            "source": "Custom"
        },
        
        # ============================================
        # 5. ADVANCED METHODS
        # ============================================
        
        # Model Fine-tuning (1 prompt)
        {
            "title": "LLM Fine-tuning Data Prep Guide",
            "prompt_text": """Guide me in preparing data to fine-tune an LLM for: {task}

Current data: {data_description}
Target model: {model}
Goal: {objective}

Provide: Data requirements, formatting, quality checks, split strategy.

---EXAMPLE---

Task: Classify research paper abstracts by methodology (qualitative/quantitative/mixed)
Data: 500 labeled abstracts
Model: GPT-3.5
Goal: 90%+ accuracy on new abstracts

FINE-TUNING DATA PREPARATION GUIDE:

1. Data Requirements Assessment

Minimum: 500-1000 examples for classification task ✓ (you have 500)
Recommended: 2000+ for robust performance
Quality > Quantity: Ensure clean labels

Your data status: MARGINAL - consider collecting 500 more examples

2. Data Format (OpenAI Fine-tuning)

Convert to JSONL (JSON Lines) format:

{"messages": [{"role": "system", "content": "Classify research methodology"}, {"role": "user", "content": "Abstract: This study used semi-structured interviews..."}, {"role": "assistant", "content": "Qualitative"}]}
{"messages": [{"role": "system", "content": "Classify research methodology"}, {"role": "user", "content": "Abstract: We conducted a randomized controlled trial..."}, {"role": "assistant", "content": "Quantitative"}]}

System prompt: Keep consistent across all examples
User message: "Abstract: {abstract_text}"
Assistant response: One word - "Qualitative" or "Quantitative" or "Mixed"

3. Data Quality Checks

Run these validations:

✓ Label consistency:
  - Check for typos (e.g., "Qualatative" vs "Qualitative")
  - Standardize capitalization
  - Verify only three classes used

✓ Length distribution:
  - Abstracts should be 100-300 words
  - Remove outliers (very short/long)
  - OpenAI limit: 8192 tokens total per example

✓ Class balance:
  Count per class:
  - Qualitative: 180 (36%)
  - Quantitative: 240 (48%)
  - Mixed: 80 (16%)
  
  ⚠️ Mixed methods underrepresented - collect 70 more examples

✓ Ambiguous cases:
  - Manually review borderline cases (qual + stats)
  - Consider creating "Mixed" subcategories if needed
  - Inter-rater reliability check (if multiple labelers)

4. Train/Validation/Test Split

Recommended split:
- Training: 70% (350 examples)
- Validation: 15% (75 examples)
- Test: 15% (75 examples)

Stratification: Ensure class distribution equal across splits

Python code:
```python
from sklearn.model_selection import train_test_split

# First split: separate test set
train_val, test = train_test_split(
    data, test_size=0.15, stratify=data['label'], random_state=42
)

# Second split: separate validation
train, val = train_test_split(
    train_val, test_size=0.176, stratify=train_val['label'], random_state=42
)  # 0.176 * 0.85 ≈ 0.15 of total

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
```

5. Fine-tuning Parameters (OpenAI GPT-3.5)

Based on your dataset size:

- **Learning rate**: 0.1 (default for small datasets)
- **Batch size**: 4-8 (start with 4)
- **Epochs**: 3-4 (monitor validation loss)
- **Evaluation**: After each epoch on validation set

Cost estimate: ~$2-5 for 350 training examples (GPT-3.5)

6. Validation Strategy

After fine-tuning, test on validation set:

Expected results:
- Baseline (no fine-tuning): ~60-70% accuracy
- After fine-tuning: Target 85-92% accuracy

If accuracy < 85%:
1. Check for mislabeled examples
2. Increase dataset to 1000+ examples
3. Try 1-2 more epochs
4. Review confused classes (e.g., mixed vs qualitative)

7. Final Quality Check

Before deployment:
✓ Test on held-out test set (75 examples)
✓ Manual review of misclassifications
✓ Edge case testing (very short abstracts, jargon-heavy)
✓ Consistency check (same input → same output?)

Success criteria: ≥90% accuracy on test set

8. Deployment Checklist

□ Model ID saved
□ System prompt documented
□ Error handling implemented
□ Fallback for low-confidence predictions
□ Monitoring plan (track accuracy over time)

NEXT STEPS:
1. Collect 70 more "Mixed methods" examples (balance dataset)
2. Format all 570 examples as JSONL
3. Run quality checks (script provided above)
4. Upload to OpenAI and start fine-tuning job
5. Validate on test set
6. Deploy if accuracy ≥90%

Timeline: 2-3 days (data prep: 1 day, fine-tuning: 2-4 hours, validation: 4 hours)

[Complete, actionable guidance ready for implementation]""",
            "category": "Advanced Methods > Model Fine-tuning",
            "tags": ["llm", "fine-tuning", "machine-learning", "ai"],
            "source": "Custom"
        },
        
        # Custom API Integration (1 prompt)
        {
            "title": "Research Workflow API Automation",
            "prompt_text": """Design an API workflow to automate: {research_task}

Data sources: {apis}
Frequency: {schedule}
Output: {desired_output}

Provide: Architecture, API calls, error handling, code.

---EXAMPLE---

Task: Daily tracking of news mentions about "climate policy"
APIs: NewsAPI, OpenAI (sentiment analysis)
Schedule: Every morning at 6 AM
Output: Email summary with article links, sentiment, key quotes

AUTOMATED RESEARCH WORKFLOW:

System Architecture:
```
NewsAPI → Fetch articles → Filter relevant → OpenAI sentiment analysis → 
Store in database → Generate summary → Email report
```

1. API Requirements

NewsAPI:
- Endpoint: /v2/everything
- Authentication: API key (free tier: 100 requests/day)
- Rate limit: 1 request/second

OpenAI API:
- Model: GPT-3.5-turbo
- Purpose: Sentiment analysis + quote extraction
- Cost: ~$0.002 per article

Email:
- SMTP (Gmail) or SendGrid API
- Authentication: App password

2. Implementation (Python)

```python
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import time
import sqlite3

# Configuration
NEWS_API_KEY = "your_key_here"
OPENAI_API_KEY = "your_key_here"
EMAIL_TO = "researcher@university.edu"

# Initialize APIs
client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_news_articles():
    \"\"\"Fetch articles from NewsAPI\"\"\"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'climate policy',
        'from': yesterday,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 20,
        'apiKey': NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json()['articles']
        print(f"✓ Fetched {len(articles)} articles")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"✗ NewsAPI error: {e}")
        return []

def analyze_sentiment(article_text):
    \"\"\"Analyze sentiment using OpenAI\"\"\"
    prompt = f\"\"\"Analyze sentiment of this news article about climate policy.
    
Article: {article_text[:500]}...

Provide:
1. Sentiment: Positive/Negative/Neutral
2. Confidence: 0-100%
3. Key quote (one sentence)

Format: JSON\"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"✗ OpenAI error: {e}")
        return None

def store_in_database(article_data):
    \"\"\"Store results in SQLite\"\"\"
    conn = sqlite3.connect('climate_research.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            sentiment TEXT,
            confidence REAL,
            key_quote TEXT,
            date TEXT
        )
    ''')
    
    cursor.execute('''
        INSERT INTO articles (title, url, sentiment, confidence, key_quote, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', article_data)
    
    conn.commit()
    conn.close()

def send_email_report(summary_html):
    \"\"\"Send email summary\"\"\"
    msg = MIMEText(summary_html, 'html')
    msg['Subject'] = f"Climate Policy News Summary - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = "researcher@university.edu"
    msg['To'] = EMAIL_TO
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("your_email@gmail.com", "app_password")
            server.send_message(msg)
        print("✓ Email sent successfully")
    except Exception as e:
        print(f"✗ Email error: {e}")

def main():
     \"\"\"Main workflow\"\"\"
    print(f"Starting climate policy tracker - {datetime.now()}")
    
    # Step 1: Fetch articles
    articles = fetch_news_articles()
    if not articles:
        print("No articles found. Exiting.")
        return
    
    # Step 2: Analyze each article
    results = []
    for i, article in enumerate(articles, 1):
        print(f"Processing article {i}/{len(articles)}...")
        
        # Combine title + description
        text = f"{article['title']}. {article.get('description', '')}"
        
        # Analyze sentiment
        analysis = analyze_sentiment(text)
        
        if analysis:
            results.append({
                'title': article['title'],
                'url': article['url'],
                'analysis': analysis,
                'source': article['source']['name']
            })
            
            # Store in database
            # (parse analysis and store - simplified here)
        
        # Rate limiting
        time.sleep(1)
    
    # Step 3: Generate HTML summary
    html = f\"\"\"
    <html>
    <body>
    <h2>Climate Policy News - {datetime.now().strftime('%B %d, %Y')}</h2>
    <p>Found {len(results)} relevant articles:</p>
    <hr>
    \"\"\"
    
    for r in results:
        html += f\"\"\"
        <h3><a href="{r['url']}">{r['title']}</a></h3>
        <p><strong>Source:</strong> {r['source']}</p>
        <p><strong>Analysis:</strong> {r['analysis']}</p>
        <hr>
        \"\"\"
    
    html += \"\"\"
    </body>
    </html>
    \"\"\"
    
    # Step 4: Send email
    send_email_report(html)
    
    print("✓ Workflow complete")

if __name__ == "__main__":
    main()
```

3. Scheduling (Linux/Mac)

Add to crontab:
```bash
# Run every day at 6 AM
0 6 * * * /usr/bin/python3 /path/to/climate_tracker.py >> /path/to/log.txt 2>&1
```

Windows: Use Task Scheduler

4. Error Handling Strategies

- **API failures**: Retry 3 times with exponential backoff
- **Rate limits**: Track requests, pause if approaching limit
- **Data quality**: Validate JSON responses, skip malformed data
- **Email failures**: Log locally, retry next day
- **Database errors**: Backup before inserts

5. Monitoring & Alerts

Log to file:
- Successful runs: article count, API costs
- Failures: which API, error message, timestamp
- Weekly summary: total articles, sentiment distribution

Set alerts if:
- Zero articles fetched (NewsAPI issue?)
- OpenAI error rate >10%
- Email not sent

6. Cost Estimate

Daily costs:
- NewsAPI: Free (100 requests/day limit)
- OpenAI: 20 articles × $0.002 = $0.04/day
- Total: ~$1.20/month

Optimizations:
- Cache duplicate articles (check by URL)
- Batch OpenAI requests to reduce overhead
- Use GPT-3.5-turbo (cheaper than GPT-4)

7. Extensions

Possible additions:
- Twitter API for real-time mentions
- Store full article text (web scraping)
- Trend analysis over time (sentiment shifts)
- Alert on major policy announcements
- Export to CSV for analysis

RESULT:
Fully automated research assistant that delivers daily climate policy insights to your inbox, costs <$2/month, runs unattended.

[Production-ready code with error handling, monitoring, and cost optimization]""",
            "category": "Advanced Methods > Custom API Integration",
            "tags": ["api", "automation", "research-workflow", "python"],
            "source": "Custom"
        },
    ]
    
    # Insert all example prompts
    for prompt_data in example_prompts:
        query = prompts.insert().values(**prompt_data, views=0, created_at=datetime.utcnow())
        await database.execute(query)
    
    print(f"✅ Seeded database with {len(example_prompts)} social science research prompts")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)