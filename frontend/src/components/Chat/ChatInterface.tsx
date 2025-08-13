import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { BASE_URL } from "../../api/url";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { Message } from "../../types/Chat";

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
    let firstChunkReceived = false;

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
            accumulatedMessage += ev.data;

            // Update assistant message content and on first chunk remove its isLoading flag
            setMessages((prev) => {
              if (prev.length === 0) return prev;
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;

              // make sure last message is the assistant placeholder
              if (lastIndex < 0) return prev;

              const last = { ...newMessages[lastIndex] };
              last.content = accumulatedMessage;
              last.timestamp = new Date(); // force re-render
              // on first chunk, stop showing the "Thinking..." spinner and display content
              if (!firstChunkReceived) {
                last.isLoading = false;
                firstChunkReceived = true;
              }

              newMessages[lastIndex] = last;
              return newMessages;
            });
          },
          onerror(err) {
            console.error("SSE error:", err);
            // mark last message as not loading and append error text
            setMessages((prev) => {
              if (prev.length === 0) return prev;
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;
              const last = { ...newMessages[lastIndex] };
              last.isLoading = false;
              last.content =
                (last.content || "") + `\n\n[Error receiving stream]`;
              last.timestamp = new Date();
              newMessages[lastIndex] = last;
              return newMessages;
            });
            setIsLoading(false);
            // rethrow to let fetchEventSource handle closure
            throw err;
          },
          onclose() {
            // streaming finished: ensure assistant message is marked not loading and final content is saved
            setMessages((prev) => {
              if (prev.length === 0) return prev;
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;
              const last = { ...newMessages[lastIndex] };
              last.isLoading = false;
              last.content = accumulatedMessage;
              last.timestamp = new Date();
              newMessages[lastIndex] = last;
              return newMessages;
            });
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
