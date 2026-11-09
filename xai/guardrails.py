from pydantic import (
    BaseModel,
    Field
)


from guardrails import (
    Guard
)


class SafeAgriculturalResponse(
    BaseModel
):

    disease: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    explanation: str

    guidance: str

    uncertainty: str


guard = Guard.from_pydantic(
    output_class=
        SafeAgriculturalResponse
)


def validate_output(
    data
):

    try:

        result = (
            guard.parse(
                data
            )
        )


        validated = getattr(
            result,
            "validated_output",
            None
        )


        if validated is not None:

            return validated


        return data


    except Exception as error:

        print(
            "Guardrails validation warning:",
            error
        )


        return {

            "disease":
                str(
                    data.get(
                        "disease",
                        "Unknown"
                    )
                ),

            "confidence":
                max(
                    0.0,
                    min(
                        1.0,
                        float(
                            data.get(
                                "confidence",
                                0.0
                            )
                        )
                    )
                ),

            "explanation":
                str(
                    data.get(
                        "explanation",
                        "Vision explanation unavailable."
                    )
                ),

            "guidance":
                str(
                    data.get(
                        "guidance",
                        "Confirm with local agricultural guidance."
                    )
                ),

            "uncertainty":
                str(
                    data.get(
                        "uncertainty",
                        "AI output is not a definitive field diagnosis."
                    )
                )
        }
        
        
        
        
        