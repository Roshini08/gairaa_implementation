import json
import logging
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import ValidationError

from schemas import TravelState, TravelClassification

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_NAME = "qwen2.5:3b-instruct"


llm = ChatOllama(model=MODEL_NAME, temperature=0.2)




CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a travel request analyzer. Read the user's travel request "
            "and respond with ONLY a JSON object (no extra text, no markdown "
            "fences) with exactly these keys: "
            "destination, trip_type, duration, traveler_type, budget_level, reasoning. "
            "trip_type must be one of: family, budget, business, leisure. "
            "budget_level must be one of: low, medium, high.",
        ),
        ("human", "{query}"),
    ]
)


def analyze_and_classify(state: TravelState) -> dict:
    
    chain = CLASSIFICATION_PROMPT | llm

    try:
        response = chain.invoke({"query": state["user_query"]})
    except Exception as exc:
      
        logger.error("LLM call failed during analysis: %s", exc)
        return {"error": f"Could not reach local LLM (is Ollama running?): {exc}"}

    raw_text = response.content.strip()

    
    try:
        start = raw_text.index("{")
        end = raw_text.rindex("}") + 1
        parsed_json = json.loads(raw_text[start:end])
        classification = TravelClassification(**parsed_json)
    except (ValueError, json.JSONDecodeError, ValidationError) as exc:
        logger.error("Invalid classification from LLM: %s | raw=%s", exc, raw_text)
        return {"error": f"Invalid classification returned by LLM: {exc}"}

    return {
        "destination": classification.destination,
        "trip_type": classification.trip_type,
        "duration": classification.duration,
        "traveler_type": classification.traveler_type,
        "budget_level": classification.budget_level,
        "reasoning": classification.reasoning,
    }



def route_by_trip_type(
    state: TravelState,
) -> Literal["family_handler", "budget_handler", "business_handler", "leisure_handler"]:
    """
    ROUTER function (not a node -- it produces no state update).
    Input it receives: the full state (specifically reads trip_type).
    Output it produces: the STRING NAME of the next node to run.
    This is passed to add_conditional_edges(), which uses the returned
    name to look up the actual next node via the mapping dict.
    """
    if state.get("error"):
        return "leisure_handler"

    trip_type = state.get("trip_type")
    if trip_type == "family":
        return "family_handler"
    if trip_type == "budget":
        return "budget_handler"
    if trip_type == "business":
        return "business_handler"
    return "leisure_handler"




def _generate_plan(state: TravelState, style_instruction: str) -> dict:
    """
    Shared helper used by all four handlers so we don't repeat the same
    LangChain wiring four times. Not a node itself -- called BY nodes.
    """
    if state.get("error"):
        return {"final_plan": f"Could not generate a plan: {state['error']}"}

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are a travel planner. {style_instruction} "
                "Keep the plan to 4-6 short bullet points.",
            ),
            (
                "human",
                "Destination: {destination}\n"
                "Duration: {duration}\n"
                "Traveler type: {traveler_type}\n"
                "Budget level: {budget_level}\n"
                "Original request: {user_query}",
            ),
        ]
    )
    chain = prompt | llm

    try:
        response = chain.invoke(
            {
                "destination": state.get("destination", "unspecified"),
                "duration": state.get("duration", "unspecified"),
                "traveler_type": state.get("traveler_type", "unspecified"),
                "budget_level": state.get("budget_level", "unspecified"),
                "user_query": state["user_query"],
            }
        )
    except Exception as exc:
        logger.error("LLM call failed during plan generation: %s", exc)
        return {"final_plan": f"Could not generate a plan (LLM error): {exc}"}

    return {"final_plan": response.content.strip()}


def family_handler(state: TravelState) -> dict:
    """NODE. Generates a family-oriented plan. Input: TravelState. Output: final_plan."""
    return _generate_plan(
        state,
        "Focus on family-friendly activities, safety, and comfortable pacing.",
    )


def budget_handler(state: TravelState) -> dict:
    """NODE. Generates a low-cost oriented plan."""
    return _generate_plan(
        state,
        "Focus on low-cost options: budget stays, free/cheap attractions, local food.",
    )


def business_handler(state: TravelState) -> dict:
    """NODE. Generates a business-trip oriented plan."""
    return _generate_plan(
        state,
        "Focus on efficiency: proximity to business districts, quick meals, minimal downtime.",
    )


def leisure_handler(state: TravelState) -> dict:
    """NODE. Generates a general leisure/relaxation oriented plan (default route)."""
    return _generate_plan(
        state,
        "Focus on relaxation, sightseeing, and a comfortable, unhurried pace.",
    )



def build_travel_graph():
    """
    Wires all nodes and edges together and compiles the graph.

    StateGraph(TravelState): every node here reads/writes TravelState.
    add_node(): registers each function under a name.
    add_edge(): fixed transitions (START -> analyze, handlers -> END).
    add_conditional_edges(): branches based on route_by_trip_type().
    compile(): validates the graph and returns a runnable object.
    """
    builder = StateGraph(TravelState)

    builder.add_node("analyze_and_classify", analyze_and_classify)
    builder.add_node("family_handler", family_handler)
    builder.add_node("budget_handler", budget_handler)
    builder.add_node("business_handler", business_handler)
    builder.add_node("leisure_handler", leisure_handler)

    builder.add_edge(START, "analyze_and_classify")

    builder.add_conditional_edges(
        "analyze_and_classify",
        route_by_trip_type,
        {
            "family_handler": "family_handler",
            "budget_handler": "budget_handler",
            "business_handler": "business_handler",
            "leisure_handler": "leisure_handler",
        },
    )

    builder.add_edge("family_handler", END)
    builder.add_edge("budget_handler", END)
    builder.add_edge("business_handler", END)
    builder.add_edge("leisure_handler", END)

    return builder.compile()
