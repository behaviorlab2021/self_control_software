def distance_from_center (point_x, point_y, center_x, center_y, aspect_ratio):
    return (((point_x - center_x) * aspect_ratio) **2 + (point_y - center_y)**2 ) ** 0.5
