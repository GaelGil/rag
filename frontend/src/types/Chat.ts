export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export interface ChatBlock {
  type: "init_response" | "final_response" | "tool_use" | "tool_result";
  content?: string;
  tool_name?: string;
  tool_input?: any;
  tool_result?: any;
}

export interface ChatResponse {
  blocks: ChatBlock[];
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

export interface ToolBlockProps {
  type: "tool_use" | "tool_result";
  toolName: string;
  toolInput?: any;
  toolResult?: any;
}
