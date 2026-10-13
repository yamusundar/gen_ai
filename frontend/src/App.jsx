
import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceMessage, setVoiceMessage] = useState("");
  const [language, setLanguage] = useState("en-IN");
  const [speaking, setSpeaking] = useState(false);
  function speakAnswer() {
    if (!answer) {
      return;
    }

    if (!("speechSynthesis" in window)) {
      alert("Sorry, your browser does not support spoken answers.");
      return;
    }

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(answer);
    const voices = window.speechSynthesis.getVoices();

    // Detect the language of the answer
    const tamilPattern = /[\u0B80-\u0BFF]/;
    const hindiPattern = /[\u0900-\u097F]/;

    let targetLanguage = "en-IN";

    if (tamilPattern.test(answer)) {
      targetLanguage = "ta-IN";
    } else if (hindiPattern.test(answer)) {
      targetLanguage = "hi-IN";
    }

    speech.lang = targetLanguage;
    speech.rate = 0.9;

    // Choose a voice for the detected language
    const matchingVoice = voices.find(
      (voice) => voice.lang.toLowerCase() === targetLanguage.toLowerCase()
    ) || voices.find(
      (voice) => voice.lang.toLowerCase().startsWith(targetLanguage.split("-")[0])
    );

    if (matchingVoice) {
      speech.voice = matchingVoice;
    }

    speech.onstart = () => setSpeaking(true);
    speech.onend = () => setSpeaking(false);
    speech.onerror = () => setSpeaking(false);

    window.speechSynthesis.speak(speech);
  }

  function startListening() {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setVoiceMessage(
        "Voice recognition is not supported in this browser. Please try Google Chrome."
      );
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = language;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setListening(true);
      setVoiceMessage("Listening... Speak your question.");
    };

    recognition.onresult = (event) => {
      const spokenText = event.results[0][0].transcript;
      setQuestion(spokenText);
      setVoiceMessage("Voice captured! Click Ask Railway AI.");
    };

    recognition.onerror = () => {
      setVoiceMessage(
        "Could not capture your voice. Please check microphone permission and try again."
      );
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  }


  async function askQuestion() {
    if (!question.trim()) {
      setAnswer("Please enter a question first.");
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/ask?question=${encodeURIComponent(question)}`
      );

      if (!response.ok) {
        throw new Error("The backend returned an error.");
      }

      const data = await response.json();
      setAnswer(data.answer || "No answer was returned.");
    } catch (error) {
      setAnswer(
        "Could not connect to the railway assistant. Please check that your Python backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="train-icon">🚆</div>
        <h1>Railway AI Assistant</h1>
        <p>Ask railway questions in your preferred language.</p>
      </header>

      <main className="chat-card">
        <label htmlFor="question">Your question</label>
        <select
          id="language"
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
        >
          <option value="en-IN">English</option>
          <option value="ta-IN">தமிழ் (Tamil)</option>
          <option value="hi-IN">हिन्दी (Hindi)</option>
        </select>

        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Example: What is the route of train 12675?"
          rows={4}
        />
        <div className="voice-controls">
          <button
            type="button"
            className="mic-button"
            onClick={startListening}
            disabled={listening || loading}
          >
            {listening ? "🎙️ Listening..." : "🎤 Speak Your Question"}
          </button>

          {voiceMessage && (
            <p className="voice-message">{voiceMessage}</p>
          )}
        </div>

        <button onClick={askQuestion} disabled={loading}>
          {loading ? "Getting answer..." : "Ask Railway AI"}
        </button>

        {answer && (
          <section className="answer" aria-live="polite">
            <h2>Assistant's Answer</h2>
            <p>{answer}</p>

            <button
              type="button"
              onClick={speakAnswer}
              disabled={speaking}
            >
              {speaking ? "🔊 Speaking..." : "🔊 Speak Answer"}
            </button>
          </section>
        )}
      </main>

      <footer>
        Railway information is based on the project's sample database.
      </footer>
    </div>
  );
}

export default App;
