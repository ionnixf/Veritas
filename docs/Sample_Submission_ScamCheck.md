Sample Submission: ScamCheck, a scam text ﬁlter for grandparents

Sample Submission: ScamCheck, a scam text
filter for grandparents

About this sample

This is a sample submission made by the Veritas AI team to show what a complete project

looks like. The team is fictional, but the code and results are real: the notebook runs from

start to finish in Google Colab in under a minute.

It starts from suggested project 5.1 (Scam text filter) in the AI + Finance brief and adds

the team's own test set and user. Your project can be on any track, and it doesn't need to

be this long. Use it to see the level of detail judges look for:

A specific user. Grandparents who get suspicious texts.

A baseline. Results compared with the simplest rule, labelling every message "not

spam".

Something of your own. A new test set of 40 modern messages the team wrote.

Honest results. Including the scams the model still misses and the normal texts it

wrongly flags.

There are two parts: the answers this team gave on the submission form, then their one-
page write-up.

Part 1: Submission form answers

Form question

Sample answer

Project title

Building as

Team name

Team members

ScamCheck: a scam text filter for grandparents

Team

Team ScamCheck

Alex Kim and Priya Nair (fictional), with each
member's email and school

Track

AI + Finance

Starting point

5.1 Scam text filter

Page 1 of 4

Sample Submission: ScamCheck, a scam text ﬁlter for grandparents

Form question

Sample answer

One-sentence pitch

Code link

Write-up link

Demo video link

What we added

Datasets, models and AI tools used

ScamCheck helps a grandparent who isn't sure
about a text by taking the message and telling
them whether it looks like a scam, and which words
made it suspicious.

ScamCheck notebook in Google Colab

This document (Part 2), shared so anyone with the
link can view

Left blank. The video is optional, and this team
chose to spend their time on testing instead.

We wrote 40 new messages (20 modern scams, 20
normal texts) to test whether a model trained on
2010-era UK spam catches the scams people get
today. We also made the tool explain its warnings in
plain words for grandparents.

SMS Spam Collection (UCI); scikit-learn TF-IDF and
logistic regression; our own 40 test messages;
ChatGPT for debugging one pandas error and
suggesting class_weight.

New to AI?

No, at least one of us has built with AI before

Part 2: Write-up

ScamCheck: a scam text filter for grandparents

Track: AI + Finance · Team: Alex Kim and Priya Nair

This project is a prototype and is not financial advice.

The problem

Scam texts change quickly, and they are written to look like messages from real

companies. Both our grandparents have recently received fake parcel and toll texts, and
they often aren't sure whether a message is real. They need a quick second opinion that

also teaches them what to look out for.

Page 2 of 4

Sample Submission: ScamCheck, a scam text ﬁlter for grandparents

What we built

ScamCheck takes a text message and returns either "Looks like a SCAM" or "Looks

normal", with a scam score and up to three warning signs. For example:

FedEx: Your parcel is held at our depot. A redelivery fee of $1.99 is required: http://…
⚠ Looks like a SCAM (58%). Warning signs: a web link, "99", "held". Don't tap any
links. Call the company using a number you already trust.

It runs as a function in our notebook, with an optional Gradio app that has a text box and a

Check button.

What we added

The suggested project trains and tests on the SMS Spam Collection. When we read

through the spam, we noticed most of it is UK prize and ringtone texts from around 2010.

So we wrote 40 new messages modelled on texts our grandparents get today: 20 scams
(parcel redelivery, unpaid tolls, bank alerts, "Hi Mum, new number") and 20 normal texts

(doctor's reminders, family messages, bills). We used them only for testing. We also added

plain-language explanations to every warning.

How it works

Data: 5,572 labelled messages, 13.4% spam. We split them 80/20 into training and test

sets, with the same share of spam in each.

Model: TF-IDF word features with logistic regression in scikit-learn.

Our improvement: our first model never flagged a normal message but missed 20% of
spam. We set  class_weight="balanced"  so a missed scam counts for more, because

for grandparents a missed scam is worse than an extra warning.

Explanations: for each message we multiply each word's TF-IDF value by the model's

weight for that word, then show the top three. Filler words like "our" are skipped, and
link words like "http" are shown as "a web link".

Results

Model

Old test set (1,115
messages)

Modern
scams caught

False alarms on
20 normal texts

Baseline: always "not
spam"

86.6% accuracy, 0% recall

0 / 20

0

Page 3 of 4

Sample Submission: ScamCheck, a scam text ﬁlter for grandparents

Model

Old test set (1,115
messages)

Modern
scams caught

False alarms on
20 normal texts

Model 1: TF-IDF +
logistic regression

97.3% accuracy, 100%
precision, 79.9% recall

Model 2: + balanced
class weights (final)

98.4% accuracy, 95.2%
precision, 92.6% recall

3 / 20

16 / 20

0

3

Our biggest finding is that a model can score 97% on its test set and still miss most real

scams today. Model 1 learned old words like "txt", "claim" and "150p".

Where it fails. Model 2 still misses the "family emergency" and "wrong number" scams,

because they contain no scammy words and work by pretending to be someone you
know. It also wrongly flags three genuine business texts, like a doctor's reminder that says

"Reply C" and "call", because real companies and scammers use similar words.

We also tried reading chunks of letters instead of whole words. It caught the same 16

scams with only 1 false alarm, but its warning signs came out as fragments like "ttp:/",

which wouldn't help a grandparent. We kept the word model. We compared the two using
our modern test set, so a fresh set would be needed to confirm that choice.

What we'd do next

Test on real scam texts our family members have received, with their permission,

since our 40 messages are a small set written by us in US English.

Add a rule that warns about any message from an unknown number that asks for

money or gift cards, to catch impersonation scams.

Try ScamCheck with our grandparents and find out whether the warning signs

actually help them decide.

Sources

SMS Spam Collection, Almeida and Gómez Hidalgo, UCI Machine Learning Repository

(loaded from a public copy on GitHub)

scikit-learn, pandas, NumPy and Gradio (optional app)

40 modern test messages written by our team

AI tools: ChatGPT, used to debug a pandas error and to suggest the class_weight

setting, which we read about in the scikit-learn documentation before using it

Page 4 of 4
