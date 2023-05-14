import { useState, useReducer, useRef, useEffect } from "react";

export function chatHistoryReducer(chatHistory, action) {
  const { bookId } = action;
  const history = chatHistory[bookId] || [];

  if (action.type == "add") {
    const { id, question, answer, quote, error, references } = action;
    const historyEntry = {
      id, question, answer, quote, error, references
    };
    return { ...chatHistory, [bookId]: [historyEntry, ...history] }
  } else if (action.type == "init") {
    return { ...chatHistory, [bookId]: action.history }
  } else {
    throw new Error("Invalid action type");
  }
}

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
