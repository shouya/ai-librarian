import React, { useState } from "react";

import { FaTrash } from "react-icons/fa";

import * as t from "./types";
import { deleteHistory } from "./api";

interface IHistoryEntryProps {
  bookId: t.BookId;
  entry: t.HistoryEntry;
  dispatchHistory: (action: t.HistoryAction) => void;
}

function HistoryEntry({ bookId, entry, dispatchHistory }: IHistoryEntryProps) {
  const [expand, setExpand] = useState(false);

  if (entry.error !== null) {
    return (
      <div className="history-entry history-entry-error">
        Error: <span>{entry.error}</span>
      </div>
    );
  }

  function deleteEntry() {
    console.log(`Deleting ${entry.id} (${entry.question})`);

    deleteHistory(bookId, entry.id).then(() => {
      dispatchHistory({ type: "delete", id: entry.id });
    });
  }

  const { question, answer, quote, references } =
    entry as t.HistoryEntrySuccess;

  return (
    <div className="history-entry">
      <div className="question-line">
        <div className="question">{question}</div>
        <div className="del-button" onClick={deleteEntry}>
          <FaTrash />
        </div>
      </div>
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
  bookId: t.BookId;
  history: t.History;
  dispatchHistory: (action: t.HistoryAction) => void;
}

export function HistoryBacklog({
  history,
  dispatchHistory,
  bookId,
}: IHistoryBacklogProps) {
  return (
    <div className="history-backlog">
      {history.map((entry) => (
        <HistoryEntry
          key={entry.id}
          entry={entry}
          bookId={bookId}
          dispatchHistory={dispatchHistory}
        />
      ))}
    </div>
  );
}
