import cv2
import mediapipe as mp
import numpy as np
import time
import collections
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pyautogui

from core.gaze_heatmap import GazeHeatmap

class GazeTracker:
    def __init__(self, smoothing_factor=0.35, buffer_size=7):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.show_landmarks = False
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.8,

        )
        
        self.smoothing_factor = smoothing_factor
        self.buffer_size = buffer_size
        self.gaze_x_buffer = collections.deque(maxlen=buffer_size)
        self.gaze_y_buffer = collections.deque(maxlen=buffer_size)
        self.last_smoothed_x = None
        self.last_smoothed_y = None
        
        self.right_eye_indices = [33, 133, 157, 158, 159, 160, 161, 173, 155, 154, 153, 145, 144, 163, 139]
        self.left_eye_indices = [
            263, 362, 385, 386, 387, 388, 389, 390,  # puntos externos
            373, 374, 380, 381, 382,                # puntos internos
            263, 249, 390, 373, 374                  # puntos adicionales para mejorar seguimiento vertical
        ]
        self.right_iris_indices = [469, 470, 471, 472]
        self.left_iris_indices = [474, 475, 476, 477]

        self.SCREEN_W, self.SCREEN_H = pyautogui.size()


        self.calibration_points = [
            (self.SCREEN_W // 4, self.SCREEN_H // 8),        
            (self.SCREEN_W * 3 // 4, self.SCREEN_H // 8),      
            (self.SCREEN_W // 2, self.SCREEN_H // 2),          
            (self.SCREEN_W // 4, self.SCREEN_H * 7 // 8),      
            (self.SCREEN_W * 3 // 4, self.SCREEN_H * 7 // 8)   
        ]
        
        self.calibration_data = {point: [] for point in self.calibration_points}
        self.calibration_matrix = None

    def smooth_gaze(self, new_x, new_y):
        if self.last_smoothed_x is None:
            self.last_smoothed_x = new_x
            self.last_smoothed_y = new_y
            self.gaze_x_buffer.append(new_x)
            self.gaze_y_buffer.append(new_y)
            return new_x, new_y

        smoothed_x = (self.smoothing_factor * new_x + (1 - self.smoothing_factor) * self.last_smoothed_x)
        smoothed_y = (self.smoothing_factor * new_y + (1 - self.smoothing_factor) * self.last_smoothed_y)
        self.gaze_x_buffer.append(smoothed_x)
        self.gaze_y_buffer.append(smoothed_y)
        avg_x = np.mean(self.gaze_x_buffer)
        avg_y = np.mean(self.gaze_y_buffer)
        self.last_smoothed_x = avg_x
        self.last_smoothed_y = avg_y
        return int(avg_x), int(avg_y)

    def _get_bounding_box(self, landmarks, indices, frame_w, frame_h):
        pts = np.array([(int(landmarks[i].x * frame_w), int(landmarks[i].y * frame_h)) for i in indices])
        x_min, y_min = np.min(pts, axis=0)
        x_max, y_max = np.max(pts, axis=0)
        padding = 10
        return max(0, x_min - padding), max(0, y_min - padding), min(frame_w, x_max + padding), min(frame_h, y_max + padding)

    def _get_iris_center(self, landmarks, iris_indices, frame_w, frame_h):
        pts = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in iris_indices])
        iris_x = np.median(pts[:, 0])
        iris_y = np.median(pts[:, 1])
        return tuple(map(int, (iris_x, iris_y)))

    def _compute_gaze_ratio(self, eye_bbox, iris_center):
        x_min, y_min, x_max, y_max = eye_bbox
        eye_width = x_max - x_min
        eye_height = y_max - y_min

        if eye_width == 0 or eye_height == 0:
            return 0.5, 0.5

        ratio_x = max(0, min(1, (iris_center[0] - x_min) / eye_width))
        ratio_y = max(0, min(1, (iris_center[1] - y_min) / eye_height))
        ratio_y = np.power(ratio_y, 1.8)  # mayor énfasis vertical
        return ratio_x, ratio_y

    def advanced_calibration(self, duration_per_point=7):
        self.SCREEN_W, self.SCREEN_H = pyautogui.size()
        
        cap = cv2.VideoCapture(0)
        
        for point_index, point in enumerate(self.calibration_points):
            calibration_screen = np.zeros((self.SCREEN_H, self.SCREEN_W, 3), dtype=np.uint8)
            cv2.circle(calibration_screen, point, 40, (0, 174, 42), -1)
            cv2.circle(calibration_screen, point, 45, (255, 255, 255), 3)

            
            cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Calibration", calibration_screen)
            cv2.waitKey(1000) 
            
            start_time = time.time()
            point_data = []
            while time.time() - start_time < duration_per_point:
                success, frame = cap.read()
                if not success:
                    break
                frame = cv2.flip(frame, 1)
                frame_h, frame_w, _ = frame.shape
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:

                        right_eye_bbox = self._get_bounding_box(face_landmarks.landmark, self.right_eye_indices, frame_w, frame_h)
                        right_iris_center = self._get_iris_center(face_landmarks.landmark, self.right_iris_indices, frame_w, frame_h)
                        right_ratio = self._compute_gaze_ratio(right_eye_bbox, right_iris_center)

                        left_eye_bbox = self._get_bounding_box(face_landmarks.landmark, self.left_eye_indices, frame_w, frame_h)
                        left_iris_center = self._get_iris_center(face_landmarks.landmark, self.left_iris_indices, frame_w, frame_h)
                        left_ratio = self._compute_gaze_ratio(left_eye_bbox, left_iris_center)

                        avg_ratio_x = (right_ratio[0] * 0.6 + left_ratio[0] * 0.4)
                        avg_ratio_y = (right_ratio[1] * 0.6 + left_ratio[1] * 0.4)
                        point_data.append((avg_ratio_x, avg_ratio_y))
                
                remaining_time = int(duration_per_point - (time.time() - start_time))
                calibration_screen = np.zeros((self.SCREEN_H, self.SCREEN_W, 3), dtype=np.uint8)
                cv2.circle(calibration_screen, point, 40, (0, 174, 42), -1)
                cv2.line(calibration_screen, (point[0]-10, point[1]), (point[0]+10, point[1]), (255, 255, 255), 2)
                cv2.line(calibration_screen, (point[0], point[1]-10), (point[0], point[1]+10), (255, 255, 255), 2)
                cv2.putText(calibration_screen, f"{remaining_time}s", 
                            (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Calibration", calibration_screen)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            self.calibration_data[point] = point_data
        
        cap.release()
        cv2.destroyAllWindows()
        self._compute_advanced_calibration_matrix()
        return self.calibration_data

    def _compute_advanced_calibration_matrix(self):
        """Crea la matriz de calibración usando regresión polinomial (grado 2)."""
        X, y_x, y_y = [], [], []
        for point, data in self.calibration_data.items():
            for ratio in data:
                X.append(list(ratio))
                y_x.append(point[0])
                y_y.append(point[1])
        if X:
            poly = PolynomialFeatures(degree=1)
            X_poly = poly.fit_transform(X)
            regressor_x = LinearRegression()
            regressor_y = LinearRegression()
            regressor_x.fit(X_poly, y_x)
            regressor_y.fit(X_poly, y_y)
            self.calibration_matrix = (regressor_x, regressor_y, poly)

    def map_gaze_to_screen(self, gaze_ratios):
        """Mapeo avanzado de los ratios al tamaño de la pantalla."""
        if self.calibration_matrix is None:
            pointer_x = int(gaze_ratios[0] * self.SCREEN_W)
            pointer_y = int(np.power(gaze_ratios[1], 1.2) * self.SCREEN_H)
        else:
            regressor_x, regressor_y, poly = self.calibration_matrix
            gaze_poly = poly.transform([gaze_ratios])
            pointer_x = int(regressor_x.predict(gaze_poly)[0])
            pointer_y = int(regressor_y.predict(gaze_poly)[0])
        return max(0, min(pointer_x, self.SCREEN_W)), max(0, min(pointer_y, self.SCREEN_H))

    def process_gaze(self, frame):
        """Procesa la imagen y devuelve las coordenadas de la pantalla tras suavizar."""
        frame_h, frame_w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                right_eye_bbox = self._get_bounding_box(face_landmarks.landmark, self.right_eye_indices, frame_w, frame_h)
                right_iris_center = self._get_iris_center(face_landmarks.landmark, self.right_iris_indices, frame_w, frame_h)
                right_ratio = self._compute_gaze_ratio(right_eye_bbox, right_iris_center)
                
                left_eye_bbox = self._get_bounding_box(face_landmarks.landmark, self.left_eye_indices, frame_w, frame_h)
                left_iris_center = self._get_iris_center(face_landmarks.landmark, self.left_iris_indices, frame_w, frame_h)
                left_ratio = self._compute_gaze_ratio(left_eye_bbox, left_iris_center)
                
                avg_ratio_x = (right_ratio[0] * 0.6 + left_ratio[0] * 0.4)
                avg_ratio_y = (right_ratio[1] * 0.6 + left_ratio[1] * 0.4)
                
                pointer_x, pointer_y = self.map_gaze_to_screen((avg_ratio_x, avg_ratio_y))
                return self.smooth_gaze(pointer_x, pointer_y), face_landmarks
        return None, None

    def show_eye_landmarks(self, frame, face_landmarks, show_eyes=True, show_iris=True, show_indices=False):
        frame_h, frame_w = frame.shape[:2]
        
        eye_color = (0, 255, 0)
        iris_color = (0, 0, 255)
        index_color = (255, 255, 255)
        landmark_radius = 1
        iris_radius = 2
        font_scale = 0.4
        
        if show_eyes:
            for idx in self.right_eye_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), landmark_radius, eye_color, -1)
                if show_indices:
                    cv2.putText(frame, str(idx), (x+2, y-2), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, index_color, 1)
            
            for idx in self.left_eye_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), landmark_radius, eye_color, -1)
                if show_indices:
                    cv2.putText(frame, str(idx), (x+2, y-2), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, index_color, 1)

        if show_iris:
            for idx in self.right_iris_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), iris_radius, iris_color, -1)
                if show_indices:
                    cv2.putText(frame, str(idx), (x+2, y-2), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, index_color, 1)
            
            for idx in self.left_iris_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), iris_radius, iris_color, -1)
                if show_indices:
                    cv2.putText(frame, str(idx), (x+2, y-2), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, index_color, 1)

        return frame

gaze_tracker = GazeTracker(
    smoothing_factor=0.36,
    buffer_size=7
)

optimized_heatmap = GazeHeatmap(blur_radius=40, decay_factor=0.95)

def startCalibration():
    gaze_tracker.advanced_calibration()

def main():
    cap = cv2.VideoCapture(0)
    gaze_path = []

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        result, face_landmarks = gaze_tracker.process_gaze(frame)

        if result:
            pointer_x, pointer_y = result
            # optimized_heatmap.add_gaze_point(pointer_x, pointer_y)
            # heatmap_frame = optimized_heatmap.update()
            # frame = optimized_heatmap.overlay_on_frame(frame, heatmap_frame)
            
            if gaze_tracker.show_landmarks:
                frame = gaze_tracker.show_eye_landmarks(
                    frame, face_landmarks,
                    show_eyes=True,
                    show_iris=True,
                    show_indices=False
                )
            
            gaze_path.append((pointer_x, pointer_y))
            if len(gaze_path) > 100:
                gaze_path.pop(0)
            
            gaze_screen = np.zeros((gaze_tracker.SCREEN_H, gaze_tracker.SCREEN_W, 3), dtype=np.uint8)
            # SHOW THE EYE TRACKING POINT 
            # if len(gaze_path) > 1:
            #     for i in range(1, len(gaze_path)):
            #         cv2.line(gaze_screen, gaze_path[i-1], gaze_path[i], (0, 255, 255), 2)
            # if gaze_path:
            #     cv2.circle(gaze_screen, gaze_path[-1], 20, (0, 0, 255), -1)
            
            cv2.imshow("Gaze Tracker", gaze_screen)

        cv2.imshow("Webcam Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()