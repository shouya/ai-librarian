import React, { useState } from "react";

import { FaTrash } from "react-icons/fa";
import { MdExpandMore, MdExpandLess } from "react-icons/md";

import * as t from "./types";
import { deleteHistory } from "./api";
import { escapeRegExp } from "./util";

interface HistoryEntryProps {
  bookId: t.BookId;
  entry: t.HistoryEntry;
  dispatchHistory: (action: t.HistoryAction) => void;
}

function HistoryEntry({ bookId, entry, dispatchHistory }: HistoryEntryProps) {
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

  const { quote, answer } = entry as t.HistoryEntrySuccess;
  const quoteValue = quote || null;

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
          <div className="quote"> {quoteValue ?? "<quote not given>"} </div>
        </div>
        <div className={"references " + ((expanded && "expanded") || "")}>
          {references.map((r) => (
            <Reference key={r.id} reference={r} quote={quoteValue} />
          ))}
        </div>
      </div>
    </div>
  );
}

interface ReferenceProps {
  reference: t.Reference;
  quote: string | null;
}

function highlightedInReference({ reference, quote }: ReferenceProps): React.ReactNode {
  let { content } = reference;
  if (quote === null || quote.trim() === "") {
    return content;
  }

  // normalize the spaces
  content = content.replace(/\s+/gm, " ");
  quote = quote.replace(/\s+/gm, " ");

  // try to match the quote in a full piece.
  const split = content.split(new RegExp(escapeRegExp(quote), "i"));
  if (split.length === 2) {
    const [left, right] = split;
    return (
      <>
        {left}
        <span className="highlight">{quote}</span>
        {right}
      </>
    );
  }

  // try to break down the quote into sentences and highlight segments in the content.
  const quoteSegments = quote.split(/[,.?!“”]+/).map(s => escapeRegExp(s.trim())).filter(s => s.length > 3);
  const regexp = quoteSegments.join("|");
  const segments = content.split(new RegExp(`(${regexp})`, "ig"));
  return (
    <span>
      {segments.map((segment, index) => {
        if (RegExp(regexp).test(segment)) {
          return <span key={index} className="highlight">{segment}</span>;
        }
        return segment;
      })}
    </span>
  );
}

function Reference({ reference, quote }: ReferenceProps) {
  const highlighted = highlightedInReference({ reference, quote });
  return (
    <div className="reference">
      <div className="content">{highlighted}</div>
      <div className="metadata">
        <div className="chapter">{reference.metadata.chapter_title}</div>
        <div className="ref-id">{reference.id}</div>
      </div>
    </div>
  );
}

interface HistoryBacklogProps {
  bookId: t.BookId;
  history: t.History;
  dispatchHistory: (action: t.HistoryAction) => void;
}

export function HistoryBacklog({
  history,
  dispatchHistory,
  bookId,
}: HistoryBacklogProps) {
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
