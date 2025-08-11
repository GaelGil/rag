from flask import Blueprint, jsonify, request, stream_with_context, Response
from app.chat.services import ChatService
import asyncio

chat = Blueprint("chat", __name__)
chat_service = ChatService()
chat_service.init_chat_services()


def generate_response(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async_gen = chat_service.process_message(message)

    try:
        while True:
            chunk = loop.run_until_complete(async_gen.__anext__())
            yield f"data: {chunk}\n\n"  # SSE format
    except StopAsyncIteration:
        pass
    finally:
        loop.close()


@chat.route("/message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Message required"}), 400

    return Response(
        stream_with_context(generate_response(message)),
        content_type="text/event-stream",
    )


@chat.route("/health", methods=["GET"])
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
