import pandas as pd 
import numpy as np 

class CourtCoordinates:
    '''
    Stores court dimensions and calculates the (x,y,z) coordinates of the outside perimeter, 
    three point line, backboard, and hoop.
    The default dimensions of a men's ncaa court according to https://modutile.com/basketball-half-court-dimensions/#
    '''
    def __init__(self):
        self.court_length = 94                 # the court is 94 feet long
        self.court_width = 50                  # the court is 50 feet wide
        self.hoop_loc_x = 25                   # we will build a court with the center, length-wise, being right at 0 on the x-axis
        self.hoop_loc_y = 4.25                 # the center of the hoop is 63 inches from the baseline
        self.hoop_loc_z = 10                   # the hoop is 10 feet off the ground
        self.hoop_radius = .75
        self.three_arc_distance = 22.146       # the NCAA men's three arc is 22ft and 1.75in from the center of the hoop
        self.three_straight_distance = 21      # the NCAA men's three straight section is 21ft 8in from the center of the hoop
        self.three_straight_length = 8.89      # the NCAA men's three straight section length is 8ft and 10.75in
        self.backboard_width = 6               # backboard is 6ft wide
        self.backboard_height = 4              # backboard is 4ft tall
        self.backboard_baseline_offset = 3     # backboard is 3ft from the baseline
        self.backboard_floor_offset = 9        # backboard is 9ft from the floor

    @staticmethod
    def calculate_quadratic_values(a, b, c):
        '''
        Given values a, b, and c,
        the function returns the output of the quadratic formula
        '''
        x1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        x2 = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

        return x1, x2

    def __get_court_perimeter_coordinates(self):
        '''
        Returns coordinates of full court perimeter lines. A court that is 50 feet wide and 94 feet long
        In shot chart data, each foot is represented by 10 units.
        '''
        width = self.court_width
        length = self.court_length
        court_perimeter_bounds = [
            [0, 0, 0], 
            [width, 0, 0], 
            [width, length, 0], 
            [0, length, 0], 
            [0, 0, 0]
        ]

        court_df = pd.DataFrame(court_perimeter_bounds, columns=['x','y','z'])
        court_df['line_group'] = 'outside_perimeter'
        court_df['color'] = 'court'
        
        return court_df
    
    def __get_half_court_coordinates(self):
        '''
        Returns coordinates for the half court line.
        '''
        width = self.court_width 
        half_length = self.court_length / 2
        half_court_bounds = [[0, half_length, 0], [width, half_length, 0]]

        half_df = pd.DataFrame(half_court_bounds, columns=['x','y','z'])
        half_df['line_group'] = 'half_court'
        half_df['color'] = 'court'

        return half_df

    def __get_backboard_coordinates(self, loc):
        '''
        Returns coordinates of the backboard on both ends of the court
        A backboard is 6 feet wide, 4 feet tall 
        '''

        backboard_start = (self.court_width/2)  -  (self.backboard_width/2)
        backboard_end = (self.court_width/2) + (self.backboard_width/2)
        height = self.backboard_height
        floor_offset = self.backboard_floor_offset
        if loc == 'far':
            offset = self.backboard_baseline_offset
        if loc == 'near':
            offset = self.court_length - self.backboard_baseline_offset

        backboard_bounds = [
            [backboard_start, offset, floor_offset], 
            [backboard_start, offset, floor_offset + height], 
            [backboard_end, offset, floor_offset + height], 
            [backboard_end, offset, floor_offset], 
            [backboard_start, offset, floor_offset]
        ]

        backboard_df = pd.DataFrame(backboard_bounds, columns=['x','y','z'])
        backboard_df['line_group'] = f'{loc}_backboard'
        backboard_df['color'] = 'court'

        return  backboard_df
    
    def __get_three_point_coordinates(self, loc):
        '''
        Returns coordinates of the three point line on both ends of the court
        Given that the ncaa men's three point line is 22ft and 1.5in from the center of the hoop
        '''
        
        # init values
        hoop_loc_x, hoop_loc_y = self.hoop_loc_x, self.hoop_loc_y
        strt_dst_start = (self.court_width/2) - self.three_straight_distance
        strt_dst_end = (self.court_width/2) + self.three_straight_distance
        strt_len = self.three_straight_length
        arc_dst = self.three_arc_distance

        start_straight = [
            [strt_dst_start,0,0],
            [strt_dst_start,strt_len,0]
        ]
        end_straight = [
            [strt_dst_end,strt_len,0], 
            [strt_dst_end,0,0]
        ]
        line_coordinates = []

        if loc == 'near': 
            crt_len = self.court_length
            hoop_loc_y = crt_len - hoop_loc_y
            start_straight = [[strt_dst_start,crt_len,0],[strt_dst_start,crt_len-strt_len,0]]
            end_straight = [[strt_dst_end,crt_len-strt_len,0], [strt_dst_end,crt_len,0]]

        # drawing the three point line
        line_coordinates.extend(start_straight)
        
        a = 1
        b = -2 * hoop_loc_y
        d = arc_dst 
        for x_coord in np.linspace(int(strt_dst_start), int(strt_dst_end), 100):
            c = hoop_loc_y ** 2 + (x_coord - 25) ** 2 - (d) ** 2

            y1, y2 = self.calculate_quadratic_values(a, b, c)
            if loc == 'far':
                y_coord = y1
            if loc == 'near':
                y_coord = y2
        
            line_coordinates.append([x_coord, y_coord, 0])

        line_coordinates.extend(end_straight)

        far_three_df = pd.DataFrame(line_coordinates, columns=['x', 'y', 'z'])
        far_three_df['line_group'] = f'{loc}_three'
        far_three_df['color'] = 'court'

        return far_three_df

    def __get_hoop_coordinates(self, loc):
        '''
        Returns the hoop coordinates of the far/near hoop
        '''
        hoop_coordinates_top_half = []
        hoop_coordinates_bottom_half = []

        hoop_loc_x, hoop_loc_y, hoop_loc_z = (self.hoop_loc_x, self.hoop_loc_y, self.hoop_loc_z)

        if loc == 'near': 
            hoop_loc_y = self.court_length - hoop_loc_y

        hoop_radius = self.hoop_radius
        hoop_min_x, hoop_max_x = (hoop_loc_x - hoop_radius, hoop_loc_x + hoop_radius)
        hoop_step = 0.1

        a = 1
        b = -2 * hoop_loc_y
        for hoop_coord_x in np.arange(hoop_min_x, hoop_max_x + hoop_step/2, hoop_step):
            c = hoop_loc_y ** 2 + (hoop_loc_x - round(hoop_coord_x,2)) ** 2 - hoop_radius ** 2
            hoop_coord_y1, hoop_coord_y2 = self.calculate_quadratic_values(a, b, c)

            hoop_coordinates_top_half.append([hoop_coord_x, hoop_coord_y1, hoop_loc_z])
            hoop_coordinates_bottom_half.append([hoop_coord_x, hoop_coord_y2, hoop_loc_z])

        hoop_coordinates_df = pd.DataFrame(hoop_coordinates_top_half + hoop_coordinates_bottom_half[::-1], columns=['x','y','z'])
        hoop_coordinates_df['line_group'] = f'{loc}_hoop'
        hoop_coordinates_df['color'] = 'hoop'
        
        return hoop_coordinates_df


    def get_court_lines(self):
        '''
        Returns a concatenated DataFrame of all the court coordinates 
        '''

        court_df = self.__get_court_perimeter_coordinates()
        half_df = self.__get_half_court_coordinates()
        backboard_home = self.__get_backboard_coordinates('near')
        backboard_away = self.__get_backboard_coordinates('far')
        hoop_away = self.__get_hoop_coordinates('near')
        hoop_home = self.__get_hoop_coordinates('far')
        three_home = self.__get_three_point_coordinates('near')
        three_away = self.__get_three_point_coordinates('far')

        court_lines_df = pd.concat([court_df, half_df, backboard_home, backboard_away, hoop_away, hoop_home, three_home, three_away])

        return court_lines_df
