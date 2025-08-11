from flask import Blueprint, jsonify, request
from app.chat.services import ChatService
import asyncio

chat = Blueprint("chat", __name__)
chat_service = ChatService()
chat_service.init_chat_services()


@chat.route("/message", methods=["POST"])
def send_message():
    """Send a message to the AI agent and get a streaming response."""
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get response from agent
        response_data = asyncio.run(chat_service.process_message(message))

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500


@chat.route("/health", methods=["GET"])
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200