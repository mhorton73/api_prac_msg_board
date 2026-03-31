
let currentPage = 1;
const limit = 10;

console.log("Running");

async function loadMessages() {
  console.log("loading messages");
  try {
    const res = await fetch(`http://127.0.0.1:8000/messages?page=${currentPage}&limit=${limit}`);
    if (!res.ok) throw new Error("Request failed");

    const data = await res.json();
    
    // Clear the list so we don't get duplicates when we repopulate
    const list = document.getElementById("messages");
    list.innerHTML = "";

    // Add the new message.
    data.messages.forEach(m => list.appendChild(createMessageCard(m)));

    updatePageCount(data.total);

  } catch (err) {
    console.error("Failed to load messages", err);
    alert("Error loading messages");
  }
}

async function postMessage() {
  
  const authorInput = document.getElementById("author");
  const textInput = document.getElementById("text");  
  
  const author = authorInput.value;
  const text = textInput.value;

  // Check if the user input is correct
  if (!author || !text) {
    alert("Please enter both author and message");
    return;
  }

  console.log("posting message");

  // Wrapped in try/ catch incase an error occurs
  try {
    // Use POST endpoint
    await fetch("http://127.0.0.1:8000/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
            body: JSON.stringify({
            author,
            text,
            tags: []
        })
    });

    // Clears input fields
    // authorInput.value = "";
    textInput.value = "";

    // Reloads the message board
    currentPage = 1;
    await loadMessages(); 
  } catch (err) {
    console.error("Failed to post message:", err);
    alert("Error posting message. Check console for details.");
  }
}

loadMessages();

// -------- Helper functions --------

function createMessageCard (m) {
    const li = document.createElement("li");
    li.classList.add("message");

    const author = createDiv("author", m.author);
    const text = createDiv("text", m.text);
    const time = createDiv("timestamp", new Date(m.timestamp).toLocaleString())
    li.append(author, text, time);

    const editBtn = createButton("edit-button", "Edit");
    editBtn.onclick = () => edit(m, li, editBtn);
    
    const delBtn = createButton("delete-button", "Delete");
    delBtn.onclick = () => deleteMessage(m.id);

    li.append(editBtn, delBtn);
    return li;
}

function createDiv (className, text = "") {
    const div = document.createElement("div");
    div.classList.add(className);
    div.textContent = text;
    return div;
}

function createButton (className, text = "") {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add(className)
    button.textContent = text;
    return button;
}

function edit (m, li, editBtn) {
    const currentText = li.querySelector(".text");
    
    const input = document.createElement("textarea");
    input.value = currentText.textContent;
    input.style.width = "600px";
    input.style.height = "100px";

    li.replaceChild(input, currentText);
    editBtn.textContent = "Save";
    editBtn.onclick = () => editSave(m, li, editBtn, currentText, input);
}

async function editSave(m, li, editBtn, currentText, input) {
    const newText = input.value; 
    try {
        await fetch(`http://127.0.0.1:8000/messages/${m.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: newText,
                author: m.author,
                tags: m.tags
            })
        });
        currentText.textContent = newText;
        li.replaceChild(currentText, input);
        editBtn.textContent = "Edit";
        editBtn.onclick = () => edit(m, li, editBtn);
    } catch (err) {
        console.error("Failed to edit:", err);
        alert("Error editing message");
    }
}

async function deleteMessage (id) {
    const confirmed = confirm("Are you sure you want to delete this message?");
    if (!confirmed) return;
    console.log("deleting message");
    try {
        await fetch(`http://127.0.0.1:8000/messages/${id}`, {
            method: "DELETE"
        });
        loadMessages(); // refresh the list
    } catch (err) {
        console.error("Failed to delete:", err);
        alert("Error deleting message");
    }
}

function updatePageCount(total) {
  const totalPages = Math.ceil(total / limit);

  document.getElementById("pageInfo").textContent =
    `Page ${currentPage} of ${totalPages}`;

  // Disable buttons when needed
  document.querySelector("button[onclick='prevPage()']").disabled = currentPage === 1;
  document.querySelector("button[onclick='nextPage()']").disabled = currentPage === totalPages;
}

function nextPage() {
  currentPage++;
  loadMessages();
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    loadMessages();
  }
}