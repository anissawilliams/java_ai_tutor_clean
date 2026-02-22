import pandas as pd
import json
import matplotlib.pyplot as plt

# data_dict = pd.read_json("array_list_session_data.json")
# print(data_dict.head())
# print(data_dict.columns)
data_dict = json.load(open("array_list_session_data.json"))
users = data_dict["users"]
sessions = []
session = []
completed_arraylist_sessions = []
arraylist = []
for user in users:
    session = users[user]["sessions"]
    sessions.append(session)

for s in sessions:
    if s["arraylist"]["status"] == "completed":
        completed_arraylist_sessions.append(s["arraylist"])

cs = pd.DataFrame(completed_arraylist_sessions)

survey_responses = cs["survey_responses"]
engagement = []
helpfulness = []
understanding = []
vs_other_ai = []
what_liked = []
#engagement': 'Agree',
        #'learning_helpfulness': 'Agree',
       # 'understanding': 'Agree',
        #'vs_other_ai': 'Agree',
       # 'what_liked': 'thanks for the other languages',
        #'would_use_again': 'Yes'
for s in survey_responses:
    engagement.append(s["engagement"])
    helpfulness.append(s["learning_helpfulness"])
    understanding.append(s["understanding"])
    vs_other_ai.append(s["vs_other_ai"])
    what_liked.append(s["what_liked"])

survey_responses_df = pd.DataFrame()
survey_responses_df["engagement"] = engagement
survey_responses_df["learning_helpfulness"] = helpfulness
survey_responses_df["understanding"] = understanding
survey_responses_df["vs_other_ai"] = vs_other_ai
survey_responses_df["what_liked"] = what_liked

print(survey_responses_df.head())

plt.hist(engagement)
plt.title("Engagement")
plt.show()
plt.hist(helpfulness)
plt.title("Learning Helpfulness")
plt.show()
plt.hist(understanding)
plt.title("Understanding")
plt.show()
plt.hist(vs_other_ai)
plt.title("VS Other AI")
plt.show()
#plt.hist(what_liked)
#plt.show()

print(survey_responses_df["engagement"].value_counts())









# sessions = users.get("sessions")
# print(sessions)
