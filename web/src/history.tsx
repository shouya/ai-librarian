import React, { useState } from "react";

import * as t from "./types";

interface IHistoryEntryProps {
  entry: t.HistoryEntry;
}

function HistoryEntry({ entry }: IHistoryEntryProps) {
  const [expand, setExpand] = useState(false);

  if (entry.error !== null) {
    return (
      <div className="history-entry history-entry-error">
        Error: <span>{entry.error}</span>
      </div>
    );
  }

  const { question, answer, quote, references } =
    entry as t.HistoryEntrySuccess;

  return (
    <div className="history-entry">
      <div className="question">{question}</div>
      <div className="answer">{answer}</div>
      <div
        className="quote"
        onClick={() => setExpand((e) => !e)}
        title="Click to expand"
      >
        {quote}
      </div>
      <div className={"references " + (expand && "expanded")}>
        {references.map((r) => (
          <Reference key={r.id} reference={r} />
        ))}
      </div>
    </div>
  );
}

interface IReferenceProps {
  reference: t.Reference;
}
function Reference({ reference }: IReferenceProps) {
  return (
    <div className="reference">
      <div className="content">{reference.content}</div>
      <div className="metadata">
        <div className="chapter">{reference.metadata.chapter_title}</div>
        <div className="ref-id">{reference.id}</div>
      </div>
    </div>
  );
}

interface IHistoryBacklogProps {
  history: t.History;
}

export function HistoryBacklog({ history }: IHistoryBacklogProps) {
  return (
    <div className="history-backlog">
      {history.map((entry) => (
        <HistoryEntry key={entry.id} entry={entry} />
      ))}
    </div>
  );
}
