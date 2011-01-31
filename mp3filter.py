#! /usr/bin/python
# -*- coding: utf-8 -*-

__module_name__ = "Filter for mp3 notification"
__module_version__ = "0.0.4"
__module_description__ = "Hide mp3's notification on irc channels"
__module_author__ = "Mirko Chialastri"

######### Config #############
filter_event = (
                "Channel Action",
                "Channel Action Hilight",
                "Channel Message",
                "Channel Message Hilight"
                )
######## End config ##########

import xchat
from re import match, compile, sub
from os import path
from sre_constants import error as regc

class mp3filter:
      def __init__(self):
          """ Costruttore """
          self.pattern = []
          self.stats = {}
          self.pattern_stats = [0, (0, 0)]

          self.debug = False
          self.label = "Mp3 filter"            

          self.load_config()
          for evnt in filter_event:
               xchat.hook_print(evnt, self.ignore_mp3_notification)            

          xchat.hook_command("mp3filter_reload", self.reload_config,
                               help="Carica nuovamente i filtri dalla config")
          xchat.hook_command("mp3filter_stats", self.pattern_status,
                                          help="Statistiche sui filtri usati")
          xchat.hook_command("mp3filter_debug", self.debug_swap,
                                        help="Stampa i messaggi che vengono \
                                              bloccati; Utile per capire \
                                  quali messaggi bloccano gli attuali filtri")

          xchat.command('MENU ADD "%s"' % self.label)
          xchat.command('MENU ADD "%s/Ricarica filtri" "mp3filter_reload"' %
                                                                   self.label)
          xchat.command('MENU ADD "%s/Statistiche filtri" "mp3filter_stats"' %
                                                                   self.label)
          xchat.command('MENU ADD "%s/Debug" "mp3filter_debug None"' %
                                                                   self.label)

          print "Filtro mp3 caricato su: \x0304%s\x03" % ', '.join(filter_event)
          s=self.pattern_stats
          print "%d/%d filtri caricati!" % (s[1][0], s[0])

      def unload(self, userdata):
           """ Unload plugin """
           xchat.command("MENU DEL "+self.label)
           self.pattern = []
           print 'Filtro scaricato..'.ljust(60), "[\x0309OK\x03]"

      def load_config(self):
            """ Carica pattern da config file """
            conf = path.join(xchat.get_info('xchatdir'), 'mp3filters.conf')
            print 'Lettura config'.ljust(60),
            if path.exists(conf):
                try:
                    conf = open(conf)
                    self.pattern = [ line.rstrip("\n") for line in conf ]
                    conf.close()
                    print "[\x0309OK\x03]"
                    self.pattern_stats = self.pattern_check_implicit()
                except:
                        print "[\x0304ERROR\x03]"
                        print " Impossibile caricare file config; Assicurarsi \
                                di avere i permessi in lettura del file config."
            else:
                  try:
                      print "Creazione file config %s".ljust(60), conf,
                      conf = open(conf, 'w')
                      print "[\x0309OK\x03]"
                  except:
                         print "[\x0304ERROR\x03]"
                         print "Impossibile creare file config; Assicurarsi di \
                                 avere i permessi di scrittura nella directory."
                         return 0

                  try:
                      print "Popolamento config files con pattern generici in \
                                                            corso... ".lrust(60)
                      conf.write("""(?i)^((is\s)?listen(ing|s)?|np|now playing|(is\s)?ascolting|(is\s)?playing|ascolta)(:|\s).+""")
                      conf.close()
                      print "[\x0309OK\x03]"
                      return 1
                  except:
                         print "[\x0304ERROR\x03]"
                         print "Impossibile popolare file config"
                         return 0

      def reload_config(self, word, word_eol, userdata):
           """ Ricarica filtri """
           print "Ricarico config".ljust(60),
           try:
               print "[\x0309OK\x03]"
               self.load_config()
           except: print "[\x0304ERROR\x03]"
           return xchat.EAT_ALL

      def ignore_mp3_notification(self, word, word_eol, userdata):
           """ Blocca il parsing della stringa se coincide con uno dei filtri
                                                                 della confi """
           for pattern in self.pattern:
               if match(pattern, word[1].strip("\x02")):
                  if self.debug:
                     print "\002\x0304** blocking\002\x03: %s %s" % (
                                                               word[0], word[1])
                  try:
                      self.stats[pattern] += 1
                  except KeyError: self.stats[pattern] = 1
                  return xchat.EAT_ALL
           return xchat.EAT_NONE

      def mp3sfilter_pattern(self, word, word_eol, userdata):
          """ Stampa tutti i filtri caricati """
          print "Pattern filter:"
          for pattern in self.pattern:
              print '\t\x0304»\x03', pattern
          return xchat.EAT_ALL

      def debug_swap(self, word, word_eol, status=None):
          """ Funzione di swap per modalità debug """
          print "Modalità debug".ljust(60),
          if status is None:
             self.debug = not(self.debug)
          elif int(status) in (0,1): self.debug = bool(status)
          print self.debug and '[\x0309ON\x03]' or '[\x0304OFF\x03]'
          return xchat.EAT_ALL

      def pattern_status(self, word, word_eol, userdata):
           t = layout((('Pattern', 30), ('Status', 10), ('Blocked', 10)))
           for p in self.pattern:
               try:
                   t.write((p, 'Active', str(self.stats[p])))
               except KeyError:
                   t.write((p, 'Active', '0'))
           return xchat.EAT_ALL        

      def pattern_check_implicit(self):
           errors = []

           for p in self.pattern:
                try:
                    compile(p)
                except regc, e:
                    errors.append((p, str(e)))
                    self.pattern.remove(p)

           total = len(self.pattern)
           errnum = len(errors)

           if errnum > 0:
              print "Elimino i seguenti pattern dai filtri attivi, poichè non \
                                                                         validi"
              t = layout((('Pattern', 35), ('Error', 45)))
              for e in errors:
                   t.write((e[0], e[1]))

           return [total, (total - errnum, errnum)]

class layout:
      def __init__(self, table):
          self.table = table
          self.label(table)       

      def label(self, line, align="left"):
          """ Stampa i label del layout """
          c = 0
          for l in line:
               maxchars = self.table[c][1]
               label = len(l[0]) > self.table[c][1] and "%s...." % \
                                                      l[0][:maxchars-4] or l[0]
               print '\x0301,00', label.ljust(l[1], " "),
               c += 1
          print

      def write(self, line, align="left", delimiter=" "):
          """ Stampa i campi della tabella """
          c = 0
          for l in line:
               maxchars = self.table[c][1]
               str = len(l) > self.table[c][1] and "%s...." % \
                                                            l[:maxchars-4] or l
               strlen = len(str)

               if align == 'left': print str.ljust(maxchars, delimiter),
               else: print str.rust(maxchars, delimiter)
               c += 1
          print

mp3blocker = mp3filter()
cososwap = mp3filter.debug_swap
xchat.hook_unload(mp3blocker.unload)

