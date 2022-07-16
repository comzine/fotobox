fotoboxCfg = {}

fotoboxCfg['window-width']    = 1920
fotoboxCfg['window-height']   = 1080


# Depending on the camera used previews might got smaller than set here
fotoboxCfg['cam-p-width']     = 1350
# fotoboxCfg['cam-p-width']     = 1920
# fotoboxCfg['cam-p-height']    = 900 # 1350 * 9 / 16 = 760
# fotoboxCfg['cam-p-height']    = 760 # 1350 * 9 / 16 = 760
fotoboxCfg['cam-p-height']    = 1012 # 1350 * 9 / 16 = 760
fotoboxCfg['cam-p-x']         = 35
#fotoboxCfg['cam-p-x']         = 35
#fotoboxCfg['cam-p-x']         = 15
fotoboxCfg['cam-p-y']         = 35
#fotoboxCfg['cam-p-y']         = 157
#fotoboxCfg['cam-p-y']         = 15
fotoboxCfg['cam-p-hflip']     = True # False = Like a camera, True = Like a mirror

# Preview 4:3 1640x1232
# PiCam v1: 2592x1944, v2: 3280x2464, HQ: 4056x3040
fotoboxCfg['cam-c-width']     = 3280
fotoboxCfg['cam-c-height']    = 2464
fotoboxCfg['cam-c-hflip']     = False # False = Like a camera, True = Like a mirror

fotoboxCfg['nopi']            = False #True = Skip rasperry specific modules

fotoboxCfg['gphoto']          = True

fotoboxCfg['temp']            = '/home/pi/fotobox/tmp/'
fotoboxCfg['save']            = '/home/pi/fotobox/images/'

fotoboxCfg['countdown']       = 5 # Seconds

fotoboxCfg['takePics']       = 4 # Number of pictures to take
fotoboxCfg['template']       = 'images/collage8.png' # Number of pictures to take
fotoboxCfg['templateOverlay']       = 'images/collage8Overlay.png' # Number of pictures to take

fotoboxText = {}

fotoboxText['info-home']    = 'Hallo und willkommen in der Fotobox!<br>Drücke einfach auf &quot;Aufnahme&quot; und los geht es!'
fotoboxText['info-count']   = 'Los geht es!<hr><span style="font-size: 200%; font-weight: bolder;"></span>'
# fotoboxText['info-count']   = 'Los geht es!<hr><span style="font-size: 200%; font-weight: bolder;">${countdown}</span>'
fotoboxText['info-capture'] = '<span style="font-size: 200%; font-weight: bolder;">Bitte lächeln!</span>'
fotoboxText['info-review']  = 'Alles OK?<br>Wenn ja drücke auf "Speichern". Doch zu blöd geguckt? Dann versuch es gleich nochmal.'
fotoboxText['info-view']    = 'Hier kannst du dir die Fotos der Veranstaltung direkt anschauen. Mit "Nächstes" und "Vorheriges" kannst du zwischen den Bildern wechseln. Mit "Zurück" geht es wieder zur Kamera.'
fotoboxText['info-print']    = 'Drucken?<br>Nicht gedruckte Bilder bleiben digital erhalten.'

fotoboxText['btn-capture']  = 'Aufnahme'
fotoboxText['btn-view']     = '' #'Ansehen ▶'
fotoboxText['btn-save']     = 'Speichern'
fotoboxText['btn-recapture'] = '<span style="font-size: 75%">Neuer Versuch</span>'
fotoboxText['btn-cancel']   = 'Abbruch'
fotoboxText['btn-print']   = 'Drucken'
fotoboxText['btn-next']     = 'Nächstes'
fotoboxText['btn-previous'] = 'Vorheriges'
fotoboxText['btn-back']     = 'Zurück'
fotoboxText['btn-empty']    = ''
