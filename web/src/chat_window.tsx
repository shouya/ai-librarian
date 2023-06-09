import React, { useReducer, useEffect } from "react";

import { listHistory } from "./api";
import { HistoryBacklog } from "./history";

import * as t from "./types";
import { AskBar } from "./ask_bar";

function historyReducer(history: t.History, action: t.HistoryAction) {
  if (action.type == "add") {
    return [action.entry, ...history];
  } else if (action.type == "init") {
    return action.history;
  } else if (action.type == "delete") {
    return history.filter((entry) => entry.id !== action.id);
  } else {
    throw new Error("Invalid action type");
  }
}

interface ChatWindowProps {
  bookId: t.BookId | null;
}
export function ChatWindow({ bookId }: ChatWindowProps) {
  const [history, dispatchHistory] = useReducer(historyReducer, null);

  useEffect(() => {
    listHistory(bookId).then((history) =>
      dispatchHistory({ type: "init", history })
    );
  }, [bookId]);

  if (!bookId)
    return <div className="chat-window unavailable">Select a book.</div>;

  if (!history)
    return <div className="chat-window unavailable">Loading history...</div>;

  return (
    <div className="chat-window">
      <HistoryBacklog
        bookId={bookId}
        history={history}
        dispatchHistory={dispatchHistory}
      />
      <AskBar
        bookId={bookId}
        history={history}
        dispatchHistory={dispatchHistory}
      />
    </div>
  );
}
