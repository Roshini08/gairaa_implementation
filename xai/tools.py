import requests


def get_agricultural_guidance(disease: str):
    """
    Dynamically retrieves agricultural information for the predicted disease
    using the Wikipedia Search API and REST API.
    """

    if not disease or not isinstance(disease, str):
        return {
            "success": False,
            "error": "Disease name is required."
        }

    try:
        clean_disease = disease.replace("___", " ").replace("_", " ").strip()

        search_url = "https://en.wikipedia.org/w/api.php"

        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": clean_disease,
            "srlimit": 5,
            "format": "json"
        }

        search_response = requests.get(
            search_url,
            params=search_params,
            timeout=10
        )

        search_response.raise_for_status()

        search_data = search_response.json()
        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            return {
                "success": False,
                "disease": clean_disease,
                "error": "No agricultural information found."
            }

        article_title = search_results[0].get("title")

        if not article_title:
            return {
                "success": False,
                "disease": clean_disease,
                "error": "No valid article found."
            }

        summary_url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + requests.utils.quote(article_title)
        )

        summary_response = requests.get(
            summary_url,
            timeout=10
        )

        summary_response.raise_for_status()

        summary_data = summary_response.json()

        return {
            "success": True,
            "disease": clean_disease,
            "article": article_title,
            "summary": summary_data.get(
                "extract",
                "No detailed summary available."
            ),
            "url": summary_data.get(
                "content_urls",
                {}
            ).get(
                "desktop",
                {}
            ).get(
                "page",
                ""
            )
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "disease": disease,
            "error": f"Knowledge retrieval failed: {str(error)}"
        }

    except Exception as error:
        return {
            "success": False,
            "disease": disease,
            "error": f"Unexpected error: {str(error)}"
        }


def get_weather(city: str):
    """
    Retrieves current weather information using Open-Meteo.
    """

    if not city or not isinstance(city, str):
        return {
            "success": False,
            "error": "City name is required."
        }

    try:
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geocoding_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        geocoding_response.raise_for_status()

        geocoding_data = geocoding_response.json()
        locations = geocoding_data.get("results", [])

        if not locations:
            return {
                "success": False,
                "city": city,
                "error": "City not found."
            }

        location = locations[0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        resolved_city = location.get("name", city)
        country = location.get("country", "")

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m"
            )
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data.get("current", {})

        return {
            "success": True,
            "city": resolved_city,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature_2m"),
            "humidity_percent": current.get(
                "relative_humidity_2m"
            ),
            "precipitation_mm": current.get(
                "precipitation"
            ),
            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            )
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "city": city,
            "error": f"Weather retrieval failed: {str(error)}"
        }

    except Exception as error:
        return {
            "success": False,
            "city": city,
            "error": f"Unexpected error: {str(error)}"
        }


def get_tool_definitions():
    """
    Defines the tools that Gemini can call.
    """

    return [
        {
            "name": "get_agricultural_guidance",
            "description": (
                "Retrieve relevant agricultural information "
                "for a predicted crop disease."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "disease": {
                        "type": "string",
                        "description": (
                            "Predicted crop disease name."
                        )
                    }
                },
                "required": ["disease"]
            }
        },
        {
            "name": "get_weather",
            "description": (
                "Retrieve current weather information "
                "for a specified city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": (
                            "City name for which current "
                            "weather information is required."
                        )
                    }
                },
                "required": ["city"]
            }
        }
    ]


def execute_tool(name: str, arguments: dict):
    """
    Executes the tool requested by the Gemini agent.
    """

    if name == "get_agricultural_guidance":
        return get_agricultural_guidance(
            arguments.get("disease", "")
        )

    if name == "get_weather":
        return get_weather(
            arguments.get("city", "")
        )

    return {
        "success": False,
        "error": f"Unknown tool: {name}"
    }
    
    