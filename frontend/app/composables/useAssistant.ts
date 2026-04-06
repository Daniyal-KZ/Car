 export type MessageRole = "user" | "assistant";

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
};

export type Chat = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
};

const createId = () => crypto.randomUUID();

const nowIso = () => new Date().toISOString();

const makeChatTitle = (text: string) => {
  const normalized = text.trim();
  if (!normalized) return "New chat";
  return normalized.length > 30 ? normalized.slice(0, 30) + "..." : normalized;
};

export const useAssistant = () => {
  const chats = useState<Chat[]>("assistant-chats", () => []);

  const sortedChats = computed(() => {
    return [...chats.value].sort((a, b) => {
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  });

  const createChat = () => {
    const id = createId();
    const timestamp = nowIso();

    const chat: Chat = {
      id,
      title: "New chat",
      createdAt: timestamp,
      updatedAt: timestamp,
      messages: [],
    };

    chats.value.unshift(chat);
    return chat;
  };

  const getChatById = (id: string) => {
    return chats.value.find((chat) => chat.id === id);
  };

  const addMessage = (chatId: string, role: MessageRole, content: string) => {
    const chat = getChatById(chatId);
    if (!chat) return;

    const message: Message = {
      id: createId(),
      role,
      content,
      createdAt: nowIso(),
    };

    chat.messages.push(message);
    chat.updatedAt = nowIso();

    if (chat.messages.length === 1 && role === "user") {
      chat.title = makeChatTitle(content);
    }

    return message;
  };

  const sendMessage = async (chatId: string, content: string) => {
    const text = content.trim();
    if (!text) return;

    const chat = getChatById(chatId);
    if (!chat) return;

    addMessage(chatId, "user", text);

    await new Promise((resolve) => setTimeout(resolve, 500));

    addMessage(
      chatId,
      "assistant",
      `Это заглушка ответа на сообщение: "${text}"`
    );
  };

  const ensureChat = (id?: string) => {
    if (!id) return createChat();
    const existing = getChatById(id);
    return existing ?? createChat();
  };

  return {
    chats,
    sortedChats,
    createChat,
    getChatById,
    addMessage,
    sendMessage,
    ensureChat,
  };
};
