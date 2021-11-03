import turtle as tl
import math

def draw_tree(size):
    if size >= 5:
        tl.pensize(max(size / 25, 1))
        tl.forward(size)
        tl.left(35)
        draw_tree(size / 2)
        tl.right(65)
        draw_tree(size / 1.5)
        tl.left(30)
        #tl.pensize(size / 1.5)
        tl.penup()
        tl.backward(size)
        tl.pendown()
    else:
        tl.pensize(3)
        tl.dot       

size = 200

tl.hideturtle()
tl.penup()
tl.goto(0, -300)
tl.showturtle()
tl.pendown()   
tl.delay(0)   
tl.shape("turtle")
tl.pencolor('#654321')
tl.setheading(90)

draw_tree(size)
tl.done()