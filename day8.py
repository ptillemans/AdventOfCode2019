import numpy as np
import pytest


with open('day8_input.txt', 'r') as f:
    day8_input = f.read().strip()
    
    
def split_layers(input, rows, cols):
    data = [int(c) for c in input]
    layers = len(data) // (rows * cols)   
    return np.array(data).reshape((layers, rows, cols))
    
def count_elements_equal(arr, value):
    return (arr == value).sum()

def checksum(image, layers):
    layer = min([image[i] for i in range(layers)], key=lambda arr: count_elements_equal(arr, 0))
    ones = count_elements_equal(layer, 1)
    twos = count_elements_equal(layer, 2)
    return ones * twos
    
def flatten_image(image):
    reducer = np.frompyfunc(lambda r, x: x if r == 2 else r, 2, 1)
    return reducer.reduce(image, axis=0)
    
def test_split_layers():
    image_input = '123456789012'
    image = split_layers(image_input, 2, 3)
    expected = np.array([[[1, 2, 3], 
                          [4, 5, 6]], 
                         [[7, 8, 9], 
                          [0, 1, 2]]])
    assert np.array_equal(image, expected)
    
def test_count_elements():
    arr = np.array([[1, 2, 3], [2, 3, 2]])
    assert count_elements_equal(arr, 2) == 3
    
                                                          
if __name__ == '__main__':
    pytest.main([__file__])
    
    image = split_layers(day8_input, 6, 25)
    (layers, cols, rows) = image.shape
    print(f'dimensions{image.shape}')
    check = checksum(image, layers)
    print(f'check: {check}')
    flattened = flatten_image(image)
    print(flattened)
    (rows, cols) = flattened.shape
    for row in range(rows):
        print(['X' if x == 1 else ' ' for x in flattened[row]])
