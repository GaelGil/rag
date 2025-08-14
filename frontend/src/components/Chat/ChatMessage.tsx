import ThinkingBlock from "./ChatThinkingBlock";
import ToolBlock from "./ToolBlock";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { ChatMessageProps } from "../../types/Chat";

const ChatMessage = ({ message }: ChatMessageProps) => {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] bg-blue-600 text-white rounded-lg px-4 py-2">
          <div className="prose prose-sm prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code: ({ inline, className, children, ...props }: any) => {
                  const match = /language-(\w+)/.exec(className || "");
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={oneLight}
                      language={match[1]}
                      PreTag="div"
                      className="rounded-md"
                      {...props}
                    >
                      {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                  ) : (
                    <code
                      className="bg-blue-700 px-1 py-0.5 rounded text-sm"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                p: ({ children }: any) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }: any) => (
                  <ul className="mb-2 last:mb-0 list-disc list-inside">
                    {children}
                  </ul>
                ),
                ol: ({ children }: any) => (
                  <ol className="mb-2 last:mb-0 list-decimal list-inside">
                    {children}
                  </ol>
                ),
                blockquote: ({ children }: any) => (
                  <blockquote className="border-l-4 border-blue-400 pl-4 italic">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
          <p className="text-xs text-blue-100 mt-1">
            {message.timestamp.toLocaleTimeString()}
          </p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] bg-white rounded-lg border border-gray-200 overflow-hidden">
        {message.isLoading ? (
          <div className="px-4 py-3">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-gray-600">Thinking...</span>
            </div>
          </div>
        ) : message.response ? (
          <div className="space-y-0">
            {message.response.blocks.map((block, index) => {
              switch (block.type) {
                case "thinking":
                case "redacted_thinking":
                  return (
                    <ThinkingBlock
                      key={index}
                      content={block.content || ""}
                      isRedacted={block.type === "redacted_thinking"}
                      iteration={block.iteration}
                    />
                  );
                case "tool_use":
                  return (
                    <ToolBlock
                      key={index}
                      type="use"
                      toolName={block.tool_name || ""}
                      toolInput={block.tool_input}
                      iteration={block.iteration}
                    />
                  );
                case "tool_result":
                  return (
                    <ToolBlock
                      key={index}
                      type="result"
                      toolName={block.tool_name || ""}
                      toolInput={block.tool_input}
                      toolResult={block.tool_result}
                      iteration={block.iteration}
                    />
                  );
                case "text":
                  return (
                    <div
                      key={index}
                      className="px-4 py-3 border-t border-gray-100"
                    >
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code: ({
                              inline,
                              className,
                              children,
                              ...props
                            }: any) => {
                              const match = /language-(\w+)/.exec(
                                className || ""
                              );
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  style={oneLight}
                                  language={match[1]}
                                  PreTag="div"
                                  className="rounded-md my-3"
                                  {...props}
                                >
                                  {String(children).replace(/\n$/, "")}
                                </SyntaxHighlighter>
                              ) : (
                                <code
                                  className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono"
                                  {...props}
                                >
                                  {children}
                                </code>
                              );
                            },
                            p: ({ children }: any) => (
                              <p className="mb-3 last:mb-0 text-gray-900">
                                {children}
                              </p>
                            ),
                            h1: ({ children }: any) => (
                              <p className="text-[1.2rem] font-semibold mb-3 text-gray-900">
                                {children}
                              </p>
                            ),
                            h2: ({ children }: any) => (
                              <p className="text-[1.1rem] font-semibold mb-2 text-gray-900">
                                {children}
                              </p>
                            ),
                            h3: ({ children }: any) => (
                              <p className="text-[1rem] font-semibold mb-2 text-gray-900">
                                {children}
                              </p>
                            ),
                            ul: ({ children }: any) => (
                              <ul className="mb-3 last:mb-0 list-disc list-inside space-y-1">
                                {children}
                              </ul>
                            ),
                            ol: ({ children }: any) => (
                              <ol className="mb-3 last:mb-0 list-decimal list-inside space-y-1">
                                {children}
                              </ol>
                            ),
                            li: ({ children }: any) => (
                              <li className="text-gray-900">{children}</li>
                            ),
                            blockquote: ({ children }: any) => (
                              <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-700 my-3">
                                {children}
                              </blockquote>
                            ),
                            a: ({ children, href, ...props }: any) => (
                              <a
                                href={href}
                                className="text-blue-600 hover:text-blue-800 underline"
                                target="_blank"
                                rel="noopener noreferrer"
                                {...props}
                              >
                                {children}
                              </a>
                            ),
                            table: ({ children }: any) => (
                              <div className="overflow-x-auto my-3">
                                <table className="min-w-full border border-gray-300 rounded-lg">
                                  {children}
                                </table>
                              </div>
                            ),
                            thead: ({ children }: any) => (
                              <thead className="bg-gray-50">{children}</thead>
                            ),
                            th: ({ children }: any) => (
                              <th className="border border-gray-300 px-3 py-2 text-left font-semibold text-gray-900">
                                {children}
                              </th>
                            ),
                            td: ({ children }: any) => (
                              <td className="border border-gray-300 px-3 py-2 text-gray-900">
                                {children}
                              </td>
                            ),
                          }}
                        >
                          {block.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  );
                default:
                  return null;
              }
            })}
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Completed in {message.response.total_iterations} iteration
                {message.response.total_iterations !== 1 ? "s" : ""} •{" "}
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ) : (
          <div className="px-4 py-3">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: ({ inline, className, children, ...props }: any) => {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneLight}
                        language={match[1]}
                        PreTag="div"
                        className="rounded-md my-3"
                        {...props}
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    ) : (
                      <code
                        className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  p: ({ children }: any) => (
                    <p className="mb-3 last:mb-0 text-gray-900">{children}</p>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
