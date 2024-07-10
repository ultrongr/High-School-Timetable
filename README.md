# High School Timetable

This is a timetable generator for Greek high schools utilizing Linear Programming. It is written in Python and uses the pymprog library for solving the linear programming problem.

## Installation

### Prerequisites

- Python 3.9 or later
- pip (or any other Python package manager)

### Setup

1. **Clone the repository or Download the Project**

    - **Clone the repository**:
        ```bash
        git clone https://github.com/ultrongr/High-School-Timetable
        cd High-School-Timetable
        ```

    - **Download the project** as a zip file and extract it:
        ```bash
        unzip High-School-Timetable.zip
        cd High-School-Timetable-main
        ```

2. **Install the required packages**

   - 
        ```bash
        pip install -r requirements.txt
        ```

## Usage

1. **Select input**

    There are 3 input files containing the necessary parameters for the timetable generation. 
    These files are the following:

    - `input_data.py`: Contains the input data for the timetable generation. It creates a 5 day/week, 5 period/day timetable for 3 classes.
    - `input_data_non_complete.py`: Used to test the program with a scenario where the generation of a complete timetable is not possible.
    - `input_data_real.py`: Contains the input data for the timetable generation according to the material provided by the Greek Ministry of Education (with an exception of 2 hours of Physical Education per week for each class). It creates a 5 day/week, 6 period/day timetable for 3 classes. The rest of the parameters (such as unavailable hours etc, are randomly generated just like in the other input files.)

2. **Run the program**

    ```bash
    python main.py
    ```

    The program will generate a timetable for a high school according to the input file defined in the first lines of the `main.py` file.

    The result will be the printing of the results as defined in the main function, as well as the creation of 4 graphs illustrating the percentages of the preferences of the teachers that were fulfilled.


## Communication

- If you **need help**, you can contact me at up1083865@ac.upatras.gr
