import dotenv
import os

if not os.getenv("MONGO_URI"):
    dotenv.load_dotenv()

