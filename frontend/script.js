const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const clearChat = document.querySelector("#clear-chat");
const legacyInput = document.querySelector("#input");
const legacyResponse = document.querySelector("#response");

const apiUrl = 'http://127.0.0.1:8000/api/chat';

async function askFaqFlow(query) {
  const response = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

if (form && input && messages) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = input.value.trim();
    if (!query) return;

    addMessage("You", query);
    input.value = "";
    input.disabled = true;
    const thinking = addMessage("FAQFlow", "Thinking...");

    try {
      const data = await askFaqFlow(query);
      updateMessage(thinking, data.answer);
    } catch (error) {
      updateMessage(thinking, "Could not reach the backend.\n\nStart it with:\npython app/main.py");
    } finally {
      input.disabled = false;
      input.focus();
    }
  });
}

if (clearChat && messages) {
  clearChat.addEventListener("click", resetChat);
}

async function send() {
  const query = legacyInput?.value.trim();
  if (!query) return;

  try {
    const data = await askFaqFlow(query);
    if (legacyResponse) legacyResponse.innerText = data.answer;
  } catch (error) {
    if (legacyResponse) {
      legacyResponse.innerText = "Could not reach the backend. Start it with: python app/main.py";
    }
  }
}

function addMessage(author, text) {
  const item = document.createElement("article");
  const isUser = author === "You";
  item.className = `message ${isUser ? "user" : "bot"}`;
  item.innerHTML = `
    <div class="avatar">${isUser ? "Y" : "F"}</div>
    <div class="bubble">
      <span class="author">${author}</span>
      <div class="content"></div>
    </div>
  `;
  item.querySelector(".content").append(...formatMessage(text));
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function resetChat() {
  messages.replaceChildren();
  addMessage("FAQFlow", "Ask a customer support question to get a grounded answer.");
  input?.focus();
}

function updateMessage(message, text) {
  const content = message.querySelector(".content");
  content.replaceChildren(...formatMessage(text));
  messages.scrollTop = messages.scrollHeight;
}

function formatMessage(text) {
  const trimmed = String(text || "").trim();
  const lines = trimmed.split(/\n+/).map((line) => line.trim()).filter(Boolean);

  if (lines.some((line) => /^[-*]\s+/.test(line))) {
    const list = document.createElement("ul");
    lines.forEach((line) => {
      const item = document.createElement("li");
      item.textContent = line.replace(/^[-*]\s+/, "");
      list.appendChild(item);
    });
    return [list];
  }

  return lines.map((line) => {
    const paragraph = document.createElement("p");
    paragraph.textContent = line;
    return paragraph;
  });
}
