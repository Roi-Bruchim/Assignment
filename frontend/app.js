const chatBox = document.getElementById("chat");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function addMessage(text, sender = "bot") {
  const div = document.createElement("div");
  div.classList.add("message", sender);
  div.innerText = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  
  addMessage(text, "user");
  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: text }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error("Server error:", response.status, errText);
      addMessage(`Server error (${response.status})`, "bot");
      return;
    }

    const data = await response.json();

    if (!data.results || data.results.length === 0) {
      addMessage("No quotes found for this query.", "bot");
      return;
    }

    addMessage("Here’s what I found:", "bot");

    data.results.forEach((item) => {
      const quoteDiv = document.createElement("div");
      quoteDiv.classList.add("quote-box");
      quoteDiv.innerText = `${item.quote}\n— ${item.metadata.author || "Unknown"}`;
      chatBox.appendChild(quoteDiv);
    });

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (err) {
    console.error(err);
    addMessage("Error contacting server. Check console.", "bot");
  }
}
