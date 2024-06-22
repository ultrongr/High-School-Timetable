import numpy as np

np.random.seed(0)

number_of_classes = 3
number_of_days = 5
number_of_hours_per_day = [5,5,5,5,5]
number_of_hours = 5
number_of_professors = 20

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
days_initials = ['M', 'T', 'W', 'Th', 'F']

## Create the required hours per class per proffessor:
## for example [[2,2,2], ...] means that the proffesor with id 0 needs 2 hours for each class
required_hours_per_professor_per_class = [[] for _ in range(number_of_professors)]
for class_id in range(number_of_classes):
    hours_left_for_class = np.sum(number_of_hours_per_day)
    for professor_id in range(number_of_professors):
        if hours_left_for_class == 0:
            required_hours_per_professor_per_class[professor_id].append(int(0))
            continue
            
        try:
            prof_hours_for_class = np.random.randint(1, min(4, hours_left_for_class))
        except ValueError:
            prof_hours_for_class = hours_left_for_class
        required_hours_per_professor_per_class[professor_id].append(int(prof_hours_for_class))
        hours_left_for_class -= prof_hours_for_class


if __name__ == '__main__':
    for i in range(number_of_professors):
        print(f"Professor {i} needs to teach each class for {required_hours_per_professor_per_class[i]} hours")
    print(np.sum(required_hours_per_professor_per_class, axis=0))

               
        
