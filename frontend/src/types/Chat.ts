export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

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

export interface ChatMessageProps {
  message: Message;
}

export interface ThinkingBlockProps {
  content: string;
  isRedacted?: boolean;
  iteration?: number;
}

export interface ToolBlockProps {
  type: "use" | "result";
  toolName: string;
  toolInput?: any;
  toolResult?: any;
  iteration?: number;
}
