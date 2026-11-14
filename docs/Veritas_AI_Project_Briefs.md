VERITAS AI · International High School Hackathon 2026 Project Briefs
VERITAS AI
INTERNATIONAL HIGH SCHOOL HACKATHON 2026
Project Briefs
Everything your team needs to pick a track, build something real and
submit it this weekend.
HACKING STARTS SUBMISSIONS CLOSE SUBMIT HERE QUESTIONS?
Sat, Nov 14, 12:00 AM ET Sun, Nov 15, 11:59 PM ET Submission form contact@veritasai.com
CONTENTS
1 Welcome and overview 2
2 The rules 3
3 What every project should show 4
4 The tracks 5
4.1 AI + Health 5
4.1.1 Pneumonia screening from chest X-rays 5
4.1.2 Heart disease risk from checkup data 6
4.1.3 Country-level health risk 7
4.1.4 Your own idea 7
4.2 AI + Finance 8
4.2.1 Scam text filter 8
4.2.2 Card fraud detection 9
4.2.3 Fairness audit of a loan model 9
4.2.4 News headlines and the stock market 10
4.2.5 Your own idea 10
4.3 AI + Climate 12
4.3.1 Next-day solar energy forecast 12
4.3.2 Next-day air quality forecast 13
4.3.3 Land-use mapping from satellite images 13
4.3.4 Your own idea 14
4.4 AI + Languages 15
4.4.1 Language identification 15
4.4.2 Translation quality test 16
4.4.3 Speech recognition across accents 16
4.4.4 Your own idea 17
5 How to submit 18
6 How judging works 20
7 Frequently asked questions 21
highschoolhackathon.org Page 1 of 22

VERITAS AI  ·  International High School Hackathon 2026 Project Briefs
1 Welcome and overview
Welcome to the hackathon! This weekend, your team picks one of the four tracks below, builds one
working AI project, and submits it through the submission form by 11:59 PM ET on Sunday,
November 15.
Each track brief explains the challenge and what your project needs to include, then gives you three or
four suggested projects with datasets and step-by-step instructions. You don't have to use the
suggested projects. If you follow one, you'll end up with a working baseline, and teams that build on that
baseline with something of their own are more likely to win higher awards (more on this in section 3).
You're welcome to build any project that meets your track's challenge.
There's no kickoff call and nothing you need to attend live this weekend. You'll find everything you need in
this document and the Hacker Guide.
A quick heads-up: our team can't give technical help during the hackathon, such as debugging code, fixing
errors or choosing a model. The only thing we can help with is your submission, so if something goes wrong
when you submit, email contact@veritasai.com.
Key times
| Where you are   |     | Hacking starts        | Submissions close     |
| --------------- | --- | --------------------- | --------------------- |
| US Eastern (ET) |     | Sat, Nov 14, 12:00 AM | Sun, Nov 15, 11:59 PM |
| US Pacific (PT) |     | Fri, Nov 13, 9:00 PM  | Sun, Nov 15, 8:59 PM  |
| London          |     | Sat, Nov 14, 5:00 AM  | Mon, Nov 16, 4:59 AM  |
| UAE             |     | Sat, Nov 14, 9:00 AM  | Mon, Nov 16, 8:59 AM  |
| India           |     | Sat, Nov 14, 10:30 AM | Mon, Nov 16, 10:29 AM |
Singapore and China Sat, Nov 14, 1:00 PM Mon, Nov 16, 12:59 PM
| South Korea |     | Sat, Nov 14, 2:00 PM | Mon, Nov 16, 1:59 PM |
| ----------- | --- | -------------------- | -------------------- |
| Sydney      |     | Sat, Nov 14, 4:00 PM | Mon, Nov 16, 3:59 PM |
The four tracks
| Track | Your challenge |     | Suggested projects |
| ----- | -------------- | --- | ------------------ |
AI + Health Help one specific person catch a health Pneumonia screening from chest X-rays;
problem sooner, or manage one better heart disease risk from checkup data;
country-level health risk
AI + Finance Help a person or small business make a Scam text filter; card fraud detection; fairness
safer or fairer money decision audit of a loan model; news headlines and the
stock market
highschoolhackathon.org Page 2 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Track Your challenge Suggested projects
AI + Climate Help a community, city or energy system Next-day solar forecast; next-day air quality
measure, predict or reduce its climate forecast; land-use mapping from satellite
impact images
AI + Languages Help people understand each other, learn Language identification; translation quality
a language or be understood test; speech recognition across accents
Project levels
Each suggested project has a level, so pick one that matches your team's experience. Beginner projects
can win awards too, including Best Beginner Build.
Level Pick this if your team… Tools we recommend
Beginner has never coded, or knows only the basics Teachable Machine (no code) or Google
Colab with the starter notebooks
Intermediate can write some Python Google Colab, pandas, scikit-learn, Gradio
Advanced has trained models before PyTorch or Hugging Face Transformers, with a
free GPU on Colab or Kaggle
2 The rules
We've kept the rules short. Please give them a quick read before you start.
1. Teams. Each team has one to three high school students. Your teammates can come from different
schools and countries, and everyone you list on the submission needs to have contributed.
2. Build during the weekend. Your team needs to do all project work between the start time and the
deadline. You're welcome to learn tools, run the starter notebooks and browse datasets beforehand,
but you can't extend a project you built before the hackathon.
3. AI must be central. Your project needs to use AI or machine learning to do its main job. If you build a
regular website or app with AI coding tools, that doesn't count on its own.
4. What you can use. You can use public datasets, pretrained models, AI APIs (such as the free tier of
the Gemini API), open-source libraries, tutorial code, and coding assistants or chatbots. Just cite all of
them in your write-up. Your team should understand every part of the project and be ready to explain
it to the judges.
5. What you can't do. If you submit someone else's project as your own, we'll have to disqualify your
team. Please don't collect anyone's personal information without their permission, and stick to public
or synthetic data.
6. One project per team, one track per project. You'll choose your track on the submission form. You can
resubmit as many times as you like before the deadline, and judges will look at your latest version.
7. Disclaimers. If you build a health or finance project, say in your write-up that it's a prototype and not
medical or financial advice.
8. Honest results. Report the results you actually got, including weak ones.
highschoolhackathon.org Page 3 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
3 What every project should show
Whatever track you pick, your write-up and demo should answer these four questions.
1. Who is it for? Name one specific user and the moment they'd reach for your tool.
2. What goes in, and what comes out? Show judges a real input producing a result.
3. Does it beat a simple baseline? A baseline is the simplest possible guess, like always predicting the
most common answer. For example, if 87% of messages aren't spam, a "model" that labels everything
"not spam" is already 87% accurate. Report your baseline's score next to your model's score, so judges
can see how much your model actually adds.
4. Where does it fail? Show at least one example your model gets wrong and explain why you think that
happens.
Make sure all your results come from test data your model didn't see during training.
Make it your own
If you follow a suggested project in section 4, you'll reach a working baseline. Teams that stop there
still have a complete submission and judges will score it, but it will land toward the lower end of the
range. Teams that add at least one thing of their own score higher:
Your own user or setting. Pick a specific person, place or community, and design the tool around
how they'd use it.
Your own data. Use a different or local dataset, data you collected with permission, or test on data
from a new source.
Your own question. Ask something the brief doesn't, like when the model fails, who it fails for, or
whether it holds up in a new situation.
You'll find ideas at the end of each suggested project. Tell us what you added in your write-up and on
the submission form.
Suggested schedule
Here's a rough plan to keep your team on track.
By Where you should be
Saturday, first 2 hours You've picked your track and idea, and your data is loading in your
notebook
Saturday evening Your baseline and first model work: an input goes in and a result comes
out
Sunday midday You've made and measured one improvement, and your demo runs
from start to finish
Sunday, 2 hours before the Your write-up is done, your video is uploaded and your project is
deadline submitted
If you can't get your data loading within about 30 minutes, switch to another dataset or idea. That's a smart
move, not a setback.
highschoolhackathon.org Page 4 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4 The tracks
Each track below has its own challenge, a short list of what your project needs, and three or four
suggested projects. Pick one track and build one project for it.
4.1 AI + Health
Your challenge. Build an AI tool that helps one specific person catch a health problem sooner, or
manage an ongoing one better.
Doctors, nurses and community health workers often have more patients than time. When a tool flags
the most urgent cases or estimates risk from routine measurements, they can decide where to look first.
Design your project around one user, such as a doctor, nurse, patient, parent or public health worker.
What your project needs
Name your user and explain how they'd use your tool.
Report missed cases (false negatives) and false alarms (false positives) separately, not just overall
accuracy.
Include this line in your write-up: "This project is a prototype and is not medical advice."
Use public datasets only. Please don't use real patient records, even ones you can access through
family, school or work.
PROJECTS
4.1.1 Pneumonia screening from chest X-rays
LEVEL DATA DATASETS TOOLS
Beginner Images PneumoniaMNIST, Chest X-Ray Teachable Machine, or Google
Images (Pneumonia) Colab with PyTorch
Goal. Build a model that labels a chest X-ray as normal or pneumonia, so doctors can review urgent
scans first.
Getting to a baseline
1. Choose your route. If you've never coded, download the Kaggle dataset and use Teachable Machine.
If you know some Python, use PneumoniaMNIST in Colab (pip install medmnist). It comes already
split into training, validation and test sets.
2. Teachable Machine route: Create an Image Project with two classes, Normal and Pneumonia. Upload
about 100 images to each class from the train folder and click Train. Then test your model on images
from the test folder, which it hasn't seen, and record how many it gets right in each class.
3. Python route: Train a small convolutional neural network, or fine-tune a pretrained model such as
ResNet-18. If you use the Kaggle version, skip its val folder (it only has 16 images) and take a validation
set from train instead.
4. Compare your model with a baseline that predicts pneumonia for every image. The training data has
about three pneumonia images for every normal one, so this baseline gets a high accuracy score
even though it's useless.
highschoolhackathon.org Page 5 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
5. Report recall for pneumonia (the share of real pneumonia cases your model catches) and the
number of false alarms.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Pick a real setting, such as a rural clinic with no radiologist, and design the tool around how staff
there would use it.
Test whether your model still works on X-rays from a different source than the one you trained it on.
Decide how your tool should handle scans it's unsure about, and explain why you chose that.
4.1.2 Heart disease risk from checkup data
LEVEL DATA DATASETS TOOLS
Intermediate Tabular UCI Heart Disease Google Colab, pandas, scikit-learn,
Gradio
Goal. Predict whether a patient is likely to have heart disease from routine checkup measurements, and
show which measurements matter most.
Getting to a baseline
1. Load the Cleveland data: about 300 patients and 13 measurements such as age, resting blood
pressure and cholesterol. In Colab, run pip install ucimlrepo and load it with fetch_ucirepo(id=45).
2. The target column num runs from 0 (no disease) to 4. Convert it to two classes: 0 for no disease and 1
for any disease.
3. A few rows have missing values in the ca and thal columns. Drop or fill them, and note which you
did.
4. Split the data into training and test sets (for example 80/20), then train a logistic regression. Compare
it with a baseline that always predicts the most common class.
5. Report accuracy and recall, and use your model's coefficients to list the most important
measurements.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Test whether a model you trained on the Cleveland patients works on the dataset's other hospitals
(Hungary, Switzerland and Long Beach).
Design how a nurse or patient would actually use the risk score, and try your design out with a real
person.
Check whether your model works equally well for men and women and across age groups, and
what you'd change if it doesn't.
highschoolhackathon.org Page 6 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.1.3 Country-level health risk
LEVEL DATA DATASETS TOOLS
Advanced Tabular, by WHO Global Health Observatory, Google Colab, pandas, scikit-learn,
country and year Our World in Data Plotly
Goal. Predict which countries are most at risk for one health outcome, such as child mortality or measles
cases, so aid organisations know where to focus.
Getting to a baseline
1. Pick one outcome and five or six indicators you think might predict it, such as vaccination coverage,
access to clean water or income per person. You can download any Our World in Data chart as a CSV
file.
2. Merge the tables by country and year. You'll likely find missing values, so note how you handle them.
3. Train on earlier years and test on the most recent years. Don't split the rows randomly, because that
lets your model learn from the future.
4. Compare your model with a baseline that assumes this year's value equals last year's.
5. Report the error for your model and the baseline, and list the ten countries your model rates as
highest risk.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Pick an outcome or region that matters to your team, and explain who would act on your
predictions.
Test whether your model would have flagged a real past outbreak or crisis before it happened.
Show how missing or unreliable data in some countries changes your conclusions.
4.1.4 Your own idea
You can build any project that meets the challenge. For example, you could build sign language
recognition from webcam images, a mood journal that tags entries with a pretrained emotion classifier,
or a tool that reads medicine labels aloud. Hugging Face Datasets and Kaggle are great places to find
data.
What judges look for in this track
Judges score every project on technical quality, impact, creativity and clarity (see section 6). In this
track, judges pay extra attention to how clearly you identify your user, how honestly you report
missed cases and false alarms, and whether you checked that your model works equally well across
groups such as age, sex or, for skin images, skin tone.
highschoolhackathon.org Page 7 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.2 AI + Finance
Your challenge. Build an AI tool that helps a person or a small business make a safer or fairer
money decision, and show that it beats a simple rule.
Software now makes many financial decisions, such as approving a card payment, filtering a message
or granting a loan, often with little explanation. In this track, your project should protect the person whose
money is at stake. Plenty of finance models look impressive but do worse than a simple rule, so a fair
comparison with a baseline is essential.
What your project needs
Compare your model with at least one simple baseline and report both results.
Choose a measure that fits the problem. For rare events such as fraud, report precision and recall
rather than accuracy.
If your data has dates, train on earlier data and test on later data.
Include this line in your write-up: "This project is a prototype and is not financial advice."
PROJECTS
4.2.1 Scam text filter
LEVEL DATA DATASETS TOOLS
Beginner Text SMS Spam Collection (also on Google Colab, scikit-learn
Hugging Face)
Goal. Build a filter that flags whether a text message is spam or a scam, so people think twice before
opening a link.
Getting to a baseline
1. Load the SMS Spam Collection: 5,574 English text messages, each labelled spam or ham (not spam).
About 13% are spam.
2. Split into training and test sets with the same share of spam in each (use stratify in scikit-learn's
train_test_split).
3. Turn the messages into features with TfidfVectorizer, then train a logistic regression or naive Bayes
classifier.
4. Compare your model with a baseline that labels every message "not spam". That baseline is about
87% accurate but catches nothing.
5. Report precision and recall for spam, and show five messages your model gets wrong.
Make it your own (required)
Add at least one thing of your own. A few ideas:
These messages were collected more than ten years ago. Collect or write examples of scams that
are common in your country or language today, and test whether your model catches them.
Have your filter explain why it flagged a message, so people learn to spot scams themselves.
Design for a specific user, such as an elderly relative, and test the tool with them.
highschoolhackathon.org Page 8 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.2.2 Card fraud detection
LEVEL DATA DATASETS TOOLS
Intermediate Tabular Credit Card Fraud Detection Google Colab, pandas, scikit-learn
Goal. Flag card transactions that are likely to be fraud, so a bank can review them before approving the
payment.
Getting to a baseline
1. Download the dataset from Kaggle (you'll need a free account). It contains 284,807 transactions
made by European cardholders over two days in 2013, and 492 of them are fraud.
2. Most columns (V1 to V28) are anonymised for privacy. You also have Time, Amount and the label
Class (1 for fraud).
3. Watch out for the baseline: if you predict "not fraud" every time, you'll be 99.8% accurate and catch no
fraud at all. So don't use accuracy as your main measure.
4. Train a logistic regression with class_weight="balanced", then a tree-based model such as a random
forest.
5. Report precision, recall and the area under the precision-recall curve on the test set.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Pick a decision threshold based on the cost of missed fraud versus wrongly blocked cards, and
explain your choice.
Test whether fraud patterns change over the two days, and what that would mean for a model a
bank actually uses.
Make each flag easy to understand for a bank employee who has to decide whether to block the
card.
4.2.3 Fairness audit of a loan model
LEVEL DATA DATASETS TOOLS
Intermediate Tabular Statlog German Credit Google Colab, pandas, scikit-learn
Goal. Build a model that classifies loan applicants as good or bad credit risks, then test whether it treats
groups of applicants differently.
Getting to a baseline
1. Load the dataset with fetch_ucirepo(id=144) (pip install ucimlrepo). It has 1,000 applicants and 20
attributes such as age, employment, savings and loan purpose. 700 are labelled good risks and 300
bad.
2. Train a simple model and compare its accuracy with a baseline that approves every applicant.
3. Compare your model's approval rates for two groups, for example applicants under 25 and
applicants aged 25 or older.
4. If you find a gap, figure out which features drive it.
5. Report accuracy, the approval rate for each group, and the gap between them.
highschoolhackathon.org Page 9 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Make it your own (required)
Add at least one thing of your own. A few ideas:
Find which features act as stand-ins for age or other personal details, even after you remove those
columns.
Propose and test a change that narrows the gap, and report what it costs you in accuracy. The
dataset's documentation treats approving a bad risk as five times as costly as rejecting a good
one, which you can use in your evaluation.
Compare the dataset's assumptions with how lending works in your own country.
4.2.4 News headlines and the stock market
LEVEL DATA DATASETS TOOLS
Advanced Text and time Daily News for Stock Market Google Colab, pandas, Hugging
series Prediction, yfinance, FRED Face Transformers
Goal. Test whether each day's top news headlines tell you anything about the direction of the Dow Jones
Industrial Average, and report the answer honestly, even if it's "not really".
Getting to a baseline
1. Use the file Combined_News_DJIA.csv. It has one row per trading day from August 2008 to July 2016, with
the top 25 world news headlines and a label (1 if the index rose or stayed the same, 0 if it fell).
2. Split by date, never at random. Train on 2008 to 2014 and test on 2015 to 2016.
3. Score each day's headlines for sentiment with a pretrained model, such as FinBERT on Hugging Face
or VADER in NLTK, and use the scores as features.
4. Compare your model with two baselines: one that always predicts "up", and one that predicts the
same direction as the previous day.
5. Report accuracy on the test period for your model and both baselines.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Test a different market, time period or news source, for example individual stocks from yfinance or
indicators from FRED.
Ask whether some kinds of headlines matter more than others, and test it.
Say clearly what your results would and wouldn't justify an investor doing. If your results look far
better than the baselines, first check that no later dates leaked into training.
4.2.5 Your own idea
You can build any project that meets the challenge. For example, you could build a budgeting assistant
for teenagers with their first debit card, an inflation tracker for your city, or a tool that explains bank fees
in plain language. World Bank Open Data and Kaggle are great places to find data.
highschoolhackathon.org Page 10 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
What judges look for in this track
In this track, judges pay extra attention to whether you chose the right measure of success, whether
you compared your model fairly against a simple baseline, and whether a real person could trust
your tool enough to act on it. Teams that check for unfair treatment of a group, even when age or
gender isn't a direct input, really stand out.
highschoolhackathon.org Page 11 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.3 AI + Climate
Your challenge. Build an AI tool that helps a community, a city or an energy system measure,
predict or reduce its climate impact.
People make most climate-related decisions locally and day to day: a grid operator decides how much
backup power to keep ready, a school decides whether to hold sports practice outdoors, and forest
rangers decide where to patrol. Pick one place, ideally one you know, and one person who would use your
tool. You can test a forecast for a specific city, but you usually can't test one for "the world".
What your project needs
Focus on one location or region.
For forecasts, train on earlier dates and test on later ones. Never shuffle days together.
Compare your model with the persistence baseline: "tomorrow will be the same as today."
Explain what decision your prediction supports and who makes it.
PROJECTS
4.3.1 Next-day solar energy forecast
LEVEL DATA DATASETS TOOLS
Beginner Tabular weather NASA POWER, Open-Meteo Google Colab, pandas, scikit-learn
data
Goal. Predict tomorrow's solar energy for one location from today's weather, so a solar farm or a
household battery can plan ahead.
Getting to a baseline
1. Open the NASA POWER Data Access Viewer, choose your location and select daily data. Download
several years of solar radiation (ALLSKY_SFC_SW_DWN, measured in kWh/m² per day), together with
temperature, cloud amount and humidity, as a CSV file. You won't need any code for this step.
2. Load the file in Colab and create your target, tomorrow's solar radiation, with
df["target"] = df["ALLSKY_SFC_SW_DWN"].shift(-1).
3. Keep the most recent year as your test set and train on the years before it.
4. Calculate the baseline (tomorrow equals today), then train a linear regression on today's weather.
5. Report the mean absolute error for the baseline and for your model. This baseline is hard to beat, so
any improvement you make is a real result.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Forecast for your own city, or compare how predictable solar output is in two very different climates.
Turn your forecast into a decision a real household, school or solar farm would make, and measure
how good those decisions are.
Find out how far ahead your forecast stays useful: one day, three days or a week.
highschoolhackathon.org Page 12 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.3.2 Next-day air quality forecast
LEVEL DATA DATASETS TOOLS
Intermediate Time series OpenAQ (free API key), Open-Meteo Google Colab, pandas, scikit-learn
Goal. Forecast tomorrow's average fine particle pollution (PM2.5) for one city, so schools and families
know when to limit time outdoors.
Getting to a baseline
1. Register for a free OpenAQ API key (it only takes a few minutes). Choose one monitoring station with
at least a year of mostly complete PM2.5 readings.
2. Convert the hourly readings into daily averages.
3. Add daily weather for the same location from Open-Meteo's historical weather API, especially wind
speed and rainfall, since both strongly affect air quality.
4. Calculate the baseline (tomorrow equals today), then train a regression model on today's PM2.5 and
weather.
5. Test on the most recent months and report the mean absolute error for the baseline and your model.
If there's no OpenAQ station near you, you can use Open-Meteo's air quality API, which doesn't need a key. Its
values are model estimates rather than measurements, so mention that in your write-up.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Choose a city where air quality is a real issue for your community, and design the warning for the
people who would receive it.
Focus on the worst days. A common threshold is a daily average above 35 µg/m³, the US EPA 24-
hour standard. Decide how to balance missed warnings against false alarms, and explain why.
Investigate what drives pollution in your city, such as traffic, season or wind direction.
4.3.3 Land-use mapping from satellite images
LEVEL DATA DATASETS TOOLS
Advanced Satellite images EuroSAT, Global Forest Watch Google Colab or Kaggle with a GPU,
PyTorch, torchvision
Goal. Train a model that recognises land use in satellite images, such as forest, farmland, rivers and
towns, and use it to spot change in a place you care about.
Getting to a baseline
1. Load EuroSAT: 27,000 labelled 64×64 Sentinel-2 image tiles in 10 classes. You can load the RGB version
directly with torchvision.datasets.EuroSAT.
2. Split into training, validation and test sets.
3. Fine-tune a small pretrained model, such as ResNet-18, on a free GPU.
4. Compare your model with a baseline that always predicts the most common class.
5. Report accuracy for each class and a confusion matrix showing which classes your model mixes up.
highschoolhackathon.org Page 13 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Make it your own (required)
Add at least one thing of your own. A few ideas:
Apply your model to a place you know, using Sentinel-2 images from Copernicus Browser (free
account), and look for real change over time.
Test how well it works outside Europe and explain what goes wrong.
Link your results to a decision, such as where a ranger or local council should look first. Global Forest
Watch's tree cover loss figures give useful context.
4.3.4 Your own idea
You can build any project that meets the challenge. For example, you could map the largest emitters in
your country with Climate TRACE, forecast a building's energy use, estimate a meal's carbon footprint
from a photo, or predict which streets flood after heavy rain. Our World in Data has clean country-level
climate and energy tables.
What judges look for in this track
In this track, judges pay extra attention to a fair comparison with a simple forecast, a clear link
between your prediction and a decision someone could make, and a test period your model never
saw. Teams that build a small project tied to a real place usually score better than teams that tackle
the whole planet.
highschoolhackathon.org Page 14 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.4 AI + Languages
Your challenge. Build an AI tool that helps people understand each other, learn a language or be
understood, especially in a language that technology serves poorly.
Translation, speech recognition and other language tools work best for English and a small number of
widely spoken languages. For thousands of other languages, quality is much lower. If someone on your
team speaks one of those languages, you have a real advantage in this track.
What your project needs
Report results separately for each language or accent you test, not just an overall average.
Show real examples: your model's output next to the correct output.
Use public datasets, or your own voice and writing. Please don't record or use other people's voices
or messages without their permission.
PROJECTS
4.4.1 Language identification
LEVEL DATA DATASETS TOOLS
Beginner Text Tatoeba Google Colab, pandas, scikit-learn
Goal. Build a model that reads a sentence and identifies its language. Most translation and search tools
start with language identification, and it often fails on smaller languages.
Getting to a baseline
1. Download the sentences file from the Tatoeba downloads page. Each line has a sentence ID, a three-
letter language code (such as eng, spa or ind) and the sentence.
2. Pick 5 to 10 languages and take the same number of sentences from each, for example 2,000.
3. Split into training and test sets.
4. Turn each sentence into letter patterns with TfidfVectorizer(analyzer="char", ngram_range=(1, 3)),
then train a logistic regression or naive Bayes classifier.
5. Report accuracy for each language and a confusion matrix. For comparison, run the same test
sentences through an existing detector such as the langdetect library.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Include a language your team speaks that existing detectors often get wrong.
Focus on hard cases: very short messages, slang, look-alike languages such as Malay and
Indonesian, or text that mixes two languages.
Build a tool that uses language detection for a real purpose, such as sending messages to the right
translator or support volunteer.
highschoolhackathon.org Page 15 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
4.4.2 Translation quality test
LEVEL DATA DATASETS TOOLS
Intermediate Text and NLLB-200, FLORES+ Google Colab, Hugging Face
pretrained Transformers, sacrebleu
models
Goal. Measure how well a free translation model handles a less widely served language compared with a
widely spoken one, then find and explain where it struggles.
Getting to a baseline
1. Create a free Hugging Face account and accept the FLORES+ terms of use. FLORES+ has the same set
of about 1,000 sentences professionally translated into more than 200 languages.
2. Pick two target languages: one widely spoken, such as French, and one less widely served, such as
Swahili, Yoruba or a language your team speaks.
3. Translate 100 English sentences into both languages with facebook/nllb-200-distilled-600M in Colab.
NLLB uses language codes such as fra_Latn, swh_Latn and yor_Latn.
4. Score each set of translations against the professional ones with chrF, using the sacrebleu library.
5. Report the score for each language and show the five worst translations next to the professional
versions.
Make it your own (required)
Add at least one thing of your own. A few ideas:
Use a language your team speaks, and check whether your own ratings agree with chrF.
Find one type of error, such as names, numbers or idioms, and test a way to reduce it.
Translate text from a real setting, such as school notices or medicine instructions, and decide
whether people could safely rely on it.
4.4.3 Speech recognition across accents
LEVEL DATA DATASETS TOOLS
Advanced Audio Mozilla Common Voice, FLEURS Google Colab with a GPU, Whisper,
jiwer
Goal. Measure how well speech-to-text works across different accents or languages, and try to narrow
the gap for one that performs poorly.
Getting to a baseline
1. Pick either one language with accent labels in Common Voice, or two languages from FLEURS.
2. Select a few hundred clips for each accent or language. You don't need to download the whole
dataset.
3. Transcribe the clips with openai/whisper-small on a free GPU.
4. Normalise the text (lower case, no punctuation) and calculate the word error rate with the jiwer
library.
5. Report the word error rate for each group, and listen to the clips with the highest error to find out why.
highschoolhackathon.org Page 16 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Make it your own (required)
Add at least one thing of your own. A few ideas:
Record and test your own accent, or a family member's with their permission, alongside the public
data.
Find which sounds, words or speaking styles cause the most errors.
Test a fix, such as telling Whisper the language in advance or fine-tuning on a small set of clips, and
measure the change.
4.4.4 Your own idea
You can build any project that meets the challenge. For example, you could build a tool that rewrites
complicated forms in plain language for new speakers, an app that reads and translates street signs, or
a conversation practice partner for learners. If you build on a large language model API, judges will focus
on what you add around it: your data, how you tested it and who it's for.
What judges look for in this track
In this track, judges pay extra attention to real examples shown side by side (what your model
produced and what it should have produced), results broken down by language or accent, and
checks by a real speaker of the language.
highschoolhackathon.org Page 17 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
5 How to submit
Submit your project through the submission form by 11:59 PM ET on Sunday, November 15. One person
submits for the whole team. You can resubmit as many times as you like before the deadline, and we'll
keep your latest version.
What to include Required? Details
Code Yes Share a Google Colab notebook or GitHub repository so anyone with the
link can view it. Save your notebook with its outputs visible. If you can't
use Google Colab where you live, use GitHub.
Write-up Yes About one page, using the template below. Share it as a Google Doc set
to "anyone with the link can view", use your GitHub README, or upload a
PDF or Word file on the form.
Demo video Optional, but Up to 2 minutes. Upload it to YouTube as unlisted, or share it from
recommended Google Drive with "anyone with the link can view".
Team details Yes Your track, plus every team member's name, email and school. We use
these for certificates and awards.
Credits Yes Every dataset, pretrained model, tutorial and AI tool you used, with links.
Your submission is complete once it includes working links to both your code and your write-up.
Before you submit
Open every link in a private or incognito window to check it opens without signing in.
Double-check that every teammate's name and email are spelled correctly.
Submit a first version at least a few hours before the deadline, then resubmit as you improve it.
highschoolhackathon.org Page 18 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Write-up template
Copy this into your Google Doc or README.
# Project name
**Track:** Health / Finance / Climate / Languages
**Team:** names
## The problem
Who has this problem, and why does it matter? (2-3 sentences)
## What we built
What goes in, what comes out, and how someone would use it.
## What we added
If you started from a suggested project: which one, and what you added
or changed (your own user, data or question). Otherwise, write "Our own
idea".
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
Demo video structure
Here's a simple structure for your video.
Part Length What to show
The problem About 15 seconds Who your project is for and why it matters
The demo About 60 seconds A real input going in and the result coming out
How it works About 30 seconds Your data, your model and how it compares with the baseline
Next steps About 15 seconds One limitation and what you'd do next
A screen recording with your voice over it is plenty. You don't need to edit it.
highschoolhackathon.org Page 19 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
6 How judging works
In Round 1, the Veritas AI team reviews every complete submission blind, without names or schools. We'll
email shortlisted students and finalists on Wednesday, November 18. Finalists then present live to a panel
of AI researchers at the Award Ceremony on Saturday, November 21 at 11:00 AM ET.
Criterion What judges look for How you can show it
Technical Your project works, your approach is Compare with a baseline, report results on
quality sound and you tested it fairly unseen test data, and show where it fails
Impact Your project tackles a real problem for Explain who it helps and what would change for
real people them
Creativity You take a fresh approach rather than Apply a known technique to an unusual dataset,
repeating a tutorial question or group of users
Clarity A judge can understand your project in Give a clear demo, a concise write-up and one
two minutes main takeaway
If your results look too good to be true, test data has usually leaked into training. Judges score an honest,
modest result higher than an unexplained high one.
How suggested projects are judged
Many teams will start from the same suggested project. Reviewers compare those projects with each
other and score each team on what it added beyond the steps in this document: its own user, data or
question, and how well it tested the result. Teams that follow the steps exactly still have complete
submissions, but they'll score toward the lower end of the range.
highschoolhackathon.org Page 20 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
7 Frequently asked questions
Question Answer
Do we have to build one of the No. They're optional starting points, and you can build any project
suggested projects? that meets a track's challenge. If you use one, add at least one
thing of your own (see section 3).
Our idea fits more than one track. Which Pick the track that fits best. Judges score each project in one track
do we choose? only.
Which track is the most or least There isn't an easier track to win. Teams only choose their track
competitive? when they submit, so nobody knows how many teams are in each
one until the deadline. Judges also score every track on the same
four criteria. The best strategy is to pick the track where your team
cares most about the problem, because that usually leads to a
stronger project.
Our idea doesn't fit any track. What You'll need to pick an idea that falls within one of the four tracks:
should we do? Health, Finance, Climate or Languages. Judges score every project
within a track, so they can't judge ideas outside them. The tracks
are broad, so try reframing your idea around a problem in one of
them.
Can we get technical help during the Unfortunately not. Our team can't help with technical questions
hackathon? during the hackathon, such as debugging code, fixing errors or
choosing a model. We can only help with problems submitting your
project. The Hacker Guide and the documentation for each tool are
the best places to look if you get stuck.
Do we need to train our own model? No. You can use pretrained models and AI APIs. Judges focus on
what you build around them: your data, how you tested it and who
it's for.
Can we use ChatGPT, Claude, Copilot or Yes, as long as your team understands every part of the project and
other AI tools? can explain it. List every AI tool you used in your write-up and on the
form.
Can we use a dataset that isn't listed Yes. You can use any public dataset. Just check its licence and cite
here? it with a link.
Is there a minimum accuracy? No. Judges look at whether your project works, how fairly you tested
it and how honestly you report your results.
Is the demo video required? No. It's optional but recommended. You do need to submit your
code and write-up.
Google Colab is blocked where we live. Share your code as a GitHub repository instead.
What should we use?
Our team changed during the weekend. List everyone who worked on the project on the submission form.
We give awards and certificates to the students listed there.
highschoolhackathon.org Page 21 of 22

VERITAS AI · International High School Hackathon 2026 Project Briefs
Question Answer
Can we submit more than once? Yes. Resubmit as often as you like before the deadline, and we'll
keep your latest version.
Our upload failed at the deadline. Email contact@veritasai.com right away with links to your code and
write-up.
Can we keep working after the Yes, but judges only see what you submitted before 11:59 PM ET on
deadline? Sunday, November 15.
Do we need to attend anything live this No. There's no kickoff call or check-in. Build on your own schedule
weekend? within the 48 hours.
When will we hear the results? We'll email shortlisted students and finalists on November 18, and
announce the winners at the Award Ceremony on November 21 at
11:00 AM ET.
Good luck, and have fun building!
Got a question we didn't cover? Remember that we can only help with submission issues, not technical
ones. Check the Hacker Guide or email contact@veritasai.com.
The Veritas AI team
highschoolhackathon.org Page 22 of 22
