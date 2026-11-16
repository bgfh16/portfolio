"""Asks a fixed list of test questions and prints the best match for each,
so we can check which chunks come back and how the scores compare.

Run from the project folder:
    python utils/rag_check.py
"""

import warnings
warnings.filterwarnings("ignore")

import rag

QUESTIONS = [
    ("COVERED", "How do I control cassava mealybug?"),
    ("COVERED", "What fertiliser should I use on maize in Kano?"),
    ("COVERED", "When should I plant rice in Niger State?"),
    ("COVERED", "How do I store cowpea without chemicals?"),
    ("COVERED", "What causes late blight on tomatoes?"),
    ("COVERED", "How far apart should I plant pineapple?"),
    ("VAGUE", "my leaves are yellow"),
    ("VAGUE", "best crop to plant now"),
    ("NOT COVERED", "How do I grow ginger?"),
    ("NOT COVERED", "How do I grow sugarcane?"),
    ("NOT COVERED", "How do I grow watermelon?"),
    ("NOT COVERED", "How do I raise broiler chickens?"),
    ("NOT COVERED", "How do I start a fish pond?"),
    ("NOT FARMING", "What is the capital of France?"),
    ("NOT FARMING", "Write me a poem about love"),
    ("NOT FARMING", "Who won the last World Cup?"),
    ("NOT FARMING", "How do I fix my laptop screen?"),
]

if __name__ == "__main__":
    index = rag.load_index()
    print(f"{'GROUP':<12} {'BEST':>5}  QUESTION  ->  the chunks, in the order returned")
    for group, question in QUESTIONS:
        results = rag.search(question, index=index)
        best_closeness = max(score for _, score in results)
        print(f"{group:<12} {best_closeness:>5.3f}  {question}")
        for doc, score in results:
            print(f"{'':<19}{score:.3f}  {doc.metadata['chunk_id']}")
