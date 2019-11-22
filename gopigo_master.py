import cv2
import numpy as np
from easygopigo3 import EasyGoPiGo3
font = cv2.FONT_HERSHEY_COMPLEX


class Robot:
    '''Class for controlling the GoPiGo3
    '''
    
    def __init__(self):
        try:
            self.gopigo3_robot = EasyGoPiGo3() # init gopigo3
            self.gopigo3_robot.set_speed(500) # adjust this accordingly
        except IOError:
            print("GoPiGo3 robot not detected")
            exit(0)
        try:
            self.distance_sensor = self.gopigo3_robot.init_distance_senseor() # init dist sensor
        except:
            print("GoPiGo3 distance sensor not detected")
            exit(0)
        try:
            self.servo = self.gopigo3_robot.init_servo() # init servo
            self.servo.reset_servo() # reset servo to straight ahead
        except:
            print("GoPiGo3 servo not detected")
            exit(0)
        
    def basic_controls(self, command): # allow for basic control of gopigo3
        if command == 'forward':
            self.gopigo3_robot.forward()
            return 'moving forward'
        elif command == 'backward':
            self.gopigo3_robot.backward()
            return 'moving backward'
        elif command == 'left':
            self.gopigo3_robot.left()
            return 'turning left'
        elif command == 'right':
            self.gopigo3_robot.right()
            return 'turning right'
        elif command == 'stop':
            self.gopigo3_robot.stop()
            return 'stopping'
        
    def orbit_robot(self, degrees, radius_cm=0):
        if (type(degrees) == int) & (type(radius_cm) == int) & (degrees >= -360 & degrees <= 360):
            self.gopigo3_robot.orbit(degrees, radius_cm)
        else:
            print('Unable to orbit with GoPiGo3')      
    
    def read_distance(self):
        return self.distance_sensor.read_mm() # return distance to nearest object in mm
        
    def rotate_serv(self, degrees): # rotate servo
        if (type(degrees) == int) & (degrees >= 0 & degrees <= 180):
            self.servo.rotate_servo(degrees)
        else:
            print('Unable to rotate servo')


class Camera:
    '''Class for connecting to camera.
    '''
    
    def __init__(self):
        try:
            self.cap = cv2.VideoCapture(0)
        except:
            print('--(!)Error connecting to webcam')
            exit(0)
        
    def get_cap(self):
        return self.cap
            
            
class Cone_Color:
    '''Class for setting RGB ranges for cone color.
    '''
    
    def __init__(self, color):
        if color.lower() == 'orange':
            self.color_MIN = np.array([0, 83, 255],np.uint8)
            self.color_MAX = np.array([178, 230, 255],np.uint8)
        elif color.lower() == 'yellow':
            self.color_MIN = np.array([17, 40, 185],np.uint8)
            self.color_MAX = np.array([74, 120, 255],np.uint8)
        elif color.lower() == 'green':
            self.color_MIN = np.array([67, 60, 164],np.uint8)
            self.color_MAX = np.array([180, 255, 243],np.uint8)
        elif color.lower() == 'steve':
            self.color_MIN = np.array([0, 77, 84],np.uint8)
            self.color_MAX = np.array([15, 183, 212],np.uint8)
        else:
            print('--(!)Error setting cone color')
            exit(0)
            
    def color_range(self):
        return self.color_MIN, self.color_MAX
    
    
class Cone:
    '''Class for finding a cone. Returns boolean, cones location as dict.
    '''
    def __init__(self, color):
        
        self.cone = Cone_Color(color)
        self.color_MIN, self.color_MAX = self.cone.color_range()
        self.cap = Camera().get_cap()
        self.cone_color = f'{color} Cone'
        
    def find_cone(self):
        loc = 0
    
        while loc<1:
            _, frame = self.cap.read()
            # Flip video for camera upside down
            #frame = cv2.flip(frame, -1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
            mask = cv2.inRange(hsv, self.color_MIN, self.color_MAX)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel)
        
            # Contours detection
            if int(cv2.__version__[0]) > 3:
                # Opencv 4.x.x
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            else:
                # Opencv 3.x.x
                _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
            for cnt in contours:
                area = cv2.contourArea(cnt)
                approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True)
                x = approx.ravel()[0]
                y = approx.ravel()[1]
        
                if area > 400:
                    cone_color_area = self.cone_color #, " ", area
                    cv2.drawContours(frame, [approx], 0, (0, 0, 0), 5)
        
                    if len(approx) == 4:
                        cv2.putText(frame, cone_color_area, (x, y), font, 1, (0, 0, 0))
                        loc=2
        
                        
            cv2.imshow("Frame", frame)
        
            key = cv2.waitKey(1)
            if key == 27:
                break
        
        self.cap.release()
        cone_hloc = int(x)
        center = (int(x),int(y))
        print(self.color_MIN)
        print(self.color_MAX)
        print(self.color + " cone")
        
#        answer = input('press enter to continue:')
        cv2.destroyAllWindows()
        return self.cone, area, center, cone_hloc
    
    
color = input("Please enter color: ")
cone, area, center, cone_hloc = Cone(color).find_cone()
print (f"I found the {color} Cone + and it is {area} units big, located at {center}  and specificially at {cone_hloc} on the horizontal axis.")
