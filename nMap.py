
#will create a function to confine the colors for the hight mapping to a range
#takes in a value and maps it to the min and max of a range, that way we can map to a color range of like 80-255 (rgb)
def nMap(n, min1, max1, min2, max2):
    return ((n-min1)/(max1-min1))*(max2-min2)+min2