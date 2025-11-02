import { useState } from "react";
import api from "./api";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return alert("Please enter a question!");

    setLoading(true);
    setAnswer("");
    setAudioUrl("");

    try {
      const formData = new FormData();
      formData.append("question", question);

      const res = await api.post("/ask", formData);
      setAnswer(res.data.answer);
      setAudioUrl(`http://127.0.0.1:8000/${res.data.audio_file}`);
    } catch (err) {
      console.error(err);
      alert("Error communicating with the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        fontFamily: "sans-serif",
        padding: "2rem",
        textAlign: "center",
        maxWidth: "600px",
        margin: "0 auto",
      }}
    >
      <h1>🎙️ AI Voice Agent</h1>
      <textarea
        rows="4"
        placeholder="Ask your question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "100%", margin: "1rem 0", padding: "0.5rem" }}
      />
      <br />
      <button
        onClick={handleAsk}
        disabled={loading}
        style={{
          padding: "0.5rem 1rem",
          cursor: "pointer",
          backgroundColor: "#4F46E5",
          color: "white",
          border: "none",
          borderRadius: "6px",
        }}
      >
        {loading ? "Thinking..." : "Ask Agent"}
      </button>

      {answer && (
        <div style={{ marginTop: "2rem" }}>
          <h3>💬 Response:</h3>
          <p>{answer}</p>
        </div>
      )}

      {audioUrl && (
        <div style={{ marginTop: "1rem" }}>
          <h3>🔊 Audio:</h3>
          <audio controls src={audioUrl}></audio>
        </div>
      )}
    </div>
  );
}

export default App;
