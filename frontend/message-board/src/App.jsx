import { useState} from "react";
import Messages from "./Messages";
import { authenticate, logout } from "./api";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [currentUser, setCurrentUser] = useState(localStorage.getItem("username"));

  const login = async () => {

    try {
      const data = await authenticate("login", username, password);

      localStorage.setItem("username", data.username);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      setCurrentUser(data.username);
      setToken(data.access_token);
      setPassword("");
    } catch (err) {
      console.error("Login failed:", err);
      alert(err.message);
    }
  };

  const register = async () => {
    try {
      await authenticate("register", username, password);
      await login();
    } catch (err) {
      console.error("Register failed:", err);
      alert(err.message);
    }
  };

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    await logout(refreshToken);
    localStorage.removeItem("username");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setCurrentUser(null);
    setToken(null);
  };

  return (
    <div>
      {token ? (
        <button onClick={handleLogout}>Logout</button>
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

      <Messages token={token} currentUser={currentUser} />
    </div>
  );
}

export default App;