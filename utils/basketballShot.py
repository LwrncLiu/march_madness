import numpy as np
import pandas as pd

class BasketballShot:
    def __init__(self, shot_start_x, shot_start_y, shot_id, play_description, shot_made, team):
        self.hoop_loc_x = 25
        self.hoop_loc_y = None
        self.hoop_loc_z = 10
        self.hoop_baseline_offset = 4.25
        self.num_coordinates = 100
        self.shot_start_x = shot_start_x
        self.shot_start_y = shot_start_y
        self.shot_vertex_z = 0
        self.shot_distance = 0
        self.shot_path_possible = True
        self.shot_path_coordinates_df = pd.DataFrame()
        self.calculate_side_on = False
        self.shot_id = shot_id
        self.shot_made = shot_made
        self.team = team
        self.play_description = play_description

    def __adjust_shot_and_hoop_coordinates(self):
        '''
        Adjust shot coordinates to align with court view and whether the shot was from the home/away team
        The home team will shoot against the right half-court and the away team will shoot against the left half-court
        '''
        if self.team == 'home':
            self.shot_start_y = 94 - self.shot_start_y - self.hoop_baseline_offset
            self.hoop_loc_y = 94 - self.hoop_baseline_offset
        if self.team == 'away':
            self.shot_start_x = 50 - self.shot_start_x
            self.shot_start_y = self.shot_start_y + self.hoop_baseline_offset
            self.hoop_loc_y = self.hoop_baseline_offset

    def __calculate_shot_possible(self):
        '''
        Determine's if a shot is inside the hoop cylinder, as it is unrealisitic to draw a shot path if so 
        '''
        if self.shot_distance <= 0.75:
            self.shot_path_possible = False

    def __adjust_shot_calculate_perspective(self):
        '''
        The default is to calculate a shot's 2D parabola from a person's perspective if they were standing under the hoop
        However, if the shot is directly inlien with the hoop, then you need to calculate the hoop from a side view to avoid 
        divide by zero errors
        '''
        if self.shot_start_x == self.hoop_loc_x: 
            self.calculate_side_on = True

    def __calculate_shot_distance(self):
        '''
        Calculates the shot's distance to the hoop
        '''
        x1, y1 = self.shot_start_x, self.shot_start_y
        x2, y2 = self.hoop_loc_x, self.hoop_loc_y
        
        d = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        self.shot_distance = d

    def __calculate_shot_height(self):
        '''
        Gives a guestimate of the shot's arc height given how far away from the basket it was
        '''

        self.__calculate_shot_distance()
        self.__calculate_shot_possible()

        if self.shot_distance >= 23:     # 3-point territory
            self.shot_vertex_z = 17     
        elif self.shot_distance >= 9:    # mid-range territory
            self.shot_vertex_z = 15 
        else:                            # roughly in the paint
            self.shot_vertex_z = 13

    @staticmethod
    def __calculate_shot_vertex_x_quadratic_coefficients(x1, y1, x2, y2, k):
        '''
        Calculates the quadratic coefficients of two vertex form equations (y = a(x-h)**2 + k) that were solving for 
        the possible values of h
        '''
        a = y2 - y1
        b = -2 * x1 * (y2 - k) + 2 * x2 * (y1 - k)
        c = x1 ** 2 * (y2 - k) - x2 ** 2 * (y1 - k)

        return a, b, c
    
    @staticmethod
    def __calculate_quadratic_values(a, b, c):
        '''
        Calculates the two possible values when solving the quadratic equation when provided the coefficients 
        a, b, and c
        '''
        x1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        x2 = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

        return x1, x2

    def __calculate_parabola_vertex(self, x1, y1, x2, y2, k):
        '''
        From a shot 2D perspective, given the location and hoop location and the shot arc height,
        calculates the shot arc's "x" value when it reaches its' vertex
        '''

        a, b, c = self.__calculate_shot_vertex_x_quadratic_coefficients(x1, y1, x2, y2, k)

        shot_vertex_h1, shot_vertex_h2 = self.__calculate_quadratic_values(a, b, c)

        # choose the vertex h that lies between the shot and hoop
        if x1 <= shot_vertex_h1 <= x2 or x2 <= shot_vertex_h1 <= x1:
            shot_vertex_h = shot_vertex_h1
        else:
            shot_vertex_h = shot_vertex_h2

        return shot_vertex_h

    @staticmethod
    def __calculate_2d_parabola_coefficient_a(x, y, h, k):
        '''
        Given a known (x, y) coordinate of the shot's 2D parabola and the calculated (h, k) coordinate
        of the shot's vertex, calculate the a coefficient in the parabola's vertex form equation
        '''
        a = (y - k)/(x - h)**2

        return a
    
    def __calculate_shot_path_coordinates(self):
        '''
        Given the (x, y) starting coordinates of the shot location,
        the function will return 100 coordinates in 3D space mapping the 
        shot from the start to the center of the hoop
        '''
        num_coords = self.num_coordinates
        shot_path_coords = []

        self.__adjust_shot_and_hoop_coordinates()
        # shot coordinates
        shot_start_x, shot_start_y, shot_start_z = self.shot_start_x, self.shot_start_y, 0

        # hoop coordinates
        hoop_x, hoop_y, hoop_z = self.hoop_loc_x, self.hoop_loc_y, self.hoop_loc_z

        self.__calculate_shot_height()
        self.__adjust_shot_calculate_perspective()

        # if shot is in the hoop cylinder, or the shot was missed, just return a dataframe with one row, the shot start coordinate.
        if not self.shot_path_possible or not self.shot_made: 
            shot_coordinates = [0, shot_start_x, shot_start_y, shot_start_z]
            self.shot_path_coordinates_df = pd.DataFrame([shot_coordinates], columns=['shot_coord_index', 'x', 'y', 'z'])
            return 

        shot_vertex_z = self.shot_vertex_z

        # default calculation method
        if not self.calculate_side_on:
            shot_vertex_x = self.__calculate_parabola_vertex(shot_start_x, shot_start_z, hoop_x, hoop_z, shot_vertex_z)
            
            a = self.__calculate_2d_parabola_coefficient_a(shot_start_x, shot_start_z, shot_vertex_x, shot_vertex_z)
            
            y_shift = hoop_y - shot_start_y
            y_shift_per_coord = y_shift / num_coords

            for index, x in enumerate(np.linspace(shot_start_x, hoop_x, num_coords + 1)):

                z = a * (x - shot_vertex_x)**2 + shot_vertex_z
                shot_path_coords.append([index, x, shot_start_y + (y_shift_per_coord * index), z])

        # alternate calculation method        
        else:
            shot_vertex_y = self.__calculate_parabola_vertex(shot_start_y, shot_start_z, hoop_y, hoop_z, shot_vertex_z)

            a = self.__calculate_2d_parabola_coefficient_a(shot_start_y, shot_start_z, shot_vertex_y, shot_vertex_z)

            x_shift = hoop_x - shot_start_x
            x_shift_per_coord = x_shift / num_coords

            for index, y in enumerate(np.linspace(shot_start_y, hoop_y, num_coords + 1)):
                z = a * (y - shot_vertex_y)**2 + shot_vertex_z
                shot_path_coords.append([index, shot_start_x + (x_shift_per_coord * index), y, z])

        self.shot_path_coordinates_df = pd.DataFrame(shot_path_coords, columns=['shot_coord_index', 'x', 'y', 'z'])

    def get_shot_path_coordinates(self) -> pd.DataFrame:
        '''
        Returns a dataframe of the estimated shot trajectory
        '''
        self.__calculate_shot_path_coordinates()

        self.shot_path_coordinates_df['line_id'] = self.shot_id
        self.shot_path_coordinates_df['description'] = self.play_description
        self.shot_path_coordinates_df['shot_made'] = 'made' if self.shot_made else 'missed' 
        self.shot_path_coordinates_df['team'] = self.team

        return self.shot_path_coordinates_df
