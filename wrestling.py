from flask import Flask, request, render_template, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

app = Flask(__name__)

# use creds to create a client to interact with the Google Drive API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "wwe-tracker-421019-657b24ee796a.json", scope
)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
wrestlers_sheet = client.open("wwe-tracker").worksheet("wrestlers")

matches_sheet = client.open("wwe-tracker").worksheet("matches")


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/wrestlers", methods=["GET", "POST"])        
def wrestlers():
    if request.method == "POST":
        data = request.form
        row = [data["name"]]
        wrestlers_sheet.append_row(row)
        return redirect(url_for("wrestlers"))
    return render_template("wrestlers.html")


expected_headers = [
    "matchid",
    "matchseq",
    "person",
    "matchtype",
    "show",
    "year",
    "month",
    "week",
    "championship",
    "result",
    "storyline",
    "notes",
]


@app.route("/insert_matches", methods=["GET", "POST"])
def insert_matches():
    wrestlers = wrestlers_sheet.get_all_records()
    wrestler_names = [
        wrestler["name"] for wrestler in wrestlers
    ]  
    if request.method == "POST":
        data = request.form
        matchid = (
            len(matches_sheet.get_all_records(expected_headers=expected_headers)) + 1
        )  # Generate a new matchid
        row = [
            matchid,
            data["matchseq"],
            data["person"],
            data["matchtype"],
            data["show"],
            data["year"],
            data["month"],
            data["week"],
            data["championship"],
            data["result"],
            data["storyline"],
            data["notes"],
        ]
        print(f"Row to append: {row}")  # Print the row to append
        matches_sheet.insert_row(row, index=matchid + 1)  # Insert the new row
        return redirect(url_for("insert_matches"))
    return render_template("insert_matches.html", wrestlers=wrestler_names)


@app.route("/view_wrestlers", methods=["GET", "POST"])
def view_wrestlers():
    if request.method == "POST":
        data = request.form
        row = [data["name"]]
        wrestlers_sheet.append_row(row)
        return redirect(url_for("wrestlers"))

    # Get all records from the wrestlers sheet
    records = wrestlers_sheet.get_all_records()

    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(records)

    # Perform operations on the DataFrame here...
    # For example, let's sort the DataFrame by 'name'
    df = df.sort_values("name")

    # Convert the DataFrame back to a list of dictionaries to pass to the template
    sorted_wrestlers = df.to_dict("records")

    return render_template("view_wrestlers.html", wrestlers=sorted_wrestlers)


@app.route("/view_matches", methods=["GET"])
def view_matches():
    matches = matches_sheet.get_all_records()
    return render_template("view_matches.html", matches=matches)


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


@app.route("/update_matches", methods=["GET", "POST"])
def update_matches():
    data = request.form
    records = matches_sheet.get_all_records()  # Retrieve the records once
    for i in range(len(records)):
        row = [
            None,
            data[f"matchseq-{i}"], # if is_int(data[f"matchseq-{i}"]) else 0,
            data[f"person-{i}"],
            data[f"matchtype-{i}"],
            data[f"show-{i}"],
            int(data[f"year-{i}"]) if is_int(data[f"year-{i}"]) else 0,
            int(data[f"month-{i}"]) if is_int(data[f"month-{i}"]) else 0,
            int(data[f"week-{i}"]) if is_int(data[f"week-{i}"]) else 0,
            data[f"championship-{i}"],
            data[f"result-{i}"],
            data[f"storyline-{i}"],
            data[f"notes-{i}"],
        ]
        try:
            matches_sheet.update(
                "A" + str(i + 2), [row]
            )  # Update the row in Google Sheets
        except gspread.exceptions.APIError as error:
            print("An error occurred:", error)
    return redirect(url_for("view_matches"))


if __name__ == "__main__":
    app.run(debug=True)
