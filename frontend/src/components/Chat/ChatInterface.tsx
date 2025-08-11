import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { PROJECT_LOGO } from "../../data/ProjectLogo";
import { BASE_URL } from "../../api/url";
import { PROJECT_NAME } from "../../data/ProjectName";
import { io, Socket } from "socket.io-client";
export interface ChatBlock {
  type: "thinking" | "redacted_thinking" | "text" | "tool_use" | "tool_result";
  content?: string;
  tool_name?: string;
  tool_input?: any;
  tool_result?: any;
  tool_id?: string;
  iteration?: number;
}

export interface ChatResponse {
  blocks: ChatBlock[];
  stop_reason: string;
  total_iterations: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  timestamp: Date;
  isLoading?: boolean;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socket = useRef<Socket | null>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Only run once to connect to socket
    socket.current = io("http://localhost:8080/chat");

    socket.current.on("connect", () => {
      console.log("🔌 Connected to WebSocket server");
    });
    socket.current.on("log", (data: { message: string }) => {
      const streamedMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
        isLoading: true, // optional – you can use this to style it differently
      };

      setMessages((prev) => [...prev, streamedMessage]);
    });

    socket.current.on("disconnect", () => {
      console.log("❌ Disconnected from WebSocket server");
    });

    return () => {
      socket.current?.off("log");
      socket.current?.disconnect();
    };
  }, []);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "Thinking...",
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/api/chat/message`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: "Assistant response",
          response: data.response,
          timestamp: new Date(),
        };

        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = assistantMessage;
          return newMessages;
        });
      } else {
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            content: `Error: ${data.error}`,
            isLoading: false,
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content: `Error: Failed to send message`,
          isLoading: false,
        };
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className=" bg-white">
      {/* Chat Section */}
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-100 px-8 py-4">
        <div className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-[#ffffff] to-[#eceaff] rounded-lg flex items-center justify-center p-1">
              {PROJECT_LOGO}
            </div>
            <p className="text-xl p-0 m-0 font-semibold text-gray-900">
              {PROJECT_NAME}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-8 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                Your Personal Essay Writing Assistant
              </h2>
              <p className="text-gray-600 mb-2 max-w-md mx-auto">
                I can help you write an essay on any topic or review an existing
                essay.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}

      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
