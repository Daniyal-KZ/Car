export type MessageRole = "user" | "assistant";

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  intent?: string | null;
  actionJson?: string | null;
};

export type AssistantAction = {
  type: string;
  route?: string;
  label?: string;
};

export type Chat = {
  id: string;
  title: string;
  provider: string;
  createdAt: string;
  updatedAt: string;
  messagesCount: number;
  messages: Message[];
};

export const useAssistant = () => {
  const config = useRuntimeConfig();
  const auth = useAuthStore();
  const { t, locale } = useI18n();
  const chats = useState<Chat[]>("assistant-chats", () => []);
  const activeChat = useState<Chat | null>("assistant-active-chat", () => null);

  const api = () => `${config.public.apiBase}/assistant`;

  const authHeaders = computed(() => ({
    Authorization: auth.token ? `Bearer ${auth.token}` : "",
    "X-Lang": locale.value,
  }));

  const normalizeMessage = (message: any): Message => ({
    id: String(message.id),
    role: message.role,
    content: message.content,
    createdAt: message.created_at || message.createdAt,
    intent: message.intent ?? null,
    actionJson: message.action_json ?? message.actionJson ?? null,
  });

  const parseAction = (actionJson?: string | null): AssistantAction | null => {
    if (!actionJson) return null;
    try {
      const parsed = JSON.parse(actionJson);
      return parsed && typeof parsed === "object" ? parsed : null;
    } catch {
      return null;
    }
  };

  const normalizeChat = (chat: any): Chat => ({
    id: String(chat.id),
    title: chat.title || t("new_chat"),
    provider: chat.provider || "gemini",
    createdAt: chat.created_at || chat.createdAt,
    updatedAt: chat.updated_at || chat.updatedAt,
    messagesCount: chat.messages_count ?? chat.messagesCount ?? (chat.messages?.length || 0),
    messages: Array.isArray(chat.messages) ? chat.messages.map(normalizeMessage) : [],
  });

  const sortedChats = computed(() => {
    return [...chats.value].sort((a, b) => {
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  });

  const upsertChat = (chat: any) => {
    const normalized = normalizeChat(chat);
    const index = chats.value.findIndex((item) => item.id === normalized.id);
    if (index === -1) {
      chats.value.unshift(normalized);
    } else {
      chats.value[index] = normalized;
    }
    if (activeChat.value?.id === normalized.id) {
      activeChat.value = normalized;
    }
    return normalized;
  };

  const appendLocalMessage = (chatId: string, role: MessageRole, content: string) => {
    const chat = chats.value.find((item) => item.id === chatId) || activeChat.value;
    if (!chat || chat.id !== chatId) return;

    const message: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      createdAt: new Date().toISOString(),
    };

    chat.messages = [...chat.messages, message];
    chat.messagesCount = chat.messages.length;
    chat.updatedAt = message.createdAt;

    if (chat.messages.length === 1 && role === "user") {
      chat.title = content.trim().slice(0, 40) || t("new_chat");
    }
  };

  const fetchChats = async () => {
    const result = await $fetch<any[]>(`${api()}/chats`, {
      headers: authHeaders.value,
    });
    const previousById = new Map(chats.value.map((chat) => [chat.id, chat]));

    chats.value = result.map((rawChat) => {
      const normalized = normalizeChat(rawChat);
      const previous = previousById.get(normalized.id);
      const hasMessagesPayload = Array.isArray(rawChat?.messages);

      // Summary endpoint intentionally omits messages; keep already loaded message history.
      if (!hasMessagesPayload && previous?.messages?.length) {
        normalized.messages = previous.messages;
        normalized.messagesCount = normalized.messagesCount || previous.messages.length;
      }

      return normalized;
    });

    if (activeChat.value) {
      const synced = chats.value.find((chat) => chat.id === activeChat.value?.id);
      if (synced) {
        if (!synced.messages.length && activeChat.value.messages.length) {
          synced.messages = activeChat.value.messages;
          synced.messagesCount = synced.messages.length;
        }
        activeChat.value = synced;
      }
    }

    return chats.value;
  };

  const renameChat = async (id: string, title: string) => {
    const result = await $fetch<any>(`${api()}/chats/${id}`, {
      method: "PATCH",
      headers: authHeaders.value,
      body: { title },
    });
    return upsertChat(result);
  };

  const deleteChat = async (id: string) => {
    await $fetch(`${api()}/chats/${id}`, {
      method: "DELETE",
      headers: authHeaders.value,
    });
    chats.value = chats.value.filter((chat) => chat.id !== id);
    if (activeChat.value?.id === id) {
      activeChat.value = null;
    }
  };

  const createChat = async (title?: string) => {
    const result = await $fetch<any>(`${api()}/chats`, {
      method: "POST",
      headers: authHeaders.value,
      body: title ? { title } : {},
    });
    const chat = normalizeChat(result);
    upsertChat(chat);
    activeChat.value = chat;
    return chat;
  };

  const loadChat = async (id: string) => {
    const result = await $fetch<any>(`${api()}/chats/${id}`, {
      headers: authHeaders.value,
    });
    return upsertChat(result);
  };

  const getChatById = (id: string) => {
    return chats.value.find((chat) => chat.id === id) ?? (activeChat.value?.id === id ? activeChat.value : undefined);
  };

  const ensureChat = async (id?: string) => {
    if (!id) {
      return createChat();
    }
    const existing = getChatById(id);
    if (existing?.messages) {
      return existing;
    }
    try {
      return await loadChat(id);
    } catch {
      return createChat();
    }
  };

  const sendMessage = async (chatId: string, content: string) => {
    const text = content.trim();
    if (!text) return;

    appendLocalMessage(chatId, "user", text);

    try {
      const response = await $fetch<any>(`${api()}/chats/${chatId}/messages`, {
        method: "POST",
        headers: authHeaders.value,
        body: { message: text },
      });

      const normalized = upsertChat(response.chat);
      activeChat.value = normalized;
      return {
        chat: normalized,
        answer: response.answer,
        intent: response.intent,
        actionJson: response.action_json,
        action: parseAction(response.action_json),
        provider: response.provider,
        model: response.model,
      };
    } catch (error: any) {
      const status = error?.status || error?.response?.status;
      const detail = error?.data?.detail || error?.response?._data?.detail;
      let fallback = t("assistant_error_default");

      if (status === 400) {
        fallback = t("assistant_error_api_key_missing");
      } else if (status === 401) {
        fallback = t("assistant_error_session_expired");
      } else if (typeof detail === "string" && detail.length > 0) {
        fallback = detail;
      }

      appendLocalMessage(chatId, "assistant", fallback);
      return {
        chat: getChatById(chatId) || activeChat.value,
        answer: fallback,
        intent: null,
        actionJson: null,
        action: null,
        provider: "gemini",
        model: "gemini",
      };
    }
  };

  return {
    chats,
    sortedChats,
    activeChat,
    fetchChats,
    createChat,
    renameChat,
    deleteChat,
    loadChat,
    getChatById,
    sendMessage,
    ensureChat,
    parseAction,
  };
};
