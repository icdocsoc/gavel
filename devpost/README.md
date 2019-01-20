This folder contains scripts that transform CSV data exported from Devpost to a format accepted by Gavel (the version used by nwHacks that supports multiple categories).

It currently exports `projects` and `categories`.

## Usage
### 1. Exporting Devpost Data
1. Go to `https://manage.devpost.com/challenges/<hackathon_id>/dashboard/reports/activity`
2. Use the following settings and press the `Generate .csv report` button.
![image](https://user-images.githubusercontent.com/12876696/51438262-ee2de700-1c5e-11e9-909f-d401803c0ab5.png)
3. Clone this repo, and change directory into this folder.
3. After the file has finished processing, right-click `Download report` and save the file as `submissions.csv` in this folder.

### 2. Using the CLI tool
1. Ensure that you have Python 3 installed with `python --v`
2. Run `python main.py submissions.csv` from this folder.

The tool will have outputted `categories.csv` and `projects.csv`, both of which can be imported directly to Gavel.
