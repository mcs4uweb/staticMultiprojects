import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import notte

load_dotenv()

try:
    from google import genai  # Preferred modern Gemini SDK (`google-genai`)
    _GENAI_LIB = "google-genai"
except ModuleNotFoundError:
    try:
        import google.generativeai as genai  # Legacy SDK (`google-generativeai`)
        _GENAI_LIB = "google-generativeai"
    except ModuleNotFoundError as import_error:
        raise ModuleNotFoundError(
            "Missing Gemini SDK. Install `google-genai` (preferred) or "
            "`google-generativeai` to enable Gemini features."
        ) from import_error

# --- 1. SETUP AND CONFIGURATION ---
# IMPORTANT: Replace this with your actual Gemini API Key
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
 
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

GEMINI_CLIENT = None
if _GENAI_LIB == "google-generativeai":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)


# --- 2. DATA MODELS (PYDANTIC) ---
# These classes define the structured data we want the AI agent to extract.

class ProductInfo(BaseModel):
    name: str
    price: str
    rating: Optional[float]
    availability: str
    description: str

class NewsArticle(BaseModel):
    title: str
    summary: str
    url: str
    date: str
    source: str

class SocialMediaPost(BaseModel):
    content: str
    author: str
    likes: int
    timestamp: str
    platform: str

class SearchResult(BaseModel):
    query: str
    results: List[dict]
    total_found: int


# --- 3. THE CORE AGENT CLASS ---
# This class wraps the `notte` agent and provides high-level methods for specific tasks.

class AdvancedNotteAgent:
    def __init__(self, headless=True, max_steps=20):
        self.headless = headless
        self.max_steps = max_steps
        self.session = None
        self.agent = None

    def __enter__(self):
        """Initializes the browser session when using a 'with' statement."""
        self.session = notte.Session(headless=self.headless)
        self.session.__enter__()
        self.agent = notte.Agent(
            session=self.session,
            reasoning_model='gemini/gemini-2.5-flash', # Corrected from 2.5 to a valid model
            max_steps=self.max_steps
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up the browser session when exiting the 'with' statement."""
        if self.session:
            self.session.__exit__(exc_type, exc_val, exc_tb)

    def research_product(self, product_name: str, website: str = "amazon.com") -> ProductInfo:
        """Research a product and extract structured information"""
        task = f"Go to {website}, search for '{product_name}', click on the first relevant product, and extract detailed product information including name, price, rating, availability, and description."
        response = self.agent.run(
            task=task,
            response_format=ProductInfo,
            url=f"https://{website}"
        )
        return response.answer

    def news_aggregator(self, topic: str, num_articles: int = 3) -> List[NewsArticle]:
        """Aggregate news articles on a specific topic"""
        task = f"Search for recent news about '{topic}', find {num_articles} relevant articles, and extract title, summary, URL, date, and source for each."
        response = self.agent.run(
            task=task,
            url="https://news.google.com",
            response_format=List[NewsArticle]
        )
        return response.answer

    def social_media_monitor(self, hashtag: str, platform: str = "twitter") -> List[SocialMediaPost]:
        """Monitor social media for specific hashtags"""
        if platform.lower() == "twitter":
            url = "https://x.com" # Updated from twitter.com
        elif platform.lower() == "reddit":
            url = "https://reddit.com"
        else:
            url = f"https://{platform}.com"

        task = f"Go to {platform}, search for posts with hashtag '{hashtag}', and extract content, author, engagement metrics, and timestamps from the top 5 posts."
        response = self.agent.run(
            task=task,
            url=url,
            response_format=List[SocialMediaPost]
        )
        return response.answer

    def competitive_analysis(self, company: str, competitors: List[str]) -> dict:
        """Perform competitive analysis by gathering pricing and feature data"""
        results = {}
        for competitor in [company] + competitors:
            task = f"Go to {competitor}'s website, find their pricing page or main product page, and extract key features, pricing tiers, and unique selling points."
            try:
                response = self.agent.run(
                    task=task,
                    url=f"https://{competitor}.com"
                )
                results[competitor] = response.answer
                time.sleep(2)
            except Exception as e:
                results[competitor] = f"Error: {str(e)}"
        return results

    def job_market_scanner(self, job_title: str, location: str = "remote") -> List[dict]:
        """Scan job market for opportunities"""
        task = f"Search for '{job_title}' jobs in '{location}', extract job titles, companies, salary ranges, and application URLs from the first 10 results."
        response = self.agent.run(
            task=task,
            url="https://indeed.com"
        )
        return response.answer

    def price_comparison(self, product: str, websites: List[str]) -> dict:
        """Compare prices across multiple websites"""
        price_data = {}
        for site in websites:
            task = f"Search for '{product}' on this website and find the best price, including any discounts or special offers."
            try:
                response = self.agent.run(
                    task=task,
                    url=f"https://{site}"
                )
                price_data[site] = response.answer
                time.sleep(1)
            except Exception as e:
                price_data[site] = f"Error: {str(e)}"
        return price_data

    def content_research(self, topic: str, content_type: str = "blog") -> dict:
        """Research content ideas and trending topics"""
        if content_type == "blog":
            url = "https://medium.com"
            task = f"Search for '{topic}' articles, analyze trending content, and identify popular themes, engagement patterns, and content gaps."
        elif content_type == "video":
            url = "https://youtube.com"
            task = f"Search for '{topic}' videos, analyze view counts, titles, and descriptions to identify trending formats and popular angles."
        else:
            url = "https://google.com"
            task = f"Search for '{topic}' content across the web and analyze trending discussions and popular formats."

        response = self.agent.run(task=task, url=url)
        return {"topic": topic, "insights": response.answer, "platform": content_type}


# --- 4. DEMO FUNCTIONS ---
# Each function showcases a specific capability of the AdvancedNotteAgent.

def demo_ecommerce_research(product_query: str = "arch oil diesel treatment", retailer: str = "amazon.com"):
    """Demo: E-commerce product research and comparison"""
    print("[E-commerce Research Demo]")
    print("=" * 50)
    with AdvancedNotteAgent(headless=True) as agent:
        product = agent.research_product(product_query, retailer)
        print("Product Research Results:")
        print(f"Name: {product.name}")
        print(f"Price: {product.price}")
        print(f"Rating: {product.rating}")
        print(f"Availability: {product.availability}")
        print(f"Description: {product.description[:100]}...")

        print("\nPrice Comparison:")
        websites = ["amazon.com", "ebay.com", "walmart.com"]
        if retailer not in websites:
            websites.insert(0, retailer)
        prices = agent.price_comparison(product_query, websites)
        for site, data in prices.items():
            print(f"{site}: {data}")

def demo_news_intelligence():
    """Demo: News aggregation and analysis"""
    print("📰 News Intelligence Demo")
    print("=" * 50)
    with AdvancedNotteAgent() as agent:
        articles = agent.news_aggregator("artificial intelligence", 3)
        for i, article in enumerate(articles, 1):
            print(f"\nArticle {i}:")
            print(f"Title: {article.title}")
            print(f"Source: {article.source}")
            print(f"Summary: {article.summary}")
            print(f"URL: {article.url}")

def demo_social_listening():
    """Demo: Social media monitoring and sentiment analysis"""
    print("👂 Social Media Listening Demo")
    print("=" * 50)
    with AdvancedNotteAgent() as agent:
        posts = agent.social_media_monitor("#AI", "reddit")
        for i, post in enumerate(posts, 1):
            print(f"\nPost {i}:")
            print(f"Author: {post.author}")
            print(f"Content: {post.content[:100]}...")
            print(f"Engagement: {post.likes} likes")
            print(f"Platform: {post.platform}")

def demo_market_intelligence():
    """Demo: Competitive analysis and market research"""
    print("📊 Market Intelligence Demo")
    print("=" * 50)
    with AdvancedNotteAgent() as agent:
        company = "openai"
        competitors = ["anthropic", "google"]
        analysis = agent.competitive_analysis(company, competitors)
        for comp, data in analysis.items():
            print(f"\n{comp.upper()}:")
            print(f"Analysis: {str(data)[:200]}...")

def demo_job_market_analysis():
    """Demo: Job market scanning and analysis"""
    print("💼 Job Market Analysis Demo")
    print("=" * 50)
    with AdvancedNotteAgent() as agent:
        jobs = agent.job_market_scanner("python developer", "san francisco")
        print(f"Found {len(jobs)} job opportunities:")
        for job in jobs[:3]:
            print(f"- {job}")

def demo_content_strategy():
    """Demo: Content research and trend analysis"""
    print("✍️ Content Strategy Demo")
    print("=" * 50)
    with AdvancedNotteAgent() as agent:
        blog_research = agent.content_research("machine learning", "blog")
        video_research = agent.content_research("machine learning", "video")
        print("Blog Content Insights:")
        print(str(blog_research["insights"])[:300] + "...")
        print("\nVideo Content Insights:")
        print(str(video_research["insights"])[:300] + "...")


# --- 5. MULTI-AGENT WORKFLOW ---
# Demonstrates coordinating multiple agent tasks in a sequence.

class WorkflowManager:
    def __init__(self):
        self.agents = []
        self.results = {}

    def add_agent_task(self, name: str, task_func, *args, **kwargs):
        """Add an agent task to the workflow"""
        self.agents.append({
            'name': name,
            'func': task_func,
            'args': args,
            'kwargs': kwargs
        })

    def execute_workflow(self, parallel=False):
        """Execute all agent tasks in the workflow"""
        print("🚀 Executing Multi-Agent Workflow")
        print("=" * 50)
        for agent_task in self.agents:
            name = agent_task['name']
            func = agent_task['func']
            args = agent_task['args']
            kwargs = agent_task['kwargs']
            print(f"\n🤖 Executing {name}...")
            try:
                result = func(*args, **kwargs)
                self.results[name] = result
                print(f"✅ {name} completed successfully")
            except Exception as e:
                self.results[name] = f"Error: {str(e)}"
                print(f"❌ {name} failed: {str(e)}")
            if not parallel:
                time.sleep(2)
        return self.results

def research_trending_products(category: str):
    """Research trending products in a category"""
    with AdvancedNotteAgent(headless=True) as agent:
        task = f"Research trending {category} products, find top 5 products with prices, ratings, and key features."
        response = agent.agent.run(
            task=task,
            url="https://amazon.com"
        )
        return response.answer

def analyze_competitors(company: str, category: str):
    """Analyze competitors in the market"""
    with AdvancedNotteAgent(headless=True) as agent:
        task = f"Research {company} competitors in {category}, compare pricing strategies, features, and market positioning."
        response = agent.agent.run(
            task=task,
            url="https://google.com"
        )
        return response.answer

def monitor_brand_sentiment(brand: str):
    """Monitor brand sentiment across platforms"""
    with AdvancedNotteAgent(headless=True) as agent:
        task = f"Search for recent mentions of {brand} on social media and news, analyze sentiment and key themes."
        response = agent.agent.run(
            task=task,
            url="https://reddit.com"
        )
        return response.answer

def market_research_workflow(company_name: str, product_category: str):
    """Complete market research workflow"""
    workflow = WorkflowManager()
    workflow.add_agent_task(
        "Product Research",
        lambda: research_trending_products(product_category)
    )
    workflow.add_agent_task(
        "Competitive Analysis",
        lambda: analyze_competitors(company_name, product_category)
    )
    workflow.add_agent_task(
        "Social Sentiment",
        lambda: monitor_brand_sentiment(company_name)
    )
    return workflow.execute_workflow()


# --- 6. QUICK HELPER FUNCTIONS ---
# Simplified functions for common, one-off tasks.

def quick_scrape(url: str, instructions: str = "Extract main content"):
    """Quick scraping function for simple data extraction"""
    with AdvancedNotteAgent(headless=True, max_steps=5) as agent:
        response = agent.agent.run(
            task=f"{instructions} from this webpage",
            url=url
        )
        return response.answer

def quick_search(query: str, num_results: int = 5):
    """Quick search function with structured results"""
    with AdvancedNotteAgent(headless=True, max_steps=10) as agent:
        task = f"Search for '{query}' and return the top {num_results} results with titles, URLs, and brief descriptions."
        response = agent.agent.run(
            task=task,
            url="https://google.com",
            response_format=SearchResult
        )
        return response.answer

def quick_form_fill(form_url: str, form_data: dict):
    """Quick form filling function"""
    with AdvancedNotteAgent(headless=False, max_steps=15) as agent:
        data_str = ", ".join([f"{k}: {v}" for k, v in form_data.items()])
        task = f"Fill out the form with this information: {data_str}, then submit it."
        response = agent.agent.run(
            task=task,
            url=form_url
        )
        return response.answer


# --- 7. MAIN EXECUTION BLOCK ---
# Controls the flow of the script.

def main():
    """Main function to run all demos"""
    print("🚀 Advanced Notte AI Agent Tutorial")
    print("=" * 60)
    print("Note: Make sure to set your GEMINI_API_KEY at the top of the file!")
    print("Get your free API key at: https://aistudio.google.com/app/apikey")
    print("=" * 60)

    if GEMINI_API_KEY == "USE YOUR OWN API KEY HERE":
        print("❌ Please set your GEMINI_API_KEY in the code above!")
        return

    try:
        print("\n1. E-commerce Research Demo")
        demo_ecommerce_research("arch oil diesel treatment", retailer="amazon.com")

        """   print("\n2. News Intelligence Demo")
        demo_news_intelligence()

        print("\n3. Social Media Listening Demo")
        demo_social_listening()

        print("\n4. Market Intelligence Demo")
        demo_market_intelligence()

        print("\n5. Job Market Analysis Demo")
        demo_job_market_analysis()

        print("\n6. Content Strategy Demo")
        demo_content_strategy()

        print("\n7. Multi-Agent Workflow Demo")
        results = market_research_workflow("Tesla", "electric vehicles")
        print("Workflow Results:")
        for task, result in results.items():
            print(f"{task}: {str(result)[:150]}...") """

    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("💡 Tip: Make sure your Gemini API key is valid and you have internet connection")

if __name__ == "__main__":
    print("🧪 Quick Test Examples:")
    print("=" * 30)
    main()
    print("\n✨ Tutorial Complete!")
    """  print("1. Quick Scrape Example:")
    try:
        result = quick_scrape("https://news.ycombinator.com", "Extract the top 3 post titles")
        print(f"Scraped: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Quick Search Example:")
    try:
        # NOTE: This function may fail due to a bug in the library with this specific Pydantic model.
        # It's included to match the notebook but might need debugging or library updates.
        print("Skipping Quick Search example as it may have library compatibility issues.")
        # search_results = quick_search("latest AI news", 3)
        # print(f"Search Results: {search_results}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n3. Custom Agent Task:")
    try:
        with AdvancedNotteAgent(headless=True) as agent:
            response = agent.agent.run(
                task="Go to Wikipedia, search for 'artificial intelligence', and summarize the main article in 2 sentences.",
                url="https://wikipedia.org"
            )
            print(f"Wikipedia Summary: {response.answer}")
    except Exception as e:
        print(f"Error: {e}")

    # Uncomment the line below to run the full suite of demos
     """

    print("\n✨ Tutorial Complete!")
    print("💡 Tips for success:")
    print("- Start with simple tasks and gradually increase complexity")
    print("- Use structured outputs (Pydantic models) for reliable data extraction")
    print("- Handle errors gracefully in production workflows")
    print("\n🚀 Next Steps:")
    print("- Customize the agents for your specific use cases")
    print("- Add error handling and retry logic for production")
    print("- Implement logging and monitoring for agent activities")
