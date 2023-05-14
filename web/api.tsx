export const listBooks = (callback) => {
  return fetch("/api/books")
    .then(response => response.json())
    .then(json => json.map(book => {
      return { id: book.book_id, title: book.name }
    }))
    .then(json => callback(json))
    .catch(error => console.log(error));
};

export const listHistory = (book_id, callback) => {
  if (!book_id) {
    console.log(book_id);
    return callback([]);
  }

  return fetch(`/api/books/${book_id}/history`)
    .then(response => response.json())
    .then(json => json.map(entry => {
      return {
        ...entry,
        references: entry.rel_docs || [],
        id: entry.log_id
      }
    }))
    .then(json => callback(json))
    .catch(error => console.log(error));
};

export const ask = (book_id: string, question: string, callback) => {
  if (!book_id) {
    console.log(book_id);
    return callback(null);
  }

  return fetch(`/api/books/${book_id}/ask?q=${encodeURIComponent(question)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then(json => callback(json))
    .catch(error => console.log(error));
};
