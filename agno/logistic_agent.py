import re
from itertools import permutations
from agno.agent import Agent
from agno.models.openai import OpenAIChat


# Sample data for shipments and distances
tracking_data = {
    "TRK12345": "In transit at Toronto distribution center",
    "TRK98765": "Delivered on 2025-03-09 10:24",
    "TRK55555": "Out for delivery - last scanned at Vancouver hub"
}
distance_matrix = {
    "Warehouse": {"A": 10, "B": 15, "C": 20},
    "A": {"Warehouse": 10, "B": 12, "C": 5},
    "B": {"Warehouse": 15, "A": 12, "C": 8},
    "C": {"Warehouse": 20, "A": 5,  "B": 8}
}
# Define custom tools
class TrackingTool:
    def __init__(self):
        self.name = "TrackingTool"
        self.description = "Provides shipment status updates given a tracking ID."
    def run(self, query: str) -> str:
        match = re.search(r"\bTRK\d+\b", query.upper())
        if not match:
            return "Please provide a valid tracking ID."
        tid = match.group(0)
        status = tracking_data.get(tid)
        return f"Status for {tid}: {status}" if status else f"No information for {tid}."

class RouteTool:
    def __init__(self):
        self.name = "RouteTool"
        self.description = "Computes the best delivery route given a start and destinations."
    def run(self, query: str) -> str:
        m = re.search(r"from\s+([\w\s]+)\s+to\s+(.+)", query, re.IGNORECASE)
        if not m:
            return "Specify route as 'from <Origin> to <Dest1>, <Dest2>, ...'."
        origin = m.group(1).strip()
        dests = [d.strip() for d in re.split(r",| and ", m.group(2)) if d.strip()]
        if origin not in distance_matrix:
            return f"Unknown origin: {origin}."
        for loc in dests:
            if loc not in distance_matrix:
                return f"Unknown destination: {loc}."
        best_distance = float('inf')
        best_order = None
        for perm in permutations(dests):
            total = 0
            cur = origin
            for nxt in perm:
                total += distance_matrix[cur][nxt]
                cur = nxt
            if total < best_distance:
                best_distance = total
                best_order = perm
        route_plan = " -> ".join([origin] + list(best_order)) if best_order else origin
        return f"Optimal route: {route_plan} (Total distance: {best_distance} km)"
# Create the agent with model, instructions, and tools
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="You are a knowledgeable logistics assistant.",
    instructions=[
        "If the user asks about a shipment or tracking ID, use the TrackingTool.",
        "If the user asks about route optimization or best route, use the RouteTool.",
        "Provide concise and clear answers, including relevant details from the tools."
    ],
    tools=[TrackingTool(), RouteTool()],
    show_tool_calls=True,  # set to False for clean output (True for debugging)
    markdown=True
)
# Example usage
# Execute the agent queries

agent.print_response("Where is shipment TRK12345?")


agent.print_response("What is the best route from Warehouse to A, B and C?")