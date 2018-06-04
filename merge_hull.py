from matplotlib import pyplot as plt
import random
import threading
import multiprocessing


class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __repr__(self):
        return '({}, {})'.format(self._x, self._y)

# Checks whether the turn around the point O from A to B is:
#     counterclockwise - if positive
#     clockwise - if negative
#     points are collinear - if zero
def cross(o, a, b):
    return (a._x - o._x) * (b._y - o._y) - (a._y - o._y) * (b._x - o._x)


#Andrew's monotone chain convex hull algorithm
def sequential_convex_hull(points):

    if len(points) <= 1:
        return points

    # Lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Last point of each list is omitted because it coincides with the beginning of the other list.
    return lower[:-1] + upper[:-1]

def scatter_plot(points, convex_hull,color='r'):
    xs = [pp._x for pp in points]
    ys = [pp._y for pp in points]
    plt.scatter(xs, ys)

    for i in range(1, len(convex_hull) + 1):
    	if i == len(convex_hull):
            i=0
    	c0 = convex_hull[i-1]
    	c1 = convex_hull[i]
    	plt.plot((c0._x, c1._x), (c0._y, c1._y), color)
    plt.show()

def mergehull_help(lst, res_list, idx):
    res_list[idx] = parallel_merge_hull(lst)

def lower_tang(h, point1, point2, idx):
    lenh = len(h)
    if idx == 0:
        return (cross(point1, point2, h[lenh - 1]) >=0) and (cross(point1, point2, h[idx + 1]) >= 0)
    elif idx == lenh - 1:
        return (cross(point1, point2, h[idx - 1]) >= 0) and (cross(point1, point2, h[0]) >= 0)
    else:
        return (cross(point1, point2, h[idx - 1]) >= 0) and (cross(point1, point2, h[idx + 1]) >= 0)

def upper_tang(h, point1, point2, idx):
    lenh = len(h)
    if idx == 0:
        return (cross(point1, point2, h[lenh - 1]) <=0) and (cross(point1, point2, h[idx + 1]) <= 0)
    elif idx == lenh - 1:
        return (cross(point1, point2, h[idx - 1]) <= 0) and (cross(point1, point2, h[0]) <= 0)
    else:
        return (cross(point1, point2, h[idx - 1]) <= 0) and (cross(point1, point2, h[idx + 1]) <= 0)



def join_hulls(h1, h2):

    idx_rightmost = 0
    idx_leftmost = 0
    for i in range(1, len(h1)):
        if h1[i]._x > h1[idx_rightmost]._x:
            idx_rightmost = i
    for i in range(1, len(h2)):
        if h2[i]._x < h2[idx_leftmost]._x:
            idx_leftmost = i

    a = h1[idx_rightmost]
    b = h2[idx_leftmost]
    c = a
    d = b
    idx_rightmost_copy = idx_rightmost
    idx_leftmost_copy = idx_leftmost


    while not(lower_tang(h1, a, b, idx_rightmost)) or not(lower_tang(h2, a, b, idx_leftmost)):
        while not(lower_tang(h1, a, b, idx_rightmost)):

            idx_rightmost = (idx_rightmost - 1 + len(h1)) % len(h1)
            a = h1[idx_rightmost]
        while not(lower_tang(h2, a, b, idx_leftmost)):

            idx_leftmost = (idx_leftmost + 1) % len(h2)
            b = h2[idx_leftmost]



    while not(upper_tang(h1, c, d, idx_rightmost_copy)) or not(upper_tang(h2, c, d, idx_leftmost_copy)):
        while not(upper_tang(h1, c, d, idx_rightmost_copy)):
            idx_rightmost_copy = (idx_rightmost_copy + 1) % len(h1)
            c = h1[idx_rightmost_copy]

        while not(upper_tang(h2, c, d, idx_leftmost_copy)):
            idx_leftmost_copy = (idx_leftmost_copy - 1 + len(h2)) % len(h2)
            d = h2[idx_leftmost_copy]

    if idx_rightmost_copy >= len(h1):
        idx_rightmost_copy -= len(h1)

    if idx_leftmost_copy < 0:
        idx_leftmost_copy += len(h2)

    result = []
    result += h1[:idx_rightmost + 1]
    if idx_leftmost_copy == 0:
        result += h2[idx_leftmost:]
        result.append(h2[0])
    else:
        result += h2[idx_leftmost: idx_leftmost_copy + 1]
    if not(idx_rightmost_copy == 0):
        result += h1[idx_rightmost_copy:]

    return result

def parallel_merge_hull(points):
    if len(points) <= 50:
        return sequential_convex_hull(points)
    else:
        length_p = len(points)


        max_cores = multiprocessing.cpu_count()
        res_list = [[]]*max_cores

        thread_list = []

        for i in range(max_cores):
            px = points[(i * length_p)//max_cores : ((i + 1) * length_p)// max_cores]
            th = threading.Thread(target=mergehull_help, args=(px, res_list, i))
            thread_list.append(th)
            th.start()
        for i in range(max_cores):
            thread_list[i].join()

        while len(res_list) > 1:
            resulting = []
            for j in range(0, len(res_list), 2):

                resulting.append(join_hulls(res_list[j], res_list[j+1]))
            res_list = resulting



        return res_list[0]



p = []
for i in range(1000):
    p.append(Point(random.uniform(-100, 100), random.uniform(-100, 100)))

#p = [Point(0,1), Point(2,1),Point(3,1), Point(5,1), Point(1,0), Point(1,2),Point(4,0), Point(4,2)]

p = sorted(set(p), key=lambda pp: tuple([pp._x, pp._y]))
print(p)

seq_hull = sequential_convex_hull(p)
scatter_plot(p, seq_hull)

par_hull = parallel_merge_hull(p)

scatter_plot(p, par_hull)
