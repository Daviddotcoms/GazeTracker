import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

class GazeHeatmap:
    def __init__(self, frame_shape=(768, 1366), blur_radius=30, decay_factor=0.94):
        self.heatmap = np.zeros(frame_shape[:2], dtype=np.float32)
        self.blur_radius = blur_radius
        self.decay_factor = decay_factor
        
        self.color_lut = self._create_color_lookup_table()
        
    def _create_color_lookup_table(self):
        indices = [0, 30, 50, 80, 90, 100, 120, 200]
        rgbs = [
            (50, 50, 50),   
            (50, 50, 50),    
            (0, 0, 200),     
            (0, 255, 200),   
            (0, 255, 0),     
            (0, 255, 0),     
            (255, 255, 0),  
            (255, 0, 0)      
        ]
        alphas = [0, 0, 50, 50, 50, 200, 200, 200]
        
        lut = np.zeros((256, 4), dtype=np.uint8)
        for i in range(256):
            idx = np.searchsorted(indices, i)
            if idx == 0:
                t = 0.0
                low, high = indices[0], indices[0]
            elif idx >= len(indices):
                t = 1.0
                low, high = indices[-1], indices[-1]
            else:
                low = indices[idx-1]
                high = indices[idx]
                t = (i - low) / (high - low) if high != low else 0.0
                
            if idx == 0 or idx >= len(rgbs):
                rgb = rgbs[min(idx, len(rgbs)-1)]
                alpha = alphas[min(idx, len(alphas)-1)]
            else:
                rgb_low = np.array(rgbs[idx-1])
                rgb_high = np.array(rgbs[idx])
                alpha_low = alphas[idx-1]
                alpha_high = alphas[idx]
                
                rgb = (rgb_low * (1 - t) + rgb_high * t).astype(int)
                alpha = int(alpha_low * (1 - t) + alpha_high * t)
            
            lut[i] = [*rgb, alpha]
            
        return lut

    def add_gaze_point(self, x, y, intensity=1.0):
        if 0 <= x < self.heatmap.shape[1] and 0 <= y < self.heatmap.shape[0]:
            self.heatmap[y, x] += intensity

    def update(self):
        self.heatmap *= self.decay_factor
        blurred = gaussian_filter(self.heatmap, sigma=self.blur_radius)
        normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
        indices = normalized.astype(np.uint8)
        colored = self.color_lut[indices]
        
        return colored

    def overlay_on_frame(self, frame, heatmap):
        heatmap_bgra = cv2.cvtColor(heatmap, cv2.COLOR_RGBA2BGRA)
        
        if heatmap_bgra.shape[:2] != frame.shape[:2]:
            heatmap_bgra = cv2.resize(heatmap_bgra, (frame.shape[1], frame.shape[0]))
            
        alpha = heatmap_bgra[..., 3] / 255.0
        overlay = frame.copy()
        for c in range(3):
            overlay[..., c] = overlay[..., c] * (1 - alpha) + heatmap_bgra[..., c] * alpha
            
        return overlay.astype(np.uint8)