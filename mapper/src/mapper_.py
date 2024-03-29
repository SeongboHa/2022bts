#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from mapper.msg import detection, detections
import cv2
import numpy as np
import math

class mapper():
    def __init__(self):

        lidar_topic = "/scan"
        self.image_size = 640
        self.detections = detections()
        self.lidar_data = LaserScan()

        rospy.Subscriber(lidar_topic, LaserScan, self.lidar_input)
        rospy.Subscriber("detections", detections, self.detection_input)
        
        rospy.spin()

    def lidar_input(self, data):
        self.lidar_data = data
        #self.lidar_data.ranges[degree]

    def detection_input(self, data):
        self.detections = data
        self.mapping2(self.lidar_data, self.detections.detections)

    def mapping2(self, lidar_data, detections):
        projected = []

        # lidar 값들 평면에 사영

        for i in range(60,0,-1):
            if lidar_data.ranges[i] != float("inf"):
                projected.append((i, int(320 - 550/math.tan(math.radians(90 - i)))))

        for i in range(359,300,-1):
            if lidar_data.ranges[i] != float("inf"):
                projected.append((i, int(320 + 550/math.tan(math.radians(30 + (i-300))))))
        
        # test_image = np.zeros((640,640, 3))
        # print(projected)
        # for points in projected:
        #     cv2.line(test_image, (points, 360), (points, 360), (255,255,0), 3)

        # cv2.imshow("points", test_image)
        # cv2.waitKey(1)

        created_map = np.zeros((1000,1000,3))

        #objects = []
        # point cloud에 class 부여
        # objects 배열에 (class, x, y)로 저장
        for i in range(len(detections)):
            xmin = detections[i].xmin
            xmax = detections[i].xmax
            x = []
            y = []
            for degree, point in projected:
                if (point <= xmax and point >= xmin):
                    # range, degree값을 2차원 평면좌표로 변환
                    # 좌, 우 x축, 앞 뒤 y축    
                    xx = lidar_data.ranges[degree] * math.cos(math.radians(90+degree))
                    yy = -(lidar_data.ranges[degree] * math.sin(math.radians(90+degree)))

                    x.append(xx)
                    y.append(yy)
            
            np_x = np.array(x)
            np_y = np.array(y)

            map_x = int(500 + np.average(np_x) * 150)
            map_y = int(500 + np.average(np_y) * 150)

            cv2.rectangle(created_map, (map_x-9, map_y-9), (map_x+9, map_y+9), (255,255,0), 1)
            cv2.putText(created_map, detections[i].name, (map_x, map_y-14), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
        
        created_map = cv2.resize(created_map,(720, 720))
        cv2.imshow("map", created_map)
        cv2.waitKey(1)
        



    def mapping(self, lidar_data, detections):

        projected = []

        # lidar 값들 평면에 사영

        for i in range(60,0,-1):
            if lidar_data.ranges[i] != float("inf"):
                projected.append((i, int(320 - 550/math.tan(math.radians(90 - i)))))

        for i in range(359,300,-1):
            if lidar_data.ranges[i] != float("inf"):
                projected.append((i, int(320 + 550/math.tan(math.radians(30 + (i-300))))))
        
        test_image = np.zeros((640,640, 3))
        print(projected)
        for points in projected:
            cv2.line(test_image, (points, 360), (points, 360), (255,255,0), 3)

        cv2.imshow("points", test_image)
        cv2.waitKey(1)

if __name__ =='__main__':
    rospy.init_node("mapper")
    mapper()