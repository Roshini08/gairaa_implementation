"""
langgraph_demo.py
-----------------
Simple LangGraph demonstration without an LLM.

Flow:
START → classify → conditional routing → handler → END

The graph identifies whether the user input is a question
or a statement and then gives a suitable response.
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END




class ToyState(TypedDict):
    text: str
    category: str
    result: str



def classify_node(state: ToyState) -> dict:
    text = state["text"].lower()

    if "?" in text:
        category = "question"
    else:
        category = "statement"

    return {"category": category}




def route_by_category(
    state: ToyState,
) -> Literal["question_handler", "statement_handler"]:

    if state["category"] == "question":
        return "question_handler"

    return "statement_handler"



def question_handler(state: ToyState) -> dict:
    text = state["text"].lower()

    if "goa" in text:
        result = (
            "You can visit Baga Beach, Calangute Beach, "
            "and Anjuna Beach in Goa."
        )
    elif "chennai" in text:
        result = (
            "You can visit Marina Beach, Kapaleeshwarar Temple, "
            "and Fort St. George in Chennai."
        )
    else:
        result = (
            "Please provide a destination so I can "
            "suggest some places to visit."
        )

    return {"result": result}




def statement_handler(state: ToyState) -> dict:
    text = state["text"].lower()

    if "beach" in text:
        result = "If you like beaches, Goa is a good travel destination."
    else:
        result = "I understand your statement."

    return {"result": result}



def build_toy_graph():

    builder = StateGraph(ToyState)

    # Add nodes
    builder.add_node("classify", classify_node)
    builder.add_node("question_handler", question_handler)
    builder.add_node("statement_handler", statement_handler)

    # START → classify
    builder.add_edge(START, "classify")

    # Conditional routing
    builder.add_conditional_edges(
        "classify",
        route_by_category,
        {
            "question_handler": "question_handler",
            "statement_handler": "statement_handler",
        },
    )

    # Handlers → END
    builder.add_edge("question_handler", END)
    builder.add_edge("statement_handler", END)

    return builder.compile()




def run_demo():

    graph = build_toy_graph()

    test_inputs = [
        "Where should I go in Goa?",
        "I like beaches.",
        "What can I visit in Chennai?",
    ]

    for sample_text in test_inputs:

        initial_state = {
            "text": sample_text,
            "category": "",
            "result": "",
        }

        final_state = graph.invoke(initial_state)

        print("=" * 60)
        print("LANGGRAPH DEMO")
        print("=" * 60)

        print(f"Input    : {sample_text}")
        print(f"Category : {final_state['category']}")
        print(f"Result   : {final_state['result']}")

        print()


if __name__ == "__main__":
    run_demo()