import numpy as np 
import pymprog

import input_data as inp
# import input_data_non_complete as inp
# import input_data_real as inp


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
                # sum(all_hours_in_week) == inp.required_hours_per_professor_per_class[i][c] # Use to force the timetable to be complete
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
                    if (d, h) in inp.unavailable_hours_per_professor[i]:   
                        sum(self.K[i][d][h]) ==0


    def set_objective(self):

        
        
        params = {
            "coverage": 100,
            "preferred_days": 2,
            "avoidance_days": 2,
            "preferred_hours": 0.5,
            "avoidance_hours": 0.5,
            
        }

        # Maximize the number of classes taught
        coverage_terms = [self.K[i][d][h][c] for i in range(self.number_of_profs) for d in range(self.number_of_days) for h in range(self.number_of_hours) for c in range(self.number_of_classes)]

        # If we want to give a higher priority to certain professors we can add a weight to the choices of those proffessors:
        extra_priority =[1 for _ in range(self.number_of_profs)]
        # extra_priority[0] = 0
        # extra_priority[0] = 1
        extra_priority[0] = 2

        # Add preferences like some professors prefer to teach at certain days
        preferences_days_terms = []
        for i in range(self.number_of_profs):
            for d in inp.preferred_days_per_professor[i]:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        preferences_days_terms.append(extra_priority[i]*self.K[i][d][h][c])
            
        
        # Add preferences like some professors prefer not to teach at certain days
        avoidance_days_terms = []
        for i in range(self.number_of_profs):
            for d in inp.days_to_avoid_per_professor[i]:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        avoidance_days_terms.append(extra_priority[i]*self.K[i][d][h][c])
        
        # Add preferences like some professors prefer to teach at certain hours
        preferences_hours_terms = []
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in inp.preferred_hours_per_professor[i]:
                    for c in range(self.number_of_classes):
                        preferences_hours_terms.append(extra_priority[i]*self.K[i][d][h][c])
        
        # Add preferences like some professors prefer not to teach at certain hours
        avoidance_hours_terms = []
        for i in range(self.number_of_profs):
            for d in range(self.number_of_days):
                for h in inp.hours_to_avoid_per_professor[i]:
                    for c in range(self.number_of_classes):
                        avoidance_hours_terms.append(extra_priority[i]*self.K[i][d][h][c])
        



        
        
            

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
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
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

    def print_professors(self):

        if not self.solved:
            print("Model has not been solved yet")
            return
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        
        colors = True

        if colors:
            RED = "\033[31m"
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            BLUE = "\033[34m"
            MAGENTA = "\033[35m"
            CYAN = "\033[36m"
            RESET = "\033[0m"

        first_line = "P\\D\t|\t"
        for i in range(self.number_of_days):
            first_line += f"{inp.days_initials[i]}\t|\t"
        first_line = first_line[:-1]
        first_line += "Preferred/Avoided hours"
        out =  "\n"
        pad_after="" if inp.number_of_hours>=6 else " "
        for i in range(self.number_of_profs):
            out+=f"Prof {i}\t"
            for d in range(self.number_of_days):
                out+="|"
                if colors:
                    if d in inp.preferred_days_per_professor[i]:
                        out+=GREEN
                    elif d in inp.days_to_avoid_per_professor[i]:
                        out+=RED

                for h in range(self.number_of_hours):
                    flag = [ self.K[i][d][h][c].primal for c in range(self.number_of_classes)]
                    if sum(flag) == 0:
                        if (d, h) in inp.unavailable_hours_per_professor[i]:    
                            out+=" X" + pad_after
                        else:
                            out+=" -" + pad_after
                    else:
                        index = flag.index(1)
                        out+=" " + inp.class_names[index] + pad_after
                if colors:
                    out+=RESET
                if inp.number_of_hours>=6:                  
                    out+="\t"
            if colors:
                preferred_hours = inp.preferred_hours_per_professor[i]
                avoided_hours = inp.hours_to_avoid_per_professor[i]
                preferred_hours_print = ",".join([str(x) for x in preferred_hours])
                avoided_hours_print = ",".join([str(x) for x in avoided_hours])
                out+=f"|  {GREEN}{preferred_hours_print}{RESET} | {RED}{avoided_hours_print}{RESET}\n"
            

        print(first_line+"\n"+out)

        

    def print_stats(self):
        if not self.solved:
            print("Model has not been solved yet")
            return
        print("\n//////////////////////////////////////\n")
        print("Printing statistics\n")


        print("Preferred Days")
        counter_preferred_days=0
        for i in range(self.number_of_profs):
            preffered_days = inp.preferred_days_per_professor[i]

            counter=0
            for preferred_day in preffered_days:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        if self.K[i][preferred_day][h][c].primal == 1:
                            counter+=1
            counter_preferred_days+=counter
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            print(f"Professor {i} teaches {counter} classes on their preferred days. Total hours: {total_hours}")
        print("\n////////\n")
        print("Avoided Days")
        counter_avoided_days=0
        for i in range(self.number_of_profs):
            avoided_days = inp.days_to_avoid_per_professor[i]

            counter=0
            for avoided_day in avoided_days:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        if self.K[i][avoided_day][h][c].primal == 1:
                            counter+=1
            counter_avoided_days+=counter
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            print(f"Professor {i} teaches {counter} classes on their avoided days. Total hours: {total_hours}")
        
        print("\n////////\n")
        print("Preferred Hours")
        counter_preferred_hours=0
        for i in range(self.number_of_profs):
            preferred_hours = inp.preferred_hours_per_professor[i]

            counter=0
            for preferred_hour in preferred_hours:
                for d in range(self.number_of_days):
                    for c in range(self.number_of_classes):
                        if self.K[i][d][preferred_hour][c].primal == 1:
                            counter+=1
            counter_preferred_hours+=counter
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            print(f"Professor {i} teaches {counter} classes on their preferred hours. Total hours: {total_hours}")

        print("\n////////\n")
        print("Avoided Hours")
        counter_avoided_hours = 0
        for i in range(self.number_of_profs):
            avoided_hours = inp.hours_to_avoid_per_professor[i]

            counter=0
            for avoided_hour in avoided_hours:
                for d in range(self.number_of_days):
                    for c in range(self.number_of_classes):
                        if self.K[i][d][avoided_hour][c].primal == 1:
                            counter+=1
            counter_avoided_hours += counter
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            print(f"Professor {i} teaches {counter} classes on their avoided hours. Total hours: {total_hours}")
        
        print("\n////////\n")
        print(f"Number of hours taught in avoided days: {counter_avoided_days}")
        print(f"Number of hours taught in preferred days: {counter_preferred_days}")
        print(f"Number of hours taught in avoided hours: {counter_avoided_hours}")
        print(f"Number of hours taught in preferred hours: {counter_preferred_hours}")

    def show_stats(self):
        if not self.solved:
            print("Model has not been solved yet")
            return
        
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator

        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        fig.suptitle('Stats')

        plt.subplots_adjust(hspace=0.4, wspace=0.4)

        # Plot the number of classes taught by each professor on preferred days
        preferred_days_stats = []
        for i in range(self.number_of_profs):
            preferred_days = inp.preferred_days_per_professor[i]
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            counter=0
            for preferred_day in preferred_days:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        if self.K[i][preferred_day][h][c].primal == 1:
                            counter+=1

            preferred_days_stats.append(counter/total_hours if total_hours!=0 else 0)

        axs[0, 0].bar(range(len(preferred_days_stats)), preferred_days_stats)
        axs[0, 0].set_title('Percentage of Hours Taught on Preferred Days')
        axs[0, 0].set_xlabel('Professor id')
        axs[0, 0].set_ylabel('Percentage of weekly hours')
        axs[0, 0].xaxis.set_major_locator(MaxNLocator(integer=True))
        # axs[0, 0].yaxis.set_major_locator(MaxNLocator(integer=True))

        # Plot the number of classes taught by each professor on avoided days
        avoided_days_stats = []
        for i in range(self.number_of_profs):
            avoided_days = inp.days_to_avoid_per_professor[i]
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            counter=0
            for avoided_day in avoided_days:
                for h in range(self.number_of_hours):
                    for c in range(self.number_of_classes):
                        if self.K[i][avoided_day][h][c].primal == 1:
                            counter+=1
            avoided_days_stats.append(counter/total_hours if total_hours!=0 else 0)
        

        axs[0, 1].bar(range(len(avoided_days_stats)), avoided_days_stats)
        axs[0, 1].set_title('Percentage of Hours Taught on Avoided Days')
        axs[0, 1].set_xlabel('Professor id')
        axs[0, 1].set_ylabel('Percentage of weekly hours')
        axs[0, 1].xaxis.set_major_locator(MaxNLocator(integer=True))
        # axs[0, 1].yaxis.set_major_locator(MaxNLocator(integer=True))


        # Plot the number of classes taught by each professor on preferred hours
        preferred_hours_stats = []
        for i in range(self.number_of_profs):
            preferred_hours = inp.preferred_hours_per_professor[i]
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            counter=0
            for preferred_hour in preferred_hours:
                for j in range(self.number_of_days):
                    for c in range(self.number_of_classes):
                        if self.K[i][j][preferred_hour][c].primal == 1:
                            counter+=1
            preferred_hours_stats.append(counter/total_hours if total_hours!=0 else 0)

        axs[1, 0].bar(range(len(preferred_hours_stats)), preferred_hours_stats)
        axs[1, 0].set_title('Percentage of Hours Taught on Preferred Hours')
        axs[1, 0].set_xlabel('Professor id')
        axs[1, 0].set_ylabel('Percentage of weekly hours')
        axs[1, 0].xaxis.set_major_locator(MaxNLocator(integer=True))
        # axs[1, 0].yaxis.set_major_locator(MaxNLocator(integer=True))

        # Plot the number of classes taught by each professor on avoided hours
        avoided_hours_stats = []
        for i in range(self.number_of_profs):
            avoided_hours = inp.hours_to_avoid_per_professor[i]
            total_hours= sum(inp.required_hours_per_professor_per_class[i])
            if total_hours==0:
                continue
            counter=0
            for avoided_hour in avoided_hours:
                for j in range(self.number_of_days):
                    for c in range(self.number_of_classes):
                        if self.K[i][j][avoided_hour][c].primal == 1:
                            counter+=1
            avoided_hours_stats.append(counter/total_hours if total_hours!=0 else 0)

        axs[1, 1].bar(range(len(avoided_hours_stats)), avoided_hours_stats)
        axs[1, 1].set_title('Percentage of Hours Taught on Avoided Hours')
        axs[1, 1].set_xlabel('Professor id')
        axs[1, 1].set_ylabel('Percentage of weekly hours')
        axs[1, 1].xaxis.set_major_locator(MaxNLocator(integer=True))
        # axs[1, 1].yaxis.set_major_locator(MaxNLocator(integer=True))
        





        plt.show()


if __name__ == '__main__':
    
    timetable = Timetable(inp.number_of_professors, inp.number_of_days, inp.number_of_hours, inp.number_of_classes)
    timetable.solve()
    timetable.print_stats()
    timetable.print_classes()
    
    timetable.print_professors()

    timetable.show_stats()
