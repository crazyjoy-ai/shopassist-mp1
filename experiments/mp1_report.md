# Mini-Project 1 — report

Write every section in your own words. Each section needs at least a few real sentences: replace every line that
starts with `TODO`. The checker reads this file, and at the demo you explain any section the instructor picks.

## 1. Me, and how I used AI
TODO: your name and GitHub username. Then an honest AI-use log: which tool (ChatGPT, Copilot, Claude...), for which
task, and ONE suggestion you rejected or corrected, and why. Using AI is allowed; not understanding your own code
is not. (Never paste your .env or a key into any AI tool.)

## 2. How a request flows
TODO: follow ONE message, e.g. "Can I return the shoes in ORD-10231?", from `POST /chat/stream` to the last SSE
event. Name the functions it passes through, where memory, the system prompt and the tools come in, and the hop
through the gateway (which container calls which, on which URL).

## 3. Memory: my choice, with numbers
My memory strategy is a sliding window that keeps the last four turns (`KEEP_TURNS=4`). Session 19 measured the
cost of the last turn in a 17-turn chat. Resending the whole history took 1,896 tokens, the window took 1,013, and
the summary took 1,343. The catch is recall: the reference number from turn 2 was missing from the window's reply
and from the summary's reply at turn 17, and only the full history returned it. Even so, the window is the better
fit for a store bot. Most customers ask about an order status, a return or a quick follow-up, so a short, fixed
slice of history is enough, and it avoids the extra model call that a summary needs. Four turns also keeps the
order number from turn 1 in view at turn 4, which is what the workbook's memory probe checks. The downside is that
anything older than four turns is dropped without warning, so in a long chat a customer might have to give the
order number or another earlier detail again.

## 4. Tools and validation
TODO: your three tools and what you validate (order id format, pincode, speed, reason). Give one bad argument your
validation catches, and what the model did after it got the INVALID message (from a real run).

## 5. Defending the prompt
TODO: summarise your Security rules section. Which of the four attacks came closest to working, and why? If any
attack broke through, what did you change, and did it help?

## 6. Results
TODO: copy the Summary block from experiments/mp1_results.md. Then explain at least TWO golden questions that
failed, or would fail on a smaller model: was it the wrong tool, a wrong argument, or the wording?

## 7. Gateway, Docker and honest limits
TODO: what the gateway gives you that calling Groq directly wouldn't (one header you saw, and the fallback). Then
at least three things that would break in production (think: memory in RAM, session ids, one master key, one
server, the model inventing things) and what you would do about each one.
