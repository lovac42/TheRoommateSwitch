# -*- coding: utf-8 -*-
# Copyright: (C) 2019 Lovac42
# Support: https://github.com/lovac42/TheRoommateSwitch
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
from aqt.qt import *
from aqt import mw
from aqt.utils import tooltip
from anki.utils import intTime, ids2str
from anki.hooks import wrap, addHook
from .const import *
from .config import *


class RoommateSwitch:
    loaded=False
    card=None

    def __init__(self):
        self.conf=Config(ADDON_NAME)
        addHook(ADDON_NAME+".configLoaded", self.onConfigLoaded)
        addHook('showAnswer', self.onShowAnswer)

    def onConfigLoaded(self):
        if not self.loaded:
            self.setupMenu()
            self.loaded=True


    def setupMenu(self):
        menu=None
        for a in mw.form.menubar.actions():
            if '&Study' == a.text():
                menu=a.menu()
                # menu.addSeparator()
                break
        if not menu:
            menu=mw.form.menubar.addMenu('&Study')

        item=QAction("Swap Roommates", mw)
        item.triggered.connect(self.swap)
        key=self.conf.get("hotkey",None)
        if key: item.setShortcut(QKeySequence(key))
        menu.addAction(item)


    def getSibling(self, card):
        #Conditions: new, burried, or suspended
        cids=mw.col.db.list("""
select id from cards 
where queue<1 and type=0
and odid=0 and nid=? and id!=?
order by id""", card.nid, card.id)
        if cids:
            return cids[0]


    def swap(self):
        if mw.state!='review':
            return
        cid=self.getSibling(mw.reviewer.card)
        if cid:
            self.card=mw.col.getCard(cid)
            mw.reviewer.cardQueue.append(self.card)
            tooltip(_("Awaiting Sibling"),1500)


    def onShowAnswer(self):
        "If user leaves reviewer, sibling is left unchanged"
        if self.card and self.card.id==mw.reviewer.card.id:
            self.card.queue=0
            self.card.flushSched()
            self.card=None


rsw=RoommateSwitch()

