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

  const { answer } = entry as t.HistoryEntrySuccess;
  const quote = entry.quote === "" ? null : entry.quote;

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
          <div className="quote"> {quote ?? "<quote not given>"} </div>
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
  quote: string | null;
}

function highlightedInReference({ reference, quote }: IReferenceProps) {
  let { content } = reference;
  if (quote === null || quote.trim() === "") {
    return content;
  }

  // normalize the spaces
  content = content.replace(/\s+/gm, " ");
  quote = quote.replace(/\s+/gm, " ");
  if (/whisper/.test(content)) {
    window.q = quote;
    window.c = content;
  }

  // try to match the quote in a full piece.
  const split = content.split(new RegExp(escapeRegExp(quote), "i"));
  let highlighted: string | JSX.Element = content;
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
  const html = content.replace(new RegExp(regexp, "ig"), (match) => {
    return `<span class="highlight">${match}</span>`;
  });

  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}

function Reference({ reference, quote }: IReferenceProps) {
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
