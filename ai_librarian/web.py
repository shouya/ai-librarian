from flask import Flask, request

from .librarian import Librarian

app = Flask(__name__)


@app.route("/ask")
def ask():
    book_id = request.args.get("book_id")
    if not book_id:
        raise ValueError("book_id is required")
    q = request.args.get("q")
    if not q:
        raise ValueError("q is required")

    librarian = Librarian(book_id)
    result = librarian.ask_question(q)
    result["rel_docs"] = [doc.dict() for doc in result["rel_docs"]]
    for d in result["rel_docs"]:
        d.pop("embedding")
    return result


@app.route("/")
def index():
    return """
<html>
<body>
<h1>AI Librarian</h1>
<p>Ask a question about a book</p>
<script>
function ask() {
    var book_id = document.getElementById("book_id").value;
    var q = document.getElementById("q").value;
    var url = "/ask?book_id=" + book_id + "&q=" + encodeURIComponent(q);
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onload = function (e) {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var result = JSON.parse(xhr.responseText);
                document.getElementById("answer").innerHTML = result.answer;
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.onerror = function (e) {
        console.error(xhr.statusText);
    };
    xhr.send(null);
}
</script>
<label for="book_id">Book ID:</label><br>
<input type="text" id="book_id" name="book_id" value="1"><br>
<label for="q">Question:</label><br>
<input type="text" id="q" name="q" value="What is the meaning of life?"><br><br>
<input type="submit" value="Submit" onclick="ask()">
<p id="answer"></p>
</body>
</html>
"""
