import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: int = int(os.getenv("PORT", 8003))
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://xmrlazemifmepyahqsrz.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_BQpJ8OjTcJarh5ZIBW9mzw_OE3Ewyfk")

settings = Settings()

