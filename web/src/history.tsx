import { useState, useRef, useEffect } from "react";

export function ChatHistoryEntry({ history }) {
  const [expand, setExpand] = useState(false);
  const { question, answer, quote } = history;
  return <div className="chat-history-entry">
    <div className="question">{question}</div>
    <div className="answer">{answer}</div>
    <div className="quote" onClick={() => setExpand(e => !e)} title="Click to expand">{quote}</div>
    <div className={"references " + (expand && "expanded")} >
      {history.references.map(r => <Reference key={r.id} reference={r} />)}
    </div>
  </div>;
}

export function ChatHistoryBacklog({ chatHistory }) {
  return <div className="chat-history-backlog">
    {chatHistory.map(entry =>
      <ChatHistoryEntry key={entry.id} history={entry} />
    )}
  </div>;
}

function Reference({ reference }) {
  return <div className="reference">
    <div className="content">{reference.content}</div>
    <div className="metadata">
      <div className="chapter">{reference.metadata.chapter_title}</div>
      <div className="ref-id">{reference.id}</div>
    </div>
  </div>;
}
