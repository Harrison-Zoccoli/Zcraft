#main import is ursina
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor
from numpy import abs
import time
from random import randrange
from perlin_noise import PerlinNoise
from nMap import nMap
from numpy import sin
from numpy import cos
from numpy import radians
#####the issue appears to be with the combine feature, seems to be due to a version missmatch tommorow check video, description, comments to see if there are solutions. if not lets recode for better optimization.

app= Ursina()

window.color = color.rgb(0,200, 211)
window.exit_button.visible = False

prevTime = time.time()

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = 0.02

grassStrokeTex = 'grass_14.png'
monoTex = 'stroke_mono.png'
wireTex= 'wireframe.png'
stoneTex='grass_mono.png'


cubeTex = 'block_texture.png'

cubeModel = 'block2.obj'

buildToolEntity = Entity(model='cube', texture=wireTex)

class BTYPE:
    stone=color.rgb(255, 255, 255) 
    grass=color.rgb(0, 255, 0)
    magma = color.rgb(255, 0, 0)
    diamond = color.rgb(0, 0, 255)

blockType = BTYPE.stone
buildMode = -1  # -1 is OFF, 1 is ON, we start with it off

def buildTool():
    if buildMode == -1:
        buildToolEntity.visible = False
        return
    else:
        buildToolEntity.visible = True
    buildToolEntity.position = round(subject.position + camera.forward * 3)
    buildToolEntity.y += 2
    buildToolEntity.y= round(buildToolEntity.y)
    buildToolEntity.x= round(buildToolEntity.x)
    buildToolEntity.z = round(buildToolEntity.z)
    buildToolEntity.color = blockType

#so how we're building is essentially creating a duplicate of the buildToolEntity
#we then give it a collider, and assign it a texture of stone
def build():
    tempPlaceBlock = duplicate(buildToolEntity)
    tempPlaceBlock.collider = 'cube'
    tempPlaceBlock.texture= stoneTex
    tempPlaceBlock.color = blockType
    tempPlaceBlock.shake(duration=0.5, speed=0.01)

##temp measure put in place bc quitting at bottom sucks id rather click a button
def input(key):
    global blockType, buildMode, generating, canGenerate
    if key== 'escape':
        quit()
    
    if buildMode == 1 and key == 'right mouse up':
        build()
   
    if buildMode == 1 and key == 'left mouse up':
        hoveredBlock = mouse.hovered_entity
        destroy(hoveredBlock)
    
    if key =='b':
        buildMode*= -1

    if key =='1': 
        blockType= BTYPE.stone
    if key == '2': 
        blockType = BTYPE.grass
    if key== '3': 
        blockType =BTYPE.magma
    if key == '4': 
        blockType = BTYPE.diamond

    if key == 'g': 
        generating *= -1
        canGenerate *= -1
    
    if key == 'shift':
        subject.speed = 7.5
        subject.gravity = 0.1
    if key == 'shift up':
        subject.speed = playerSpeed
        subject.gravity = gravity

def update():
    global prevZ, prevX, prevTime, genSpeed, perCycle
    global rad, origin, generating, canGenerate
    if abs(subject.z-prevZ) > 1 or abs(subject.x-prevX) >1:
        origin = subject.position
        rad = 0
        theta = 0
        generating = 1 * canGenerate
        prevZ = subject.z
        prevX= subject.x
 
    generateShell()
 
    if time.time()- prevTime > genSpeed:
        for i in range(perCycle):
            genTerrain()
        prevTime= time.time() 


    # #incase we glitch through the floor this will reset us (shouldnt happen unless laggy or if screensharing)
    # if subject.y < -amp-1:
    #     subject.y = 2 + floor((noise([subject.x/freq, subject.z/freq]))*amp)
    #     subject.land()  # kinda resets acceleration to prevent the user from accruing fall speed

    buildTool()

###Variables
noise=PerlinNoise(octaves=1, seed=99)


megasets = []
subsets = []
subCubes = []
generating= 1  # -1 if off.
canGenerate =1  # -1 if off.
genSpeed =0
perCycle =32
currentCube =0
currentSubset =0

numSubsets = 420 #how many combine to form megaset
numSubCubes = 32
theta = 0
rad =0
#dictionary used for recording whether or not terrain blocks exist
#at location specified in key
subDic = {}
caveDic = { 'x9z9' : 'cave', 
            'x10z9' : 'cave',
            'x11z9' : 'cave', 
             }



# Use the same texture throughout
for i in range(numSubCubes):
    bud = Entity(model=cubeModel, texture=cubeTex)
    bud.disable()
    subCubes.append(bud)

 
# Create subsets with textures 
# for i in range(numSubsets):
#     bud = Entity(model=None, texture=grassStrokeTex)
#     bud.disable()
#     subsets.append(bud)
for i in range(numSubsets):
    bud = Entity(model=None)
    bud.texture = cubeTex
    bud.disable()
    subsets.append(bud)


def genPerlin(_x, _z):
    y = 0
    freq = 128
    amp = 42      
    y += ((noise([_x/freq, _z/freq]))*amp)
    freq = 32
    amp = 21
    y += ((noise([_x/freq, _z/freq]))*amp)

    #creating caves
    if caveDic.get('x' +str(int(_x))+'z'+str(int(_z))) == 'cave':
        y-=9

    return floor(y)

def genTerrain():
    global currentCube, theta, rad, currentSubset
    global generating
 
    if generating == -1: return
 
    # Decide where we should place new terrain cube
    x = floor(origin.x+sin(radians(theta)) * rad)
    z = floor(origin.z+cos(radians(theta)) * rad)

    # Check whether there is terrain here already so we dont repeat
    if subDic.get('x'+str(x)+'z'+str(z)) != 'i':
        subCubes[currentCube].enable()
        subCubes[currentCube].x = x
        subCubes[currentCube].z = z
        subDic['x'+str(x)+'z'+str(z)] = 'i'
        subCubes[currentCube].parent = subsets[currentSubset]
        subCubes[currentCube].y = genPerlin(x, z)
        
        currentCube += 1

        # When combining, don't override textures
        if currentCube == numSubCubes:

            subsets[currentSubset].combine(auto_destroy=False)
            subsets[currentSubset].texture = cubeTex
            subsets[currentSubset].enable()
            
            currentSubset += 1
            currentCube = 0

            if currentSubset == numSubsets:
                megasets.append(Entity(texture=cubeTex))  # Don't set texture here
                for s in subsets:
                    s.parent = megasets[-1]
                megasets[-1].combine(auto_destroy=False)
                currentSubset = 0
                print("made megaset" + str(len(megasets)))


    else:
        pass
        # There was terrain already there, so
        # continue rotation to find new terrain spot.
     
    if rad > 0:
        theta += 45/rad
    else: 
        rad += 0.5
    if theta>=360:
        theta = 0
        rad += 0.5

shellies =[]
shellWidth= 3
for i in range(shellWidth*shellWidth):
    bud =Entity(model='cube', collider='box', texture=grassStrokeTex)
    bud.visible= False
    shellies.append(bud)
 
def generateShell():
    global shellWidth
    for i in range(len(shellies)):
        x=shellies[i].x = floor((i/shellWidth) + subject.x - 0.5*shellWidth)
        z=shellies[i].z =floor((i%shellWidth) + subject.z - 0.5*shellWidth)
        shellies[i].y = genPerlin(x, z)





gravity = 0.5
playerSpeed = 5

subject = FirstPersonController(speed=playerSpeed)
subject.gravity = gravity

subject.cursor.visible = False
subject.x = subject.z = 5
subject.y = 64
prevZ =subject.z
prevX= subject.x
origin= subject.position  # this is a vector 3 object with an x,y,z component

generateShell()

app.run()