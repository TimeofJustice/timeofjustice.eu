from scipy.spatial import cKDTree


def rgb_to_hex(rgb):
    return '#{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def find_nearest_color(color_array, target_color):
    tree = cKDTree(color_array)
    _, index = tree.query(target_color[:3])
    return color_array[index]
