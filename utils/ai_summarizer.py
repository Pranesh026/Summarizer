import json
import logging
import time
from openai import AzureOpenAI
from azure.core.exceptions import AzureError  # Import for Azure-specific exceptions
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION,AZURE_OPENAI_DEPLOYMENT

# Set up the Azure OpenAI client
client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )

def get_summary_from_ai(data):
    retries = 3  # Number of retries before failing
    backoff_factor = 2  # Exponential backoff factor (time * factor)
    
    for attempt in range(retries):
        try:
            # Prepare the prompt with the provided JSON data
            prompt = f"Summarize the following JSON data:\n\n{json.dumps(data, indent=2)}\n\n The summarization should be in 4 to 5 sentences, Be sure to highlight the key factors that are present, such as:\n\n Part Name, Material, Size, Weight, Manufacturing Process,Part Type,Standard Part Classification,Features,  Fit Type, Assembly Type, Parent Assembly, Function, Revision/Version, Status, Date Created, Author/Creator, Keywords/Tags, Drawing Type, Clearance, Load/Stress, Surface Finish, Manufacturing Location, Custom Properties, Compatibility, Usage Frequency, Assembly Fit, Stock Availability, Part Category.\n\n If the data is missing a factor just ignore that factor.\n\n list out the factors below the summarization which all were used for this summarization."
            print(prompt)

            # Make a request to the Azure OpenAI API for summarization
            logging.info(f"Making request to Azure OpenAI with model gpt-4o-mini...")
            
            response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,  # model = "deployment_name".
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
            temperature=0.5,
            )

            # Extract the AI's summarized text
            #summary = response.choices[0].message['content'].strip()
            #summary = response
            summary = response.choices[0].message.content.strip()

            logging.info("AI summary generated successfully.")
            return summary

        except AzureError as e:
            # Handle Azure-specific exceptions (network issues, API-related issues)
            logging.error(f"Azure OpenAI error: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {backoff_factor**attempt} seconds...")
                time.sleep(backoff_factor**attempt)
            else:
                return "Error occurred while generating summary. Please try again later."

        except Exception as e:
            # Handle any other unexpected exceptions
            logging.error(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again."

    return "Failed to generate summary after multiple attempts."

