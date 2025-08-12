import { useState } from "react";
import type { ThinkingBlockProps } from "../../types/Chat";

const ThinkingBlock = ({
  content,
  isRedacted = false,
  iteration,
}: ThinkingBlockProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  console.log("ThinkingBlock Iteration", iteration);

  return (
    <div className="border-t border-gray-100 bg-gray-50">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-light text-gray-500">
              🧠{" "}
              {isRedacted ? "Redacted thinking" : "Thought for a few seconds"}
            </span>
            {/* {iteration && (
              <span className="text-xs text-gray-400">Iteration {iteration}</span>
            )} */}
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-gray-300 hover:text-gray-400 transition-all"
          >
            {isExpanded ? "▼" : "◀"}
          </button>
        </div>
        {isExpanded && (
          <div className="text-xs font-mono rounded mt-2 text-gray-500">
            {isRedacted ? (
              <span className="italic text-gray-500">
                [Thinking content has been redacted]
              </span>
            ) : (
              <pre className="whitespace-pre-wrap">{content}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ThinkingBlock;
