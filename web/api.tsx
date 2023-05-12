export const listBooks = (callback) => {
    return fetch("/api/books")
        .then(response => response.json())
        .then(json => json.map(book => {
            return { id: book.book_id, title: book.name }
        }))
        .then(json => callback(json))
        .catch(error => console.log(error));
};

export const ask = (book_id: string, question: string, callback) => {
    return fetch(`/api/books/${book_id}/ask?q=${question}`, {
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
