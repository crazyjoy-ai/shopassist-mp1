"""How much of the conversation the model sees. YOU own this file.

DECISION: sliding window, KEEP_TURNS = 4.

Evidence (S19 report, openai/gpt-oss-20b, 17-turn conversation, reference number planted at turn 2 and asked for
again at turn 17; cost = input+output tokens of the final turn only):

    strategy   turn-17 cost   recall at turn 17
    naive      1896           yes
    window     1013           no
    summarize  1343           no

What the numbers say:
- Sending everything is the only strategy that recalled turn 2, but it is the most expensive call (1896 tokens) and
  that cost keeps growing every turn. With many customers on one server this is not acceptable.
- The window cuts the turn-17 call to 1013 tokens, about 47% less than naive, and the cost stays flat however long
  the chat runs.
- The summary cost 1343 tokens, about 33% more than the window, and in my run it still did NOT recall the turn-2
  fact. It also needs an extra model call on long turns and can summarise wrongly. So here it paid more and
  recovered nothing, which is why it is not selected.
- The window forgetting the turn-2 fact at turn 17 is an expected trade-off. A 4-turn window cannot see turn 2 by
  design, and I accept it because store chats are short (an order status, a return, one follow-up).

Why KEEP_TURNS = 4: the memory probe needs the order number from turn 1 to still be visible at turn 4, so the value
must be at least 3. 4 meets that with one turn of margin while keeping the prompt small and predictable.

If a deployment needs longer recall, raise KEEP_TURNS (cost rises with it) or implement the summary strategy.
Override with MEMORY and KEEP_TURNS in .env or Docker environment variables.
"""
import os

from langchain_core.messages import HumanMessage, SystemMessage

STRATEGY = os.getenv("MEMORY") or "window"         # "window" or "summary"
KEEP_TURNS = int(os.getenv("KEEP_TURNS") or 4)     # earlier turns (question + answer) the model sees; must be >= 3


def window(history: list, keep_turns: int = KEEP_TURNS) -> list:
    """The last keep_turns turns. One turn = 2 messages (question + answer)."""
    return history[-2 * keep_turns:] if keep_turns > 0 else []


SUMMARY_PROMPT = ("Summarise this store conversation in at most 5 short bullet points. Keep every name, order "
                  "number, pincode and figure the CUSTOMER gave. Do not add anything that was not said.")


def summarise(history: list, llm, keep_turns: int = KEEP_TURNS) -> list:
    """STRETCH MP1-T4s (not selected): older turns become ONE summary message; recent turns stay word for word.

    If history is short (at most 2 * keep_turns messages), return it unchanged. Otherwise:
        old, recent = history[:-2 * keep_turns], history[-2 * keep_turns:]
        transcript = "\\n".join(f"{type(m).__name__}: {m.content}" for m in old)
        summary = llm.invoke([SystemMessage(SUMMARY_PROMPT), HumanMessage(transcript)]).content
        return [SystemMessage(f"Summary of the earlier conversation:\\n{summary}")] + recent
    Cost note: this makes one EXTRA model call on every long turn. In S19 it cost 1343 tokens vs 1013 for the window
    and did not recover the early fact, so the window is used instead.
    """
    raise NotImplementedError("stretch MP1-T4s")


def trim(history: list, llm=None) -> list:
    """What the model sees of this session's history - the strategy chosen above."""
    if STRATEGY == "summary":
        return summarise(history, llm, KEEP_TURNS)
    return window(history, KEEP_TURNS)

