// static/js/scripts.js

document.addEventListener("DOMContentLoaded", () => {
  const socket = io();

  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const messagesDiv = document.getElementById("messages");

  // Generate a unique user ID for the session
  const userId = generateUUID();

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message === "") return;

    // Display user message
    appendMessage("You", message);
    socket.emit("user_message", { message: message, user_id: userId });
    userInput.value = "";
  });

  socket.on("ai_response", (data) => {
    const aiMessage = data.message;
    appendMessage("AI Assistant", aiMessage);
  });

  function appendMessage(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");

    const senderElement = document.createElement("strong");
    senderElement.textContent = `${sender}: `;

    const textElement = document.createElement("span");
    textElement.textContent = message;

    messageElement.appendChild(senderElement);
    messageElement.appendChild(textElement);
    messagesDiv.appendChild(messageElement);

    // Scroll to the bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function generateUUID() {
    // Simple UUID generator
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
      /[xy]/g,
      function (c) {
        var r = (Math.random() * 16) | 0,
          v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }
    );
  }
});
