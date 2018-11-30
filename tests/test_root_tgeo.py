#!/usr/bin/env python
'''
Test make ROOT TGeo.

Because it's way cray cray and it's pissing off.
'''

import ROOT

element_names = ["VACUUM", "H", "HE", "LI", "BE", "B", "C", "N", "O", "F", "NE", "NA", "MG", "AL", "SI", "P", "S", "CL", "AR", "K", "CA", "SC", "TI", "V", "CR", "MN", "FE", "CO", "NI", "CU", "ZN", "GA", "GE", "AS", "SE", "BR", "KR", "RB", "SR", "Y", "ZR", "NB", "MO", "TC", "RU", "RH", "PD", "AG", "CD", "IN", "SN", "SB", "TE", "I", "XE", "CS", "BA", "LA", "CE", "PR", "ND", "PM", "SM", "EU", "GD", "TB", "DY", "HO", "ER", "TM", "YB", "LU", "HF", "TA", "W", "RE", "OS", "IR", "PT", "AU", "HG", "TL", "PB", "BI", "PO", "AT", "RN", "FR", "RA", "AC", "TH", "PA", "U", "NP", "PU", "AM", "CM", "BK", "CF", "ES", "FM", "MD", "NO", "LR", "RF", "DB", "SG", "BH", "HS", "MT", "UUN", "UUU", "UUB"]



def test_get_elements():
    '''
    Test getting elements
    '''
    tgeo = ROOT.TGeoManager()
    et = tgeo.GetElementTable()
    for count in range(et.GetNelements()):
        ele = et.GetElement(count)
        assert ele
        #print ('ELE: %4d: %s %s %d %f' % (count, ele.GetName(), ele.GetTitle(), ele.Z(), ele.A()))

    for count in range(et.GetNelementsRN()):
        ele = et.GetElementRN(count)
        ndk = ele.GetNdecays()
        niso = ele.GetNisotopes()
        assert ele
        #print ('RN: %4d: %s %s %d %f [%d %d]' % \
        #    (count, ele.GetName(), ele.GetTitle(), ele.Z(), ele.A(), ndk, niso))

def test_element():
    '''
    Make some elements
    '''
    tgeo = ROOT.TGeoManager()
    assert tgeo, 'No geo manager from ROOT'
    et = tgeo.GetElementTable()
    assert et, 'No element table from ROOT'
    nele = et.GetNelements()
    assert nele, 'ROOT should pre-fill the element table'

    for num,name in enumerate(element_names):
        ele = et.GetElement(num)
        assert ele, 'No element #%d' % num
        ele = et.FindElement(name)
        assert ele, 'No element named %s' % name


def test_failed_isotope():
    '''
    This will abort root if the last two lines are uncommented, o.w. it should be okay
    '''
    tgeo = ROOT.TGeoManager()
    et = tgeo.GetElementTable()
    u235 = ROOT.TGeoIsotope('U235', 92, 235, 235.0)
    u238 = ROOT.TGeoIsotope('U238', 92, 238, 238.0)
    et.AddElement('enriched_U', 'enriched_U', 92, 236)
    eu = et.FindElement('enriched_U')
    if not eu:
        print ('Failed to find "enriched_U" by name')
        eu = et.GetElement(et.GetNelements()-1)
        print (eeu)
    assert(eu)
    #eu.AddIsotope(u235,0.6)     # this aborts ROOT
    #eu.AddIsotope(u238,0.4)


def test_kaboom():
    '''
    Make enriched Uranium
    '''
    tgeo = ROOT.TGeoManager()
    et = tgeo.GetElementTable()
    eu = ROOT.TGeoElement("enriched_U","enriched_U", 2)
    u235 = ROOT.TGeoIsotope('U235', 92, 235, 235.0439299)
    u238 = ROOT.TGeoIsotope('U238', 92, 238, 238.0439299)
    eu.AddIsotope(u235,0.5)
    eu.AddIsotope(u238,0.5)
    assert 2 == eu.GetNisotopes()


def test_isotope():
    '''
    Test making an isotope
    '''
    tgeo = ROOT.TGeoManager()
    et = tgeo.GetElementTable()

    u235 = ROOT.TGeoIsotope('U235', 92, 235, 235.0)

    want_235 = et.FindIsotope('U235')
    assert want_235
    assert want_235 == u235

    u238 = ROOT.TGeoIsotope('U238', 92, 238, 238.0)

    eu = ROOT.TGeoElement('enriched_U', 'enriched_U', 2)
    eu.AddIsotope(u235,0.6)
    eu.AddIsotope(u238,0.4)
    print ('Neff = %f' % eu.Neff())

    # now what? how to register this element?
