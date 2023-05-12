

export const bookList = [
  {
    id: "5aaab36d14b7f88f326d5fab9",
    title: "A sport and a pastime"
  },
  {
    id: "something",
    title: "Two sports and two pastimes"
  }
];

const dummyResponse = {
  "answer": "Dean is a character mentioned in the book, but there is not enough information to determine who he is exactly.",
  "quote": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
  "rel_docs": [
    {
      "content": "In a caf\u00e9 she happens to meet a boy who knew her. He is amazed. You\u2019ve changed a hundred per cent, he tells her. She smiles. Afterwards Dean asks,\n\n\u201cWho was that?\u201dThe brother of a girl she knew. Dean is looking towards the door as if he might return. It annoys him.",
      "id": "sentence:25:26-27/69",
      "metadata": {
        "chapter_index": 25,
        "chapter_title": "[25]",
        "merged_ids": [
          "sentence:25:26/69",
          "sentence:25:27/69"
        ],
        "next_id": "sentence:25:28/69",
        "prev_id": "sentence:25:25/69"
      }
    },
    {
      "content": "around, Dean stops.",
      "id": "sentence:32:6/34",
      "metadata": {
        "chapter_index": 32,
        "chapter_title": "[32]",
        "next_id": "sentence:32:7/34",
        "prev_id": "sentence:32:5/34"
      }
    },
    {
      "content": "mirror Dean discovers a smile.",
      "id": "sentence:18:32/53",
      "metadata": {
        "chapter_index": 18,
        "chapter_title": "[18]",
        "next_id": "sentence:18:33/53",
        "prev_id": "sentence:18:31/53"
      }
    },
    {
      "content": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
      "id": "sentence:13:37/44",
      "metadata": {
        "chapter_index": 13,
        "chapter_title": "[13]",
        "next_id": "sentence:13:38/44",
        "prev_id": "sentence:13:36/44"
      }
    }
  ]
}

export const requestToGetAnswer = ({ question, bookId }, callback) => {
  // silent the unused warning
  const { } = { question, bookId };
  callback({ ...dummyResponse, question, bookId });
};

export const initHistory = {
  "5aaab36d14b7f88f326d5fab9": [{
    "id": "1",
    "question": "asdfasdf",
    "answer": "Dean is a character mentioned in the book, but there is not enough information to determine who he is exactly.",
    "quote": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
    "references": [
      {
        "content": "In a café she happens to meet a boy who knew her. He is amazed. You’ve changed a hundred per cent, he tells her. She smiles. Afterwards Dean asks,\n\n“Who was that?”The brother of a girl she knew. Dean is looking towards the door as if he might return. It annoys him.",
        "id": "sentence:25:26-27/69",
        "metadata": {
          "chapter_index": 25,
          "chapter_title": "[25]",
          "merged_ids": [
            "sentence:25:26/69",
            "sentence:25:27/69"
          ],
          "next_id": "sentence:25:28/69",
          "prev_id": "sentence:25:25/69"
        }
      },
      {
        "content": "around, Dean stops.",
        "id": "sentence:32:6/34",
        "metadata": {
          "chapter_index": 32,
          "chapter_title": "[32]",
          "next_id": "sentence:32:7/34",
          "prev_id": "sentence:32:5/34"
        }
      },
      {
        "content": "mirror Dean discovers a smile.",
        "id": "sentence:18:32/53",
        "metadata": {
          "chapter_index": 18,
          "chapter_title": "[18]",
          "next_id": "sentence:18:33/53",
          "prev_id": "sentence:18:31/53"
        }
      },
      {
        "content": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
        "id": "sentence:13:37/44",
        "metadata": {
          "chapter_index": 13,
          "chapter_title": "[13]",
          "next_id": "sentence:13:38/44",
          "prev_id": "sentence:13:36/44"
        }
      }
    ]
  },
  {
    "id": "2",
    "question": "asdfasdfasdgasdg",
    "answer": "Dean is a character mentioned in the book, but there is not enough information to determine who he is exactly.",
    "quote": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
    "references": [
      {
        "content": "In a café she happens to meet a boy who knew her. He is amazed. You’ve changed a hundred per cent, he tells her. She smiles. Afterwards Dean asks,\n\n“Who was that?”The brother of a girl she knew. Dean is looking towards the door as if he might return. It annoys him.",
        "id": "sentence:25:26-27/69",
        "metadata": {
          "chapter_index": 25,
          "chapter_title": "[25]",
          "merged_ids": [
            "sentence:25:26/69",
            "sentence:25:27/69"
          ],
          "next_id": "sentence:25:28/69",
          "prev_id": "sentence:25:25/69"
        }
      },
      {
        "content": "around, Dean stops.",
        "id": "sentence:32:6/34",
        "metadata": {
          "chapter_index": 32,
          "chapter_title": "[32]",
          "next_id": "sentence:32:7/34",
          "prev_id": "sentence:32:5/34"
        }
      },
      {
        "content": "mirror Dean discovers a smile.",
        "id": "sentence:18:32/53",
        "metadata": {
          "chapter_index": 18,
          "chapter_title": "[18]",
          "next_id": "sentence:18:33/53",
          "prev_id": "sentence:18:31/53"
        }
      },
      {
        "content": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
        "id": "sentence:13:37/44",
        "metadata": {
          "chapter_index": 13,
          "chapter_title": "[13]",
          "next_id": "sentence:13:38/44",
          "prev_id": "sentence:13:36/44"
        }
      }
    ]
  },
  {
    "id": "3",
    "question": "asdfasdg",
    "answer": "Dean is a character mentioned in the book, but there is not enough information to determine who he is exactly.",
    "quote": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
    "references": [
      {
        "content": "In a café she happens to meet a boy who knew her. He is amazed. You’ve changed a hundred per cent, he tells her. She smiles. Afterwards Dean asks,\n\n“Who was that?”The brother of a girl she knew. Dean is looking towards the door as if he might return. It annoys him.",
        "id": "sentence:25:26-27/69",
        "metadata": {
          "chapter_index": 25,
          "chapter_title": "[25]",
          "merged_ids": [
            "sentence:25:26/69",
            "sentence:25:27/69"
          ],
          "next_id": "sentence:25:28/69",
          "prev_id": "sentence:25:25/69"
        }
      },
      {
        "content": "around, Dean stops.",
        "id": "sentence:32:6/34",
        "metadata": {
          "chapter_index": 32,
          "chapter_title": "[32]",
          "next_id": "sentence:32:7/34",
          "prev_id": "sentence:32:5/34"
        }
      },
      {
        "content": "mirror Dean discovers a smile.",
        "id": "sentence:18:32/53",
        "metadata": {
          "chapter_index": 18,
          "chapter_title": "[18]",
          "next_id": "sentence:18:33/53",
          "prev_id": "sentence:18:31/53"
        }
      },
      {
        "content": "not telling the truth about Dean, I am inventing him. I am creating him out of my own inadequacies, you must always remember that.",
        "id": "sentence:13:37/44",
        "metadata": {
          "chapter_index": 13,
          "chapter_title": "[13]",
          "next_id": "sentence:13:38/44",
          "prev_id": "sentence:13:36/44"
        }
      }
    ]
  }]
};
