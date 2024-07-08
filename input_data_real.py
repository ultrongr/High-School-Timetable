import numpy as np

np.random.seed(0)

number_of_classes = 3
number_of_days = 5
number_of_hours = 6


days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
days_initials = ['M', 'T', 'W', 'Th', 'F']
class_names = ["A", "B", "C"]

## Create the required hours per class per proffessor:
## for example [[2,2,2], ...] means that the proffesor with id 0 needs 2 hours for each class

data = [
    (3, 2, 2), ## Γλώσσα
    (2, 2, 2), ## Λογοτεχνία
    (2, 2, 2), ## Αρχαία Ελληνική Γλώσσα
    (2, 2, 2), ## Αρχαία Ελληνικά Κείμενα από Μετάφραση
    (4, 4, 4), ## Μαθηματικά
    (1, 2, 2), ## Φυσική
    (0, 1, 1), ## Χημεία
    (1, 1, 1), ## Βιολογία
    (1, 2, 0), ## Γεωγραφία
    (2, 2, 2), ## Ιστορία
    (2, 2, 2), ## Θρησκευτικά
    (2, 2, 2), ## Αγγλικά
    (2, 2, 2), ## Γαλλικά
    (0, 0, 2), ## Κοινωνική και Πολιτική Αγωγή
    (1, 0, 0), ## Οικιακή Οικονομία
    (1, 1, 1), ## Τεχνολογία
    (2, 1, 1), ## Πληροφορική
    (1, 1, 1), ## Μουσική
    (1, 1, 1), ## Καλλιτεχνικά
    
]
number_of_professors = len(data)
required_hours_per_professor_per_class = [[] for _ in range(number_of_professors)]
for class_id in range(number_of_classes):
    for professor_id in range(number_of_professors):
        required_hours_per_professor_per_class[professor_id].append(data[professor_id][class_id])


## Create the max hours per class per day for each professor
## For example [[2,2,2], ...] means that the proffesor with id 0 can teach each class for up to 2 hours a day
max_hours_per_professor_per_class_per_day = [[] for _ in range(number_of_professors)]
for class_id in range(number_of_classes):
    for professor_id in range(number_of_professors):
        hours_per_week = required_hours_per_professor_per_class[professor_id][class_id]
        max_hours_per_professor_per_class_per_day[professor_id].append((hours_per_week if hours_per_week <= 2 else 2))
        
        # max_hours_per_professor_per_class_per_day[professor_id].append(np.random.randint(1, 4))





## Create the preferred days for each professor
preferred_days_per_professor = [[] for _ in range(number_of_professors)]
for professor_id in range(number_of_professors):
    # for _ in range(np.random.randint(1,4)): # Number of preferred days
    #     day = np.random.randint(0, number_of_days)
    #     preferred_days_per_professor[professor_id].append(day)
    ind1=professor_id%number_of_days
    ind2 = np.random.randint(0, number_of_days)
    while ind2==ind1 or ind2==(professor_id+1)%5:
        ind2 = np.random.randint(0, number_of_days)
    preferred_days_per_professor[professor_id] = [ind1, ind2]

## Create the days to be avoided for each professor
days_to_avoid_per_professor = [[] for _ in range(number_of_professors)]
for professor_id in range(number_of_professors):
    pref_1, pref_2 = preferred_days_per_professor[professor_id]
    ind1=(professor_id+1)%number_of_days
    ind2 = np.random.randint(0, number_of_days)
    while ind2 in [pref_1, pref_2, ind1]:
        ind2 = np.random.randint(0, number_of_days)
    days_to_avoid_per_professor[professor_id] = [ind1, ind2]

## Create the preferred hours for each professor
preferred_hours_per_professor = [[] for _ in range(number_of_professors)]
for professor_id in range(number_of_professors):
    ind1=professor_id%number_of_hours
    ind2 = np.random.randint(0, number_of_hours)
    while ind2==ind1 or ind2==(professor_id+1)%5:
        ind2 = np.random.randint(0, number_of_hours)
    preferred_hours_per_professor[professor_id] = [ind1, ind2]

## Create the hours to be avoided for each professor
hours_to_avoid_per_professor = [[] for _ in range(number_of_professors)]
for professor_id in range(number_of_professors):
    pref_1, pref_2 = preferred_hours_per_professor[professor_id]
    ind1=(professor_id+1)%number_of_hours
    ind2 = np.random.randint(0, number_of_hours)
    while ind2 in [pref_1, pref_2, ind1]:
        ind2 = np.random.randint(0, number_of_hours)
    hours_to_avoid_per_professor[professor_id] = [ind1, ind2]

## Create the unavailable hours for each professor
## For example:
## [[(0, 0), (2, 3)], [(4,4)], ...] means that the proffesor with id 0 is unavailable on 
## Monday (day 0) hour 0 and on Wednesday (day 2) hour 3
## while the professor with id 1 is unavailable on Friday (day 4) hour 4
unavailable_hours_per_professor = [[] for _ in range(number_of_professors)]
for professor_id in range(number_of_professors):

    for _ in range(np.random.randint(2,10)): # Number of unavailable hours
        day = np.random.randint(0, number_of_days)
        if day in preferred_days_per_professor[professor_id]: # Reducing the amount of unavailable hours on preferred days (not 0)
            day = np.random.randint(0, number_of_days)

        hour = np.random.randint(0, number_of_hours)
        if hour in preferred_hours_per_professor[professor_id]: # Reducing the amount of unavailable hours on preferred hours (not 0)
            hour = np.random.randint(0, number_of_hours)
        unavailable_hours_per_professor[professor_id].append((day, hour))

if __name__ == '__main__':
    pass
               
        
