from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. We create a class that inherits from BaseSettings. 
# This tells Pydantic: "Go look for environment variables that match these names."
class Settings(BaseSettings):
    # 2. These are type-hinted fields. Pydantic will automatically 
    # look for PROJECT_NAME and DATABASE_URL in your .env or OS.
    project_name: str
    database_url: str

    # 3. This 'model_config' tells the class HOW to find the data.
    # env_file=".env" tells it to check your local file.
    # extra="ignore" means if there are other variables in .env, don't crash.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# 4. We instantiate the class. This is what you will import in other files.
settings = Settings()