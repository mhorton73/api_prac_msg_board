import { useState, useEffect } from "react";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  const fetchMessages = async () => {
    const res = await fetch("http://localhost:8000/forum/messages");
    const data = await res.json();
    setMessages(data.messages);
  };

  const login = async () => {
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username: "Gandalf", password: "123" })
    });
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setToken(data.access_token);
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

  useEffect(() => {
    fetchMessages();
  }, []);

  return (
    <div>
      {token ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={login}>Login</button>
      )}

      <h2>Messages</h2>
      {messages.map(m => (
        <div key={m.id}>
          <b>{m.author}</b>: {m.text}
        </div>
      ))}

      <input value={text} onChange={e => setText(e.target.value)} />
      <button onClick={postMessage}>Post</button>
    </div>
  );
}

export default App;