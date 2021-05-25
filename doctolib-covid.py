import os
import datetime
import webbrowser
import requests
import smtplib, ssl
import time

DISABLE_EMAIL = os.environ.get("DISABLE_EMAIL")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
#RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

with open('centers.txt') as centers_txt:
    centers = centers_txt.readlines()
centers = [center.strip() for center in centers if not center.startswith("#")] 

with open('emails.txt') as emails_txt:
    emails = emails_txt.readlines()
emails = [email.strip() for email in emails if not email.startswith("#")] 

with open('vaccines.txt') as vaccines_txt:
    vaccines = vaccines_txt.readlines()
vaccines = [vaccine.strip() for vaccine in vaccines if not vaccine.startswith("#")]

clear = lambda: os.system('clear')

try:
    while (True):
        for center in centers:
            clear()
            data = requests.get(f"https://www.doctolib.de/booking/{center}.json").json()["data"]

            #https://www.doctolib.de/booking/ciz-berlin-berlin.json
            
            visit_motives = [visit_motive for visit_motive in data["visit_motives"] if any(vaccine in visit_motive["name"] for vaccine in vaccines)]
            
            if not visit_motives:
                continue
            
            places = [place for place in data["places"]]
            if not places:
                continue
            
            for place in places:
                try:
                    print(" ")
                    print("Place: " + str(place["formal_name"]))
                    #start_date = datetime.datetime.today().date().isoformat()
                    start_date = "2021-06-07"

                    visit_motive_ids = visit_motives[0]["id"]
                    practice_ids = place["practice_ids"][0]
                    place_name = place["formal_name"]
                    place_address = place["full_address"]
                    
                    agendas = [agenda for agenda in data["agendas"]
                            if agenda["practice_id"] == practice_ids and
                            not agenda["booking_disabled"] and
                            visit_motive_ids in agenda["visit_motive_ids"]]
                    if not agendas:
                        continue
                    
                    agenda_ids = "-".join([str(agenda["id"]) for agenda in agendas])
                        
                    #print("visit_motive_ids: " + str(visit_motive_ids))
                    #print("practice_ids:" + str(practice_ids))
                    #print("agenda_ids:"+ str(agenda_ids))
                    
                    response = requests.get(
                            "https://www.doctolib.de/availabilities.json",
                            params = {
                                    "start_date": start_date,
                                    "visit_motive_ids": visit_motive_ids,
                                    "agenda_ids": agenda_ids,
                                    "practice_ids": practice_ids,
                                    "insurance_sector": "public",
                                    "destroy_temporary": "true",
                                    "limit":2
                            },
                            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    )
                    response.raise_for_status()
                    nb_availabilities = response.json()["total"]
                    
                    result = str(nb_availabilities) + " appointments available at " + place_name + " - " + place_address
                    print("result: "+ str(result))

                    if nb_availabilities > 0:
                        print("RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN")
                        # open page in web browser
                        webbrowser.open(
                            "https://www.doctolib.de/profiles/" + str(data["profile"]["id"]))
                    if nb_availabilities > 0 and DISABLE_EMAIL != "true":
                        print("RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN RUNNNNNNNNN")
                        os.system('play -nq -t alsa synth {} sine {}'.format(1, 800))
                        # open page in web browser
                        webbrowser.open(
                            "https://www.doctolib.de/profiles/" + str(data["profile"]["id"]))
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as server:
                            server.login(SENDER_EMAIL, SENDER_PASSWORD)
                            for email in emails:
                                server.sendmail(SENDER_EMAIL, email, result.encode('utf-8'))
                                print("  --> Alert sent to " + RECEIVER_EMAIL)
                
                except json.decoder.JSONDecodeError:
                    print("Doctolib might be ko")
                except KeyError as e:
                    print("KeyError: " + str(e))

        time.sleep(5)
except KeyboardInterrupt:
    print("Mischief managed.")
