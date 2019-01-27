import argparse
import csv

# number of expo tables available in the venue
NUM_TABLES = 200

# default categories that all projects will automatically be assigned to
MANDATORY_CATEGORIES = ["DoCSoc Choice"]

# prefix for location field of exported projects
LOCATION_PREFIX = "Table "

IGNORED_CATEGORIES = ['Accenture: Most Ethical/(For Good) Hack', 'Microsoft: Cognitive Challenge',
                      'Next Jump: Most Helpful Hack', 'Ocado Technology: Fastest Delivery Challenge',
                      'TPP: Greatest Impact on Healthcare']

NOT_INCLUDED_TOWARDS_LIMIT = ["Newcomers' Prize"]

LIMIT = 2

# map of already-taken tables
tables_in_use = {}

# map of projects
projects = {}

# increase field size limit to handle large descriptions from Devpost projects
csv.field_size_limit(999999)

'''
Returns command line arguments
'''
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('submission_csv')
    return parser.parse_args()

'''
Fills projects with data from Devpost subsmission csv
'''
def populate_projects():
    with open(args.submission_csv, newline='', encoding='UTF8') as submission_csv:
        reader = csv.DictReader(submission_csv)
        i = 0
        for row in reader:
            i += 1
            projects[i] = {
                "name": row["Submission Title"],
                "location": row["Table Number"],
                "description": row["Plain Description"],
                "categories": row["Desired Prizes"],
            }


'''
Returns a list of categories parsed from "Desired Prizes" field of input csv
Requirements: Prize names cannot contain commas unless surrounded by 
              double-quotes because it's impossible to determine the
              word boundaries otherwise. On Devpost, ensure that 
              category names with commas meet this condtion. Examples:
                - Invalid: The best, most expensive category
                - Valid: The "best, most expensive" category
                - Valid: "The best, most expensive category"
'''
def parse_categories(categories):
    in_quote = False
    category_list = []
    i = 0
    left = 0
    while i < len(categories):
        character = categories[i]
        if character == '"':
            in_quote = not in_quote
        if not in_quote:
            if character == ',':
                category_name = categories[left:i].strip()

                if category_name not in IGNORED_CATEGORIES:
                    category_list.append(category_name)

                left = i+1
        i += 1
    if left < len(categories):
        category_name = categories[left:].strip()

        if category_name not in IGNORED_CATEGORIES:
            category_list.append(category_name)

    return category_list

'''
Projects can request a table (instead of being assigned one).
This function returns the table number as an int, or False if
the requested table number is invalid.
'''
def valid_table_number(desired_table):
    try:
        return int(desired_table)
    except ValueError:
        return False

'''
Projects can request a table (instead of being assigned one),
if the requested table is a valid number, this function reserves
that table for that specific project.
'''
def reserve_requested_tables():
    for key, project in projects.items():
        table_number = valid_table_number(project["location"])
        if table_number:
            if table_number not in tables_in_use and table_number <= NUM_TABLES:
                projects[key]["location"] = table_number
                tables_in_use[table_number] = True
            else:
                projects[key]["location"] = 0
        else:
            projects[key]["location"] = 0

'''
Assigns an available table to any project without a table.
Should be called only after reserve_requested_tables()
'''
def assign_remaining_tables():
    table_number = 1
    for key, project in projects.items():
        if project["location"] == 0:
            while table_number in tables_in_use:
                table_number += 1
            projects[key]["location"] = table_number
            tables_in_use[table_number] = True

def limit_categories(categories):
    limit = LIMIT

    for not_included in NOT_INCLUDED_TOWARDS_LIMIT:
        if not_included in categories:
            limit += 1

    return categories[:min(len(categories), limit)]

'''
Exports projects to a formatted CSV that Gavel can accept.
'''
def export_projects():
    buffer = {}
    for project in projects.values():
        if project["location"] < 44:
          LOCATION_PREFIX = "QTR "
        elif project["location"] < 75:
          LOCATION_PREFIX = "SCR "
        else:
          LOCATION_PREFIX = "JCR "
        output_project = [
            project["name"],
            LOCATION_PREFIX + str(project["location"]),
            project["description"],
        ]
        categories = limit_categories(parse_categories(project["categories"]))
        for category_name in categories:
            output_project.append(category_name)
        for category_name in MANDATORY_CATEGORIES:
            output_project.append(category_name)
        buffer[project["location"]] = output_project
    output_file = []
    for k in sorted(buffer.keys()):
        output_file.append(buffer[k])
    with open("projects.csv", 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(output_file)

'''
Exports all category names (found in the input CSV) as a CSV file that Gavel can accept.
'''
def export_available_categories():
    all_categories = {}
    for category_name in MANDATORY_CATEGORIES:
        all_categories[category_name] = True
    for project in projects.values():
        categories = parse_categories(project["categories"])
        for category_name in categories:
            if category_name not in all_categories:
                all_categories[category_name] = True
    buffer = [[category, input("Description for "+category+"? ")] for category in list(all_categories.keys())]
    with open("categories.csv", 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(buffer)

if __name__ == '__main__':
    args = get_args()
    populate_projects()
    reserve_requested_tables()
    # assign_remaining_tables()
    print("Exporting projects...")
    export_projects()
    print("Projects successfully exported!\n")
    print("Exporting categories...")
    export_available_categories()
    print("Categories successfully exported!")
