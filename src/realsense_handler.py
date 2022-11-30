import pyrealsense2 as rs
import numpy as np
import cv2
import plane_detection
import time
import random


class RealsenseHandler():
    def __init__(self) -> None:
        self.pipeline = rs.pipeline()
        self.pc = rs.pointcloud()

        config = rs.config()
        # config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
        # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

        profile = self.pipeline.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: ", depth_scale)

        clipping_distance_in_meters = 1  # 1 meter
        self.clipping_distance = clipping_distance_in_meters / depth_scale

        # align_to = rs.stream.depth
        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.color_map = []
        for i in range(100):
            r = random.random()*255
            g = random.random()*255
            b = random.random()*255
            self.color_map.append((b, g, r))

    def getFrames(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        # aligned_depth_frame = frames.get_depth_frame()
        # color_frame = frames.get_color_frame()
        self.depth = aligned_depth_frame

        if not aligned_depth_frame or not color_frame:
            return None, None

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        self.w = depth_image.shape[1]
        self.h = depth_image.shape[0]

        return color_image, depth_image

    def removeBackground(self, color_image, depth_image):
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
        bg_removed = np.where((depth_image_3d > self.clipping_distance) | (
            depth_image_3d <= 0), grey_color, color_image)
        return bg_removed

    def combineImages(self, image1, image2):
        if image1.shape != image2.shape:
            image2 = cv2.resize(image1, image2.shape[:2])
        images = np.hstack((image1, image2))
        return images

    def getPointCloud(self):
        points = self.pc.calculate(self.depth)
        self.pc.map_to(self.depth)

        v, t = points.get_vertices(), points.get_texture_coordinates()
        verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
        texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv

        return verts, texcoords

    def project(self, v):
        """project 3d vector array to 2d"""
        h, w = self.h, self.w
        view_aspect = float(h)/w
        # ignore divide by zero for invalid depth
        with np.errstate(divide='ignore', invalid='ignore'):
            proj = v[:, :-1] / v[:, -1, np.newaxis] * \
                (w*view_aspect, h) + (w/2.0, h/2.0)

        # near clipping
        znear = 0.03
        proj[v[:, 2] < znear] = np.nan
        return proj

    def detectPlanes(self, points, texcoords, down_sampling_rate=0.021):
        # points = utils.DownSample(points, voxel_size=0.3)
        points = points[::int(1.0/down_sampling_rate)]
        texcoords = texcoords[::int(1.0/down_sampling_rate)]

        points = plane_detection.RemoveNoiseStatistical(
            points, nb_neighbors=100, std_ratio=20)
        results = plane_detection.DetectMultiPlanes(
            points, min_ratio=0.3, threshold=0.05, iterations=1000)

        return results  # array of (equatino, points)

    def drawPlanes(self, image, results, marker_size=1):
        for n, (eq, plane) in enumerate(results):
            proj = self.project(plane)
            j, i = proj.astype(np.uint32).T
            m = (i >= 0) & (i < self.h) & (j >= 0) & (j < self.w)
            im = i[m]
            jm = j[m]

            for i_h, j_w in zip(im, jm):
                cv2.circle(image, (j_w, i_h),
                           marker_size, self.color_map[n % 100], thickness=-1)
            break
        return image

    def __del__(self):
        self.pipeline.stop()


if __name__ == "__main__":
    RSH = RealsenseHandler()
    try:
        while True:
            color_image, depth_image = RSH.getFrames()
            points, texcoords = RSH.getPointCloud()
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                depth_image, alpha=0.1), cv2.COLORMAP_JET)
            t0 = time.time()

            results = RSH.detectPlanes(
                points, texcoords, down_sampling_rate=1/49)

            # color_image = RSH.drawPlanes(color_image, results)
            # depth_image = RSH.drawPlanes(depth_image, results)
            # images = RSH.combineImages(color_image, depth_image)
            color_image = RSH.drawPlanes(color_image, results)
            depth_colormap = RSH.drawPlanes(depth_colormap, results)
            images = np.hstack((color_image, depth_colormap))
            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        print("closing")
        time.sleep(1)
        cv2.destroyAllWindows()
        del RSH
