import { useState } from "react";
import type { ToolBlockProps } from "../../types/Chat";
const ToolBlock = ({
  type,
  toolName,
  toolInput,
  toolResult,
}: ToolBlockProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getToolIcon = () => {
    return "🔧";
  };

  return (
    <div className="border-t border-gray-100 bg-blue-50">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-blue-700 bg-blue-200 px-2 py-1 rounded">
              {getToolIcon()} {type === "tool_use" ? "TOOL USE" : "TOOL RESULT"}
              : {toolName.toUpperCase()}
            </span>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            {isExpanded ? "Hide details" : "Show details"}
          </button>
        </div>

        {type === "tool_use" && (
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Calling {toolName}</p>

            {isExpanded && toolInput && (
              <div className="bg-white rounded border p-2 text-blue-900 font-mono text-xs">
                {JSON.stringify(toolInput, null, 2)}
              </div>
            )}
          </div>
        )}

        {type === "tool_result" && (
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Tool {toolName} returned:</p>
            {isExpanded && toolInput && (
              <div className="mb-2">
                <p className="text-xs text-blue-600 mb-1">Input:</p>
                <div className="bg-white rounded border p-2 text-blue-700 font-mono text-xs">
                  {JSON.stringify(toolInput, null, 2)}
                </div>
                <div className="bg-white rounded border p-2 text-green-800 font-mono text-xs">
                  {JSON.stringify(toolResult, null, 2)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ToolBlock;
