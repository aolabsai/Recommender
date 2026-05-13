# Board Game Night Recommender

This bounty submission adapts the AO Labs recommender pattern to a new domain:
choosing board games for a specific group, time box, and table mood.

The demo uses a local catalog, so reviewers can run it without API keys, private
packages, or paid data sources. When `ao_core` and `ao_arch` are installed, the
same 8-bit inputs can also be scored by an AO Agent.

## Domain Fit

Board game recommendations are strongly contextual:

- a two-player weeknight needs different suggestions than a six-player party;
- a 30-minute teach is not acceptable for every table;
- social energy and table mood matter as much as genre;
- user feedback can quickly change the best recommendation for the next session.

That makes the domain a good fit for a continuously trainable recommender.

## AO Input Shape

The implementation preserves the original `[3, 2, 1, 2]` architecture shape:

| Bits | Meaning |
| --- | --- |
| 3 | Game type: strategy, party, cooperative, family, duel, story, puzzle, economic |
| 2 | Duration bucket: quick, standard, long, epic |
| 1 | High-interaction flag |
| 2 | Requested table mood: casual, competitive, social, immersive |

Example: `Codenames` for a social table encodes to `00100110`.

## Files

- `board_game_domain.py` - catalog, encoding, deterministic scoring, feedback adjustment
- `board_game_recommender.py` - CLI plus optional Streamlit UI
- `arch__BoardGameRecommender.py` - AO architecture file
- `tests/test_board_game_domain.py` - unit tests for encoding, filters, and feedback

## Run Locally

```bash
python3 board_game_recommender.py --players 4 --mood social --minutes 60
```

With sample feedback:

```bash
python3 board_game_recommender.py --players 4 --mood social --minutes 60 --with-sample-feedback
```

Optional Streamlit UI:

```bash
streamlit run board_game_recommender.py
```

## Sample Output

```text
Board game night recommendations
Context: {'players': 4, 'available_minutes': 60, 'mood': 'social', ...}

1. Codenames (6.4) - fits a social table; quick to teach; high table interaction [bits=00100110]
2. Just One (6.4) - fits a social table; quick to teach; high table interaction [bits=00100110]
3. 7 Wonders (5.2) - fits a social table [bits=01101010]
```

## Validation

```bash
python3 -m unittest tests/test_board_game_domain.py
python3 -m unittest discover -s tests
python3 -m py_compile board_game_domain.py board_game_recommender.py arch__BoardGameRecommender.py tests/test_board_game_domain.py
python3 board_game_recommender.py --players 4 --mood social --minutes 60
git diff --check
```
