import { useState } from "react";
import type { ChatInputProps } from "../../types/Chat";

const ChatInput = ({ onSendMessage, disabled = false }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex space-x-3">
      <div className="flex-1 relative">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything... (Press Enter to send, Shift+Enter for new line)"
          disabled={disabled}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          rows={Math.min(Math.max(1, message.split("\n").length), 5)}
          style={{ minHeight: "50px" }}
        />
      </div>
      <button
        onClick={handleSend}
        disabled={!message.trim() || disabled}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
      >
        {disabled ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          </div>
        ) : (
          "Send"
        )}
      </button>
    </div>
  );
};

export default ChatInput;
