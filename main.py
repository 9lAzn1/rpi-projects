'''
Touch tracer - draw circle around touch
'''
__version__ = '1.0'

import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Point, GraphicException, Ellipse
from math import sqrt

import time

# global parameters
default_steps = 5
showPointer = True


def calculate_points(x1, y1, x2, y2, steps = default_steps): 
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps: 
        return None

    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o

 
class Touchtracer(FloatLayout): 
    def on_touch_down(self, touch): 
        # record the touch info
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        
        # store the point
        ud['points_list'] = [touch.x, touch.y]

        # draw the point of touch
        if showPointer: 
            with self.canvas: 
                Color(0, 0, 1, mode='hsv', group=g)
                ud['pointer']= Point(points=(ud['points_list'][-2], 
                    ud['points_list'][-1]),
                    source='particle.png', 
                    pointsize=50, group=g)
        else: 
            ud['pointer'] = None

        # print coordinates to console: 
        print "Point: (%.2f, %.2f)" % (touch.x, touch.y)        
    
        # record time
        ud['start_time'] = time.time()
        
        touch.grab(self)
        return True

    def on_touch_move(self, touch): 
        if touch.grab_current is not self: 
            return

        # update pointer location
        ud = touch.ud
        g = ud['group']
        
        try: 
            oldx, oldy = ud['points_list'][-2], ud['points_list'][-1]
        except: 
            print "something weird happened."

        points = calculate_points(oldx, oldy, touch.x, touch.y)
         
        if points: 
            try:
                for idx in range(0, len(points), 2): 
                    ud['points_list'].extend([points[idx], points[idx+1]])
                    print "Point: (%.2f, %.2f)"%(points[idx], points[idx+1])
            except GraphicException: 
                pass
    
        # redraw current pointer
        if showPointer: 
            self.update_touch_pointer(ud['pointer'], touch)


    def on_touch_up(self, touch):
        if touch.grab_current is not self: 
            return

        touch.ungrab(self)
        ud = touch.ud

        # elapsed time
        ud['end_time'] = time.time()
        ud['touch_duration'] = ud['end_time']-ud['start_time']

        # write to file
        num_points = (len(ud['points_list'])/2)
        with open('movement1.txt', 'a+') as f:
            f.write('Trace ID: %s\n' % ud['group'])
            f.write('Number of points: %d\n' % (num_points/2))
            f.write('Duration: %.2f s\n' % ud['touch_duration'])
            
            for idx in range(0, num_points, 2): 
                f.write('point: (%.2f, %.2f)\n' % 
                    (ud['points_list'][idx], 
                    ud['points_list'][idx+1]))

        f.close()
                    

        # clear canvas
        self.canvas.remove_group(ud['group'])


    def update_touch_pointer(self, pointer, touch): 
        pointer.points = (touch.x, touch.y)


class TouchtracerApp(App):
    
    def build(self): 
        return Touchtracer()

    def on_pause(self):
        return True

if __name__=='__main__':
    TouchtracerApp().run()
 
