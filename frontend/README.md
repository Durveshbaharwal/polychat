# PolyChat Frontend Widget

This is the React frontend for PolyChat. It provides the landing page and the chat widget.

---

## 🏗️ Directory Tour
```
frontend/
├── src/
│   ├── assets/          # Global styles and static assets
│   ├── components/      # UI components (ChatInput, MessageList, SuggestedQuestions, etc.)
│   │   └── landing/     # Landing page components (Quick Start & Demo Guide)
│   ├── services/        # Axios API clients for backend communication
│   ├── store/           # Zustand state store (chat session, history, loading states)
│   ├── types/           # TypeScript interface models
│   ├── App.tsx          # Main React layout
│   ├── index.css        # Tailwind configurations and custom root utility classes
│   └── main.tsx         # React DOM anchor
├── Dockerfile           # Multi-stage production build (Node compilation -> Nginx serving)
├── nginx.conf           # Reverse proxy configuration routing /api to the backend
└── vite.config.ts       # Vite bundler options
```

---

## 🎨 Key Features

### 1. Custom Language Dropdown (`components/LanguageSelector.tsx`)
Rather than generic buttons, this dropdown lists language codes using both their English and native scripts (e.g., **Punjabi (ਪੰਜਾਬੀ)**, **Hindi (हिंदी)**). It contains full outside-click listening and dropdown toggle states.

### 2. Markdown Bold Formatter (`components/Message.tsx`)
Includes a custom React-based markdown bold parser that parses double asterisks (`**text**`) inside chat responses and renders them with stylized `<strong>` tags, avoiding raw markdown text from appearing in the user's chat bubble.

### 3. Zustand Global State (`store/chatStore.ts`)
The chat store manages active session states, message history, feedback indicators, theme settings (light/dark mode toggle), and language-aware greetings/question suggestions. It persists settings (such as chosen language and theme) inside `localStorage`.
