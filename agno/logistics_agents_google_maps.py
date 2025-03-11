import os
import requests
from agno.agent import Agent
from agno.models.azure import AzureOpenAI

# Define custom Oxylabs tool
class FuelStationSearchTool:
    def __init__(self):
        self.name = "FuelStationSearchTool"
        self.description = "Fetches nearby fuel stations using Oxylabs Real-Time API."

    def run(self, location_query, pages=1):
        payload = {
            'source': 'google_maps',
            'domain': 'com',
            'query': f'fuel stations in {location_query}',
            'pages': pages,
        }

        response = requests.post(
            'https://realtime.oxylabs.io/v1/queries',
            auth=('baval_6hy9U', 'Baval=123456789'),
            json=payload,
        )

        if response.status_code != 200:
            return f"API Error: {response.status_code}, {response.text}"

        data = response.json()

        stations_info = []
        for result in data.get('results', [])[:5]:
            title = result.get('title', 'No Name')
            address = result.get('address', 'Address Unavailable')
            rating = result.get('rating', 'Rating Unavailable')
            stations_info.append(f"{title} - {address} (Rating: {rating})")

        if not stations_info:
            return "No nearby fuel stations found."

        return "\n".join(stations_info)

# Initialize Agno agent
agent = Agent(
    model=AzureOpenAI(id="gpt-4o"),
    description="An intelligent logistics assistant helping drivers find nearby services.",
    instructions=[
        "Use FuelStationSearchTool for queries about nearby fuel stations.",
        "List fuel stations clearly with names, addresses, and ratings."
    ],
    markdown=True,
    tools=[FuelStationSearchTool()]
)

# Main execution
if __name__ == "__main__":
    location_query = "NLS, Missisauga, ON"
    agent.print_response(location_query)

