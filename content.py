"""Challenge content + scoring for Levels 2-5 (kept separate so main.py routes stay unchanged)."""
import random

# Level 2: logic puzzles stored as MCQ-style rows in db.questions (same API as Level 1)
L2 = [
 ("Clue: it is red, round, grows on vines, and is a base for pasta sauce. Which ingredient?", ["Tomato", "Carrot", "Onion", "Potato"], 0),
 ("Pattern: Flour, Eggs, Milk, Flour, Eggs, Milk, Flour, ... What comes next?", ["Milk", "Eggs", "Sugar", "Flour"], 1),
 ("if (spicy and not sweet) -> Chilli. Dish is spicy and not sweet. Add:", ["Honey", "Chilli", "Sugar", "Mango"], 1),
 ("Sequence 2, 4, 8, 16 ... number of eggs doubles each batch. Eggs in batch 5?", ["24", "30", "32", "20"], 2),
 ("Clue: white, powdery, dissolves in water, makes food salty. Which ingredient?", ["Salt", "Flour", "Baking soda", "Sugar"], 0),
 ("x = 3; repeat x times: add 2 spoons. Total spoons?", ["5", "6", "8", "9"], 1),
]

# order-type challenges: items are shuffled for the player; `correct` stays on the server
L3 = [
 {"id": "r1", "lang": "python", "prompt": "Print numbers 1 to 3",
  "correct": ["for i in range(1, 4):", "    print(i)"], "points": 30},
 {"id": "r2", "lang": "c", "prompt": "Return the larger of two ints",
  "correct": ["int max(int a, int b) {", "    if (a > b) return a;", "    return b;", "}"], "points": 40},
 {"id": "r3", "lang": "python", "prompt": "Sum a list",
  "correct": ["total = 0", "for n in nums:", "    total += n", "print(total)"], "points": 30},
]
L5A = {"id": "a", "prompt": "Build a pancake: choose the ingredients you need, in order",
       "correct": ["Flour", "Eggs", "Milk", "Whisk", "Pan", "Flip"],
       "decoys": ["Gravel", "Ketchup", "Ice", "Soap"], "points": 50}
L5B = {"id": "b", "lang": "python", "prompt": "Code for the pancake recipe",
       "correct": ["batter = mix(flour, eggs, milk)", "pan = heat(pan)", "while not golden(batter):", "    cook(batter)", "flip(batter)"],
       "points": 50}

L4 = {"title": "Sum of two numbers", "statement": "Read two integers a and b (space separated) from input and print a + b.",
      "sample": {"in": "2 3", "out": "5"}, "points_per_test": 20,
      "tests": [("2 3", "5"), ("-4 10", "6"), ("0 0", "0"), ("1000000 2000000", "3000000"), ("-5 -7", "-12")]}


def items_for(ch, extra=()):
    items = list(ch["correct"]) + list(extra)
    random.shuffle(items)
    return items


def order_score(ch, given):
    """Positional match; extra/missing items lower the score. Exact = full points."""
    c = ch["correct"]
    if not isinstance(given, list):
        return 0
    hits = sum(1 for i, x in enumerate(given) if i < len(c) and x == c[i])
    return round(ch["points"] * hits / max(len(c), len(given)))
