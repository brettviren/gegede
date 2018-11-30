#!/usr/bin/env python
'''
Play with pivy
'''

from pivy import coin

def make_mother_daughter():
    '''
    Make a cube with two cylinders inside.
    '''

    tube_shape = coin.SoCylinder()
    tube_shape.radius = 0.25
    tube_shape.height = 1.5

    tube_mat = coin.SoMaterial()
    tube_mat.ambientColor = (.33, .22, .27)
    tube_mat.diffuseColor = (.78, .57, .11)
    tube_mat.specularColor = (.99, .94, .81)
    tube_mat.shininess = .28
    tube_mat.transparency = 0.5

    tube_lv = coin.SoSeparator()
    tube_lv.addChild(tube_mat)
    tube_lv.addChild(tube_shape)

    tube_tr1 = coin.SoTransform()
    tube_tr1.translation = (+0.75, 0, 0)
    tube_tr2 = coin.SoTransform()
    tube_tr2.translation = (-0.75, 0, 0)

    tube_pv1 = coin.SoSeparator()
    tube_pv1.addChild(tube_tr1)
    tube_pv1.addChild(tube_lv)

    tube_pv2 = coin.SoSeparator()
    tube_pv2.addChild(tube_tr2)
    tube_pv2.addChild(tube_lv)

    cube_lv = coin.SoSeparator()
    cube_lv.addChild(tube_pv1)
    cube_lv.addChild(tube_pv2)

    cube_mat = coin.SoMaterial()
    cube_mat.ambientColor = (.2, .2, .2)
    cube_mat.diffuseColor = (.6, .6, .6)
    cube_mat.specularColor = (.5, .5, .5)
    cube_mat.shininess = .5

    cube_shape = coin.SoCube()
    cube_shape.width = 3.0      # x
    cube_shape.height = 2.0     # y
    cube_shape.depth = 1.0      # z, out of screen

    cube_lv.addChild(cube_mat)
    cube_lv.addChild(cube_shape)

    return cube_lv


def test_save():
    cube_lv = make_mother_daughter()
    writer = coin.SoWriteAction()
    out = writer.getOutput()
    out.openFile("test_pivy.iv")
    out.setBinary(False)
    writer.apply(cube_lv)
    out.closeFile()

def main():
    from pivy import sogui
    #from pivy import soqt as sogui

    win = sogui.SoGui.init()
    world = coin.SoSeparator()

    cube_lv = make_mother_daughter()
    world.addChild(cube_lv)

    view = sogui.SoGuiExaminerViewer(win)
    view.setSceneGraph(world)
    view.setTitle("Test")
    view.show()
    view.viewAll()
    sogui.SoGui.show(win)
    sogui.SoGui.mainLoop()

if '__main__' == __name__:
    #main()
    test_save()
