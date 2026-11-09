import json
import os
from typing import Any, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
).strip()



try:

    if GEMINI_API_KEY:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print(
            "Gemini client initialized successfully."
        )

    else:

        client = None

        print(
            "ERROR: GEMINI_API_KEY is missing."
        )

except Exception as error:

    client = None

    print(
        "Gemini initialization error:",
        error
    )




try:

    from tools import (
        execute_tool,
        get_tool_definitions
    )

except Exception as error:

    print(
        "Tool import error:",
        error
    )

    execute_tool = None

    def get_tool_definitions():
        return []



def run_tool(
    tool_name: str,
    arguments: Dict[str, Any]
):

    if execute_tool is None:

        return {

            "success": False,

            "error": "Tool execution unavailable."
        }

    try:

        result = execute_tool(
            tool_name,
            arguments
        )

        return {

            "success": True,

            "result": result
        }

    except Exception as error:

        return {

            "success": False,

            "error": str(error)
        }



def fallback_response(
    disease: str,
    confidence: float,
    explanation: str = ""
):


    if confidence < 0.70:

        return {

            "disease": disease,

            "confidence": confidence,

            "explanation": explanation,

            "guidance": (
                "The prediction confidence is low. "
                "Please upload a clearer leaf image and "
                "confirm the diagnosis with an agricultural "
                "expert before taking treatment-related action."
            ),

            "uncertainty": (
                "Low-confidence prediction. "
                "Specific treatment advice should not be "
                "given from this prediction alone."
            )
        }


    return {

        "disease": disease,

        "confidence": confidence,

        "explanation": explanation,

        "guidance": (
            "The AI advisory service is temporarily "
            "unavailable. Please verify the detected "
            "disease using reliable agricultural guidance "
            "before taking action."
        ),

        "uncertainty": (
            "The Gemini advisory service or external "
            "agricultural knowledge tool could not be used."
        )
    }


def build_gemini_tools():

    definitions = get_tool_definitions()

    function_declarations = []

    for tool in definitions:

        function_declarations.append(

            types.FunctionDeclaration(

                name=tool["name"],

                description=tool["description"],

                parameters=tool["parameters"]
            )
        )

    return [

        types.Tool(

            function_declarations=function_declarations
        )

    ]


def run_agent(
    disease: str,
    confidence: float,
    explanation: str = "",
    question: str = ""
):

    

    disease = str(
        disease
    )

    confidence = float(
        confidence
    )

    explanation = str(
        explanation or ""
    )

    question = str(
        question or ""
    ).strip()


 

    if confidence < 0.70:

        print(
            "\nLOW CONFIDENCE:"
            f" {confidence:.2%}"
        )

        print(
            "Gemini advisory skipped for safety."
        )

        return fallback_response(

            disease=disease,

            confidence=confidence,

            explanation=explanation
        )


    if client is None:

        print(
            "\nERROR: Gemini client unavailable."
        )

        return fallback_response(

            disease=disease,

            confidence=confidence,

            explanation=explanation
        )


  

    try:

        gemini_tools = build_gemini_tools()

        print(
            "\nAvailable Gemini tools:"
        )

        for tool in get_tool_definitions():

            print(
                " -",
                tool["name"]
            )

    except Exception as error:

        print(
            "\nTool definition error:",
            error
        )

        return fallback_response(

            disease=disease,

            confidence=confidence,

            explanation=explanation
        )



    system_instruction = """
You are an agricultural advisory AI agent.

The CNN has already performed disease classification.

You MUST NOT perform disease classification yourself.

Your responsibilities:

1. Preserve the exact CNN disease prediction.

2. Preserve the supplied confidence score.

3. Understand and answer the user's actual question.

4. When the user asks about disease symptoms,
   management, prevention, precautions, or agricultural
   guidance, CALL get_agricultural_guidance.

5. Do NOT invent disease-specific agricultural facts.

6. Use information returned by the agricultural knowledge
   tool for disease-specific factual guidance.

7. If weather or environmental conditions are relevant,
   CALL get_weather.

8. Do not call tools unnecessarily.

9. Never claim that a tool was used unless it was
   actually called.

10. Do not provide unsupported chemical names,
    pesticide dosages, concentrations, or dangerous
    treatment instructions.

11. Clearly communicate uncertainty.

12. Answer the user's question directly.

13. AI-assisted disease predictions should be verified
    before important agricultural decisions.

14. Do not change or replace the CNN prediction.

Architecture:

CNN
→ Grad-CAM
→ Integrated Gradients
→ Gemini Agent
→ Tool Calling
→ Agent Response
→ Guardrails
"""


 

    user_message = f"""
CNN DISEASE PREDICTION
======================

Disease:
{disease}

Confidence:
{confidence:.2%}

XAI Explanation:
{explanation}

USER QUESTION:
{
    question
    if question
    else
    "What should I do about this result?"
}

IMPORTANT:

Use the agricultural knowledge tool when
disease-specific information is required.

Use the weather tool when environmental
conditions are relevant.

Do not invent agricultural facts.
"""


    
    contents = [

        types.Content(

            role="user",

            parts=[

                types.Part(
                    text=user_message
                )

            ]
        )

    ]




    config = types.GenerateContentConfig(

        system_instruction=system_instruction,

        tools=gemini_tools,

        temperature=0.2,

        max_output_tokens=1000
    )


    

    max_iterations = 5

    for iteration in range(
        max_iterations
    ):

        print(
            "\n=========================================="
        )

        print(
            f"GEMINI AGENT ITERATION {iteration + 1}"
        )

        print(
            "=========================================="
        )

        try:

            response = client.models.generate_content(

                model=GEMINI_MODEL,

                contents=contents,

                config=config
            )

        except Exception as error:

            print(
                "\n========== GEMINI ERROR =========="
            )

            print(
                repr(error)
            )

            print(
                "===================================\n"
            )

            return fallback_response(

                disease=disease,

                confidence=confidence,

                explanation=explanation
            )




        if not response.candidates:

            print(
                "Gemini returned no candidates."
            )

            return fallback_response(

                disease=disease,

                confidence=confidence,

                explanation=explanation
            )


        model_content = (
            response.candidates[0].content
        )


        

        function_calls = []

        for part in model_content.parts:

            function_call = getattr(

                part,

                "function_call",

                None
            )

            if function_call:

                function_calls.append(
                    function_call
                )


        

        if not function_calls:

            final_text = str(
                response.text or ""
            ).strip()

            if final_text:

                print(
                    "\n========== GEMINI FINAL RESPONSE =========="
                )

                print(
                    final_text
                )

                print(
                    "============================================\n"
                )

                return {

                    "disease": disease,

                    "confidence": confidence,

                    "explanation": explanation,

                    "guidance": final_text,

                    "uncertainty": (
                        "The response was generated using "
                        "the CNN prediction and Gemini. "
                        "External agricultural information "
                        "was used when a tool was called."
                    )
                }

            return fallback_response(

                disease=disease,

                confidence=confidence,

                explanation=explanation
            )


        contents.append(
            model_content
        )



        function_response_parts = []

        for function_call in function_calls:

            tool_name = (
                function_call.name
            )

            arguments = dict(
                function_call.args or {}
            )

            print(
                "\n========== GEMINI TOOL CALL =========="
            )

            print(
                "Tool:",
                tool_name
            )

            print(
                "Arguments:",
                arguments
            )

            print(
                "=======================================\n"
            )


           

            tool_result = run_tool(

                tool_name,

                arguments
            )


            print(
                "\n========== TOOL RESULT =========="
            )

            print(
                json.dumps(

                    tool_result,

                    indent=2,

                    ensure_ascii=False,

                    default=str
                )
            )

            print(
                "=================================\n"
            )


            function_response_parts.append(

                types.Part.from_function_response(

                    name=tool_name,

                    response={
                        "result": tool_result
                    }
                )
            )


        contents.append(

            types.Content(

                role="user",

                parts=function_response_parts
            )
        )


    print(
        "\nGemini reached maximum tool iterations."
    )

    return fallback_response(

        disease=disease,

        confidence=confidence,

        explanation=explanation
    )




if __name__ == "__main__":

    result = run_agent(

        disease="Grape___Black_rot",

        confidence=0.8710,

        explanation=(
            "Grad-CAM and Integrated Gradients "
            "provided visual attribution."
        ),

        question=(
            "What are the symptoms, management steps, "
            "prevention methods, and precautions for "
            "this disease?"
        )
    )


    print(
        "\n========== RESULT ==========\n"
    )

    print(

        json.dumps(

            result,

            indent=2,

            ensure_ascii=False,

            default=str
        )
    )
    
    
    
    
    
    
    
    