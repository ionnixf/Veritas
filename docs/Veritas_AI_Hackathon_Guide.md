| VERITAS AI |     |     | HACKER GUIDE · 2026 |
| ---------- | --- | --- | ------------------- |
THE OFFICIAL PARTICIPANT GUIDE
Veritas AI
International High
School Hackathon
> 48 hours. One AI project. Built from scratch.
| Nov 14–15 | 48 hrs | 1–3 | Free |
| --------- | ------ | --- | ---- |
Hacking weekend (ET) On the clock Hackers per team Fully virtual, worldwide
highschoolhackathon.org Finals & awards
Questions? contact@veritasai.com Saturday, November 21, 2026

WELCOME, BUILDER
Hey, and welcome to the first
Veritas AI International High
School Hackathon!
On November 14 and 15, high schoolers from all over the world will spend one
weekend building AI projects from scratch, and we're really glad you're one of
them.
This guide walks you through everything: what to set up before Saturday, how to pick an
idea you can actually finish, the tools and datasets worth using, how judging works, and
what to submit.
Never built anything with AI? Totally fine. Plenty of great hackathon projects come from
first-timers who picked a small problem and saw it through. If you're new, start with
sections 2 and 7 and catch both workshop recordings. If you've trained models before,
sections 8 and 9 on judging and submission are where to spend your time.
Keep this guide open all weekend and tick off the checklists as you go. Got a question? Email
us at contact@veritasai.com. We're happy to help.
See you at kickoff,
The Veritas AI team
IN THIS GUIDE
01 Key dates and format 07 Learning resources
02 Before the hackathon 08 Judging
03 Choosing your project 09 Submitting your project
04 Planning your 48 hours 10 Rules and responsible AI
05 Tools 11 After the hackathon
06 Datasets 12 Frequently asked questions
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 1

Key dates and format
01
Hacking runs all day Saturday, November 14 and Sunday, November 15 (ET). The challenge
briefs for each track drop live at the kickoff call, so everyone starts at exactly the same
moment.
Format Free and fully virtual, open to high school students anywhere in the world
Teams Individuals or teams of up to 3. Teammates can be from different schools and
countries
Tracks AI + Health, AI + Finance, AI + Climate, and others listed on the hackathon
website. You choose your track at kickoff
Submission Working code, a short write-up and a demo video of up to 2 minutes
Judging Round 1 is reviewed blind by our team. Finalists present live to a panel of AI
researchers
Awards An AI internship with a partner AI company for the Gold team, scholarships of up
to 100% to Veritas AI programs, category awards for Best Beginner Build, Best AI
for Good and Judges' Choice, and Merit Awards. Scholarships are awarded to each
member of a winning team. Every participant who submits receives a certificate,
and winning projects are featured on veritasai.com
Key dates
Oct 5 Registration opens
Oct 17 Workshop 1: Intro to Google Colab
Nov 1 Workshop 2: How to Scope a Weekend AI Project
Nov 13 Registration closes at 11:59 PM ET, and the pre-event kit arrives
Nov 14–15 Hackathon weekend
Nov 18 Finalists announced
Nov 21 Live finals and awards ceremony
Dec 6 Last day for award winners to claim scholarships (11:59 PM ET)
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 2

Before the hackathon
02
Get your setup sorted before Saturday so the whole weekend can go to building. Try to get
through this checklist by Friday, November 13.
Setup checklist
Sign in to Google Colab and run a single cell to check it works
Create a GitHub account. Students can also get free tools through the GitHub Student
Developer Pack
Create a Kaggle account for datasets and free notebooks
Create a Hugging Face account for pretrained models and free app hosting
Test a screen recorder with your microphone (see section 5)
Complete your team's registration with every teammate listed. You can edit it until
registration closes on November 13 at 11:59 PM ET
Attend or watch Workshop 1 (Intro to Google Colab, October 17) and Workshop 2 (How
to Scope a Weekend AI Project, November 1). Recordings are emailed to all registrants
Open the pre-event kit when it arrives on Friday evening. It includes the starter
notebooks, the submission checklist and the kickoff link
Planning as a team
Hacking with friends? Agree on a few things before the clock starts:
Roles. For a team of three, it often works well for one person to focus on the data, one on
the model, and one on the demo and write-up
How you'll stay in touch, for example a group chat and one video call link you all use
Where your code will be kept. A single shared Colab notebook or GitHub repository
means everyone works from the same version
When you'll sleep. Seriously, plan it now
What's fine to do before kickoff
Go ahead and learn the tools, play around with the starter notebooks, and browse datasets
for the tracks you're eyeing. Just save the actual building for the weekend itself.
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 3

Choosing your project
03
Two days goes by fast, so pick an idea small enough to get working by Saturday night.
Judges need to see your project running, and you can always add to it on Sunday.
A QUICK TEST FOR ANY IDEA
Before you start coding, try completing this sentence:
“Our project helps [a specific person] by taking [an input] and giving back
[an output].”
If you can't fill in all three parts, the idea probably needs more thought.
Questions to ask about an idea
1. Is there data you can use? If you can't find a suitable dataset within about 30
minutes, it's usually better to pick another idea. Building a dataset from scratch takes up
most of a weekend.
2. Can a simple model make progress on it? Start with something straightforward,
such as a logistic regression, a small decision tree or a pretrained model from Hugging
Face.
3. Can you demonstrate it in two minutes? A judge should be able to watch an input
go in and a result come out.
4. Who would it help? Be ready to explain who would use it and why.
Examples of scoping an idea
TOO BROAD FOR A WEEKEND A REALISTIC VERSION
"An AI doctor that diagnoses A model that flags possible pneumonia on chest X-rays from one
any disease" public dataset, with its accuracy and the cases it gets wrong
"Predict the stock market" A test of whether news-headline sentiment helps predict next-
day price moves for five stocks, reported honestly either way
"Solve climate change with A forecast of tomorrow's solar output for one region from
AI" weather data, compared against a simple baseline
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 4

TOO BROAD FOR A WEEKEND A REALISTIC VERSION
"A chatbot for mental health" A mood journal that tags entries by emotion using a pretrained
classifier and charts the week
Project ideas
These are based on projects Veritas AI students have built before. Use them for inspiration,
but the challenge brief you receive at kickoff comes first.
| Health |     | Finance |
| ------ | --- | ------- |
Classify chest X-rays or images of skin Forecast cryptocurrency returns against a
lesions, predict hospital readmissions from buy-and-hold baseline, detect unusual card
patient data, or recognise sign language transactions, or build a loan-risk model and
| from webcam images |     | check it for bias |
| ------------------ | --- | ----------------- |
| Climate            |     | Other areas       |
Predict solar or wind generation from Predict match results from sports statistics,
weather data, forecast a building's energy apply art styles to photos with computer
use, or detect deforestation or changes in vision, or test whether AI-generated music
| water quality from satellite images |     | affects listeners' mood |
| ----------------------------------- | --- | ----------------------- |
Some of the most memorable projects come from something the team genuinely cares about,
like air quality in your city, a clinic near you, or a sport you play.
Planning your 48 hours
04
Here's a rough game plan. Aim to have a basic version working end to end by Saturday
night, then use Sunday to make it better and get your submission ready. Adjust it however
suits you or your team.
| WHEN | GOAL | DONE WHEN |
| ---- | ---- | --------- |
Sat · first 2 hrs Read the brief, choose an idea Your idea passes the one-sentence test and
|     | and find a dataset | the data loads in your notebook |
| --- | ------------------ | ------------------------------- |
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026  ·  HACKER GUIDE 5

WHEN GOAL DONE WHEN
Sat · midday Explore the data and build a You have a simple result to beat, such as
baseline always predicting the most common class
Sat · afternoon Train your first model It beats the baseline, and you've noted by
how much
Sat · evening Connect input to output Someone can enter new data and see a result,
even if it looks rough
Sat · night Sleep At least 7 hours. Your Sunday self will thank
you
Sun · morning Make one improvement One change is made, such as better features,
a different model or cleaner data, and its
effect is measured
Sun · midday Prepare the demo The demo runs from start to finish without
any fixes
Sun · afternoon Write up and record The write-up is finished and the demo video
is uploaded
Sun · final 2 hrs Submit Your project is submitted, with time left for
small fixes
Tips for the weekend
Stop adding new features about six hours before the deadline, and use the remaining
time for fixes and your submission
Save your work regularly, either by committing to GitHub or saving a copy of your Colab
notebook every couple of hours
Keep brief notes on what you tried and how it went. They'll make the write-up much
easier
If you've been stuck on the same problem for 30 minutes, ask a mentor for help, simplify
your approach or try a different dataset. Don't lose hours to one bug
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 6

Tools
05
Everything here is free to get started with. Pick one setup and stick with it for the weekend,
so you're building instead of learning a new tool from zero.
Recommended setups
EXPERIENCE WHERE TO CODE MODEL TOOLS DEMO
New to Google Colab with the Teachable Machine, which A screen recording of the
coding starter notebooks needs no code, for image, model working
sound or pose models
Some Google Colab scikit-learn for tabular data A simple interface built
Python and pandas for cleaning it with Gradio inside Colab
Built Colab or Kaggle PyTorch or Hugging Face An app hosted on
models Notebooks with a free Transformers with Hugging Face Spaces or
before GPU, plus a GitHub pretrained models Streamlit
repository
Pretrained models and AI APIs
The Hugging Face Hub has thousands of pretrained models for text, images and audio.
Fine-tuning an existing model is usually much faster than training one from scratch
Google AI Studio provides Gemini API keys with a free tier
The Claude and OpenAI APIs are paid, but are an option if your team already has access
If your project uses an AI API, judges will be most interested in what you've built around
it, such as your data, how you evaluated the results and your interface
Computing power Recording your demo
Google Colab and Kaggle both offer free Use OBS Studio (free on all platforms),
GPU time, which is enough for most Loom or your computer's built-in recorder.
hackathon projects. Upload to YouTube as unlisted, or to Google
Drive with "anyone with the link can view".
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 7

Datasets
06
These public sources are a great place to start hunting for data. Before you commit to a
dataset, check its licence and make sure it isn't too big to work with in a weekend.
Working with your data: look through a sample of rows or images yourself before
training anything, since it's the easiest way to spot missing or mislabelled data. Split
your data into training and test sets before you start tuning, and don't use the test set for
tuning. Cite every dataset you use in your write-up, with a link.
TRACK SOURCE GOOD FOR
Any Kaggle Datasets Ready-to-use CSVs and images, often with example
notebooks
Any Hugging Face Datasets Text, image and audio datasets that load in one line
of code
Any UCI Machine Learning Repository Small, clean tabular datasets, ideal for first models
Any Google Dataset Search Finding a dataset on a niche topic
Any Our World in Data Country-level data on health, energy, poverty and
more
Health MedMNIST Small, standardised medical image sets (X-rays,
pathology, skin) that train fast
Health Chest X-Ray Images (Pneumonia) A classic first image classifier
Health UCI Heart Disease Tabular risk prediction
Health WHO Global Health Observatory Global health indicators by country
Finance FRED Interest rates, inflation, unemployment and other
economic time series
Finance yfinance Historical stock prices in Python (unofficial, fine for
learning)
Finance Credit Card Fraud Detection Imbalanced classification, a good test of honest
evaluation
Finance World Bank Open Data Development and economic data by country
Climate NASA POWER Solar radiation and weather by location, built for
renewable energy work
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 8

TRACK SOURCE GOOD FOR
Climate Open-Meteo Free weather forecast and historical weather API, no
key needed
Climate OpenAQ Air quality readings from monitors worldwide
Climate Climate TRACE Greenhouse gas emissions by sector and facility
Climate Global Forest Watch Deforestation and land-use data
Learning resources
07
You've got about five weeks between registration opening and kickoff. Pick the level that
sounds like you and work through the list in order. Everything here is free.
Beginner: new to machine learning
1. Veritas AI Workshop 1, Intro to Google Colab (October 17). The recording is emailed to
all registrants
2. Kaggle Learn: Python, followed by Intro to Machine Learning. Both are short, hands-on
courses that run in your browser
3. 3Blue1Brown: Neural Networks, a clear visual explanation of how neural networks learn
4. Teachable Machine, which lets you train an image model in a few minutes without
writing code
5. The starter notebooks in your pre-event kit
Intermediate: some Python and a first model
1. Veritas AI Workshop 2, How to Scope a Weekend AI Project (November 1), and its
planning template
2. Google Machine Learning Crash Course
3. Kaggle Learn: Pandas and Intermediate Machine Learning
4. scikit-learn tutorials
5. Harvard CS50's Introduction to AI with Python
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 9

Advanced: ready to go further
1. fast.ai Practical Deep Learning for Coders
2. PyTorch tutorials
3. Hugging Face courses on language models, fine-tuning and more
4. Andrej Karpathy: Neural Networks: Zero to Hero
For everyone: if you're working in a team, GitHub Skills is a quick way to learn Git
and GitHub through short interactive exercises. It makes working on the same code
together much easier.
Judging
08
Projects are scored on four criteria: technical quality, impact, creativity and clarity. Round 1
is reviewed blind by our team, so reviewers see your project but not your name or school.
Finalists then present live to a panel of AI researchers.
CRITERION WHAT JUDGES LOOK FOR HOW TO SHOW IT
Technical Whether the project works, the Compare against a baseline, report results
quality approach is sound and it was tested on test data the model hasn't seen, and
fairly show where it fails
Impact Whether it addresses a real problem Explain who it helps and what would
for real people change for them
Creativity Whether it takes a fresh approach Apply a known technique to an unusual
rather than repeating a standard dataset, question or group of users
tutorial
Clarity Whether a judge can understand the A clear demo, a concise write-up and one
project in two minutes main takeaway
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 10

What makes a project stand out Common mistakes to avoid
They're open about their limitations. For Results that look too good to be true,
example, "our model is 84% accurate, which often means test data has leaked
but it misses many cases in darker skin into training
tones because the dataset includes few
Reusing a tutorial dataset without
of them" is more convincing than an
asking a new question of it
unexplained 99%
A write-up that lists the tools used but
They compare their results against a
not what the team learned
simple baseline
Links that judges can't open. Check your
The demo runs reliably from start to
sharing settings in a browser where
finish
you're logged out
They explain the reasoning behind their
choices: why this problem, this model
and these results
Submitting your project
09
Submissions close on Sunday, November 15 at [time ET]. One person submits for the whole
team, and you'll need three things: working code, a short write-up and a demo video.
Submission checklist
Your code, as a Colab notebook or GitHub repository that anyone with the link can view.
Test the link in a browser where you're logged out
A short write-up covering the problem, your approach, your results and what didn't
work, using the template below
A demo video of up to two minutes, uploaded to YouTube as unlisted or shared from
Google Drive
The names of all team members
Citations for every dataset, model and code source you used
Write-up template
You can copy this into your README or the submission form.
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 11

# Project name
**Track:** Health / Finance / Climate / ...
**Team:** names
## The problem
Who has this problem, and why does it matter? (2-3 sentences)
## What we built
What goes in, what comes out, and how someone would use it.
## How it works
Data: which dataset, how many examples, how we cleaned it.
Model: what we used and why.
## Results
Our baseline scored X. Our model scored Y on held-out test data.
Where it fails, and why we think so.
## What we'd do next
One or two concrete next steps with more time.
## Sources
Datasets, pretrained models, tutorials and AI tools used, with links.
Demo video
This structure works well for a two-minute video:
1. The problem (about 15 seconds): who it's for and why it matters
2. The demo (about 60 seconds): a real input going in and the result coming out
3. How it works (about 30 seconds): your data, your model and how it compares to the
baseline
4. Next steps (about 15 seconds): one limitation and what you'd do next
A screen recording with your voice over it is all you need. It helps to write a short script first,
and there's no need to spend long on editing.
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 12

THE FINALS
Made the finals? Congrats! Finalists are announced on November 18 and demo live on
November 21. Each team gets five minutes to present, followed by questions from the
judges.
Follow the same structure as your video, with more time on the demo and your
results
Run the demo live if it's reliable, and keep a recorded version open as a backup
Be ready for questions such as "How do you know it works?", "What would cause it
to fail?" and "Who would use this?"
If you're in a team, agree beforehand who will answer which kinds of questions
Rules and responsible AI
10
The rules are simple: build your project during the weekend, credit anything you didn't
make yourself, and be honest about your results.
Using AI tools
You may use coding assistants and AI chatbots while you build, as long as your team
understands every part of the project and can explain it to the judges. Please list any AI tools
you used in your write-up.
Crediting sources
Public datasets, pretrained models, open-source libraries and tutorial code are all allowed,
as long as they're cited. Submitting someone else's project as your own will lead to
disqualification.
Building responsibly
Use public or synthetic data, and don't collect anyone's personal information without
their permission
Check whether your model performs equally well across different groups, and say so if it
doesn't
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 13

Make clear that health and finance projects are prototypes, not medical or financial
advice
Report the results you actually achieved, including any that were disappointing
Teams
Teams can have one to three high school students. Anyone on the team can work on any part
of the project, and everyone listed should have contributed.
After the hackathon
11
Submitting is just the start. Here are a few ways to keep going with what you've built:
Tidy up your GitHub repository, add your write-up as the README and pin it to your
profile, so you can link to it in applications
Share your certificate on LinkedIn and tag Veritas AI
Use the judges' feedback to plan a second version, with more data, a stronger evaluation
or testing with real users
Enter Singularity, the Veritas AI essay contest, which opens on November 15 and closes
on February 7
Continue your project as independent research through a Veritas AI program, working
one-on-one with a mentor from a top graduate program. Award winners have until 11:59
PM ET on December 6 to claim their scholarships
Frequently asked questions
12
Do I need AI or coding experience?
No. The workshops, starter notebooks and this guide are built for first-timers, and there's a
Best Beginner Build award.
Does it cost anything?
No. Registration is free.
Can my teammates be from other schools or countries?
Yes. Teams are 1 to 3 high school students from anywhere.
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 14

Do I need to pick a track when I register?
No. Challenge briefs are revealed at kickoff, and you choose then.
What if I miss the kickoff call?
The recording and the challenge briefs are emailed to all registrants right after.
Is the internship remote?
Yes.
Can I keep working on my project after submitting?
Yes, but judges only see what you submitted by the deadline.
Who do I contact?
Email contact@veritasai.com or visit highschoolhackathon.org.
Veritas AI International High School Hackathon 2026 Good luck, and happy hacking.
highschoolhackathon.org The Veritas AI team
VERITAS AI INTERNATIONAL HIGH SCHOOL HACKATHON 2026 · HACKER GUIDE 15
