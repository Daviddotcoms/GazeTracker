import time
import cv2
import numpy as np
from collections import deque

from gaze_app_v4.gaze_heatmap import GazeHeatmap


class OptimizedGazeHeatmap(GazeHeatmap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gaze_buffer = deque(maxlen=1000)
        self.last_update = time.time()
        self.current_overlay = None
        
        self.kernel = self._create_gaussian_kernel(self.blur_radius)
        
    def _create_gaussian_kernel(self, sigma):
        """Precompute Gaussian kernel for faster convolution"""
        kernel_size = int(2 * sigma) * 2 + 1
        kernel = cv2.getGaussianKernel(kernel_size, sigma)
        return kernel * kernel.T

    def add_gaze_point(self, x, y, intensity=1.0):
        """Store gaze points in buffer for batch processing"""
        self.gaze_buffer.append((x, y, intensity))

    def _process_buffer(self):
        """Batch process all buffered gaze points"""
        while self.gaze_buffer:
            x, y, intensity = self.gaze_buffer.popleft()
            if 0 <= x < self.heatmap.shape[1] and 0 <= y < self.heatmap.shape[0]:
                self.heatmap[y, x] += intensity

    def update(self):
        """Only update at fixed intervals"""
        now = time.time()
        if now - self.last_update >= 0.25:
            self._process_buffer()
            
            self.heatmap *= self.decay_factor ** (0.5 * 30)
            
            blurred = cv2.filter2D(self.heatmap, -1, self.kernel)
            
            normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
            self.current_overlay = self.color_lut[normalized.astype(np.uint8)]
            
            self.last_update = now
            
        return self.current_overlay

    def overlay_on_frame(self, frame):
        """Optimized overlay using cached heatmap"""
        if self.current_overlay is None:
            return frame
            
        if not hasattr(self, 'overlay_cache'):
            self.overlay_cache = cv2.resize(self.current_overlay, 
                                          (frame.shape[1], frame.shape[0]))
            
        alpha = self.overlay_cache[..., 3] / 255.0
        overlay = frame.copy()
        for c in range(3):
            overlay[..., c] = overlay[..., c] * (1 - alpha) + \
                             self.overlay_cache[..., c] * alpha
        return overlay.astype(np.uint8)