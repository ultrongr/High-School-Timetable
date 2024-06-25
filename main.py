import numpy as np 
import pymprog
# import input_data as inp
import input_data_non_complete as inp


class Timetable:

    def __init__(self, profs_n, days_n, hours_n, classes_n):
        self.number_of_classes = classes_n
        self.number_of_profs = profs_n
        self.number_of_days = days_n
        self.number_of_hours = hours_n
        self.solved = False

        self.K = np.ndarray(shape=(self.number_of_profs, self.number_of_days, self.number_of_hours, self.number_of_classes), dtype=pymprog._var)
        self.model = pymprog.model('Timetable')
        
        self.create_timetable()

        self.create_physical_constraints()
        self.create_material_coverage__constraints()
        self.create_max_hours_per_day_constraints()
        self.create_unavailable_hours_constraints()
        
        self.set_objective()

        
    
    def create_timetable(self):
        
        for i in range(self.number_of_profs):
            for j in range(self.number_of_days):
                for k in range(self.number_of_hours):
                    for l in range(self.number_of_classes):
                        self.K[i][j][k][l] = self.model.var(f"K_{i}_{j}_{k}_{l}", kind=int, bounds=(0, 1))
    
    def solve(self):
        self.model.solve()
        self.solved = True

    def create_physical_constraints(self):
        """Contraints of the type:
        -No proffessor can teach 2 classes at the same time
        -No class can be taught by 2 proffessors at the same time
        Are added here        
        """

        # No proffessor can teach 2 classes at the same time
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in range(self.number_of_hours):
                    sum(self.K[i][d][h]) <= 1
        
        # No class can be taught by 2 proffessors at the same time
        for d in range(self.number_of_days):
            for h in range(self.number_of_hours):
                for c in range(self.number_of_classes):
                    sum(self.K[:, d, h, c]) <= 1
    
    def create_material_coverage__constraints(self):
        """Contraints of the type:
        -A class can only be taught x hours per week by a proffessor, as dictated by the material needed to be covered
        Are added here        
        """
        # A proffessor i can only teach x hours per week for class l according to the input data
        for i in range(self.number_of_profs):
            for c in range(self.number_of_classes):


                all_hours_in_week = [self.K[i][d][h][c] for d in range(self.number_of_days) for h in range(self.number_of_hours)]
                # sum(all_hours_in_week) == inp.required_hours_per_professor_per_class[i][c]
                sum(all_hours_in_week) <= inp.required_hours_per_professor_per_class[i][c] # Use if you want to get uncompleted timetables as result

    def create_max_hours_per_day_constraints(self):
        """Contraints of the type:
        -A proffessor can only teach up to x hours per day for a class
        Are added here        
        """
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for c in range(self.number_of_classes):
                    sum(self.K[i, d, :, c]) <= inp.max_hours_per_professor_per_class_per_day[i][c]

    def create_unavailable_hours_constraints(self):
        """Contraints of the type:
        -A proffessor cannot teach any class at a specific time
        Are added here        
        """
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in range(self.number_of_hours):
                    # for c in range(self.number_of_classes):
                    #     if (d, h) in inp.unavailable_hours_per_professor[i]:
                    #         self.K[i][d][h][c] == 0
                    if (d, h) in inp.unavailable_hours_per_professor[i]:   
                        sum(self.K[i][d][h]) ==0


    def set_objective(self):

        
        
        params = {
            "coverage": 100,
            "preferred_days": 1,
            "avoidance_days": 1,
            "preferred_hours": 0.5,
            "avoidance_hours": 0.5,
            
        }

        # Maximize the number of classes taught
        coverage_terms = [self.K[i][d][h][c] for i in range(self.number_of_profs) for d in range(self.number_of_days) for h in range(self.number_of_hours) for c in range(self.number_of_classes)]


        # Add preferences like some professors prefer to teach at certain days
        preferences_days_terms = []
        for i in range(self.number_of_profs):
            for d in inp.preferred_days_per_professor[i]:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        preferences_days_terms.append(self.K[i][d][h][c])
            
        
        # Add preferences like some professors prefer not to teach at certain days
        avoidance_days_terms = []
        for i in range(self.number_of_profs):
            for d in inp.days_to_avoid_per_professor[i]:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        avoidance_days_terms.append(self.K[i][d][h][c])
        
        # Add preferences like some professors prefer to teach at certain hours
        preferences_hours_terms = []
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in inp.preferred_hours_per_professor[i]:
                    for c in range(self.number_of_classes):
                        preferences_hours_terms.append(self.K[i][d][h][c])
        
        # Add preferences like some professors prefer not to teach at certain hours
        avoidance_hours_terms = []
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in inp.hours_to_avoid_per_professor[i]:
                    for c in range(self.number_of_classes):
                        avoidance_hours_terms.append(self.K[i][d][h][c])
        



        
        
            

        objective_sum = params["coverage"]*sum(coverage_terms)
        objective_sum += params["preferred_days"]*sum(preferences_days_terms)
        objective_sum -= params["avoidance_days"]*sum(avoidance_days_terms)
        objective_sum += params["preferred_hours"]*sum(preferences_hours_terms)
        objective_sum -= params["avoidance_hours"]*sum(avoidance_hours_terms)

        self.model.maximize(objective_sum)
        

    def print_classes(self):
        if not self.solved:
            print("Model has not been solved yet")
            return
        class_names = ["Class A", "Class B", "Class C"]
        for c in range(self.number_of_classes):
            out=f"{class_names[c]}:\n\n"
            time_slots = [[-1 for _ in range(self.number_of_hours)] for _ in range(self.number_of_days)]
            for i in range(self.number_of_profs):
                for j in range(self.number_of_days):
                    for k in range(self.number_of_hours):
                        if self.K[i][j][k][c].primal == 1: # If proffesor i teaches class c at day j and hour k
                            time_slots[j][k] = i
            out += f"H\\D:\t"
            for i in range(self.number_of_days):
                out += f"{inp.days_initials[i]}\t"
            out += "\n"
            for i in range(self.number_of_hours):
                out += f"{i}\t"
                for j in range(self.number_of_days):
                    out += f"{time_slots[j][i]}\t"
                out += "\n"
            out+="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            print(out)

    def print_stats(self):
        if not self.solved:
            print("Model has not been solved yet")
            return
        
        for i in range(self.number_of_profs):
            preffered_day = i%5
            


            counter=0
            for k in range(self.number_of_hours):
                for l in range(self.number_of_classes):
                    if self.K[i][preffered_day][k][l].primal == 1:
                        counter+=1
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            print(f"Professor {i} teaches {counter} classes on day {preffered_day}. Total hours: {total_hours}")
        print("////////")
        for i in range(self.number_of_profs):
            avoided_day = (i+1)%5
            counter=0
            for k in range(self.number_of_hours):
                for l in range(self.number_of_classes):
                    if self.K[i][avoided_day][k][l].primal == 1:
                        counter+=1
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            print(f"Professor {i} teaches {counter} classes on day {avoided_day}. Total hours: {total_hours}")
        
        print("[[[[[[]]]]]]")

        for i in range(self.number_of_profs):
            preffered_hour = i%5
            counter=0
            for j in range(self.number_of_days):
                for l in range(self.number_of_classes):
                    if self.K[i][j][preffered_hour][l].primal == 1:
                        counter+=1
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            print(f"Professor {i} teaches {counter} classes on hour {preffered_hour}. Total hours: {total_hours}")
        print("////////")

        for i in range(self.number_of_profs):
            avoided_hour = (i+1)%5
            counter=0
            for j in range(self.number_of_days):
                for l in range(self.number_of_classes):
                    if self.K[i][j][avoided_hour][l].primal == 1:
                        counter+=1
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            print(f"Professor {i} teaches {counter} classes on hour {avoided_hour}. Total hours: {total_hours}")


if __name__ == '__main__':
    
    timetable = Timetable(inp.number_of_professors, inp.number_of_days, inp.number_of_hours, inp.number_of_classes)
    timetable.solve()
    timetable.print_classes()
    timetable.print_stats()
