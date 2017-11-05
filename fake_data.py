import pandas as pd
import random
import numpy as np
import datetime

dir = '/Users/jft703/Documents/gift_the_code/'

def random_date(n):
    year = ['2017','2016','2015']
    month = ['01','02','03','04','05','06','07','08','09','10','11','12']
    day = ['01','02','03','04','05','06','07','08','09'] + [str(i) for i in range(10,29)]
    random_dates = []
    for i in range(n):
        rand_dat = '' + random.choice(year) + '-' + random.choice(month) + '-' + random.choice(day)
        random_dates.append(rand_dat)

    return random_dates

members = pd.read_excel(dir + 'member_data.xlsx')

mock_companies = pd.read_excel(dir + 'mock_companies.xlsx')

donations_header = ['donor_type', 'company_name', 'email', 'address_line',
                    'city', 'postal_code', 'state', 'country', 'donation_amount', 'processing_fee_amount',
                    'preferred_language', 'payment_type', 'donation_date', 'fund_program' 'program_funded']

member_donation_count = 10000
random_donation_count = 2000
event_count = 2000
min_donation = 10
max_donation = 10000

member_donations = members.sample(n=member_donation_count, replace=True)
member_donations['donor_type'] = 'Individual'
member_donations['company_name'] = np.NaN
member_donations['email'] = np.NaN
member_donations['address_line'] = np.NaN
member_donations['city'] = np.NaN
member_donations['postal_code'] = np.NaN
member_donations['state'] = np.NaN
member_donations['country'] = np.NaN


member_donations['donation_amount'] = member_donations['member_id'].apply(lambda x: random.uniform(min_donation, max_donation))
member_donations['processing_fee_amount'] = 0.02*member_donations['donation_amount']
member_donations['preferred_language'] = member_donations['member_id'].apply(lambda x: random.choice(['en-CA', 'fr-CA']))
member_donations['payment_type'] = member_donations['member_id'].apply(lambda x: random.choice(['Online', 'In Person']))
member_donations['program_ind'] = member_donations['member_id'].apply(lambda x: random.choice([0, 1]))
member_donations['program_funded'] = member_donations['program_ind'].apply(lambda x: random.choice(["Housing", "Legal Clinic",
                                                                                                    "Trans Youth Mentorship",
                                                                                                    "Sunday Drop In",
                                                                                                    "New Comer Settlement Services",
                                                                                                    "Meal Trans",
                                                                                                    "Family Resource Centre"])
                                                                                                    if x == 1
                                                                                                    else np.NaN)



member_donations['donation_date'] = random_date(member_donation_count)

# Random
random_donations = pd.DataFrame(columns = member_donations.columns)
random_donations[['city', 'email', 'postal_code', 'address_line']] = mock_companies[['city', 'email', 'postal_code', 'address_line']].sample(n=random_donation_count, replace=True)
random_donations['country'] = 'Canada'

random_donations['donor_type'] = random_donations['email'].apply(lambda x: random.choice(['Individual', 'Organization']))
random_donations['company_name'] = random_donations['donor_type'].apply(lambda x: random.choice(mock_companies['company']) if x == 'Organization' else np.NaN)
random_donations['donation_amount'] = random_donations['email'].apply(lambda x: random.uniform(min_donation, max_donation))
random_donations['processing_fee_amount'] = 0.02*random_donations['donation_amount']
random_donations['preferred_language'] = random_donations['email'].apply(lambda x: random.choice(['en-CA', 'fr-CA']))
random_donations['payment_type'] = random_donations['email'].apply(lambda x: random.choice(['Online', 'In Person']))
random_donations['program_ind'] = random_donations['email'].apply(lambda x: random.choice([0, 1]))
random_donations['program_funded'] = random_donations['program_ind'].apply(lambda x: random.choice(["Housing", "Legal Clinic",
                                                                                                    "Trans Youth Mentorship",
                                                                                                    "Sunday Drop In",
                                                                                                    "New Comer Settlement Services",
                                                                                                    "Meal Trans",
                                                                                                    "Family Resource Centre"])
                                                                                                    if x == 1
                                                                                                    else np.NaN)

random_donations['donation_date'] = random_date(random_donation_count)

donations = pd.concat([member_donations, random_donations])

# # Create a Pandas Excel writer using XlsxWriter as the engine.
# writer = pd.ExcelWriter('donations.xlsx', engine='xlsxwriter')
#
# # Convert the dataframe to an XlsxWriter Excel object.
# donations.to_excel(writer, sheet_name='Sheet1', index = False)
#
# # Close the Pandas Excel writer and output the Excel file.
# writer.save()

# Export to csv
donations.to_csv('donations.csv', sep='|', index = False)

non_program_events_pre = pd.DataFrame(columns=['event_id', 'member_id', 'event_name', 'program_ind', 'program', 'event_date'])
event_list = ['Settling In',
'Next Steps',
'Queer & Trans Family Events',
'Sew What',
'MakerSpace',
'Club 519 (VIP Pass)',
'SUPERNATURE (Event)',
'Among Friends',
'Breakthrough',
'Meal Trans',
'Tax Clinic',
'Youth Action & Art Space',
'Firefly (Event)',
'Just a Taste (Event)',
'Education * Training Workshops',
'Improv with Darryl',
'Winter Celebration',
'Find your sexy! Heels, Health & Individuality']
event_id = [1000000 + i for i in range(0,event_count)]

non_program_events_pre['event_date'] = random_date(event_count)
non_program_events_pre['event_name'] = non_program_events_pre['event_date'].apply(lambda x: random.choice(event_list))
non_program_events_pre['event_id'] = event_id
non_program_events = pd.DataFrame(columns=['event_id', 'member_id', 'event_name', 'program_ind', 'program', 'event_date'])

for e_id in [1000000 + i for i in range(0,event_count)]:
    attendees = np.random.randint(1, 20)
    att = non_program_events_pre.loc[non_program_events_pre['event_id'] == e_id]
    for i in range(0,attendees):
        # attend['member_id'] = [if np.random.randint(0,2) < 1: 999999999 else data['member_id'].sample(n=1) for i in range(attendees) ]
        if np.random.randint(0,2) < 1:
            att['member_id'].loc[att['event_id'] == e_id] = [999999999]
        else :
            att.loc[att['event_id'] == e_id,'member_id'] = np.random.randint(1000)
        non_program_events = non_program_events.append(att)
non_program_events['program_ind'] = 0

program_events_pre = pd.DataFrame(columns=non_program_events.columns)
program_events_pre['event_date'] = random_date(event_count)
program_events_pre['event_name'] = np.NaN
event_id = [1000000 + i for i in range(event_count,event_count*2)]
program_events_pre['event_id'] = event_id
program_events = pd.DataFrame(columns=['event_id', 'member_id', 'event_name', 'program_ind', 'program', 'event_date'])

for e_id in [1000000 + i for i in range(event_count,event_count*2)]:
    attendees = np.random.randint(1, 10)
    att = program_events_pre.loc[program_events_pre['event_id'] == e_id]
    for i in range(0,attendees):
        # attend['member_id'] = [if np.random.randint(0,2) < 1: 999999999 else data['member_id'].sample(n=1) for i in range(attendees) ]
        if np.random.randint(0,2) < 1:
            att['member_id'].loc[att['event_id'] == e_id] = [999999999]
        else :
            att.loc[att['event_id'] == e_id,'member_id'] = np.random.randint(1000)
        program_events = program_events.append(att)

program_events['program_ind'] = 1
program_events['program'] = program_events['event_date'].apply(lambda x: random.choice(["Housing", "Legal Clinic", "Trans Youth Mentorship", "Sunday Drop In", "New Comer Settlement Services",
                            "Meal Trans", "Family Resource Centre"]))

events = pd.concat([non_program_events, program_events])

# Create a Pandas Excel writer using XlsxWriter as the engine.
# writer = pd.ExcelWriter('events.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
# events.to_csv(writer, sheet_name='Sheet1', index = False)

# Close the Pandas Excel writer and output the Excel file.
# writer.save()

# Export to csv
events.drop(['event_id']).to_csv('events.csv', sep='|', index = False)

print(members.head(20))
print(donations.head(20))
print(events.head(20))
