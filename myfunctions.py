import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform

def get_camera_perspective(img, src_points):
    IMAGE_H = img.shape[0]
    IMAGE_W = img.shape[1]
    src = np.float32(np.array(src_points))
    dst = np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])

    M = cv2.getPerspectiveTransform(src, dst)
    M_inv = cv2.getPerspectiveTransform(dst, src)

    return M, M_inv

def plot_points_on_bird_eye_view(frame, pedestrian_boxes, M, scale_w, scale_h):
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    node_radius = 10
    color_node = (192, 133, 156)
    thickness_node = 20
    solid_back_color = (41, 41, 41)

    blank_image = np.zeros(
        (int(frame_h * scale_h), int(frame_w * scale_w), 3), np.uint8
    )
    blank_image[:] = solid_back_color
    warped_pts = []
    for i in range(len(pedestrian_boxes)):

        mid_point_x = int(
            (pedestrian_boxes[i][1] * frame_w + pedestrian_boxes[i][3] * frame_w) / 2
        )
        mid_point_y = int(
            (pedestrian_boxes[i][0] * frame_h + pedestrian_boxes[i][2] * frame_h) / 2
        )

        pts = np.array([[[mid_point_x, mid_point_y]]], dtype="float32")
        warped_pt = cv2.perspectiveTransform(pts, M)[0][0]
        warped_pt_scaled = [int(warped_pt[0] * scale_w), int(warped_pt[1] * scale_h)]

        warped_pts.append(warped_pt_scaled)
        bird_image = cv2.circle(
            blank_image,
            (warped_pt_scaled[0], warped_pt_scaled[1]),
            node_radius,
            color_node,
            thickness_node,
        )

    return warped_pts, bird_image

def plot_lines_between_nodes(warped_points, bird_image, d_thresh):
    p = np.array(warped_points)
    dist_condensed = pdist(p)
    dist = squareform(dist_condensed)

    # Close enough: 10 feet mark
    dd = np.where(dist < d_thresh * 6 / 10)
    close_p = []
    color_10 = (80, 172, 110)
    lineThickness = 4
    ten_feet_violations = len(np.where(dist_condensed < 10 / 6 * d_thresh)[0])
    for i in range(int(np.ceil(len(dd[0]) / 2))):
        if dd[0][i] != dd[1][i]:
            point1 = dd[0][i]
            point2 = dd[1][i]

            close_p.append([point1, point2])

            cv2.line(
                bird_image,
                (p[point1][0], p[point1][1]),
                (p[point2][0], p[point2][1]),
                color_10,
                lineThickness,
            )