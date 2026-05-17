import { useState, useEffect } from "react";
import { fetchMessages, fetchParentMessage as parentMessageApi, postMessage, editMessage, deleteMessage } from "./api";

const MessageButtons = ({ 
  token, 
  setEditId, 
  setReplyId, 
  setEditText,
  message, 
  currentUser,
  onDelete
}) => {
  
  return(
    <>
    {token && (
      <>
          <button onClick={() => {
            setReplyId(message.id);
            setEditId(null);
          }}>Reply</button>
          {currentUser === message.author && (
            <>
              <button onClick={() => {
                setEditId(message.id);
                setReplyId(null); 
                setEditText(message.text); 
              }}>Edit</button>
              <button onClick={() => onDelete(message.id)}>Delete</button>
           </>
      )}
      </>
  )}</>)
}

const Messages = ({ token, currentUser }) => {
  const [messages, setMessages] = useState([]);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState("");
  const [replyId, setReplyId] = useState(null);
  const [replyText, setReplyText] = useState("");
  const [editId, setEditId] = useState(null);
  const [editText, setEditText] = useState("");
  const [messageCache, setMessageCache] = useState({});

  const loadMessages = async () => {
    setLoading(true);
    try {
      const data = await fetchMessages(page, limit);
      setMessages(data.messages);
      setTotalPages(Math.ceil(data.total / data.limit));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchParentMessage = async (id) => {
    if (messageCache[id]) return messageCache[id];

    const data = await parentMessageApi(id);

    setMessageCache(prev => ({
      ...prev,
      [id]: data
    }));

    return data;
  };

  useEffect(() => {
    loadMessages();
  }, [page]);

  useEffect(() => {
    const loadParents = async () => {
        const missingParents = messages
            .filter(m => m.parent_id && !messageCache[m.parent_id])
            .map(m => m.parent_id);

        await Promise.all(missingParents.map(fetchParentMessage));
    }; 

    loadParents();
  }, [messages]);

  useEffect(() => {
    if (!token) {
      setEditId(null);
      setReplyId(null);
      setEditText("");
      setReplyText("");
    }
  }, [token]);


  const handlePost = async () => {
    if (!text) return;
    await postMessage(text, token);
    setText("");
    loadMessages();
  };

  const handleReply = async() => {
    if (!replyText) return;
    await postMessage(replyText, token, replyId);
    setReplyText("");
    loadMessages();
  }

  const handleDelete = async (id) => {
    await deleteMessage(id, token);
    loadMessages();
  };

  const handleEdit = async (id) => {
    await editMessage(id, editText, token);
    setEditId(null);
    setEditText("");
    loadMessages();
  };

  return (
    <div>
      <h2>Messages</h2>

      <div>
        <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>
            Previous
        </button>
        <span> Page {page} of {totalPages} </span>
        <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>
            Next
        </button>
      </div>

      {loading && <p>Loading...</p>}

      {messages.map(m => {
        const parent = messageCache[m.parent_id];
        return(
        <div key={m.id}>
          {parent && (
            <div style={{ fontSize: "12px", color: "gray" }}>
              {parent.author}: {parent.is_deleted ? (
                <span style={{ color: "gray", fontStyle: "italic" }}>
                  [deleted]
                </span>
                
              ) : (
                parent.text.slice(0, 100)
              )}
            </div>
          )}
          <b>{m.author}</b>: 
          {editId === m.id ? (
            // If editing, show confirm and cancel buttons
            <>
              <input value={editText} onChange={e => setEditText(e.target.value)} />
              <br/>
              <button onClick={() => handleEdit(m.id)}>Confirm</button>
              <button onClick={() => setEditId(null)}>Cancel</button>
            </>
          ) : replyId === m.id ? (
            // If replying, show confirm and cancel buttons
            <>
                {m.text}
                <br/>
                <input value={replyText} onChange={e => setReplyText(e.target.value)} />
                <button onClick={() => {
                  handleReply();
                  setReplyId(null);
                }}>Confirm</button>
                <button onClick={() => {
                    setReplyId(null);
                    setReplyText("");
                }}>Cancel</button>
            </>
          ) : (
            // If not editing or replying, show reply button if logged in,
            // and show edit and delete buttons if the message comes from your account.
            <>
              {m.is_deleted ? (
                  <span style={{ color: "gray", fontStyle: "italic" }}>
                    [deleted]
                  </span>
                ) : (
                <>
                  {m.text}
                  <br/>
                  <MessageButtons
                    token={token}
                    setEditId={setEditId}
                    setReplyId={setReplyId}
                    setEditText={setEditText}
                    message={m}
                    currentUser={currentUser}
                    onDelete={handleDelete}
                  />
                </>
            )}
            </>
          )}
        </div>
        );
      })}
      { token &&
        <div>
          <input value={text} onChange={e => setText(e.target.value)} placeholder="Write a message..." />
          <button onClick={handlePost}>Post</button>
        </div>
      }
    </div>
  );
};

export default Messages;