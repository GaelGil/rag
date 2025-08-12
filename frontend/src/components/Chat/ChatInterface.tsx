import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { BASE_URL } from "../../api/url";
import { fetchEventSource } from "@microsoft/fetch-event-source";

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    };

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    let accumulatedMessage = "";

    try {
      await fetchEventSource(
        `${BASE_URL}/api/chat/message?message=${encodeURIComponent(content)}`,
        {
          method: "GET",
          credentials: "include", // send cookies/session for auth
          onopen: async (res) => {
            if (res.ok && res.status === 200) {
              console.log("SSE connection opened");
            } else {
              const text = await res.text();
              throw new Error(`SSE failed with status ${res.status}: ${text}`);
            }
          },
          onmessage(ev) {
            console.log("SSE chunk received:", ev.data);
            // Append incoming chunk to accumulated message
            accumulatedMessage += ev.data;

            // Update the last message (assistant) content live
            setMessages((prev) => {
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;
              if (
                lastIndex >= 0 &&
                newMessages[lastIndex].role === "assistant"
              ) {
                newMessages[lastIndex] = {
                  ...newMessages[lastIndex],
                  content: accumulatedMessage,
                };
              }
              return newMessages;
            });
          },
          onerror(err) {
            console.error("SSE error:", err);
            setIsLoading(false);
            throw err;
          },
          onclose() {
            setIsLoading(false);
            console.log("SSE connection closed");
          },
        }
      );
    } catch (err) {
      console.error("Streaming failed", err);
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white">
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

      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
