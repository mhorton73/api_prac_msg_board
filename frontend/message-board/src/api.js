export const authenticate = async (endpoint, username, password) => {
  const res = await fetch(`http://localhost:8000/auth/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw {
      status: res.status,
      message: data.detail || "Auth failed",
    };
  }

  return data;
};

export const fetchMessages = async (page = 1, limit = 10) => {
  const queryParams = new URLSearchParams({ page, limit });
  const res = await fetch(`http://localhost:8000/forum/messages?${queryParams.toString()}`);
  if (!res.ok) {
    throw new Error("Failed to fetch messages");
  }
  const data = await res.json();
  return data;
};

export const fetchParentMessage = async (id) => {
  const res = await fetch(`http://localhost:8000/forum/messages/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch parent message");
  }
  const data = await res.json();
  return data;
};

export const postMessage = async (text, token, parentId = null) => {
  const body = { text, tags: [] };

  if (parentId !== null) {
    body.parent_id = parentId;
  }
  
  const res = await fetch("http://localhost:8000/forum/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(body)
  });

  if (!res.ok) throw new Error("Failed to post message");
};

export const editMessage = async (id, text, token) => {
  const res = await fetch(`http://localhost:8000/forum/messages/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ text, tags: [] })
  });

  if (!res.ok) throw new Error("Failed to edit message");
};

export const deleteMessage = async (id, token) => {
  const res = await fetch(`http://localhost:8000/forum/messages/${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${token}`
    },
  });

  if (!res.ok) throw new Error("Failed to delete message");
};

export const logout = async (refreshToken) => {
  const res = await fetch("http://localhost:8000/auth/logout", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${refreshToken}`
    }
  });

  if (!res.ok) throw new Error("Logout failed");
};