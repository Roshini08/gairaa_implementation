from graph import build_travel_graph
from schemas import TravelState

TEST_CASES = [
    "My family and I want a 3-day trip to Bangalore.",
    "I want a low-budget 4-day trip to Goa.",
    "I have a 2-day business trip to Mumbai.",
    "Suggest a relaxed weekend trip to Pondicherry.",
    "Plan a trip to Kerala for 5 days.",
]


def make_initial_state(user_query: str) -> TravelState:
    """Builds a fresh, empty TravelState with only user_query filled in."""
    return {
        "user_query": user_query,
        "destination": None,
        "trip_type": None,
        "duration": None,
        "traveler_type": None,
        "budget_level": None,
        "reasoning": None,
        "final_plan": None,
        "error": None,
    }


def run_test_case(graph, index: int, user_query: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"TEST CASE {index}")
    print(f"{'=' * 70}")
    print(f"User query      : {user_query}")

    initial_state = make_initial_state(user_query)

    
    final_state = graph.invoke(initial_state)

    if final_state.get("error"):
        print(f"ERROR           : {final_state['error']}")
        return

    print(f"Destination     : {final_state.get('destination')}")
    print(f"Trip type       : {final_state.get('trip_type')}")
    print(f"Duration        : {final_state.get('duration')}")
    print(f"Traveler type   : {final_state.get('traveler_type')}")
    print(f"Budget level    : {final_state.get('budget_level')}")
    print(f"Reasoning       : {final_state.get('reasoning')}")
    print(f"Selected route  : {final_state.get('trip_type')}_handler")
    print(f"--- Final travel plan ---\n{final_state.get('final_plan')}")


def main():
    print("Building the LangGraph travel workflow...")
    graph = build_travel_graph()
    print("Graph compiled successfully.\n")

    for i, query in enumerate(TEST_CASES, start=1):
        run_test_case(graph, i, query)


if __name__ == "__main__":
    main()