import { useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: input }),
    });

    const data = await res.json();
    const botMsg = { sender: "bot", text: data.answer };
    setMessages((prev) => [...prev, botMsg]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[80vh] w-[50vh] border rounded-lg bg-white p-4">
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-2 rounded-lg ${
              msg.sender === "user"
                ? "bg-blue-100 self-end text-right"
                : "bg-gray-100 self-start text-left"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-lg p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
}