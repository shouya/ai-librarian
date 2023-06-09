# AI Librarian

It allows you to ask any questions about a book in epub format.

I often lose track of the plot while reading a book. Sometimes I forget
who a character is, or what happened in a previous chapter. I wanted to
be able to ask questions about a book, and get answers. So I built this
tool to do that.

AI Librarian makes use of OpenAI's embedding and GPT-3.5 chat API.

## Features

-   **A [novel
    approach](https://github.com/shouya/ai-librarian/blob/master/ai_librarian/retriever.py#L47)
    to dynamically extend relevant context**, resulting in high
    retrieval accuracy comparing to the naive knowledge-base
    question-answering approach
-   The book is indexed on first opening, and then cached for future use
-   Input history is saved across sessions

## Cost

For reference, a book of \~200 pages (\~50K words, \~70K tokens) costs
$0.055 to index. This is a one-time cost, and the book is cached for
future use.

Each question asked costs usually about $0.0015. The cost can float up
and down depending on the question.

## Usage

``` bash
$ export OPENAI_API_KEY=sk-...
$ ai-librarian chat -f <path/to/book.epub>
Question: Where do I live?
Answer: You are living in the Wheatlands' house, which is in a little town.

> I explain I’m living in the Wheatlands’ house. It’s in a little town.
---------------------------------------------------------------------------------------------------------
Question: What is the "little town" where Wheatlands' house is in?
Answer: The little town where Wheatlands' house is in is Autun.

> “I doubt if you’ve ever heard of it. Autun.”
---------------------------------------------------------------------------------------------------------
Question: !r

Document 0: Isabel is telling about her husband’s family. She’s sick of them. All they’re interested in is their grandbaby, she says. I explain I’m living in the Wheatlands’ house. It’s in a little town.“You know Dijon?”

“Yes.”

“It’s near Dijon.”

“It’s in the center of France,” he decides.“The very heart. It’s a small town, but it has a certain quality. I mean, it’s not rich, it’s not splendid. It’s just old and well-formed.”

“What town is it?”

Document 1: The Wheatlands’ house is in the old part of town, built right on the Roman wall. First there is a long avenue of trees and then the huge square. A street of shops. After these, nothing, houses, a Utrillo-like silence. At last the Place du Terreau. There’s a fountain, a trifoil fountain from which pigeons are drinking, and looming above, like a great, beached ship: the cathedral. It’s only possible to glimpse the spire, studded along the seams, that marvelous spire which points at the same time to the earth’s center and also the outer void. The road leads around behind. Here many windows are broken. The lead frames, formed like diamonds, are empty and black. A hundred feet farther is a small, blind street, an impasse, as they say, and there it stands.It’s a large, stone house, the roof sinking, the sills worn. A huge house, the windows tall as trees, exactly as I remember it from a few days of visiting when, on the way up from the station I had a strange conviction I was in a town I already knew. The streets were familiar to me. By the time we reached the gate I had already formed an idea that floated through my mind the rest of the summer, the idea of returning. And now I am here, before the gate. As I look at it, I suddenly see, for the first time, letters concealed in the iron foliage, an inscription: VAINCRE OU MOURIR. The VAINCRE is missing its c.

Document 2: It’s closed. A large scale. Schedules on the wall. The man behind the glass of the ticket window doesn’t look up as I walk by.The Wheatlands’ house is in the old part of town, built right on the Roman wall. First there is a long avenue of trees and then the huge square. A street of shops. After these, nothing, houses, a

Document 3: “The very heart. It’s a small town, but it has a certain quality. I mean, it’s not rich, it’s not splendid. It’s just old and well-formed.”

“What town is it?”“I doubt if you’ve ever heard of it. Autun.”

“Autun,” he says. Then, “It sounds like the real France.”

“It is the real France.”

“He’s crazy,” Billy warns.
---------------------------------------------------------------------------------------------------------
```

## Other usages

You may notice from the demo that the command \`!r\` is used to retrieve
the referenced portion of the book for the question.

The following interactive commands are available:

| Command | Aliases | Description                                  |
|---------|---------|----------------------------------------------|
| !refs   | !r      | Retrieve the referenced portion of the book. |
| !quit   | !q      | Quit the interactive shell.                  |

You can also force rebuild the book's index by calling:

``` bash
$ ai-librarian rebuild -f <path/to/book.epub>
```

## Acknowledgments

This tool was built on my re-invention of LangChain components. The
design was heavily influenced by, and some utility functions are taken
directly from, the LangChain library.
