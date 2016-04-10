# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)


class Decoder(object):

    cb = {}
    enabled = False
    silence = False
    source = ""
    srcs = ['---', 'Tuner', 'CD', 'CD Changer', 'Input AUX 1', 'Input AUX 2', 'USB', 'Bluetooth']
    have_changer = False
    cd_disk = 0
    volume = 0
    vol_change = False
    track_intro = False
    random = False
    repeat = False
    rds = False
    reg = False
    radiotext = False
    balance_lr = 0
    show_balance_lr = False
    balance_rf = 0
    show_balance_rf = False
    bass = 0
    show_bass = False
    treble = 0
    show_treble = False
    loudness = False
    show_loudness = False
    autovol = 0
    show_autovol = 0
    ambience = ""
    ambs = {0x03: 'None', 0x07: 'Classical', 0x0b: 'Jazz-Blues', 0x0f: 'Pop-Rock', 0x13: 'Vocal', 0x17: 'Techno'}
    ambience_show = False
    radio_mem = 0
    radio_band = ""
    bands = ['---', 'FM1', 'FM2', 'DAB', 'FMAST', 'AMMW', 'AMLW', '---']
    radio_freq = 0.0
    radio_ast = False
    radio_scan = False
    rds_search = False
    have_ta = False
    have_reg = False
    have_pty = False
    show_pty = False
    pty = 0
    cd_tracks = 0
    cd_len = ""
    cd_mp3 = 0
    track_num = 0
    track_time = ""
    track_len = ""
    key = {}

    def __init__(self, ss):
        self.ss = ss

    def decode(self, ci, cl, cd):
        if ci in self.cb and cd == self.cb[ci]:
            return
        self.cb[ci] = cd

        if ci == 0x131:  # cmd to cd changer
            pass

        elif ci == 0x165:  # radio status
            self.enabled = bool(cd[0] & 0x80)
            self.silence = bool(cd[0] & 0x20)
            self.source = self.srcs[(cd[2] >> 4) & 7]
            self.have_changer = bool(cd[1] & 0x10)
            #self.cd_disk = ((cd[1] >> 5) & 3) ^ 1  # for b7?

        elif ci == 0x1a5:  # volume
            self.volume = cd[0] & 0x1f
            self.vol_change = bool(cd[0] & 0x80)

        elif ci == 0x1e0:  # radio settings
            self.track_intro = bool(cd[0] & 0x20)
            self.random = bool(cd[0] & 0x04)
            self.repeat = bool(cd[1] & 0x80)
            self.rds = bool(cd[2] & 0x20)
            self.reg = bool(cd[3] & 0x80)
            self.radiotext = bool(cd[4] & 0x20)

        elif ci == 0x1e5:  # audio settings
            self.balance_lr = ((cd[0] + 1) & 0x0f) - (cd[0] ^ 0x40 & 0x40) >> 2
            self.show_balance_lr = bool(cd[0] & 0x80)
            self.balance_rf = ((cd[1] + 1) & 0x0f) - (cd[1] ^ 0x40 & 0x40) >> 2
            self.show_balance_rf = bool(cd[1] & 0x80)
            self.bass = ((cd[2] + 1) & 0x0f) - (cd[2] ^ 0x40 & 0x40) >> 2
            self.show_bass = bool(cd[2] & 0x80)
            self.treble = ((cd[4] + 1) & 0x0f) - (cd[4] ^ 0x40 & 0x40) >> 2
            self.show_treble = bool(cd[4] & 0x80)
            self.loudness = bool(cd[5] & 0x40)
            self.show_loudness = bool(cd[5] & 0x80)
            self.autovol = cd[5] & 7
            self.show_autovol = bool(cd[5] & 0x10)
            self.ambience = self.ambs.get(cd[6] & 0x1f, "Unk:" + hex(cd[6] & 0x1f))
            self.ambience_show = bool(cd[6] & 0x40)

        elif ci == 0x225:  # radio freq
            if cl == 6:  # b7, from autowp docs
                self.radio_mem = cd[0] & 7
                self.radio_band = self.bands[(cd[1] >> 5) & 7]
                self.radio_freq = ((cd[1] & 0x0f) * 256 + cd[2]) * 0.05 + 50
                self.radio_ast = False
                self.radio_scan = False

            elif cl == 5:  # b3/b5
                self.radio_mem = (cd[1] >> 4) & 7
                self.radio_band = self.bands[(cd[2] >> 4) & 7]
                self.radio_freq = ((cd[3] & 0x0f) * 256 + cd[4]) * 0.05 + 50
                self.radio_ast = bool(cd[0] & 0x08)
                self.radio_scan = bool(cd[0] & 0x02)

        elif ci == 0x265:  # rds
            self.rds_search = bool(cd[0] & 0x80)
            self.have_ta = bool(cd[0] & 0x10)
            self.have_reg = bool(cd[0] & 0x01)
            self.have_pty = bool(cd[1] & 0x80)
            self.show_pty = bool(cd[1] & 0x40)
            self.pty = cd[2]

        elif ci == 0x2a5:  # hz
            pass

        elif ci == 0x2e5:  # hz
            pass

        elif ci == 0x325:  # cd tray info
            self.cd_disk = cd[1] & 0x83

        elif ci == 0x365:  # cd disk info
            self.cd_tracks = cd[0]
            self.cd_len = "%02d:%02d" % (cd[1], cd[2]) if cd[1] != 0xff else "--:--"
            self.cd_mp3 = bool(cd[3] & 0x01)

        elif ci == 0x3a5:  # cd track info
            self.track_num = cd[0]
            self.track_len = "%02d:%02d" % (cd[1], cd[2]) if cd[1] != 0xff else "--:--"
            self.track_time = "%02d:%02d" % (cd[3], cd[4]) if cd[3] != 0xff else "--:--"

        elif ci == 0x3e5:  # keypad
            self.key['menu'] = bool(cd[0] & 0x40)
            self.key['tel'] = bool(cd[0] & 0x10)
            self.key['clim'] = bool(cd[0] & 0x01)
            self.key['trip'] = bool(cd[1] & 0x40)
            self.key['audio'] = bool(cd[1] & 0x01)
            self.key['ok'] = bool(cd[2] & 0x40)
            self.key['esc'] = bool(cd[2] & 0x10)
            self.key['dark'] = bool(cd[2] & 0x04)
            self.key['up'] = bool(cd[5] & 0x40)
            self.key['down'] = bool(cd[5] & 0x10)
            self.key['right'] = bool(cd[5] & 0x04)
            self.key['left'] = bool(cd[5] & 0x01)

        elif ci == 0x520:  # hz
            pass

        elif ci == 0x5e0:  # hw/sw radio info
            pass

        elif ci == 0x0a4:  # current cd track, multiframe
            pass

        elif ci == 0x11f:  # band press, multiframe
            pass

        elif ci == 0x125:  # track list, multiframe
            pass

        tuner = self.source == 'Tuner' and self.enabled
        cd = self.source in ('CD', 'CD Changer') and self.enabled
        aux = 'AUX' in self.source and self.enabled

        if not self.enabled:
            self.ss('icon', 'icon')
            self.ss('name', 'Disabled :(')

        elif aux:
            self.ss('icon', 'linein')
            self.ss('name', self.source)

        elif tuner:
            self.ss('icon', 'radio')
            self.ss('name', '')  # TEMP!!!

        elif cd:
            self.ss('icon', self.cd_mp3 and 'cdmp3' or 'cdaudio')
            self.ss('name', self.cd_disk in (1, 3) and ('Track %d/%d' % (self.track_num, self.cd_tracks)) or "Wait...")

        self.ss('band', tuner and self.radio_band or "")
        self.ss('info', tuner and ("%.2f Mhz" % self.radio_freq) or (cd and ("» %s%s" % (self.track_time, self.track_len != "--:--" and " / " + self.track_len or "")) or ""))
        self.ss('memch', tuner and self.radio_mem and str(self.radio_mem) or "")
        self.ss('ta', self.enabled and self.have_ta and "TA" or "")
        self.ss('reg', tuner and self.have_reg and "REG" or "")
        self.ss('rds', tuner and self.rds and "RDS" or "")
        self.ss('rdtxt_rnd', tuner and self.radiotext and "RDTXT" or (cd and self.random and "RDM" or (cd and self.track_intro and "INT" or "")))
        self.ss('loud', self.enabled and self.loudness and "LOUD" or "")
        self.ss('vol', self.enabled and ("Vol: [b]%d[/b]" % self.volume) or "")
