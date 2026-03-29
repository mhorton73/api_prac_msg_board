

async function loadMessages() {
  
  const res = await fetch("http://127.0.0.1:8000/messages");
  const data = await res.json();
  
  // Clear the list so we don't get duplicates when we repopulate
  const list = document.getElementById("messages");
  list.innerHTML = "";

  data.messages.forEach(m => {
    const li = document.createElement("li");
    
    // Author
    const author = document.createElement("div");
    author.classList.add("author");
    author.textContent = m.author;

    // Text
    const text = document.createElement("div");
    text.classList.add("text");
    text.textContent = m.text;

    // Timestamp
    const time = document.createElement("div");
    time.classList.add("timestamp");
    time.textContent = new Date(m.timestamp).toLocaleString();

    // Edit Button
    
    const edBtn = document.createElement("button");
    edBtn.textContent = "Edit";
    edBtn.classList.add("edit-button");
    edBtn.onclick = () => {
        const textDiv = li.querySelector(".text");
        
        const input = document.createElement("textarea");
        input.type = "text";
        input.value = textDiv.textContent;
        input.style.width = "90%";

        li.replaceChild(input, textDiv);
        edBtn.textContent = "Save";
        edBtn.onclick = async () => {
            const newText = input.value;

            await fetch(`http://127.0.0.1:8000/messages/${m.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: newText,
                    author: m.author,
                    tags: m.tags
                })
            });

            textDiv.textContent = newText;
            li.replaceChild(textDiv, input);
            edBtn.textContent = "Edit";
            edBtn.onclick = originalEditHandler;
        }
    }
    const originalEditHandler = edBtn.onclick;
    
    // Delete button
    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.classList.add("delete-button")
    delBtn.onclick = async () => {
        try {
            await fetch(`http://127.0.0.1:8000/messages/${m.id}`, {
                method: "DELETE"
            });
            loadMessages(); // refresh the list
        } catch (err) {
            console.error("Failed to delete:", err);
            alert("Error deleting message");
        }
    }


    li.classList.add("message");
    li.append(author, text, time, edBtn, delBtn);
    list.appendChild(li);
  });
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
    authorInput.value = "";
    textInput.value = "";

    // Reloads the message board
    await loadMessages(); 
  } catch (err) {
    console.error("Failed to post message:", err);
    alert("Error posting message. Check console for details.");
  }
}

loadMessages();