from flask import Blueprint, jsonify, request, stream_with_context, Response
from app.chat.services import ChatService
from app.auth.decorators import login_required
import sys
import json

chat = Blueprint("chat", __name__)
chat_service = ChatService()
chat_service.init_chat_services()


def generate_response(message):
    try:
        for chunk in chat_service.process_message(message):
            if isinstance(chunk, str):
                yield f"data: {chunk}\n\n"
                sys.stdout.flush()
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"


@chat.route("/message", methods=["GET"])
@login_required
def send_message():
    message = request.args.get("message")  # ✅ read from query params for GET
    if not message:
        return jsonify({"error": "Message required"}), 400

    return Response(
        stream_with_context(generate_response(message)),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Credentials": "true",
        },
    )


@chat.route("/health", methods=["GET"])
@login_required
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
