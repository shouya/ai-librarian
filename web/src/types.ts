export type BookId = string & { __compile_time_only: any };
export interface Book {
  id: BookId;
  title: string;
}

export type RefId = string & { __compile_time_only: any };
export interface Reference {
  id: RefId;
  content: string;
  metadata?: {
    chapter_index?: number;
    chapter_title?: string;
    next_id?: RefId;
    prev_id?: RefId;
    merged_ids?: RefId[];
  };
}

export type HistoryEntryId = string & { __compile_time_only: any };
export interface HistoryEntryError {
  id: HistoryEntryId;
  bookId: BookId;
  question: string;
  error: string;
  // answer must be null
  answer: null;
}

export interface HistoryEntrySuccess {
  id: HistoryEntryId;
  bookId: BookId;
  question: string;
  answer: string;
  quote: string | null;
  references: Reference[];
  // error must be null
  error: null;
}

export type HistoryEntry = HistoryEntryError | HistoryEntrySuccess;

export type History = HistoryEntry[];

export type HistoryAction =
  | { type: "add"; entry: HistoryEntry }
  | { type: "init"; history: History }
  | { type: "delete"; id: HistoryEntryId };
