import pygame
import serial
import time


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

BCKG = (240, 111, 199)
BLUE = (33, 36, 228)

FPS = 60
IMAGE_TIME = 600
CAS = 30

ser = serial.Serial("/dev/tty.HC-05-DevB",baudrate = 9600) #the device address of the bluetooth module
startMarker = 60
endMarker = 62
waitForArduino()
waitingForReply = False

pygame.init() 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GAME")


hi = pygame.image.load('hi.png')
three = pygame.image.load('3.png')
two = pygame.image.load('2.png')
one = pygame.image.load('1.png')
catch_the_mouse = pygame.image.load('Catch_the_mouse.png')


intro_slides = [hi,three,two,one,catch_the_mouse]

#Importing pictures
#Myška 
pygame.mouse.set_visible( False )
pointerImg = pygame.image.load('Cursor.png')
pointerImg_rect = pointerImg.get_rect()

#file
file_icon = pygame.image.load('file.png')
rectangle = pygame.rect.Rect(10, 10, 48, 68)
rectangle_draging = False

#bin
bin_icon = pygame.image.load('bin.png')
bin_rectangle = pygame.rect.Rect(10, 10, 742, 414)

#maly stvorcek
stvorcek_icon = pygame.image.load('stvorcek.png')

def obrazek(meno,CAS):
    screen.blit(meno,(0,0))


clock = pygame.time.Clock()
ktory_obrazok = 0


running = True
intro = True

buttonpress = 0
caught = 0


while running:
    
    #Running through the intro countdown
    CAS -= 1
    if CAS == 0:
        CAS = 30
        ktory_obrazok += 1
    
    

    for event in pygame.event.get():
        pointerImg_rect.center = pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            running = False

        elif buttonpress == 1:
                   
            if rectangle.collidepoint(event.pos):
                rectangle_draging = True
                mouse_x, mouse_y = event.pos
                offset_x = rectangle.x - mouse_x
                offset_y = rectangle.y - mouse_y
                    
                    

        elif buttonpress == 0:
                        
                rectangle_draging = False

        elif event.type == pygame.MOUSEMOTION:
            if rectangle_draging:
                mouse_x, mouse_y = event.pos
                position_x = mouse_x + offset_x
                position_y = mouse_y + offset_y
                rectangle.x = position_x
                rectangle.y = position_y

                print(rectangle)
                print(rectangle[0])
                print(rectangle[1])

        if rectangle[0] > 713 and rectangle[0] < 760 and rectangle[1] > 371 and rectangle[1] < 405:
            print("You win")


    if ktory_obrazok < 4:
        obrazek(intro_slides[ktory_obrazok],CAS)
    else:
        obrazek(intro_slides[4],CAS)
        arduinoroam = 1

    

    if ktory_obrazok > 4 and caught == 1:
        
        screen.fill(BCKG)
        for j in range (0,480):
            if j % 4 == 0:
                screen.blit(stvorcek_icon, (200,j))
                screen.blit(stvorcek_icon, (400,j))
                screen.blit(stvorcek_icon, (600,j))

        #pygame.draw.rect(screen, RED, rectangle)
        screen.blit(file_icon,(rectangle[0],rectangle[1]))
        screen.blit(bin_icon,(742, 414))
    
    screen.blit(pointerImg, pointerImg_rect.center)
    #screen.blit(pointerImg, (rectangle[0],rectangle[1]))
    xmouse = pointerImg_rect.center[0]
    ymouse = pointerImg_rect.center[1]
    
    toarduinoinfo = "<FromRaspb," + str(arduinoroam) + ">"

    if waitingForReply == False:
            sendToArduino(toarduinoinfo)
            waitingForReply = True

    if waitingForReply == True:

        while ser.inWaiting() == 0:
            pass
        
        dataRecvd = recvFromArduino()
        waitingForReply = False       

    caught = check(dataRecvd)
    buttonpress = check1(dataRecvd)
    

    pygame.display.flip()

    clock.tick(FPS)


pygame.quit()

#Functions originally from user Robin2, modified--------------------------
#http://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764

def sendToArduino(sendStr):
    ser.write(sendStr.encode('utf-8')) 




def recvFromArduino():
    global startMarker, endMarker
    
    ck = ""
    x = "z" # any value that is not an end- or startMarker
    byteCount = -1 
    
    # wait for the start character
    while  ord(x) != startMarker: 
        x = ser.read()
    
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x.decode("utf-8") 
            byteCount += 1
        x = ser.read()
    
    return(ck)



def waitForArduino():

    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   
    
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

        while ser.inWaiting() == 0:
            pass
        
        msg = recvFromArduino()

        print (msg) # python3 requires parenthesis
        print ()
#----------------------------

def check(s):
    i = s.find('<')
    if s[i+8].isdigit():
        return int (s[i+8])

def check1(s):
    i = s.find('>')
    if s[i-1].isdigit():
        return int (s[i-1])