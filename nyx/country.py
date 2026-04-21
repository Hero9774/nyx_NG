# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Hilfsfunktionen zur Anzeige von Ländernamen und Flaggen-Emojis
aus ISO-3166-1-Alpha-2-Ländercodes.
"""

COUNTRY_NAMES = {
    'AD': 'Andorra', 'AE': 'Vereinigte Arabische Emirate', 'AF': 'Afghanistan',
    'AG': 'Antigua und Barbuda', 'AL': 'Albanien', 'AM': 'Armenien',
    'AO': 'Angola', 'AR': 'Argentinien', 'AT': 'Österreich',
    'AU': 'Australien', 'AZ': 'Aserbaidschan',
    'BA': 'Bosnien und Herzegowina', 'BB': 'Barbados', 'BD': 'Bangladesch',
    'BE': 'Belgien', 'BF': 'Burkina Faso', 'BG': 'Bulgarien',
    'BH': 'Bahrain', 'BI': 'Burundi', 'BJ': 'Benin', 'BN': 'Brunei',
    'BO': 'Bolivien', 'BR': 'Brasilien', 'BS': 'Bahamas', 'BT': 'Bhutan',
    'BW': 'Botswana', 'BY': 'Belarus', 'BZ': 'Belize',
    'CA': 'Kanada', 'CD': 'Kongo (DR)', 'CF': 'Zentralafrikanische Republik',
    'CG': 'Kongo', 'CH': 'Schweiz', 'CI': 'Elfenbeinküste', 'CL': 'Chile',
    'CM': 'Kamerun', 'CN': 'China', 'CO': 'Kolumbien', 'CR': 'Costa Rica',
    'CU': 'Kuba', 'CV': 'Cabo Verde', 'CY': 'Zypern', 'CZ': 'Tschechien',
    'DE': 'Deutschland', 'DJ': 'Dschibuti', 'DK': 'Dänemark',
    'DM': 'Dominica', 'DO': 'Dominikanische Republik', 'DZ': 'Algerien',
    'EC': 'Ecuador', 'EE': 'Estland', 'EG': 'Ägypten', 'ER': 'Eritrea',
    'ES': 'Spanien', 'ET': 'Äthiopien',
    'FI': 'Finnland', 'FJ': 'Fidschi', 'FM': 'Mikronesien', 'FR': 'Frankreich',
    'GA': 'Gabun', 'GB': 'Vereinigtes Königreich', 'GD': 'Grenada',
    'GE': 'Georgien', 'GH': 'Ghana', 'GM': 'Gambia', 'GN': 'Guinea',
    'GQ': 'Äquatorialguinea', 'GR': 'Griechenland', 'GT': 'Guatemala',
    'GW': 'Guinea-Bissau', 'GY': 'Guyana',
    'HN': 'Honduras', 'HR': 'Kroatien', 'HT': 'Haiti', 'HU': 'Ungarn',
    'ID': 'Indonesien', 'IE': 'Irland', 'IL': 'Israel', 'IN': 'Indien',
    'IQ': 'Irak', 'IR': 'Iran', 'IS': 'Island', 'IT': 'Italien',
    'JM': 'Jamaika', 'JO': 'Jordanien', 'JP': 'Japan',
    'KE': 'Kenia', 'KG': 'Kirgisistan', 'KH': 'Kambodscha',
    'KI': 'Kiribati', 'KM': 'Komoren', 'KN': 'St. Kitts und Nevis',
    'KP': 'Nordkorea', 'KR': 'Südkorea', 'KW': 'Kuwait', 'KZ': 'Kasachstan',
    'LA': 'Laos', 'LB': 'Libanon', 'LC': 'St. Lucia', 'LI': 'Liechtenstein',
    'LK': 'Sri Lanka', 'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Litauen',
    'LU': 'Luxemburg', 'LV': 'Lettland', 'LY': 'Libyen',
    'MA': 'Marokko', 'MC': 'Monaco', 'MD': 'Moldau', 'ME': 'Montenegro',
    'MG': 'Madagaskar', 'MH': 'Marshallinseln', 'MK': 'Nordmazedonien',
    'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolei', 'MR': 'Mauretanien',
    'MT': 'Malta', 'MU': 'Mauritius', 'MV': 'Malediven', 'MW': 'Malawi',
    'MX': 'Mexiko', 'MY': 'Malaysia', 'MZ': 'Mosambik',
    'NA': 'Namibia', 'NE': 'Niger', 'NG': 'Nigeria', 'NI': 'Nicaragua',
    'NL': 'Niederlande', 'NO': 'Norwegen', 'NP': 'Nepal', 'NR': 'Nauru',
    'NZ': 'Neuseeland',
    'OM': 'Oman',
    'PA': 'Panama', 'PE': 'Peru', 'PG': 'Papua-Neuguinea', 'PH': 'Philippinen',
    'PK': 'Pakistan', 'PL': 'Polen', 'PT': 'Portugal', 'PW': 'Palau',
    'PY': 'Paraguay',
    'QA': 'Katar',
    'RO': 'Rumänien', 'RS': 'Serbien', 'RU': 'Russland', 'RW': 'Ruanda',
    'SA': 'Saudi-Arabien', 'SB': 'Salomonen', 'SC': 'Seychellen',
    'SD': 'Sudan', 'SE': 'Schweden', 'SG': 'Singapur', 'SI': 'Slowenien',
    'SK': 'Slowakei', 'SL': 'Sierra Leone', 'SM': 'San Marino',
    'SN': 'Senegal', 'SO': 'Somalia', 'SR': 'Suriname', 'SS': 'Südsudan',
    'ST': 'São Tomé und Príncipe', 'SV': 'El Salvador', 'SY': 'Syrien',
    'SZ': 'Eswatini',
    'TD': 'Tschad', 'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tadschikistan',
    'TL': 'Osttimor', 'TM': 'Turkmenistan', 'TN': 'Tunesien', 'TO': 'Tonga',
    'TR': 'Türkei', 'TT': 'Trinidad und Tobago', 'TV': 'Tuvalu', 'TZ': 'Tansania',
    'UA': 'Ukraine', 'UG': 'Uganda', 'US': 'Vereinigte Staaten',
    'UY': 'Uruguay', 'UZ': 'Usbekistan',
    'VA': 'Vatikanstadt', 'VC': 'St. Vincent und die Grenadinen',
    'VE': 'Venezuela', 'VN': 'Vietnam', 'VU': 'Vanuatu',
    'WS': 'Samoa',
    'YE': 'Jemen',
    'ZA': 'Südafrika', 'ZM': 'Sambia', 'ZW': 'Simbabwe',
}


def flag_emoji(code):
    """Erstellt das Flaggen-Emoji aus einem 2-Buchstaben-ISO-Ländercode."""
    code = code.upper()
    if len(code) != 2 or not code.isalpha():
        return ''
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code)


def country_display(code):
    """
    Gibt 'FLAG Ländername' zurück, z. B. '🇩🇪 Deutschland'.
    Fällt auf 'FLAG CODE' zurück, wenn der Name unbekannt ist.
    """
    if not code:
        return '–'
    code = code.upper()
    flag = flag_emoji(code)
    name = COUNTRY_NAMES.get(code, code)
    return '%s %s' % (flag, name)
