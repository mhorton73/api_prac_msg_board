
// import { useState } from "react";

// function App() {
//   const [messages] = useState([
//     { id: 1, author: "Alice", text: "Hello!" },
//     { id: 2, author: "Bob", text: "Hi there!" },
//   ]);

//   return (
//     <div style={{ fontFamily: "Arial", margin: 20 }}>
//       <h1>Message Board</h1>

//       <ul style={{ listStyle: "none", padding: 0 }}>
//         {messages.map((m) => (
//           <li
//             key={m.id}
//             style={{
//               background: "#f0f8ff",
//               padding: "12px",
//               margin: "10px 0",
//               borderRadius: "8px",
//               border: "1px solid #ddd",
//               maxWidth: "600px",
//             }}
//           >
//             <div style={{ fontWeight: "bold", fontSize: "20px" }}>
//               {m.author}
//             </div>

//             <div style={{ margin: "5px 0" }}>{m.text}</div>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }

function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>{count}</h1>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  );
}

export default App;


// import { useState } from "react";

// function App() {
//   const [messages, setMessages] = useState([
//     { id: 1, author: "Alice", text: "Hello!" },
//     { id: 2, author: "Bob", text: "Hi there!" },
//   ]);

//   function addMessage() {
//     const newMessage = {
//       id: Date.now(),
//       author: "You",
//       text: "New message!",
//     };

//     setMessages([...messages, newMessage]);
//   }

//   return (
//     <div style={{ fontFamily: "Arial", margin: 20 }}>
//       <h1>Message Board</h1>

//       <button onClick={addMessage}>Add Message</button>

//       <ul style={{ listStyle: "none", padding: 0 }}>
//         {messages.map((m) => (
//           <li key={m.id}>
//             <strong>{m.author}</strong>: {m.text}
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }

// export default App;
