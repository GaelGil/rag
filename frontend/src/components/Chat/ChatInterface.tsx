// ChatInterface.tsx
import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { BASE_URL } from "../../api/url";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { Message, ChatBlock } from "../../types/Chat";

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

  // --- Helpers to manage blocks using your existing ChatBlock types ---

  // Append or upsert a streaming text block (uses type init_response while streaming;
  // when isFinal=true we either convert that block to final_response or insert final_response)
  const upsertTextBlock = (text: string, isFinal = false) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      const last = { ...newMessages[lastIndex] };

      if (!last.response) {
        last.response = { blocks: [], stop_reason: "", total_iterations: 0 };
      }
      const blocks = Array.isArray(last.response.blocks)
        ? [...last.response.blocks]
        : [];

      // find last streaming/text block if exists (init_response or final_response)
      const streamingIdx = (() => {
        for (let i = blocks.length - 1; i >= 0; i--) {
          if (
            blocks[i].type === "init_response" ||
            blocks[i].type === "final_response"
          ) {
            return i;
          }
        }
        return -1;
      })();

      if (streamingIdx >= 0) {
        // update existing text block
        const existing = { ...blocks[streamingIdx] } as ChatBlock;
        existing.content = (existing.content || "") + text;
        // if final, mark as final_response
        existing.type = isFinal ? "final_response" : "init_response";
        blocks[streamingIdx] = existing;
      } else {
        // push new text block
        const block: ChatBlock = {
          type: isFinal ? "final_response" : "init_response",
          content: text,
        };
        blocks.push(block);
      }

      last.response = { ...last.response, blocks };
      // keep a quick content copy for fallback rendering
      const latestText = blocks
        .filter(
          (b) => b.type === "final_response" || b.type === "init_response"
        )
        .map((b) => b.content || "")
        .join("\n\n");
      last.content = latestText;
      last.isLoading = !isFinal;
      last.timestamp = new Date();

      newMessages[lastIndex] = last;
      return newMessages;
    });
  };

  // Append a tool block (tool_use / tool_result) and keep it persistent
  const appendToolBlock = (block: ChatBlock) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      const last = { ...newMessages[lastIndex] };

      if (!last.response) {
        last.response = { blocks: [], stop_reason: "", total_iterations: 0 };
      }

      const blocks = Array.isArray(last.response.blocks)
        ? [...last.response.blocks, block]
        : [block];

      last.response = { ...last.response, blocks };
      last.timestamp = new Date();
      newMessages[lastIndex] = last;
      return newMessages;
    });
  };

  // Finalize streaming text blocks (convert any remaining init_response to final_response)
  const finalizeTextBlocks = () => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      const last = { ...newMessages[lastIndex] };

      if (!last.response || !Array.isArray(last.response.blocks)) {
        last.isLoading = false;
        last.timestamp = new Date();
        newMessages[lastIndex] = last;
        return newMessages;
      }

      const blocks = last.response.blocks.map((b) => {
        if (b.type === "init_response") {
          return { ...b, type: "final_response" } as ChatBlock;
        }
        return b;
      });

      last.response = { ...last.response, blocks };
      // keep content synced to final text if present
      const finalText =
        blocks
          .filter((b) => b.type === "final_response")
          .map((b) => b.content || "")
          .join("\n\n") ||
        blocks
          .filter((b) => b.type === "init_response")
          .map((b) => b.content || "")
          .join("\n\n");
      last.content = finalText;
      last.isLoading = false;
      last.timestamp = new Date();

      newMessages[lastIndex] = last;
      return newMessages;
    });
  };

  // --- sendMessage with SSE ---
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
      response: { blocks: [], stop_reason: "", total_iterations: 0 },
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    // accumulated text chunks come from SSE events; we append to the latest text block
    try {
      await fetchEventSource(
        `${BASE_URL}/api/chat/message?message=${encodeURIComponent(content)}`,
        {
          method: "GET",
          credentials: "include",
          onopen: async (res) => {
            if (!(res.ok && res.status === 200)) {
              const text = await res.text();
              throw new Error(`SSE failed with status ${res.status}: ${text}`);
            }
          },
          onmessage(ev) {
            try {
              const parsed = JSON.parse(ev.data);
              if (!parsed || typeof parsed !== "object") return;

              switch (parsed.type) {
                case "init_response":
                  // first / streaming chunks (append)
                  upsertTextBlock(parsed.content ?? "", false);
                  break;
                case "final_response":
                  // final chunk: append then mark final
                  upsertTextBlock(parsed.content ?? "", true);
                  break;
                case "tool_use":
                  appendToolBlock({
                    type: "tool_use",
                    tool_name: parsed.tool_name,
                    tool_input: parsed.tool_input,
                  });
                  break;
                case "tool_result":
                  appendToolBlock({
                    type: "tool_result",
                    tool_name: parsed.tool_name,
                    tool_input: parsed.tool_input,
                    tool_result: parsed.tool_result,
                  });
                  break;
                default:
                  console.warn("Unknown SSE chunk type:", parsed.type);
              }
            } catch (err) {
              console.error("Invalid SSE chunk:", ev.data, err);
            }
          },
          onerror(err) {
            console.error("SSE error", err);
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
            throw err;
          },
          onclose() {
            // make sure any streaming text is finalized
            finalizeTextBlocks();
            setIsLoading(false);
            // small delay and scroll to bottom
            setTimeout(scrollToBottom, 10);
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
                I am your personal AI assistant
              </h2>
              <p className="text-gray-600 mb-2 max-w-md mx-auto">
                Ask Anything
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
