# -*- coding: utf-8 -*-
# LookupKanji 0.2
# Anki1 Version based on jmrGloss
# Ported to Anki2 with help of AwesomeTTS
# By shufps.wordpress.com (shufps80@gmail.com)

import subprocess, re, urllib, urllib2

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from aqt import mw, utils
from aqt.utils import tooltip
from anki.hooks import addHook
from aqt.utils import showInfo, askUser
from aqt.qt import *

import string
import codecs

srcField_name="Expression"
dstField_name="RTK"
dataFile='rtk_4th_german.txt'

heisig=dict()

def read_heisig():
	dn, fn = os.path.split(os.path.abspath(__file__))

	f=codecs.open(dn+"/"+dataFile, encoding='utf-8')
	for line in f:
		p=line.split(";")
		ch=unicode(p[0])[0]
		heisig[ch]=[p[1],p[2]]
		#print heisig[ch]
	f.close()

def fetchKanji_find(x, s, e):
	sidx = x.find(s)
	if sidx == -1:
		return ''
    
	eidx = x.find(e, sidx)
	if eidx == -1:
		return ''
    
	return x[sidx+len(s):eidx]

def fetchKanjiSub(exp):
	html = ''
#	expx = ''
	for ch in unicode(exp):
		print ch+" "+str(ord(ch))
		if ord(ch) < 19968:
			continue
		if heisig.has_key(ch):
			info = heisig[ch]
			line=""+ch+": "+info[0]+" ("+info[1]+")<br/>"
			html+=line
			#print "line added: "+line
		else:
			print 'key not found!: '+ch

	return html

#### Update facts with Kanjis

def onFetchKanji( self ):
	sf = self.selectedNotes()
	if not sf:
		utils.showInfo("Select the notes and then use the Lookup RTK plugin")
		return

	self.mw.checkpoint(_("Lookup RTK"))
	self.mw.progress.start(immediate=True, label="Looking up RTK ...")

	self.model.beginReset()
   
	(n, missing, ok, nop, failed) = fetchKanji( sf )

	self.model.endReset()
	self.mw.progress.finish()
   
   
	utils.showInfo(
		str(n)+" total notes\n"+
		str(ok)+" notes sucessfully fetched\n"+
		str(missing)+" notes are missing tags "+srcField_name+" and/or "+dstField_name+"\n"+
		str(nop)+" notes not updated (nothing overwritten)\n"+
		str(failed)+" notes failed"
	)

def fetchKanji( fids ):
	nelements = len(fids)
	failed=0
	notupdated=0
	missingtag=0
	ok=0
	for c, id in enumerate( fids ):
		note = mw.col.getNote(id)
		
		if (not srcField_name in note.keys() or not dstField_name in note.keys()):
			missingtag+=1
			note.flush()
			continue	   

		mw.progress.update(label="Looking up RTK ... \n%s of %s\n%s" % (c+1, nelements,note[srcField_name]))		
	   
		try:
			old=note[dstField_name].strip()
			if old == "" or old == "<br />" or old == "<br/>":
				note[dstField_name] = fetchKanjiSub( note[srcField_name])
				ok+=1
			else:
				print "not updated: "+note[dstField_name]
				notupdated+=1
				continue
		except:
			import traceback
			print 'lookup RTK failed:'
			traceback.print_exc()
			failed+=1
			
		note.flush()	   
		
	return (nelements, missingtag, ok, notupdated, failed)


def setupMenu(editor):
	a = QAction("Lookup RTK", editor)
	editor.form.menuEdit.addAction(a)
	editor.connect(a, SIGNAL("triggered()"), lambda e=editor: onFetchKanji(e))

addHook("browser.setupMenus", setupMenu)

read_heisig()