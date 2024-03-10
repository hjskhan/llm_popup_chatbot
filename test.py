import os
import dotenv
dotenv.load_dotenv()
print(os.getenv('ASTRA_DB_API_ENDPOINT'))
print(type(os.getenv('ASTRA_DB_API_ENDPOINT')))