# Country, states codes
oas_codes = {'01': 'Alabama',
             '02': 'Alaska',
             '04': 'Arizona',
             '05': 'Arkansas',
             '06': 'California',
             '08': 'Colorado',
             '09': 'Connecticut',
             '10': 'Delaware',
             '11': 'DC',
             '12': 'Florida',
             '13': 'Georgia',
             '15': 'Hawaii',
             '16': 'Idaho',
             '17': 'Illinois',
             '18': 'Indiana',
             '19': 'Iowa',
             '20': 'Kansas',
             '21': 'Kentucky',
             '22': 'Louisiana',
             '23': 'Maine',
             '24': 'Maryland',
             '25': 'Massachusetts',
             '26': 'Michigan',
             '27': 'Minnesota',
             '28': 'Mississippi',
             '29': 'Missouri',
             '30': 'Montana',
             '31': 'Nebraska',
             '32': 'Nevada',
             '33': 'New Hampshire',
             '34': 'New Jersey',
             '35': 'New Mexico',
             '36': 'New York',
             '37': 'North Carolina',
             '38': 'North Dakota',
             '39': 'Ohio',
             '40': 'Oklahoma',
             '41': 'Oregon',
             '42': 'Pennsylvania',
             '44': 'Rhode Island',
             '45': 'South Carolina',
             '46': 'South Dakota',
             '47': 'Tennessee',
             '48': 'Texas',
             '49': 'Utah',
             '50': 'Vermont',
             '51': 'Virginia',
             '53': 'Washington',
             '54': 'West Virginia',
             '55': 'Wisconsin',
             '56': 'Wyoming',
             'CA': 'Canada',
             'MX': 'Mexico',
             'PR': 'Puerto Rico',
             'BS': 'Bahamas',
             'AG': 'Antigua and Barbuda',
             'AI': 'Anguilla',
             'NL': 'Netherlands Antilles (formerly AN)',
             'AW': 'Aruba',
             'CU': 'Cuba',
             'DM': 'Dominica',
             'DO': 'Dominican Republic',
             'GP': 'Guadeloupe',
             'HN': 'Honduras',
             'HT': 'Haiti',
             'JM': 'Jamaica',
             'KN': 'St. Kitts and Nevis',
             'KY': 'Cayman Islands',
             'LC': 'Saint Lucia',
             'MQ': 'Martinique',
             'MS': 'Montserrat',
             'TC': 'Turks and Caicos Islands',
             'VG': 'British Virgin Islands',
             'VI': 'Virgin Islands',
             'AS': 'American Samoa',
             'FM': 'Federated States of Micronesia',
             'GU': 'Guam',
             'KI': 'Kiribati',
             'MH': 'Marshall Islands',
             'QM': 'Midway Islands (formerly MI)',
             'MP': 'Northern Mariana Islands',
             'PW': 'Palau',
             'RU': 'Russia',
             'TK': 'Tokelau',
             'QW': 'Wake Island (formerly WQ)',
             'WS': 'Samoa'}
# Verification status
verif_stat_codes = {'O': 'VERIFIED',
                    'U': 'UNVERIFIED'}
# Lighting type
lighting_codes = {'R': 'Red',
                  'D': 'Medium intensity White Strobe and Red',
                  'H': 'Medium intensity White Strobe',
                  'S': 'High Intensity White Strobe',
                  'F': 'Flood',
                  'C': 'Dual Medium Catenary',
                  'W': 'Synchronized Red Lighting',
                  'L': 'Lighted (Type Unknown)',
                  'N': 'None',
                  'U': 'Unknown'}
# Marking type
marking_codes = {'P': 'Orange or Orange and White Paint',
                 'W': 'White Paint Only',
                 'M': 'Marked',
                 'F': 'Flag Marker',
                 'S': 'Spherical Marker',
                 'N': 'None',
                 'U': 'Unknown'}
# Horizontal accuracy and unit of measure, NOTE: -1 indicates UNKNOWN
h_acc_codes = {'1': (20, 'FEET'),
               '2': (50, 'FEET'),
               '3': (100, 'FEET'),
               '4': (250, 'FEET'),
               '5': (500, 'FEET'),
               '6': (1000, 'FEET'),
               '7': (0.5, 'NM'),
               '8': (1, 'NM'),
               '9': (-1, 'UNKNOWN')}
# Vertical accuracy, NOTE: -1 indicates unknown
v_acc_codes = {'A': 3,
               'B': 10,
               'C': 20,
               'D': 50,
               'E': 125,
               'F': 250,
               'G': 500,
               'H': 1000,
               'I': -1}


class ObstacleFAADOF:
    """ Class to store obstacle retrieved from Federal Aviation Administration Digital Obstacle File """
    def __init__(self, line, coordinates_dd=False, decode_values=False):
        """ Constructor
        :param line: string, line of FAA DOF
        :param coordinates_dd: bool, indicates if store latitude and longitude also in decimal degrees format
        :param decode_values: bool, indicates if decode codes for ctry, lighting, marking, horizontal and vertical
                              accuracy
        NOTE: if there are no values for agl height, amsl height = value -9999 is inserted
        """
        self.oas_code = line[0:2]
        self.obs_number = line[0:9]
        self.verif_stat_code = line[10]
        self.lat_dms = line[35:47]
        self.lon_dms = line[48:61]
        self.obs_type = line[62:80].rstrip()
        self.agl_height = line[83:88].lstrip('0')
        if self.agl_height == '':
            self.agl_height = -9999
        self.amsl_height = line[89:94].lstrip('0')
        if self.amsl_height == '':
            self.amsl_height = -9999
        self.lighting_code = line[95]
        self.h_acc_code = line[97]
        self.v_acc_code = line[99]
        self.marking_code = line[101]
        self.jdate = line[120:127]

        if coordinates_dd is False:
            self.lat_dd = None
            self.lon_dd = None
        else:
            self.lat_dd = self.faa_dof_dms2dd(self.lat_dms)
            self.lon_dd = self.faa_dof_dms2dd(self.lon_dms)

        if decode_values is False:
            self.ctry_name = ''
            self.verif_stat_desc = ''
            self.marking_desc = ''
            self.lighting_desc = ''
            self.h_acc_value = ''
            self.h_acc_uom = ''
            self.v_acc_value = ''
            self.v_acc_uom = ''
        else:
            try:
                self.ctry_name = oas_codes.get(self.oas_code)
            except KeyError:
                self.ctry_name = ''

            try:
                self.verif_stat_desc = verif_stat_codes.get(self.verif_stat_code)
            except KeyError:
                self.verif_stat_desc = ''

            try:
                self.marking_desc = marking_codes.get(self.marking_code)
            except KeyError:
                self.marking_desc = ''

            try:
                self.lighting_desc = lighting_codes.get(self.lighting_code)
            except KeyError:
                self.lighting_desc = ''

            try:
                self.v_acc_value = v_acc_codes.get(self.v_acc_code, -999)
                self.v_acc_uom = 'FEET'
            except KeyError:
                self.v_acc_value = -999
                self.v_acc_uom = ''

            try:
                if self.h_acc_code == '':
                    self.h_acc_value = -9999
                    self.h_acc_uom = 'NO DATA'
                else:
                    h_acc_decode = h_acc_codes.get(self.h_acc_code)
                    if h_acc_decode is None:
                        self.h_acc_value = -999
                        self.h_acc_uom = 'NO_DATA'
                    else:
                        self.h_acc_value = h_acc_decode[0]
                        self.h_acc_uom = h_acc_decode[1]
            except KeyError:
                self.v_acc_value = -9999
                self.v_acc_uom = 'NO_DATA'

    @staticmethod
    def faa_dof_dms2dd(dms):
        """ Converts DMS format of latitude, longitude in DOF file to DD format
        param: dms: string, latitude or longitude in degrees, minutes, seconds format
        return: dd: float, latitude or longitude in decimal degrees format
        """
        h = dms[len(dms) - 1]
        dms_m = dms[:len(dms) - 1]
        dms_t = dms_m.split(' ')
        d = float(dms_t[0])
        m = float(dms_t[1])
        s = float(dms_t[2])

        dd = d + m / 60 + s / 3600
        if h in ['W', 'S']:
            dd = - dd
        return dd
