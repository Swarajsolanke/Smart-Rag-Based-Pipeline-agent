# config/settings.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
# QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "ai_pipeline_collection")

# Embedding model (sentence-transformers local model name)
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LLM config (Gemini model name)
# 


# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM (Gemini via LangChain)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # flash is friendlier on free tier

# Weather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "ai_pipeline_collection")

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LangSmith (set these to enable tracing)
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")  # "true" to enable
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "ai-pipeline-demo")

