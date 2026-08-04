import os
from typing import Dict, Any
from app.graphs.state import AgentState
from app.config.settings import settings
from app.services.vision_service import vision_service
from app.utils.logger import app_logger

async def file_agent_node(state: AgentState) -> Dict[str, Any]:
    """File Agent: Manages document/file parsing and image vision analysis via OpenRouter Vision API."""
    query = state.get("user_query", "")
    app_logger.info(f"[FileAgent] Processing document/image request: '{query[:50]}'")

    file_results = []
    extracted_responses = []

    # Check STORAGE_DIR for uploaded files
    storage_dir = settings.STORAGE_DIR
    if os.path.exists(storage_dir):
        saved_files = sorted(os.listdir(storage_dir), key=lambda x: os.path.getmtime(os.path.join(storage_dir, x)), reverse=True)
        image_files = [f for f in saved_files if vision_service.is_image_file(f)]

        if image_files:
            # Process latest uploaded image
            latest_image = image_files[0]
            image_path = os.path.join(storage_dir, latest_image)
            app_logger.info(f"[FileAgent] Processing image with OpenRouter Vision API: {latest_image}")
            try:
                vision_analysis = await vision_service.analyze_image_async(image_path, prompt=query)
                file_results.append({
                    "action": "openrouter_vision",
                    "file": latest_image,
                    "status": "success",
                    "analysis": vision_analysis
                })
                extracted_responses.append(vision_analysis)
            except Exception as e:
                app_logger.error(f"[FileAgent] Vision error for {latest_image}: {e}")
                file_results.append({
                    "action": "openrouter_vision",
                    "file": latest_image,
                    "status": "error",
                    "error": str(e)
                })

    reasoning = state.get("intermediate_reasoning", []) + ["File Agent processed image/document using OpenRouter Vision API"]

    result: Dict[str, Any] = {
        "current_agent": "file",
        "next_agent": "validator",
        "file_results": file_results,
        "intermediate_reasoning": reasoning
    }

    if extracted_responses:
        result["formatted_response"] = "\n\n".join(extracted_responses)

    return result
