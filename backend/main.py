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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/promptdb")

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
    
    return dict(result)

@app.get("/api/categories")
async def get_categories():
    """Get all unique categories"""
    query = sqlalchemy.select([prompts.c.category]).distinct()
    results = await database.fetch_all(query)
    categories = [row["category"] for row in results]
    return {"categories": categories}

@app.get("/api/stats", response_model=PromptStats)
async def get_stats():
    """Get statistics about prompts"""
    # Total count
    count_query = sqlalchemy.select([sqlalchemy.func.count()]).select_from(prompts)
    total = await database.fetch_val(count_query)
    
    # Count by category
    category_query = (
        sqlalchemy.select([
            prompts.c.category,
            sqlalchemy.func.count().label("count")
        ])
        .group_by(prompts.c.category)
    )
    category_results = await database.fetch_all(category_query)
    categories_dict = {row["category"]: row["count"] for row in category_results}
    
    return {
        "total_prompts": total,
        "categories": categories_dict
    }

# Seed database with example prompts from Wolfram
async def seed_database():
    """Populate database with example prompts if empty"""
    count_query = sqlalchemy.select([sqlalchemy.func.count()]).select_from(prompts)
    count = await database.fetch_val(count_query)
    
    if count > 0:
        return  # Database already has data
    
    example_prompts = [
        {
            "title": "Sentiment Analysis for Survey Responses",
            "prompt_text": "Analyze the sentiment of the following survey response. Classify it as positive, negative, or neutral, and provide a brief explanation:\n\n{survey_response}",
            "category": "Sentiment Analysis",
            "tags": ["survey", "sentiment", "classification"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Qualitative Data Coding Assistant",
            "prompt_text": "You are a qualitative research assistant. Read the following interview transcript and identify key themes. For each theme, provide:\n1. Theme name\n2. Supporting quotes\n3. Brief interpretation\n\nTranscript:\n{transcript}",
            "category": "Qualitative Coding",
            "tags": ["coding", "themes", "qualitative"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Academic Literature Summarizer",
            "prompt_text": "Summarize the following academic paper in 3-4 sentences. Focus on:\n1. Research question\n2. Methodology\n3. Key findings\n4. Implications\n\nPaper abstract:\n{abstract}",
            "category": "Summarization",
            "tags": ["academic", "summary", "literature"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Survey Question Generator",
            "prompt_text": "Generate 5 survey questions to measure {construct} in the context of {context}. Each question should:\n- Use clear, simple language\n- Avoid leading or double-barreled questions\n- Include a 5-point Likert scale\n\nProvide questions in numbered format.",
            "category": "Survey Design",
            "tags": ["survey", "questionnaire", "research-design"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Text Classification for Social Media",
            "prompt_text": "Classify the following social media post into one of these categories: Political, Entertainment, News, Personal, Marketing.\n\nPost: {post}\n\nProvide the category and a confidence score (0-100%).",
            "category": "Text Classification",
            "tags": ["social-media", "classification", "content-analysis"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Focus Group Discussion Analyzer",
            "prompt_text": "Analyze this focus group discussion and identify:\n1. Main topics discussed\n2. Areas of consensus\n3. Areas of disagreement\n4. Emerging insights\n5. Quotes that illustrate key points\n\nDiscussion:\n{discussion}",
            "category": "Qualitative Analysis",
            "tags": ["focus-group", "discussion", "analysis"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Research Hypothesis Generator",
            "prompt_text": "Based on the following research question: '{research_question}'\n\nGenerate:\n1. A null hypothesis\n2. An alternative hypothesis\n3. Three testable predictions\n4. Suggested methodology\n\nEnsure hypotheses are specific, measurable, and falsifiable.",
            "category": "Research Design",
            "tags": ["hypothesis", "research-design", "methodology"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Interview Transcript Thematic Coder",
            "prompt_text": "Code the following interview transcript using thematic analysis. Identify:\n1. Initial codes (descriptive labels)\n2. Focused codes (analytical categories)\n3. Theoretical codes (conceptual themes)\n\nFor each code, note the line numbers where it appears.\n\nTranscript:\n{transcript}",
            "category": "Qualitative Coding",
            "tags": ["interview", "thematic-analysis", "coding"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Policy Document Summarizer",
            "prompt_text": "Summarize the following policy document for a general audience:\n\n{policy_text}\n\nProvide:\n1. Main purpose (1 sentence)\n2. Key provisions (bullet points)\n3. Who is affected\n4. Implementation timeline\n5. Potential impacts",
            "category": "Summarization",
            "tags": ["policy", "government", "summary"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Mixed Methods Data Integration",
            "prompt_text": "I have quantitative and qualitative data on {topic}:\n\nQuantitative findings: {quant_data}\nQualitative themes: {qual_data}\n\nIntegrate these findings by:\n1. Identifying convergence (where data agree)\n2. Identifying divergence (where data differ)\n3. Providing possible explanations for discrepancies\n4. Suggesting integrated conclusions",
            "category": "Mixed Methods",
            "tags": ["mixed-methods", "integration", "triangulation"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Grant Proposal Abstract Writer",
            "prompt_text": "Write a 250-word abstract for a research grant proposal based on:\n\nResearch question: {question}\nMethodology: {method}\nExpected outcomes: {outcomes}\nSignificance: {significance}\n\nThe abstract should be compelling, clear, and follow standard academic grant writing conventions.",
            "category": "Academic Writing",
            "tags": ["grant", "proposal", "academic-writing"],
            "source": "Wolfram Prompt Repository"
        },
        {
            "title": "Ethnographic Field Notes Analyzer",
            "prompt_text": "Analyze these ethnographic field notes:\n\n{field_notes}\n\nProvide:\n1. Descriptive observations (what happened)\n2. Analytical memos (interpretations)\n3. Methodological notes (reflection on data collection)\n4. Potential patterns or themes\n5. Questions for further investigation",
            "category": "Ethnography",
            "tags": ["ethnography", "fieldwork", "observation"],
            "source": "Wolfram Prompt Repository"
        }
    ]
    
    # Insert all example prompts
    for prompt_data in example_prompts:
        query = prompts.insert().values(**prompt_data, views=0, created_at=datetime.utcnow())
        await database.execute(query)
    
    print(f"✅ Seeded database with {len(example_prompts)} example prompts")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
