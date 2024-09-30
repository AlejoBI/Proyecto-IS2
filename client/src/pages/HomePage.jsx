import { useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';

const HomePage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);

  const handleSend = () => {
    if (input.trim() || file) {
      setMessages([...messages, { text: input, file: file ? file.name : null, sender: "user" }]);
      setInput("");
      setFile(null);
    }
  };

  return (
    <div className="container mt-5 p-5 border rounded shadow-sm bg-light">
      <nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <a className="navbar-brand" href="#">Hi ✌️</a>
      </nav>
      <header className="mb-4">
        <h1 className="text-center">Welcome to LosAPIS's ChatBot</h1>
        <p className="text-center">Type something and I'll help you</p>
      </header>
      <div className="chat-container border rounded p-3 mb-4" style={{ height: '400px', overflowY: 'scroll' }}>
        {messages.map((msg, index) => (
          <div key={index} className={`d-flex ${msg.sender === "user" ? "justify-content-end" : "justify-content-start"}`}>
            <div className={`p-2 mb-2 rounded ${msg.sender === "user" ? "bg-primary text-white" : "bg-secondary text-white"}`}>
              {msg.text}
              {msg.file && <div className="mt-2"><strong>File:</strong> {msg.file}</div>}
            </div>
          </div>
        ))}
      </div>
      <div className="input-group">
        <input
          type="file"
          className="form-control"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <input
          type="text"
          className="form-control"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="input-group-append">
          <button className="btn btn-primary" onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;