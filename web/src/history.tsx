import React, { useState } from "react";

import { FaTrash } from "react-icons/fa";
import { MdExpandMore, MdExpandLess } from "react-icons/md";

import * as t from "./types";
import { deleteHistory } from "./api";
import { escapeRegExp } from "./util";

interface IHistoryEntryProps {
  bookId: t.BookId;
  entry: t.HistoryEntry;
  dispatchHistory: (action: t.HistoryAction) => void;
}

function HistoryEntry({ bookId, entry, dispatchHistory }: IHistoryEntryProps) {
  const [expanded, setExpanded] = useState(false);

  function deleteEntry() {
    console.log(`Deleting ${entry.id} (${entry.question})`);

    deleteHistory(bookId, entry.id).then(() => {
      dispatchHistory({ type: "delete", id: entry.id });
    });
  }

  const { question, references } = entry;

  if (entry.error !== null) {
    return (
      <div className="history-entry history-entry-error">
        <div className="question-line">
          <div className="question">{question}</div>
          <div className="del-button" onClick={deleteEntry}>
            <FaTrash />
          </div>
        </div>
        <div className="error-message">
          <span>{entry.error}</span>
        </div>
      </div>
    );
  }

  const { answer, quote } = entry as t.HistoryEntrySuccess;

  return (
    <div className="history-entry">
      <div className="question-line">
        <div className="question">{question}</div>
        <div className="del-button" onClick={deleteEntry}>
          <FaTrash />
        </div>
      </div>
      <div className="answer">{answer}</div>
      <div className="quote-and-ref">
        <div className="quote-line">
          <div className="expand-button" onClick={() => setExpanded((e) => !e)}>
            {" "}
            {expanded ? <MdExpandLess /> : <MdExpandMore />}{" "}
          </div>
          {quote && <div className="quote"> {quote} </div>}
        </div>
        <div className={"references " + ((expanded && "expanded") || "")}>
          {references.map((r) => (
            <Reference key={r.id} reference={r} quote={quote} />
          ))}
        </div>
      </div>
    </div>
  );
}

interface IReferenceProps {
  reference: t.Reference;
  quote: string;
}
function Reference({ reference, quote }: IReferenceProps) {
  let { content } = reference;

  // normalize the spaces
  content = content.replace(/\s+/gm, " ");
  quote = quote.replace(/\s+/gm, " ");
  if (/whisper/.test(content)) {
    window.q = quote;
    window.c = content;
  }

  const split = content.split(new RegExp(escapeRegExp(quote), "i"));

  let highlighted_content: string | JSX.Element = content;
  if (split.length === 2) {
    const [left, right] = split;
    highlighted_content = (
      <>
        {left}
        <span className="highlight">{quote}</span>
        {right}
      </>
    );
  }

  return (
    <div className="reference">
      <div className="content">{highlighted_content}</div>
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
