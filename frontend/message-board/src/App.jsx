import { useState, useEffect } from "react";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [editId, setEditId] = useState(null);
  const [editText, setEditText] = useState("");

  const fetchMessages = async () => {
    const res = await fetch("http://localhost:8000/forum/messages");
    const data = await res.json();
    setMessages(data.messages);
  };

  const login = async () => {
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        username,
        password,
      })
    });
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setToken(data.access_token);
    setPassword("");
  };

  const register = async () => {
    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        username,
        password,
      })
    });
    
    if (!res.ok) {
      const error = await res.json();
      alert(error.detail || "Registration failed");
      return;
    }

    await login()
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    const res = await fetch("http://localhost:8000/auth/logout", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${refreshToken}`
      }
    });
    
    if (!res.ok) {
      console.error("Logout failed");
      return;
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
  };

  const postMessage = async () => {
    await fetch("http://localhost:8000/forum/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ text, tags: [] })
    });
    fetchMessages();
  };

  const deleteMessage = async (id) => {
    await fetch(`http://localhost:8000/forum/messages/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      },
    });
    fetchMessages();
  }

  const editMessage = async (id) => {
    await fetch(`http://localhost:8000/forum/messages/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ text: editText, tags: [] })
    });

    setEditId(null);
    setEditText("");
    fetchMessages();
  }

  useEffect(() => {
    fetchMessages();
  }, []);

  return (
    <div>
      {token ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={login}>Login</button>
          <button onClick={register}>Register</button>
        </div>
      )}

      <h2>Messages</h2>
      {messages.map(m => (
        <div key={m.id}>
          <b>{m.author}</b>: 
          {editId === m.id ? (
            <>
              <input
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
              />

              <button onClick={() => editMessage(m.id)}>
                Confirm
              </button>

              <button onClick={() => setEditId(null)}>
                Cancel
              </button>
            </>
          ) : (
            <>
              {m.text}

              <button onClick={() => {
                setEditId(m.id);
                setEditText(m.text);
              }}>
                Edit
              </button>
              <button onClick={() => deleteMessage(m.id)}>
                Delete
              </button>
            </>
          )}

          
        </div>
      ))}

      <input value={text} onChange={e => setText(e.target.value)} />
      <button onClick={() => {
        postMessage()
        setText("")
      }}>
        Post
      </button>
    </div>
  );
}

export default App;