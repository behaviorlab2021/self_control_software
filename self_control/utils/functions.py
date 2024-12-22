from kivy.core.window import Window

def distance_from(x1, y1, x2, y2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2),
    adjusting for the aspect ratio.
    """
    distance_x = (x1 - x2) 
    distance_y = (y1 - y2)
    return (distance_x ** 2 + distance_y ** 2) ** 0.5

def is_within_ellipse(click_x, click_y, center_x_norm, center_y_norm, radius_norm, aspect_ratio):
    """
    Check if a click is within a circle, considering the window's aspect ratio.
    Parameters:
    - click_x, click_y: Normalized click coordinates (0 to 1).
    - center_x_norm, center_y_norm: Normalized circle center (0 to 1).
    - radius_norm: Normalized radius of the circle (0 to 1).
    - aspect_ratio: The aspect ratio of the window (width / height).
    """

    # Adjust the click coordinates for the aspect ratio
    adjusted_click_x = click_x * aspect_ratio
    adjusted_center_x = center_x_norm * aspect_ratio

    # Calculate the distance with the adjusted coordinates
    distance = distance_from(adjusted_click_x, click_y, adjusted_center_x, center_y_norm)

    return distance <= radius_norm
