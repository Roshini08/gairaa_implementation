from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field



TripType = Literal[
    "family",
    "budget",
    "business",
    "leisure"
]

BudgetLevel = Literal[
    "low",
    "medium",
    "high"
]


class TravelClassification(BaseModel):
    

    destination: str = Field(
        description="City or region the user wants to visit"
    )

    trip_type: TripType = Field(
        description="One of: family, budget, business, leisure"
    )

    
    duration: str | int = Field(
        description="Trip length, for example 4 or '4 days'"
    )

   
    traveler_type: str = Field(
        default="unspecified",
        description=(
            "Who is travelling, e.g. family, couple, solo, "
            "colleagues, or unspecified"
        )
    )

    budget_level: BudgetLevel = Field(
        description="One of: low, medium, high"
    )

    
    reasoning: str = Field(
        default="",
        description="One short sentence explaining the classification"
    )


class TravelState(TypedDict):
    

    user_query: str

    destination: Optional[str]

    trip_type: Optional[TripType]

    duration: Optional[str | int]

    traveler_type: Optional[str]

    budget_level: Optional[BudgetLevel]

    reasoning: Optional[str]

    final_plan: Optional[str]

    error: Optional[str]
    