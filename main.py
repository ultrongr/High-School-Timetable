import numpy as np 
import pymprog
import input_data as inp


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
        
        self.set_objective()
        self.model.solve()
        self.solved = True
        self.print_classes()
    
    def create_timetable(self):
        
        for i in range(self.number_of_profs):
            for j in range(self.number_of_days):
                for k in range(self.number_of_hours):
                    for l in range(self.number_of_classes):
                        self.K[i][j][k][l] = self.model.var(f"K_{i}_{j}_{k}_{l}", kind=int, bounds=(0, 1))
    


    def create_physical_constraints(self):
        """Contraints of the type:
        -No proffessor can teach 2 classes at the same time
        -No class can be taught by 2 proffessors at the same time
        Are added here        
        """

        # No proffessor can teach 2 classes at the same time
        for i in range(self.number_of_profs):
            for j in range(self.number_of_days):
                for k in range(self.number_of_hours):
                    sum(self.K[i][j][k]) <= 1
        
        # No class can be taught by 2 proffessors at the same time
        for j in range(self.number_of_days):
            for k in range(self.number_of_hours):
                for l in range(self.number_of_classes):
                    sum(self.K[:, j, k, l]) <= 1
    
    def create_material_coverage__constraints(self):
        """Contraints of the type:
        -A class can only be taught x hours per week by a proffessor, as dictated by the material needed to be covered
        Are added here        
        """
        # A proffessor i can only teach x hours per week for class l according to the input data
        for i in range(self.number_of_profs):
            for l in range(self.number_of_classes):

                # sum(self.K[i, :, :, l]) == inp.required_hours_per_professor_per_class[i][l]
                all_hours_in_week = [self.K[i][j][k][l] for j in range(self.number_of_days) for k in range(self.number_of_hours)]
                sum(all_hours_in_week) == inp.required_hours_per_professor_per_class[i][l]

    def set_objective(self):

        # Maximize the number of classes taught
        all_vars = [self.K[i][j][k][l] for i in range(self.number_of_profs) for j in range(self.number_of_days) for k in range(self.number_of_hours) for l in range(self.number_of_classes)]
        self.model.maximize(sum(all_vars))

    def print_classes(self):
        if not self.solved:
            print("Model has not been solved yet")
            return
        for c in range(self.number_of_classes):
            out=""
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
                out += f"{i+1}\t"
                for j in range(self.number_of_days):
                    out += f"{time_slots[j][i]}\t"
                out += "\n"
            out+="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            print(out)

        


if __name__ == '__main__':
    
    timetable = Timetable(inp.number_of_professors, inp.number_of_days, len(inp.number_of_hours_per_day), inp.number_of_classes)

    # for i in range(inp.number_of_professors):
    #     for l in range(inp.number_of_hours):
    #         for k in range(inp.number_of_days):
    #             for j in range(inp.number_of_classes):
    #                 if timetable.K[i][k][l][j].primal == 1:
    #                     print(f"Professor {i} teaches class {j} on day {inp.days[k]} at hour {l}")
    #                     print(f"K_{i}_{k}_{l}_{j} = {timetable.K[i][k][l][j].primal}")
    #                     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    