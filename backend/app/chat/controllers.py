from flask import Blueprint, jsonify, request, stream_with_context, Response
from app.chat.services import ChatService

chat = Blueprint("chat", __name__)
chat_service = ChatService()
chat_service.init_chat_services()


def generate_response(message):
    try:
        for chunk in chat_service.process_message(message):
            print(f"Yielding chunk: {chunk}")  # DEBUG
            yield f"data: {chunk}\n\n"
    except Exception as e:
        print(f"Exception in generate_response: {e}")
        yield f"data: [Error] {str(e)}\n\n"


@chat.route("/message", methods=["GET"])
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
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
