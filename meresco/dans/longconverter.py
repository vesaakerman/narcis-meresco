## begin license ##
#
#
## end license ##

import sys

from lxml import etree
from lxml.etree import parse, _ElementTree, tostring

from StringIO import StringIO
from xml.sax.saxutils import escape as escapeXml

from meresco.core import Observable
from meresco.components import lxmltostring
from meresco.dans.metadataformats import MetadataFormat
from meresco.dans.uiaconverter import UiaConverter
from meresco.dans.nameidentifier import Orcid, Dai, Isni, Rid, NameIdentifierFactory
from meresco.xml import namespaces

from re import compile

from dateutil.parser import parse as parseDate
from datetime import *

import time

namespacesmap = namespaces.copyUpdate({ #  See: https://github.com/seecr/meresco-xml/blob/master/meresco/xml/namespaces.py
    
    'dip'    : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'    : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'dai'    : 'info:eu-repo/dai',
    'gal'    : 'info:eu-repo/grantAgreement',
    'wmp'    : 'http://www.surfgroepen.nl/werkgroepmetadataplus',
    'prs'    : 'http://www.onderzoekinformatie.nl/nod/prs',
    'proj'   : 'http://www.onderzoekinformatie.nl/nod/act',
    'org'    : 'http://www.onderzoekinformatie.nl/nod/org',
    'long'   : 'http://www.knaw.nl/narcis/1.0/long/',
    'short'  : 'http://www.knaw.nl/narcis/1.0/short/',
    'mods'   : 'http://www.loc.gov/mods/v3',
    'didl'   : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'norm'   : 'http://dans.knaw.nl/narcis/normalized',
})


LONG_VERSION = '1.0'

marcRelatorRoleTerms=['abr','acp','act','adi','adp','aft','anl','anm','ann','ant','ape','apl','app','aqt','arc','ard','arr','art','asg','asn','ato','att','auc','aud','aui','aus','aut','bdd','bjd','bkd','bkp','blw','bnd','bpd','brd','brl','bsl','cas','ccp','chr','clb','cli','cll','clr','clt','cmm','cmp','cmt','cnd','cng','cns','coe','col','com','con','cor','cos','cot','cou','cov','cpc','cpe','cph','cpl','cpt','cre','crp','crr','crt','csl','csp','cst','ctb','cte','ctg','ctr','cts','ctt','cur','cwt','dbp','dfd','dfe','dft','dgg','dgs','dis','dln','dnc','dnr','dpc','dpt','drm','drt','dsr','dst','dtc','dte','dtm','dto','dub','edc','edm','edt','egr','elg','elt','eng','enj','etr','evp','exp','fac','fds','fld','flm','fmd','fmk','fmo','fmp','fnd','fpy','frg','gis','grt','his','hnr','hst','ill','ilu','ins','inv','isb','itr','ive','ivr','jud','jug','lbr','lbt','ldr','led','lee','lel','len','let','lgd','lie','lil','lit','lsa','lse','lso','ltg','lyr','mcp','mdc','med','mfp','mfr','mod','mon','mrb','mrk','msd','mte','mtk','mus','nrt','opn','org','orm','osp','oth','own','pan','pat','pbd','pbl','pdr','pfr','pht','plt','pma','pmn','pop','ppm','ppt','pra','prc','prd','pre','prf','prg','prm','prn','pro','prp','prs','prt','prv','pta','pte','ptf','pth','ptt','pup','rbr','rcd','rce','rcp','rdd','red','ren','res','rev','rpc','rps','rpt','rpy','rse','rsg','rsp','rsr','rst','rth','rtm','sad','sce','scl','scr','sds','sec','sgd','sgn','sht','sll','sng','spk','spn','spy','srv','std','stg','stl','stm','stn','str','tcd','tch','ths','tld','tlp','trc','trl','tyd','tyg','uvp','vac','vdg','voc','wac','wal','wam','wat','wdc','wde','win','wit','wpr','wst']

## ORDER DOES MATTER!:
pubTypes=['annotation','article','bachelorthesis','book','bookpart','bookreview','conferencepaper','contributiontoperiodical','doctoralthesis','researchproposal','lecture','masterthesis','patent','preprint','report','studentthesis','technicaldocumentation','workingpaper','conferenceobject','other','conferenceitem','conferenceitemnotinproceedings','conferenceposter','conferenceproceedings','reportpart','review']

#Taken from: http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
ISO639 = ["aar", "abk", "ace", "ach", "ada", "ady", "afa", "afh", "afr", "ain", "aka", "akk", "alb", "ale", "alg", "alt", "amh", "ang", "anp", "apa", "ara", "arc", "arg", "arm", "arn", "arp", "art", "arw", "asm", "ast", "ath", "aus", "ava", "ave", "awa", "aym", "aze", "bad", "bai", "bak", "bal", "bam", "ban", "baq", "bas", "bat", "bej", "bel", "bem", "ben", "ber", "bho", "bih", "bik", "bin", "bis", "bla", "bnt", "bos", "bra", "bre", "btk", "bua", "bug", "bul", "bur", "byn", "cad", "cai", "car", "cat", "cau", "ceb", "cel", "cha", "chb", "che", "chg", "chi", "chk", "chm", "chn", "cho", "chp", "chr", "chu", "chv", "chy", "cmc", "cop", "cor", "cos", "cpe", "cpf", "cpp", "cre", "crh", "crp", "csb", "cus", "cze", "dak", "dan", "dar", "day", "del", "den", "dgr", "din", "div", "doi", "dra", "dsb", "dua", "dum", "dut", "dyu", "dzo", "efi", "egy", "eka", "elx", "eng", "enm", "epo", "est", "ewe", "ewo", "fan", "fao", "fat", "fij", "fil", "fin", "fiu", "fon", "fre", "frm", "fro", "frr", "frs", "fry", "ful", "fur", "gaa", "gay", "gba", "gem", "geo", "ger", "gez", "gil", "gla", "gle", "glg", "glv", "gmh", "goh", "gon", "gor", "got", "grb", "grc", "gre", "grn", "gsw", "guj", "gwi", "hai", "hat", "hau", "haw", "heb", "her", "hil", "him", "hin", "hit", "hmn", "hmo", "hrv", "hsb", "hun", "hup", "iba", "ibo", "ice", "ido", "iii", "ijo", "iku", "ile", "ilo", "ina", "inc", "ind", "ine", "inh", "ipk", "ira", "iro", "ita", "jav", "jbo", "jpn", "jpr", "jrb", "kaa", "kab", "kac", "kal", "kam", "kan", "kar", "kas", "kau", "kaw", "kaz", "kbd", "kha", "khi", "khm", "kho", "kik", "kin", "kir", "kmb", "kok", "kom", "kon", "kor", "kos", "kpe", "krc", "krl", "kro", "kru", "kua", "kum", "kur", "kut", "lad", "lah", "lam", "lao", "lat", "lav", "lez", "lim", "lin", "lit", "lol", "loz", "ltz", "lua", "lub", "lug", "lui", "lun", "luo", "lus", "mac", "mad", "mag", "mah", "mai", "mak", "mal", "man", "mao", "map", "mar", "mas", "may", "mdf", "mdr", "men", "mga", "mic", "min", "mis", "mkh", "mlg", "mlt", "mnc", "mni", "mno", "moh", "mon", "mos", "mul", "mun", "mus", "mwl", "mwr", "myn", "myv", "nah", "nai", "nap", "nau", "nav", "nbl", "nde", "ndo", "nds", "nep", "new", "nia", "nic", "niu", "nno", "nob", "nog", "non", "nor", "nqo", "nso", "nub", "nwc", "nya", "nym", "nyn", "nyo", "nzi", "oci", "oji", "ori", "orm", "osa", "oss", "ota", "oto", "paa", "pag", "pal", "pam", "pan", "pap", "pau", "peo", "per", "phi", "phn", "pli", "pol", "pon", "por", "pra", "pro", "pus", "que", "raj", "rap", "rar", "roa", "roh", "rom", "rum", "run", "rup", "rus", "sad", "sag", "sah", "sai", "sal", "sam", "san", "sas", "sat", "scn", "sco", "sel", "sem", "sga", "sgn", "shn", "sid", "sin", "sio", "sit", "sla", "slo", "slv", "sma", "sme", "smi", "smj", "smn", "smo", "sms", "sna", "snd", "snk", "sog", "som", "son", "sot", "spa", "srd", "srn", "srp", "srr", "ssa", "ssw", "suk", "sun", "sus", "sux", "swa", "swe", "syc", "syr", "tah", "tai", "tam", "tat", "tel", "tem", "ter", "tet", "tgk", "tgl", "tha", "tib", "tig", "tir", "tiv", "tkl", "tlh", "tli", "tmh", "tog", "ton", "tpi", "tsi", "tsn", "tso", "tuk", "tum", "tup", "tur", "tut", "tvl", "twi", "tyv", "udm", "uga", "uig", "ukr", "umb", "und", "urd", "uzb", "vai", "ven", "vie", "vol", "vot", "wak", "wal", "war", "was", "wel", "wen", "wln", "wol", "xal", "xho", "yao", "yap", "yid", "yor", "ypk", "zap", "zbl", "zen", "zha", "znd", "zul", "zun", "zxx", "zza", "bod", "ces", "cym", "deu", "ell", "eus", "fas", "fra", "hye", "isl", "kat", "mkd", "mri", "msa", "mya", "nld", "ron", "slk", "sqi", "zho", "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv", "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd", "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb","lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru", "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"]

BINDING_DELIMITER = '; '

# mods:nameIdentifiers that will be processed to long. Other types will be ignored!
# ORDER does matter!
supportedNids = ['dai-nl', 'orcid', 'isni', 'nod-prs']

class NormaliseOaiRecord(UiaConverter):

    ACCESS_LEVELS = ['openAccess', 'restrictedAccess', 'closedAccess', 'embargoedAccess']

    def __init__(self, fromKwarg, toKwarg=None, name=None):
        UiaConverter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._metadataformat = None
        self._openAccess = True

    def _convert(self, lxmlNode):
        self._openAccess = True #Reset AccesRights to openAcces

        record_part = lxmlNode.xpath("//document:document/document:part[@name='record']/text()", namespaces=namespacesmap)
        metapart = lxmlNode.xpath("//document:document/document:part[@name='meta']/text()", namespaces=namespacesmap)
        wcpcollection = None
        if len(metapart) == 1:
            meta_lxml = etree.fromstring(metapart[0])
            collection = meta_lxml.xpath('//meta:repository/meta:collection/text()', namespaces=namespacesmap)
            if len(collection) == 1: wcpcollection = collection[0]

        record_lxml = etree.fromstring(record_part[0]) # Geen xml.sax.saxutils.unescape() hier: Dat doet lxml reeds voor ons.
        self._metadataformat = MetadataFormat.getFormat(record_lxml, self._uploadid) #TODO: pass it somehow from DNA, so we need to look this up only once per record.
        converted_record_lxml = self._convertRecordMetadataToLong(record_lxml, wcpcollection)# Check en insert normalised mods into record part.
        record_txt = etree.tostring(converted_record_lxml, encoding="UTF-8") # convert from lxml to text.
        record_txt = record_txt.decode('utf-8') # Soms worden er chars opgestuurd die geen unicode zijn. Deze converteren we 'brute force'.
        lxmlNode.find('document:part[@name="record"]', namespaces=namespacesmap).text = record_txt # Set as text value.
        # etree.cleanup_namespaces(lxmlNode)
        return lxmlNode



    def _convertRecordMetadataToLong(self, lxmlNode, wcpCollection):
        
    # lxmlNode record example:
    # 
    # <record xmlns="http://www.openarchives.org/OAI/2.0/"
    #     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    #     <header xmlns="http://www.openarchives.org/OAI/2.0/">
    #         <identifier>record:1</identifier>
    #         <datestamp>2008-12-15T14:08:34Z</datestamp>
    #     </header>
    #     <metadata xmlns="http://www.openarchives.org/OAI/2.0/">
    #         <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
    #             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    #             xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/      http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
    #             <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/"
    #                 >http://meresco.com?record=1</dc:identifier>
    #             <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">This is an example program
    #                 about Search with Meresco</dc:description>
    #             <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Example Program 1</dc:title>
    #             <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:creator>
    #             <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Seecr</dc:publisher>
    #             <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2016</dc:date>
    #             <dc:type xmlns:dc="http://purl.org/dc/elements/1.1/">Example</dc:type>
    #             <dc:subject xmlns:dc="http://purl.org/dc/elements/1.1/">Search &amp; Destroy</dc:subject>
    #             <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
    #             <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">Open Source</dc:rights>
    #         </oai_dc:dc>
    #     </metadata>
    # </record>

        # De twee placeholders voor het originele- en genormaliseerde record:
        e_original_root = etree.Element(namespacesmap.curieToTag('norm:md_original'))
        e_norm_root = etree.Element(namespacesmap.curieToTag('norm:normalized'))

        if self._metadataformat is not None:
            # Create rootelement:
            e_longroot = etree.SubElement(e_norm_root, namespacesmap.curieToTag('long:long'), nsmap={None:namespacesmap['long']})
            # e_longroot = etree.Element(namespacesmap.curieToTag('long:long'), nsmap={None:namespacesmap['long']})
            e_longroot.set("version", LONG_VERSION)
            # Add WCP Collection to long format:
            etree.SubElement(e_longroot, "wcpcollection").text = wcpCollection

            e_longmetadata = etree.Element("metadata")

            if self._metadataformat in (MetadataFormat.MD_FORMAT[5], MetadataFormat.MD_FORMAT[6], MetadataFormat.MD_FORMAT[7]): # NOD records
                self._convertNODRecord2long(lxmlNode, e_longmetadata)
                e_longroot.append(e_longmetadata)

            else: # Publications and datasets...

                # Toplevel elements:
                self._getModificationDate(lxmlNode, e_longroot)
                self._getHumanStartPage(lxmlNode, e_longroot)
                self._getPersistentIdentifier(lxmlNode, e_longroot)
                self._getObjectFiles(lxmlNode, e_longroot)
                # All ObjectFiles have been looped through: accessright should now be known:
                self._getAccessRights(lxmlNode, e_longroot) #TODO: double check this.

                # Second level metadata elements:
                self._getTitleInfo(lxmlNode, e_longmetadata)
                self._getNames(lxmlNode, e_longmetadata)
                self._getRightsDescription(lxmlNode, e_longmetadata)
                self._getGenre(lxmlNode, e_longmetadata)
                self._getPublisher(lxmlNode, e_longmetadata)
                self._getPhysicalDescription(lxmlNode, e_longmetadata)
                self._getSubject(lxmlNode, e_longmetadata)
                self._getAbstract(lxmlNode, e_longmetadata)
                self._getDateIssued(lxmlNode, e_longmetadata)
                self._getModsIdentifier(lxmlNode, e_longmetadata)
                self._getLanguage(lxmlNode, e_longmetadata)
                self._getLocationUrl(lxmlNode, e_longmetadata)
                self._getRelatedItems(lxmlNode, e_longmetadata)
                self._getPlaceterm(lxmlNode, e_longmetadata)
                self._getCoverage(lxmlNode, e_longmetadata)
                self._getFormat(lxmlNode, e_longmetadata)
                self._getTypeOfResource(lxmlNode, e_longmetadata)
                self._getFunding(lxmlNode, e_longmetadata)

                # Add metadata element to 'long' root:
                e_longroot.append(e_longmetadata)

                # print "WST:", type(e_longroot)
                # savedxml = etree.ElementTree(e_longroot)
                # print "CONVERTED:", type(savedxml)
                # We need to parse the _Element type first to be able to use proper xpath with namespaces on the nodes? WHY? Conversion to _ElementTree does NOT work??
                # tree_long = None
                try: # TODO: try this: .getroot().getroottree()
                    e_longroot = parse(StringIO(tostring(e_longroot)))
                except:
                    print 'Error while parsing', tostring(e_longroot)
                    raise
                self._addHostCitation(e_longroot) # Adds hostcitation string from '/long/metadata' to 'long' node.

            # print 'Long convertion succeeded...' # , tostring(e_norm_root)


        metadata_tags = lxmlNode.xpath("//oai:metadata/*", namespaces=namespacesmap)

        for child in metadata_tags:
            e_original_root.append(child) # voeg originele md toe aan placeholder origineel...
            metadata_tags.remove(child) # verwijder originele md van oai metadata tag...

        for child in lxmlNode.getchildren():
            if child.tag == namespacesmap.curieToTag('oai:metadata'):
                child.append(e_original_root)
                child.append(e_norm_root)
                e_original_root.text = child.text # Copy any (incorrect!) text node from metadata tag to the placeholder origineel.
                child.text = "" # Delete (incorrect!) text node from metadata tag.

        return lxmlNode


    def _convertNODRecord2long(self, lxmlNode, e_longmetadata):
        
        title, title_en, penvoerder_nl, penvoerder_en, abstract, abstract_en, locatie, status, knaw_long, genre, e_name = None, None, None, None, None, None, None, None, None, None, None

        # ORGANISATIE:
        if self._metadataformat == MetadataFormat.MD_FORMAT[5]:
            genre = 'organisation'

            title = lxmlNode.xpath('//org:naam_nl/text()', namespaces=namespacesmap)
            title_en = lxmlNode.xpath('//org:naam_en/text()', namespaces=namespacesmap)
        
            abstract = lxmlNode.xpath("//org:taak_nl/text()", namespaces=namespacesmap)
            abstract_en = lxmlNode.xpath("//org:taak_en/text()", namespaces=namespacesmap)
            
            # Locatie: In Dutch (NL) only!
            locatie = lxmlNode.xpath("//org:locatie/text()", namespaces=namespacesmap)
        
        # PROJECT:
        elif self._metadataformat == MetadataFormat.MD_FORMAT[6]:
            genre = 'research'

            title = lxmlNode.xpath('//proj:title_nl/text()', namespaces=namespacesmap)
            title_en = lxmlNode.xpath('//proj:title_en/text()', namespaces=namespacesmap)

            abstract = lxmlNode.xpath("//proj:summary_nl/text()", namespaces=namespacesmap)
            abstract_en = lxmlNode.xpath("//proj:summary_en/text()", namespaces=namespacesmap)
        
            # Penvoerder:
            penvoerder = lxmlNode.xpath("//proj:penvoerder/proj:naam[@xml:lang='nl']/text()", namespaces=namespacesmap)
            penvoerder_en = lxmlNode.xpath("//proj:penvoerder/proj:naam[@xml:lang='en']/text()", namespaces=namespacesmap)
        
            # Status onderzoek (C/D):
            status = lxmlNode.xpath("//proj:status/text()", namespaces=namespacesmap)
        
        # PERSOON:
        elif self._metadataformat == MetadataFormat.MD_FORMAT[7]:
            genre = 'person'

            title = lxmlNode.xpath("//prs:fullName/text()", namespaces=namespacesmap)
            if not title:
                title.append('n.a.')
            title_en = title
        
            abstract = lxmlNode.xpath("//prs:expertise_nl/text()", namespaces=namespacesmap)
            abstract_en = lxmlNode.xpath("//prs:expertise_en/text()", namespaces=namespacesmap)
        
            # Copy ALL nameIdentifiers + OLD <dai> tag ########
            e_name = etree.Element("name")
            etree.SubElement(e_name, "type").text = 'personal'
            etree.SubElement(e_name, "name").text = title[0]
            # dai = self._findAndBind(lxmlNode, '\n<dai>info:eu-repo/dai/nl/%s</dai>', '//prs:persoon/prs:dai/text()')
            dai = lxmlNode.xpath("//prs:persoon/prs:dai/text()", namespaces=namespacesmap)
            if dai and len(dai) > 0:

                nameId = NameIdentifierFactory.factory('dai-nl', dai[0].strip())
                if nameId.is_valid():
                    etree.SubElement(e_name, "dai").text = nameId.get_id()

            nids = lxmlNode.xpath("//prs:persoon/prs:nameIdentifier", namespaces=namespacesmap)
            for nid in nids:  # serialize complete tag and remove default namespace...
                nid_type = nid.xpath('self::prs:nameIdentifier/@type', namespaces=namespacesmap)
                nid_val = nid.xpath('self::prs:nameIdentifier/text()', namespaces=namespacesmap)
                if len(nid_type) > 0 and len(nid_val) > 0:
                    etree.SubElement(e_name, "nameIdentifier", type=nid_type[0]).text = nid_val[0]


        ############ ADD Titles #######################
        if title and len(title) > 0:
            etree.SubElement(etree.SubElement(e_longmetadata, "titleInfo"), "title").text = title[0]

        if title_en and len(title_en) > 0:
            e_titleInfo = etree.SubElement(e_longmetadata, "titleInfo")
            e_titleInfo.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
            etree.SubElement(e_titleInfo, "title").text = title_en[0]


        ###### Penvoerder ##################
        if penvoerder_nl and len(penvoerder_nl) > 0:
            e_penvoerder = etree.SubElement(e_longmetadata, "penvoerder")
            e_penvoerder.attrib[namespacesmap.curieToTag('xml:lang')] = "nl"
            e_penvoerder.text = penvoerder_nl[0]

        if penvoerder_en and len(penvoerder_en) > 0:
            e_penvoerder_en = etree.SubElement(e_longmetadata, "penvoerder")
            e_penvoerder_en.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
            e_penvoerder_en.text = penvoerder_en[0]

        ######## Add name elements (3rd last)#######
        if e_name is not None:
            e_longmetadata.append(e_name)
            # etree.SubElement(e_longmetadata, e_name.getroot())

        ######## Add Genre (2nd last)#######
        etree.SubElement(e_longmetadata, "genre").text = genre

        ############ ADD Abstracts (1 na laatste) #######################
        if abstract and len(abstract) > 0:
            etree.SubElement(e_longmetadata, "abstract").text = abstract[0]

        if abstract_en and len(abstract_en) > 0:
            e_abstract = etree.SubElement(e_longmetadata, "abstract")
            e_abstract.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
            e_abstract.text = abstract_en[0]

        ############ laatste 'status' #######################
        if status and len(status) > 0:
            etree.SubElement(e_longmetadata, "status").text = status[0]


    def _getModificationDate(self, lxmlNode, e_longRoot):
        datestamp = lxmlNode.xpath('//oai:header/oai:datestamp/text()', namespaces=namespacesmap)
        if len(datestamp) > 0:
            etree.SubElement(e_longRoot, "modificationDate").text = datestamp[0]


    def _getTitleInfo(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
        # In contrast to all other translated tags(xml:lang="en"), this tag will ALWAYS have an xml:lang="en" and none xml:lang value.
        # Others (f.i. <abstract>) might lack the xml:lang="en" tag.
        if self._metadataformat in (MetadataFormat.MD_FORMAT[5], MetadataFormat.MD_FORMAT[6], MetadataFormat.MD_FORMAT[7]):
            title = self._findFirstXpath(lxmlNode, '//org:naam_nl/text()', '//proj:title_nl/text()', '//prs:fullName/text()')
            if len(title) > 0:
                etree.SubElement(etree.SubElement(e_longmetadata, "titleInfo"), "title").text = title[0]
                if self._metadataformat == MetadataFormat.MD_FORMAT[7]: # Person name also in english:
                    e_titleInfo = etree.SubElement(e_longmetadata, "titleInfo")
                    e_titleInfo.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
                    etree.SubElement(e_titleInfo, "title").text = title[0]

            title_en = self._findFirstXpath(lxmlNode, '//org:naam_en/text()', '//proj:title_en/text()')
            if len(title_en) > 0:
                e_titleInfo = etree.SubElement(e_longmetadata, "titleInfo")
                e_titleInfo.attrib[namespacesmap.curieToTag('xml:lang')] = "en"
                etree.SubElement(e_titleInfo, "title").text = title_en[0]
        else:
            # In contrast to all other translated tags(xml:lang="en"), this tag will ALWAYS have an xml:lang="en" and none xml:lang value. Others (f.i. <abstract>) might lack the xml:lang="en" tag.
            # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
            # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
            titleNL = ['',''] #wrapper for titleInfo string -> [('NL'||empty||!='EN')|| DC], ['EN' || [first titleInfo]].
            titleEN = None
            #Get title from any dc: (only ONE)
            if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]): #if not fullmods:
                dc_titles = lxmlNode.xpath('//dc:title[1]/text()', namespaces=namespacesmap)
                if dc_titles: # Found dc:title. Do NOT check if we're dealing with a subtitle (colon delimited according to SurfShare DC):
                    titleNL[0] = dc_titles[0]
            # Override found DC (sub)title with (m)mods's title value's:
            if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                en = lxmlNode.xpath(root+"mods:titleInfo[@xml:lang='en']", namespaces=namespacesmap)
                nl = lxmlNode.xpath(root+"mods:titleInfo[@xml:lang='nl']", namespaces=namespacesmap)
                if len(nl) == 0: #If no Dutch, try to find tag without a language designation.
                    nl = lxmlNode.xpath(root+"mods:titleInfo[not(@xml:lang)]", namespaces=namespacesmap)
                    if len(nl) == 0: #If not empty language desigation, try to find tag with language designation other than 'en':
                        nl = lxmlNode.xpath(root+"mods:titleInfo[not(@xml:lang='en')]", namespaces=namespacesmap)
                        if len(nl) == 0: # Assign English lang.
                            nl = en
                if len(nl) > 0:
                    titleNL = self._titleFromTitleInfo(nl[0])
                if len(en) > 0:
                    titleEN = self._titleFromTitleInfo(en[0])
            if not titleEN or not titleEN[0] or titleEN[0] == '':
                titleEN = titleNL
            e_longmetadata.append(self._titleTag(titleNL))
            e_longmetadata.append(self._titleTag(titleEN, 'en'))


    def _titleFromTitleInfo(self, titleInfoNode):
        if titleInfoNode is not None:
            title = titleInfoNode.xpath('self::mods:titleInfo/mods:title/text()', namespaces=namespacesmap)
            subtitle = titleInfoNode.xpath('self::mods:titleInfo/mods:subTitle/text()', namespaces=namespacesmap)
        else:
            return
        if len(title) > 0:
            title = title[0].strip()
        if len(subtitle) > 0:
            subtitle = subtitle[0].strip()
        return [title, subtitle]


    def _titleTag(self, titles=['',''], xmllang=None):
        if not titles or not titles[0] or titles[0] == '':
            titles = ['None', None]
        e_titleinfo = etree.Element("titleInfo")
        if xmllang is not None:
            e_titleinfo.attrib[namespacesmap.curieToTag('xml:lang')] = xmllang
        e_title = etree.SubElement(e_titleinfo, "title").text = titles[0]
        subtitle = ''
        if titles[1]:
            e_subtitle = etree.SubElement(e_titleinfo, "subtitle").text = titles[1]
        return e_titleinfo


    def _getHumanStartPage(self, lxmlNode, e_longRoot):
        # DIDL or DC(1st dc:identifier)
        hsp = self._findFirstXpath(lxmlNode,
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        "//dc:identifier[contains(.,'://')]/text()", #fallback DC        
        "//mods:mods/mods:location/mods:url[contains(.,'://')]/text()", #fallback MODS
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        "//dc:identifier[1]/text()") #Greedy fallback DC. If all else fails...
        if len(hsp) > 0:
            etree.SubElement(e_longRoot, "humanStartPage").text = hsp[0].strip()

    def _getPersistentIdentifier(self, lxmlNode, e_longRoot):
        pi = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=namespacesmap)
        if len(pi) > 0:
            e_pi = etree.SubElement(e_longRoot, "persistentIdentifier")
            e_pi.text = pi[0].strip()
            uri = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref', namespaces=namespacesmap)
            if len(uri) > 0:
                e_pi.attrib['ref'] = uri[0]

    def _getObjectFiles(self, lxmlNode, e_longRoot):
        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
        e_objectFiles = None
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): #FULLMODS only!
            if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): # MODS >= 3.0
                objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]', namespaces=namespacesmap)
            else: #Fallback to DIDL 2.3.1
                objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]', namespaces=namespacesmap)
            if len(objectfiles) > 0: e_objectFiles = etree.SubElement(e_longRoot, "objectFiles")
            
            if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                # >= DIDL3.0 only:
                # Get all accessRights for all objectFiles in one list:
                accesssRights = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=namespacesmap)
                if (len(objectfiles) > 0 and len(accesssRights) == len(objectfiles) and str(accesssRights).lower().find('openaccess') == -1 ) or (len(objectfiles)==0):
                    self._openAccess = False
#                     print "FOUND CLOSED ACCESS!"

            for objectfile in objectfiles:
                #create objectFile element:
                e_objectFile = etree.SubElement(e_objectFiles, "objectFile")
                #Look for resources to add:
                didl_resources = objectfile.xpath('self::didl:Item/didl:Component/didl:Resource', namespaces=namespacesmap)
                for resource in didl_resources:
                    e_resource = etree.SubElement(e_objectFile, "resource")
                    mimeType = resource.xpath('self::didl:Resource/@mimeType', namespaces=namespacesmap)
                    uri = resource.xpath('self::didl:Resource/@ref', namespaces=namespacesmap)
                    if mimeType:
                        e_resource.set("mimeType", mimeType[0])
                    if uri:
                        e_resource.set("ref", uri[0])
                        
                #Look for PI:3.0=mandatory; < 3.0=optional!
                pi = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=namespacesmap)
                if pi:
                    e_persistentIdentifier = etree.SubElement(e_objectFile, "persistentIdentifier")
                    e_persistentIdentifier.text = pi[0].strip()

                #DIDL3.0 stuff:
                if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
                    #look for embargo:
                    embargo = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:available/text()', namespaces=namespacesmap)
                    if embargo:
                        e_embargo = etree.SubElement(e_objectFile, "embargo")
                        e_embargo.text = embargo[0].strip() 
                    #look for description:
                    descrip = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dc:description/text()', namespaces=namespacesmap)
                    if descrip:
                        e_descrip = etree.SubElement(e_objectFile, "description")
                        e_descrip.text = descrip[0].strip()
                    #look for published version(author/publisher):
                    publicationVersion = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/rdf:type/@rdf:resource[contains(.,"published") or contains(.,"author")]', namespaces=namespacesmap)
                    if publicationVersion: #both (author/publisher) may be available: we'll take the first one...
                        e_publicationVersion = etree.SubElement(e_objectFile, "publicationVersion")
                        e_publicationVersion.text = publicationVersion[0].strip()[publicationVersion[0].strip().rfind('/')+1:]
                    #Look for AccessRights:
                    oa = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=namespacesmap)
                    if oa:
                        e_accessRights = etree.SubElement(e_objectFile, "accessRights")
                        if oa[0].lower().find('openaccess') >= 0:
                            e_accessRights.text = NormaliseOaiRecord.ACCESS_LEVELS[0]
                        else:
                            e_accessRights.text = NormaliseOaiRecord.ACCESS_LEVELS[2]

    def _getAccessRights(self, lxmlNode, e_longRoot):
        # Let op: Het aantal objectFiles dient bij aanroep reeds bekend te zijn in _getObjectFiles().
        # All formats different from DIDL3.0: No way to determine AccessRights (yet).
        # In this case, accessRights SHOULD be available from the metaPart (stack), if not, we will default to 'openAccess'
        accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] # default 'openAccess'

        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
        
        #Check for DC: See if any valid dc:rights element is available, if not AccessLevel is available from the requestscope (CA-mapper)
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0]):
            # if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None:
            #     accessRight = self.ctx.requestScope.get('accessRights') #AR set in metaPart by mapper: Setting AR to stack value
            # else:
            accessLevels = lxmlNode.xpath('//dc:rights/text()', namespaces=namespacesmap)
            if len(accessLevels) > 0:
                for dc_accesslevel in accessLevels: # dc:rights may contain any kind of text, so we will look for the first valid occurence!
                    for ar in NormaliseOaiRecord.ACCESS_LEVELS:
                        if ar.lower() in dc_accesslevel.strip().lower():
                            accessRight = ar
                            break
        
        # if self._ssFormat not in (SurfShareFormat.SURFSHARE_FORMAT[4]): #No format found capable of setting accessRights from metadata...
        #     if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None:
        #         accessRight = self.ctx.requestScope.get('accessRights') #AR set in metaPart by mapper: Setting AR to stack value                
                
        if self._metadataformat in (MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]): #Gets accessRights from metadata:
            #Check accessRights from metaPart are available on the stack:
            # if hasattr(self.ctx, 'requestScope') and self.ctx.requestScope.get('accessRights') is not None: raise AccessRightsError('AccessRights should not be available from metaPart when using DIDL/MODS. (use of wrong wcp mapper?)')
            # else: accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] if self._openAccess == True else NormaliseOaiRecord.ACCESS_LEVELS[2] # Found AR in metadataPart...
            accessRight = NormaliseOaiRecord.ACCESS_LEVELS[0] if self._openAccess == True else NormaliseOaiRecord.ACCESS_LEVELS[2] # Found AR in metadataPart...
            
        etree.SubElement(e_longRoot, "accessRights").text = accessRight # default 'openAccess'

    def _getNames(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
#MODS:
# <name type="personal" ID="n1">
#     <namePart type="family">Vries, de</namePart>
#     <namePart type="given">J. (Jan)</namePart>
#     <role>
#         <roleTerm authority="marcrelator" type="code">aut</roleTerm>
#     </role>
#     <nameIdentifier type="dai-nl" typeURI="info:eu-repo/dai/nl">123456789</nameIdentifier>
#     <nameIdentifier type="isni" typeURI="http://id.loc.gov/vocabulary/identifiers/isni">http://www.isni.org/0000000133334444555X</nameIdentifier>
#     <nameIdentifier type="orcid" typeURI="http://id.loc.gov/vocabulary/identifiers/orcid">http://orcid.org/0000-0002-1825-0097</nameIdentifier>
# </name>

#knaw_long:
# <dai>info:eu-repo/dai/nl/328277916</dai><nameIdentifier type=\"dai-nl\">328277916</nameIdentifier><nameIdentifier type=\"orcid\">000000021694233X</nameIdentifier><nameIdentifier type=\"isni\">0000000117247366</nameIdentifier>
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            nameTypes = ['personal','corporate','conference','NOTYPE'] # NOTYPE used to catch names without a type attribute! We will tread them as type 'personal'.
            namepartTypes=['family','given','termsOfAddress'] # 'unstructured' is special :(
            for nameType in nameTypes: #alle personal namen, alle corporate namen etc.
                if nameType == nameTypes[3]: # Change xpath, to get all names without @type
                    names = lxmlNode.xpath(root+'mods:name[not(@type)]', namespaces=namespacesmap)
                    nameType = nameTypes[0] # Assign "personal" type to them.... quick & dirty, maar we moeten wat, anders geen datasets van DANS...
                else:
                    names = lxmlNode.xpath(root+'mods:name[@type="'+nameType+'"]', namespaces=namespacesmap)
                for name in names: #voor iedere personal naam, voor iedere corrporate naam, etc.
                    namepartDict = dict.fromkeys(namepartTypes) # reset dict elements
                    unstructured = None
                    for namepartType in namepartTypes:
                        namePart = name.xpath('self::mods:name/mods:namePart[@type="'+namepartType+'"]/text()', namespaces=namespacesmap)
                        if namePart and namePart[0].strip() != '':
                            namepartDict[namepartType] = namePart[0].strip()
                    #Look for unstructured names:
                    namePart = name.xpath('self::mods:name/mods:namePart[not(@type)]/text()', namespaces=namespacesmap)
                    if namePart and namePart[0].strip() != '':
                        unstructured = namePart[0].strip()
                        
                    #mods:displayForm overrules unstructured:
                    displayForm = name.xpath('self::mods:name/mods:displayForm/text()', namespaces=namespacesmap)
                    if displayForm and displayForm[0].strip() != '':
                        unstructured = displayForm[0].strip()
                        
                    if not unstructured and not namepartDict['family']:
                        continue # no usefull name, next
                    e_name_type = etree.SubElement(e_longmetadata, 'name')
                    etree.SubElement(e_name_type, 'type').text = nameType
                    if unstructured:   
                        etree.SubElement(e_name_type, 'unstructured').text = unstructured
                    for namepartType in namepartTypes:
                        if namepartDict[namepartType]:
                            etree.SubElement(e_name_type, namepartType).text = namepartDict[namepartType]
                    # Get RoleTerm:
                    roleTerm = name.xpath('self::mods:name/mods:role/mods:roleTerm[@authority="marcrelator"]/text()', namespaces=namespacesmap)
                    if roleTerm and roleTerm[0].strip() in marcRelatorRoleTerms:
                        etree.SubElement(e_name_type, "mcRoleTerm").text = roleTerm[0].strip()
                    # Get all mods name/nameIdentifier:
                    # Known (NOD person) nameIdentifiers to look for:
                    # bln_hasDAI_NID = False
                    # supportedNids = ['dai-nl', 'orcid', 'isni']
                    # for nid_type in supportedNids:
                    #     nameidentifiers = name.xpath('self::mods:name/mods:nameIdentifier[@type="'+nid_type+'"]/text()', namespaces=namespacesmap)
                        
                    #     for nid in nameidentifiers:
                    #         nameId = NameIdentifierFactory.factory(nid_type, nid)
                    #         if nameId.is_valid():
                    #             e_nid = etree.SubElement(e_name_type, "nameIdentifier")
                    #             e_nid.attrib['type'] = nameId.get_name()
                    #             e_nid.text = nameId.get_id()
                    #             if nameId.get_name() == 'dai-nl': bln_hasDAI_NID = True

                    # # Get DAI from DaiList-extension:
                    # if not bln_hasDAI_NID: # Only look for DAI-extension if no valid dai has been found in (mods 3.6) nameIdentifier tag.
                    #     extensionid = name.xpath('self::mods:name/@ID', namespaces=namespacesmap)
                    #     if extensionid:
                    #         # Select dai and mandatory 'some' authority:
                    #         dai = lxmlNode.xpath(root+'mods:extension/dai:daiList/dai:identifier[@IDref="'+extensionid[0]+'" and @authority]/text()', namespaces=namespacesmap)
                    #         # Hack, since MODS doc example is in wrong (mods) namespace!
                    #         if not dai: dai = lxmlNode.xpath(root+'mods:extension/mods:daiList/mods:identifier[@IDref="'+extensionid[0]+'" and @authority]/text()', namespaces=namespacesmap)
                    #         if dai:
                    #             nameId = NameIdentifierFactory.factory('dai-nl', dai[0].strip())
                    #             if nameId.is_valid():
                    #                 e_nid = etree.SubElement(e_name_type, "nameIdentifier")
                    #                 e_nid.attrib['type'] = nameId.get_name()
                    #                 e_nid.text = nameId.get_id()

                    # Transfer valid & known nameIdentifiers from MODS name:
                    daiset = set() # Unique dai-container.
                    nameidentifiers = name.xpath('self::mods:name/mods:nameIdentifier', namespaces=namespacesmap)
                    for nid in nameidentifiers:
                        nid_type = nid.get("type")
                        if nid_type in supportedNids:
                            nameId = NameIdentifierFactory.factory(nid_type, nid.text)
                            if nameId.is_valid():
                                if nameId.get_name() == supportedNids[0]:
                                    daiset.add(nameId.get_id()) # Add valid dai to dai-container.
                                else: # Add valid non-dai nameIdentifiers directly 
                                    e_nid = etree.SubElement(e_name_type, "nameIdentifier")
                                    e_nid.attrib['type'] = nameId.get_name()
                                    e_nid.text = nameId.get_id()
                                
                    # Transfer valid DAI's from old style daiList-mods-extension: 
                    extensionid = name.xpath('self::mods:name/@ID', namespaces=namespacesmap)
                    if extensionid:
                        # Select dai and mandatory 'some' authority:
                        daais = lxmlNode.xpath(root+'mods:extension/dai:daiList/dai:identifier[@IDref="'+extensionid[0]+'" and @authority]/text()', namespaces=namespacesmap)
                        # Hack, since MODS doc example is in wrong (mods) namespace!
                        if not daais: daais = lxmlNode.xpath(root+'mods:extension/mods:daiList/mods:identifier[@IDref="'+extensionid[0]+'" and @authority]/text()', namespaces=namespacesmap)
                        for dai in daais:
                            nameId = NameIdentifierFactory.factory(supportedNids[0], dai.strip())
                            if nameId.is_valid():
                                daiset.add(nameId.get_id())
                            
                    for dai in sorted(daiset): # Add all (sorted, to ease unittesting) unique dai's found from old dailist and nameIdentifiers:
                        e_nid = etree.SubElement(e_name_type, "nameIdentifier")
                        e_nid.attrib['type'] = supportedNids[0]
                        e_nid.text = dai


        # Get creators and contributors from DC if NO FULLMODS available, or if MMODS did not yield any authors:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_creators = lxmlNode.xpath('//dc:creator/text()', namespaces=namespacesmap)
            for dc_creator in dc_creators:
                e_name_type = etree.SubElement(e_longmetadata, 'name')
                etree.SubElement(e_name_type, 'type').text = 'personal'
                etree.SubElement(e_name_type, 'unstructured').text = dc_creator
                etree.SubElement(e_name_type, 'mcRoleTerm').text = 'aut'

            # if dc.type == dissertation or doctoral thesis: marcrelator will be thesis advisor(ths) ctb (contributor) otherwise:
            # xpath is case sensitive: just in case...
            dc_type_thesis_dissertation = lxmlNode.xpath('//dc:type[contains(.,"issertation") or contains(.,"thesis")]', namespaces=namespacesmap)
            dc_type_e = 'ctb'
            if dc_type_thesis_dissertation: dc_type_e = 'ths'

            dc_contribs = lxmlNode.xpath('//dc:contributor/text()', namespaces=namespacesmap)
            for dc_contrib in dc_contribs:
                e_name_type = etree.SubElement(e_longmetadata, 'name')
                etree.SubElement(e_name_type, 'type').text = 'personal'
                etree.SubElement(e_name_type, 'unstructured').text = dc_contrib
                etree.SubElement(e_name_type, 'mcRoleTerm').text = dc_type_e


    def _getRightsDescription(self, lxmlNode, e_longmetadata):
        # DC: special treatment...
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_rights = lxmlNode.xpath('//dc:rights/text()', namespaces=namespacesmap)
            if len(dc_rights) > 0:
                filteredlist = [dc for dc in dc_rights if not self._isValidAccessLevel(dc)]
                if len(filteredlist) > 0:
                    etree.SubElement(e_longmetadata, 'rightsDescription').text = BINDING_DELIMITER.join(filteredlist)
        else: # DIDL variants:
            wmp_rights = lxmlNode.xpath('//mods:mods/mods:extension/wmp:rights/dc:description/text()', namespaces=namespacesmap)
            if len(wmp_rights) > 0:
                etree.SubElement(e_longmetadata, "rightsDescription").text = BINDING_DELIMITER.join(wmp_rights)


    def _getGenre(self, lxmlNode, e_longmetadata):

        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']
        # uit DC(mandatory): volgens specs mogen we first occurence pakken:
        dcGenre = lxmlNode.xpath('//dc:type[1]/text()', namespaces=namespacesmap)
        if len(dcGenre) > 0 and self._DCType2PublicationType(dcGenre[0].strip()) in pubTypes:
            etree.SubElement(e_longmetadata, "genre").text = self._DCType2PublicationType(dcGenre[0].strip())
        # FMODS checken:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            modsGenre = lxmlNode.xpath('//mods:mods/mods:genre[1]/text()', namespaces=namespacesmap)
            if len(modsGenre) > 0 and self._getLabelFromGenreURI(modsGenre[0]) in pubTypes:
                etree.SubElement(e_longmetadata, "genre").text = self._getLabelFromGenreURI(modsGenre[0])


    def _getPublisher(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
        # MODS, otherwise DC (1st dc:publisher)
        publishers = self._findFirstXpath(lxmlNode, root+'mods:originInfo/mods:publisher[1]/text()', '//dc:publisher[1]/text()')
        if len(publishers) > 0:
            etree.SubElement(e_longmetadata, "publisher").text = publishers[0]


    def _getPhysicalDescription(self, lxmlNode, e_longmetadata):
        # The nuber of pages of a book, thesis or report:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            modsGenre = lxmlNode.xpath('//mods:mods/mods:genre[1]/text()', namespaces=namespacesmap)
            if len(modsGenre) > 0 and self._getLabelFromGenreURI(modsGenre[0]) in (pubTypes[2], pubTypes[3], pubTypes[8], pubTypes[11], pubTypes[14]):
                m_extend = lxmlNode.xpath('//mods:mods/mods:physicalDescription/mods:extent[1]/text()', namespaces=namespacesmap)
                if len(m_extend) > 0:
                    etree.SubElement(e_longmetadata, "physicalDescription").text = m_extend[0]


    def _getSubject(self, lxmlNode, e_longmetadata): # TODO: Check metadataformat logic    
        subjects = [[],[]] #wrapper for max 2 subject.topic strings -> ['NL', leeg, !='EN' taal OF DC], ['EN' only].   
        # Get subjects from dc:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_subjects = lxmlNode.xpath('//dc:subject/text()', namespaces=namespacesmap)
            if len(dc_subjects) > 0:
                subjects[0] = subjects[0] + dc_subjects

        elif self._metadataformat in (MetadataFormat.MD_FORMAT[1], MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            en = lxmlNode.xpath("//mods:mods/mods:subject[@xml:lang='en']/mods:topic/text()", namespaces=namespacesmap)
            nl = lxmlNode.xpath("//mods:mods/mods:subject[@xml:lang='nl']/mods:topic/text()", namespaces=namespacesmap)
            if not nl:
                nl = lxmlNode.xpath("//mods:mods/mods:subject[not(@xml:lang)]/mods:topic/text()", namespaces=namespacesmap)
                if not nl:
                    nl = lxmlNode.xpath("//mods:mods/mods:subject[not(@xml:lang='en')]/mods:topic/text()", namespaces=namespacesmap)
                    if not nl:
                        nl = en
            if len(nl) > 0: subjects[0] = subjects[0] + nl
            if len(en) > 0: subjects[1] = subjects[1] + en

        if len (subjects[0]) > 0:
            e_subject = etree.SubElement(e_longmetadata, "subject")
            for topic in subjects[0]:
                etree.SubElement(e_subject, "topic").text = topic.strip()
        if len (subjects[1]) > 0:
            e_subject = etree.SubElement(e_longmetadata, "subject")
            e_subject.attrib[namespacesmap.curieToTag('xml:lang')] = 'en'
            for topic in subjects[1]:
                etree.SubElement(e_subject, "topic").text = topic.strip()


    def _getAbstract(self, lxmlNode, e_longmetadata): # TODO: Check metadataformat logic
        abstracts = [[],[]] #wrapper for max 2 abstract strings -> [('NL', leeg, !='EN') OF DC], ['EN' only].        
        #Get abstract from dc: (only ONE)
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_description = lxmlNode.xpath('//dc:description[1]/text()', namespaces=namespacesmap)  
            if len(dc_description) > 0: # dc:description gevonden.
                abstracts[0] = abstracts[0] + dc_description
        # Override dc:description with mods's abstract value's
        elif self._metadataformat in (MetadataFormat.MD_FORMAT[1], MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            en = lxmlNode.xpath("//mods:mods/mods:abstract[@xml:lang='en']/text()", namespaces=namespacesmap)
            nl = lxmlNode.xpath("//mods:mods/mods:abstract[@xml:lang='nl']/text()", namespaces=namespacesmap)
            if not nl:                
                nl = lxmlNode.xpath("//mods:mods/mods:abstract[not(@xml:lang)]/text()", namespaces=namespacesmap)
                if not nl:
                    nl = lxmlNode.xpath("//mods:mods/mods:abstract[not(@xml:lang='en')]/text()", namespaces=namespacesmap)
                    if not nl:
                        nl = en            
            if len(nl) > 0: abstracts[0] = abstracts[0] + nl
            if len(en) > 0: abstracts[1] = abstracts[1] + en

        if len (abstracts[0]) > 0:
            etree.SubElement(e_longmetadata, "abstract").text = abstracts[0][0].strip()

        if len (abstracts[1]) > 0:
            e_abstract = etree.SubElement(e_longmetadata, "abstract")
            e_abstract.attrib[namespacesmap.curieToTag('xml:lang')] = 'en'
            e_abstract.text = abstracts[1][0].strip()


    def _getDateIssued(self, lxmlNode, e_longmetadata, root='//mods:mods/'):

        # MODS otherwise DC(1st dc:date)
        # Return: Normalized date and original unParsed date.

        dateIssued = lxmlNode.xpath(root+"mods:originInfo/mods:dateIssued[@encoding='w3cdtf' or @encoding='iso8601']/text()", namespaces=namespacesmap)
        if len(dateIssued) > 0:
            e_dateissued = etree.SubElement(e_longmetadata, "dateIssued")
            if self._isISO8601( dateIssued[0] ):
                e_parsed = etree.SubElement(e_dateissued, "parsed").text = self._normaliseDate(dateIssued[0])
            e_unparsed = etree.SubElement(e_dateissued, "unParsed").text = dateIssued[0]
        else:
            dcdates = lxmlNode.xpath('//dc:date/text()', namespaces=namespacesmap)
            for dcdate in dcdates:
                if self._isISO8601(dcdate):
                    e_dateissued = etree.SubElement(e_longmetadata, "dateIssued")
                    e_parsed = etree.SubElement(e_dateissued, "parsed").text = self._normaliseDate(dcdate)
                    e_unparsed = etree.SubElement(e_dateissued, "unParsed").text = dcdate
                    break
            else: # No valid iso dc dates found: just add the first invalid date.
                if len(dcdates) > 0:
                    e_dateissued = etree.SubElement(e_longmetadata, "dateIssued")
                    e_unparsed = etree.SubElement(e_dateissued, "unParsed").text = dcdates[0]


    def _getModsIdentifier(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
        # FMODS only!
        # Identifies the publication or host.
        # SS-specs: [@type='uri'] is preferred. However, [@type='issn'] is valid!
        # [@type='uri']: 2 example ns's are given: URN & INFO, others are valid though.
        # Use of @type is mandatory.
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            identifierList = lxmlNode.xpath( root+"mods:identifier", namespaces=namespacesmap)
            returnXML = ''
            for identifier in identifierList:
                idType = identifier.attrib.get('type')
                if not idType or idType == 'local': continue # don't process 'local' authority.
                idType = idType.strip().lower()
                idText = identifier.text
                if not idText or idText == '' : continue
                idText = idText.strip()
                # modify data: is this the right thing todo? Tricky indeed, but normalized, sort of
                if idType == 'uri':
                    if idText.lower().startswith('info:'):
                        #Found 'uri' with info:doi/90022333
                        idText = idText.strip()
                    elif idText.lower().startswith('urn:isbn:') or idText.lower().startswith('urn:issn:'):
                        #Found 'uri' with urn:isbn:90022333 or urn:issn:90022333
                        [dummy,idType,idText] = idText.split(':', 2)
                if idText and idType:
                    etree.SubElement(e_longmetadata, "publication_identifier", type=idType.lower()).text = idText


    def _getLanguage(self, lxmlNode, e_longmetadata):
        # SSDC mandates iso639-1, SSMODS mandates iso639-1 or iso639-2 if iso639-1 is not available, but we'll settle for either 2 or 3 chars.
        rfc3066_language = self._findFirstXpath(lxmlNode, "//mods:mods/mods:language/mods:languageTerm[@type='code' and @authority='rfc3066']/text()", "//dc:language[1]/text()") #Greedy fallback DC. If all else fails...
        if len(rfc3066_language) > 0:
            # Captures first 2 or 3 language chars if nothing else OR followed by '-' and 1 to 8 alfanum chars. 
            #See also: ftp://ftp.rfc-editor.org/in-notes/rfc3066.txt
            p = compile('^([A-Za-z]{2,3})(-[a-zA-Z0-9]{1,8})?$') # TODO: Can't this be compiled once in the init method?
            m = p.match(rfc3066_language[0])
            if m and m.group(1).lower() in ISO639:
                etree.SubElement(e_longmetadata, "language").text = m.group(1).lower()

    def _getLocationUrl(self, lxmlNode, e_longmetadata):
        # FMODS only!
        # Versions of the publication OUTSIDE the repository! protocolized url's only! (://)
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            locations = lxmlNode.xpath("//mods:mods/mods:location/mods:url[contains(.,'://')]/text()", namespaces=namespacesmap)
            for loc in locations:
                e_dateissued = etree.SubElement(e_longmetadata, "location_url").text = loc


    def _getRelatedItems(self, lxmlNode, e_longmetadata):
        # Dit gaat 'slechts' 1 nivo diep. Bij diepere nesting gaat dit fout.
        # FMODS only
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            relateditemtypes = ['preceding', 'succeeding', 'host', 'series', 'otherVersion']
            for relateditemtype in relateditemtypes:
                relatedItems = lxmlNode.xpath('//mods:mods/mods:relatedItem[@type="'+relateditemtype+'"]', namespaces=namespacesmap)
                for relatedItem in relatedItems: # voor iedere relatedItem per host, series, etc.
                    # if len(relatedItem) > 0:
                    e_relateditem = etree.SubElement(e_longmetadata, "relatedItem", type=relateditemtype)
                    # Get stuff from related item:
                    self._addRelatedItemPart(relatedItem, relateditemtype, e_relateditem)
                    methodNames = [ self._getTitleInfo, self._getModsIdentifier, self._getNames, self._getDateIssued, self._getPlaceterm, self._getPublisher ]
                    for method in methodNames:
                        method(relatedItem, e_relateditem, root='self::mods:relatedItem/')


    def _getPlaceterm(self, lxmlNode, e_longmetadata, root='//mods:mods/'):
        # FMODS only! Return first palceterm we can find:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            placeterms = lxmlNode.xpath(root+"mods:originInfo/mods:place/mods:placeTerm[@type='text']/text()", namespaces=namespacesmap)
            if len(placeterms) > 0:
                etree.SubElement(e_longmetadata, "placeTerm").text = placeterms[0]


    def _getCoverage(self, lxmlNode, e_longmetadata):
        #Get coverages from dc:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_coverages = lxmlNode.xpath('//dc:coverage/text()', namespaces=namespacesmap)
            for coverage in dc_coverages:
                etree.SubElement(e_longmetadata, "coverage").text = coverage.strip()


    def _getFormat(self, lxmlNode, e_longmetadata):
        #Get formats from dc:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[0], MetadataFormat.MD_FORMAT[1]):
            dc_formats = lxmlNode.xpath('//dc:format/text()', namespaces=namespacesmap)
            for format in dc_formats:
                etree.SubElement(e_longmetadata, "format").text = format.strip()


    def _getTypeOfResource(self, lxmlNode, e_longmetadata):
        # FMODS only:
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            typeOfResources = lxmlNode.xpath('//mods:mods/mods:typeOfResource/text()', namespaces=namespacesmap)
            mods_resource_types = ['text'] # May be extended by mods3.0 with "video" etc.
            if len(typeOfResources) > 0 and typeOfResources[0].lower().strip() in mods_resource_types:
                etree.SubElement(e_longmetadata, "typeOfResource").text = typeOfResources[0].lower().strip()
        #else: # Haal het uit DC
            #Waar staat dit? dc.format, dc:type? Dit kan meerdere keren voorkomen...Welke nemen we dan?
            #kortom hopeloos: i.g.v. dc laten we het element achterwege: We weten het niet.

    def _getFunding(self, lxmlNode, e_longmetadata):
    
        # This is OpenAIRE stuff.
        # MD_FORMAT = ['oai_dc', 'didl_dc', 'didl_mods231', 'didl_mods30', 'didl_mods36', 'org', 'ond', 'prs']
        # SURFSHARE_FORMAT = ['oai_dc', 'didl_dc', 'didl_mmods', 'didl_mods231', 'didl_mods30', 'ore_rem']        
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            e_gas = None
            #Look for grantAgreements with mandatory Project Reference (@code)
            gas = lxmlNode.xpath("//mods:mods/mods:extension/gal:grantAgreementList/gal:grantAgreement[@code]", namespaces=namespacesmap)
            
            for ga in gas:
                #Look for mandatory code(m), description(o), funder(o) and title(o) to add:
                GaCode = ga.xpath('self::gal:grantAgreement/@code', namespaces=namespacesmap)
                if len(GaCode) > 0 and len(GaCode[0].strip()) > 0:
                    #Create grantAgreements element if it does not yet exist:
                    if e_gas is None: e_gas = etree.Element("grantAgreements")
                    #Create grantAgreement sub-element:
                    e_ga = etree.SubElement(e_gas, "grantAgreement")
                    etree.SubElement(e_ga, "code").text = GaCode[0]
                else: # No mandatory GA code found (Project Reference): Skip this grantAgreement...
                    continue
                GaTitle = ga.xpath('self::gal:grantAgreement/gal:title/text()', namespaces=namespacesmap)
                if GaTitle:
                    etree.SubElement(e_ga, "title").text = GaTitle[0]                
                GaDescription = ga.xpath('self::gal:grantAgreement/gal:description/text()', namespaces=namespacesmap)
                if GaDescription:
                    etree.SubElement(e_ga, "description").text = GaDescription[0]                   
                GaFunderId = ga.xpath('self::gal:grantAgreement/gal:funder/@IDref', namespaces=namespacesmap)
                if GaFunderId:
                    #found Funder: Get its (Plain) name
                    funder = lxmlNode.xpath('//mods:mods/mods:name[@ID="'+GaFunderId[0]+'"]/mods:displayForm/text()', namespaces=namespacesmap)
                    if not funder:
                        funder = lxmlNode.xpath('//mods:mods/mods:name[@ID="'+GaFunderId[0]+'"]/mods:namePart/text()', namespaces=namespacesmap)
                    if funder:
                        etree.SubElement(e_ga, "funder").text = ', '.join(funder)
            if e_gas is not None:
                e_longmetadata.append(e_gas)

################### Helper methods #########################


    def _addHostCitation(self, lxmlNode):
        relatedItems = lxmlNode.xpath("//long:long/long:metadata/long:relatedItem[@type='host']", namespaces=namespacesmap)
        if len(relatedItems) > 0:
            title, page, volume, published, issn = '', '', '', '', ''
            relatedItem = relatedItems[0]
            titles = relatedItem.xpath('self::long:relatedItem/long:titleInfo/long:title/text()', namespaces=namespacesmap)
            subtitles = relatedItem.xpath('self::long:relatedItem/long:titleInfo/long:subtitle/text()',
                                          namespaces=namespacesmap)
            if titles and titles[0] != 'None':
                title = titles[0]
                if subtitles:
                    title = '%s: %s' % (title, subtitles[0])
            volumes = relatedItem.xpath('self::long:relatedItem/long:part/long:volume/text()', namespaces=namespacesmap)
            if volumes and volumes[0] != 'None':
                volume = '<i>, %s</i>' % (volumes[0])
                issue = relatedItem.xpath('self::long:relatedItem/long:part/long:issue/text()', namespaces=namespacesmap)
                if issue:
                    volume = '%s(%s)' % (volume, issue[0])
            start_page = relatedItem.xpath('self::long:relatedItem/long:part/long:start_page/text()',
                                           namespaces=namespacesmap)
            end_page = relatedItem.xpath('self::long:relatedItem/long:part/long:end_page/text()', namespaces=namespacesmap)
            if start_page and start_page != 'None':
                page = ', %s' % (start_page[0])
                if end_page:
                    page = '%s - %s' % (page, end_page[0])
            else:
                list = relatedItem.xpath('self::long:relatedItem/long:part/long:list/text()', namespaces=namespacesmap)
                if list:
                    page = ', %s' % (list[0])
                else:
                    if end_page:
                        page = ', %s' % (end_page[0])
            place = relatedItem.xpath('self::long:relatedItem/long:placeTerm/text()', namespaces=namespacesmap)
            publisher = relatedItem.xpath('self::long:relatedItem/long:publisher/text()', namespaces=namespacesmap)
            if place:
                published = '. %s' % (place[0])
                if publisher:
                    published = '%s: %s' % (published, publisher[0])
            else:
                if publisher:
                    published = '. %s' % (publisher[0])
    
            issnen = relatedItem.xpath(
                '//long:metadata/long:relatedItem[@type="host"]/long:publication_identifier[@type="issn"]/text()',
                namespaces=namespacesmap)
            if issnen:
                issn = '. ISSN %s.' % (issnen[0])
    
            metadata = lxmlNode.xpath('//long:metadata', namespaces=namespacesmap)[0]
            citation = etree.SubElement(metadata, namespacesmap.curieToTag('long:hostCitation'))
            citation.text = '<i>%s</i>%s%s%s%s' % (title, volume, page, published, issn)


    def _addRelatedItemPart(self, lxmlNode, relatedItemType, relatedItemElement):        
        # FMODS only! part can only be used as a subelement of relatedItem type=host || type=series !
        if not relatedItemType in ('host', 'series'):
            return ''
        if self._metadataformat in (MetadataFormat.MD_FORMAT[2], MetadataFormat.MD_FORMAT[3], MetadataFormat.MD_FORMAT[4]):
            bln_foundTag = False
            #create part element:
            e_part = etree.Element("part")
            #detail section:
            detail_types = ['part', 'volume', 'issue', 'chapter', 'section']
            for detail_type in detail_types: #Haal alle numbers op: (Er kan er maar 1 per type zijn)
                numbers = lxmlNode.xpath('self::mods:relatedItem/mods:part/mods:detail[@type="'+detail_type+'"]/mods:number[1]/text()', namespaces=namespacesmap)
                if numbers:
                    etree.SubElement(e_part, detail_type).text = numbers[0]
                    bln_foundTag = True
            #extent section:
            extent_elements = ['start', 'end', 'total', 'list']
            for extent_element in extent_elements: #Haal alle extend sub-elementen op en pak de eerste start, end etc. die we tegenkomen.
                pages = lxmlNode.xpath('self::mods:relatedItem/mods:part/mods:extent[@unit="page"]/mods:'+extent_element+'[1]/text()', namespaces=namespacesmap)
                if pages:
                    etree.SubElement(e_part, extent_element+'_page').text = pages[0]
                    bln_foundTag = True
            if bln_foundTag: relatedItemElement.append(e_part)


    def _getLabelFromGenreURI(self, genreURI):
        if genreURI:
            return genreURI.strip().lower().split('/').pop()
        return ''
    
    def _DCType2PublicationType(self, dctype):        
        dctype = dctype.lower().replace(' ', '')
        if dctype in pubTypes: return dctype #1:1 occurences
        elif(dctype.find('newspaper')>=0): return pubTypes[7]
        elif(dctype.find('conferencereport')>=0): return pubTypes[18]
        elif(dctype.find('conference')>=0 or dctype.find('inmonograph')>=0 or dctype.find('inproceedings')>=0 ): return pubTypes[6]
        elif(dctype.find('dissertation')>=0): return pubTypes[8]
        elif(dctype.find('lecture')>=0): return pubTypes[10]
        elif(dctype.find('article')>=0 or dctype.find('bookreview')>=0 ): return pubTypes[1]
        elif(dctype.find('report')>=0): return pubTypes[14]
        elif(dctype.find('paper')>=0): return pubTypes[17]
        elif(dctype.find('partofbook')>=0 or dctype.find('chapterofbook')>=0): return pubTypes[4]
        elif(dctype.find('book')>=0 ): return pubTypes[3]
        return ''

    def _findFirstXpath(self, node, *xpaths):
        # Will return the first non-empty list that matches an xpath.
        for x in xpaths:
            items = node.xpath(x, namespaces=namespacesmap)
            if len(items) > 0:
                return items
        return []

    def _isValidAccessLevel(self, description):
        for al in NormaliseOaiRecord.ACCESS_LEVELS:
            if al.lower() in description.strip().lower():
                return True
        return False

    def _isISO8601(self, datestring):
        ## See: http://labix.org/python-dateutil
        if datestring is None: return False
        try:
            parseDate(datestring, ignoretz=True, fuzzy=False) # Fuzzy True will pass any date found in any srting i.e: "opgraafdatum 3000 jaar voor christus" will pass. (yielding '3000')
        except ValueError:
            return False
        return True

    def _normaliseDate(self, str_date):
        """returns only date parts that are succesfully parsed."""
        di_1 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(1900, 12, 28, 0, 0)) #1900-12-28 default year, month and day. (day 28 exists for every month:-)
        di_2 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(2000, 01, 01, 0, 0)) #2000-01-01 default year, month and day.
        
        ## Parsed date with no defaults used:
        if str(di_1.date()) == str(di_2.date()):
            return str(di_1.date()) # Dates are the same: date is succesfully parsed.
        
        ## Check for dft day and month:
        if di_1.date().day != di_2.date().day and di_1.date().month != di_2.date().month:
            return str(di_1.date().year) # Only year has been parsed succesfully.
        if di_1.date().day != di_2.date().day and di_1.date().month == di_2.date().month:
            return ('%s-%s') % (di_1.date().year, di_1.date().month) # Only year and month have been parsed succesfully.