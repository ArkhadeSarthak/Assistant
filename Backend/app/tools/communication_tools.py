from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class DraftMessageInput(BaseModel):
    recipient: str = Field(description="Recipient contact name or email address")
    message: str = Field(description="Message or email text content")
    platform: str = Field(default="email", description="Platform: 'email', 'whatsapp', 'slack', 'telegram'")

@tool("draft_message", args_schema=DraftMessageInput)
def draft_message_tool(recipient: str, message: str, platform: str = "email") -> str:
    """Drafts a message or email and returns a preview requiring explicit user confirmation before sending."""
    app_logger.info(f"Drafting {platform} message for {recipient}")

    return f"""### 📝 Draft Message Created ({platform.upper()})

- **To**: `{recipient}`
- **Platform**: `{platform}`
- **Message Content**:
> "{message}"

⚠️ **Confirmation Required**: Sending messages to external contacts requires user confirmation. Reply **'confirm'** to send or **'cancel'** to discard.
"""
