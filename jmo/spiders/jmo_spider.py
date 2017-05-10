import scrapy
from datetime import date, datetime, timedelta
from jmo.utils import utils
from jmo.items import RaceItem, RunnerItem
from collections import OrderedDict, defaultdict
import re
import ranking
import operator
# from itertools import chain

ratingpat = re.compile(r'.*Rating:([0-9]{1,3}-[0-9]{1,3}),.*')
classgrouppat = re.compile(r'.*[Class|Group]([0-9]{1})$')
prizepat = re.compile(r'.*^PrizeMoney:\$([0-9]{0,1},{0,1}[0-9]{1,3},[0-9]{1,3}).*')
distancepat = re.compile(r'\D*([0-9]{3,4})M.*')
goingpat = re.compile(r'.*(Good).*')    #add goings
trackcoursepat = re.compile(r'.*(Turf, \"A\" Course).*')
#aWT b'All Weather Track, 1650M, Good'
trackcoursepat2 = re.compile(r'.*(Turf, \"A\" Course).*')


class Jmospider(scrapy.Spider):
    name = 'jmo'
    allowed_domains = ['racing.scmp.com', 'hkjc.com']
 
    def __init__(self, racedate, racecourse, *args, **kwargs):
        assert racecourse in ['ST', 'HV']
        assert len(racedate) == 8 and racedate[:2] == '20'
        super(Jmospider, self).__init__(*args, **kwargs) #makes sure parent is init'd
        self.racedate = racedate
        self.racedateo = datetime.strptime(self.racedate, '%Y%m%d').date()
        self.racecourse = racecourse
        self.todaysdate = datetime.today().date()

    #raceday races with JMO in
    def start_requests(self):
        # is there a race today?
        urls = ['http://racing.hkjc.com/racing/Info/Meeting/RaceCard'\
                '/English/Local/{racedate}/{racecourse}/1'.format(
           racedate=self.racedate,
           racecourse=self.racecourse,
        )

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        '''
        go to generic homepage - if off season = no race within 7 days
        - get links to races put them in theraces
        then follow the links to get JMOS mounts and return as JSON
        ISSUE does not get all the urls racepaths
        '''
        try:
            rdate, rloc = response.xpath('//div[@class="newBtnContainer"]/a/text()').extract()[0].split("-")
            racecoursecode = "HV" if rloc.strip() == 'Happy Valley' else "ST"
            # happy-valley/2017-02-22
            racenet_racecoursecode = "happy-valley" if racecoursecode == "HV" else "sha-tin"

            self.log("rcode %s" % racecoursecode)
            nextracedate = datetime.strptime(rdate.strip(), "%d %b").date()
            nextracedate = nextracedate.replace(year= date.today().year)
            nextracedate_as_str = datetime.strftime(nextracedate,  "%Y%m%d")
            racenet_racedate_as_str = datetime.strftime(nextracedate,  "%Y-%m-%d")
            self.log("racedate %s" % nextracedate_as_str)
            url_stem = "http://racing.hkjc.com/racing/Info/meeting/RaceCard/english/Local/" + nextracedate_as_str + "/" + racecoursecode + "/"
            self.log(url_stem)
            #['08 Mar - Happy Valley']
        except IndexError:
            return {"error": "No race found"}

        #bail out of too far in future?

        #get maximum racenumber will alway be 1 less than length (1 is the currently selected page)
        race_paths = response.xpath('//td[@nowrap="nowrap" and @width="24px"]/a/@href').extract()
        # '/racing/Info/meeting/RaceCard/english/Local/20170308/HV/8'
        race_numbers = [int(x.split("/")[-1]) for x in race_paths ]
        max_racenumber = max(race_numbers)
        self.log(race_paths)
        self.log(max_racenumber)
        todays_racenumbers = list(range(1,max_racenumber+1))
        for rn in todays_racenumbers:
             card_url = url_stem + str(rn)
             request = scrapy.Request(card_url, callback=self.parserace)
             request.meta['racestring'] = nextracedate_as_str + "/" + racecoursecode + "/" + str(rn)
             request.meta['racenet_url'] =racenet_racecoursecode + "/" + racenet_racedate_as_str
             yield request
        #works does it work for larger number of races?
        #typical url looks like http://racing.hkjc.com/racing/Info/meeting/RaceCard/english/Local/20170308/HV/2


        # nextracedate = datetime.strptime(race_paths[0].split('/')[-3], "%Y%m%d").date()
        #if not today return JSON error


        # today7days = date.today().replace(day= date.today().day+7)
        # self.log("%s" % today7days)
        # self.log("%s" % date.today())
        # if today7days < nextracedate:
        #     rtn['errors']= "No race today- next race on %s" % nextracedate
        #     return {}
        # # method handles the response downloaed for each of the requests made
        # # page = response.url.split("/")[-2]
        # card_urls = ['http://{domain}{path}'.format(
        #         domain='racing.hkjc.com',
        #         path=path,
        #     ) for path in race_paths
        # ]
        # self.log("card urls: %s" % card_urls)
        # # result_urls = [_url.replace('RaceCard', 'Results') for _url in card_urls]
        # for card_url in card_urls:
        #     if int(card_url.split('/')[-1]) > 9:
        #         racenumber = '{}'.format(card_url.split('/')[-1])
        #     else:
        #         racenumber = '0{}'.format(card_url.split('/')[-1])
        #     yield scrapy.Request(card_url, callback=self.parserace)

        # for rp in race_paths:
        #     next_page = response.urljoin(rp)
        #     self.log("%s" % next_page)
        #     yield scrapy.Request(next_page, callback=self.parserace, meta={})

    #has race started?
    # can we return ALL runners as runner items in RUnners
    def parserace(self, response):
        '''
        racedatetime utc
        racenumber
        isStarted? nor just rely on date
        card info and get *result*
        '''
        racestring = response.meta['racestring']
        racenet_url = response.meta['racenet_url']
        # raceitem = RaceItem() #do this later
        racenumber = response.url.split('/')[-1]

        raceitem = RaceItem()
        #RESULTS SITES #1 HKJC
        # #2 https://www.racenet.com.au/horse-racing-results/happy-valley/2017-02-22
        basic_results_url = "http://racing.hkjc.com/racing/Info/meeting/Results/english/Local/" + racestring
        basic_racenet_url= "https://www.racenet.com.au/horse-racing-results/"
        # request = scrapy.Request(basic_results_url, callback=self.parse_result1)
        raceitem['hkjc_results_url'] =basic_results_url
        raceitem['hkjc_race_url'] = response.url
        raceitem['racenumber'] = int(racenumber)
        # runneritem['isStarted'] = None #update when trying to get results
        # runneritem['racenet_race_url'] = basic_racenet_url+ racenet_url
        thisracedate = datetime.strptime(response.url.split('/')[-3], "%Y%m%d")
        raceinfo_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]//descendant::text()[ancestor::td and normalize-space(.) != ""][position()>=2]').extract()
        if raceinfo_:
            #Sunday,March05,2017,ShaTin,15:00
            date_racecourse_localtime = utils.cleanstring(raceinfo_[0])
            h,m = date_racecourse_localtime.split(",")[-1].split(":")
            # self.log(thisracedate + timedelta(hours=int(h), minutes=int(m)))
            utc_localracetime = thisracedate + timedelta(hours=int(h), minutes=int(m)) + timedelta(hours=-8)
            raceitem['racedatetimeutc'] = utc_localracetime
            self.log(utc_localracetime)
            surface_distance = raceinfo_[1].encode('utf-8').strip()
            surface_distance = str(surface_distance)
            self.log("surface_distance %s" % surface_distance)
            # print "surface_distance--> {}".format(surface_distance)
            prize_rating_class = utils.cleanstring(raceinfo_[2])
            prizemoney_= re.match(prizepat, prize_rating_class).group(1)
            raceitem['prizemoney'] = utils.clean_prizemoney(prizemoney_)
            raceitem['rating'] = re.match(ratingpat, prize_rating_class).group(1)
            raceitem['raceclass'] = re.match(classgrouppat, prize_rating_class).group(1)

            # runneritem['going']= re.match(goingpat, surface_distance).group(1) b'All Weather Track, 1650M, Good' or surface_distance b'Turf, "C+3" Course, 1200M, Good'
            try:
                _surf = surface_distance.split(",")[0]
            except IndexError:
                _surf = None

            if "ALL WEATHER" in _surf.upper():
                raceitem['rail'] = None
                raceitem['distance'] = surface_distance.split(",")[1]
                raceitem['surface'] = "AWT"
            else:
                raceitem['rail'] = surface_distance.split(",")[1]
                raceitem['distance'] = surface_distance.split(",")[2]
                raceitem['surface'] = "TURF"
            try:
                _going = surface_distance.split(",")[-1]
            except IndexError:
                _going = None
            raceitem['going'] = _going.strip().upper()

        horse_items = [] #then request.meta['runners']
        racedaybeturl = "http://bet.hkjc.com/default.aspx?url=/racing/pages/odds_wp.aspx&lang=en&dv=local"
        jmo_performance_url = "http://www.hkjc.com/english/racing/JockeyPastRec.asp?JockeyCode=MOJ&season=Current"
        todaysSeasonStakes = {}
        todaysHorseWts = {}
        todaysBestTimes = {}
        raceSeasonStakes = defaultdict(dict)
        raceHorseWts = defaultdict(dict)
        raceBestTimes = defaultdict(dict)
        for tr in response.xpath('//table[@class="draggable hiddenable"]//tr[position() > 1]'):
                runneritem = RunnerItem()
                runneritem['therace'] = raceitem
                # horseno, horsecode, jockeycode, seasonstakes, trainercode, priority,
                # runnerloader = RaceItemLoader(RunnerItem(), response=response)
                # runneritem = RunnerItem()
                # attrs = list()

                horsenumber = tr.xpath('td[1]/text()').extract()[0]
                runneritem['horsenumber'] =int(horsenumber)
                # TODO GET IMAGES!
                # horsesilks_ = tr.xpath('td[3]/img/@src').extract()[0]
                # runnerloader.add_value('horsenumber', horsenumber)
                horsecode_ = tr.xpath('td[4]/a/@href').extract()[0]
                horsecode = re.match(r"^[^\?]+\?horseno=(?P<code>\w+)'.*$",
                    horsecode_).groupdict()['code']
                runneritem['horsecode'] = horsecode
                # horse_url = 'http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop'.format(horsecode)
                # self.code_set.add(horsecode)
                # todaysHorses[racenumber].append(horsecode)

                # horseattrs[horsecode]['horsenumber'] = horsenumber
                jockeycode_ = tr.xpath('td[7]/a/@href').extract()[0]
                jockeycode = re.match(r"^[^\?]+\?jockeycode=(?P<code>\w+)'.*",
                    jockeycode_).groupdict()['code']
                runneritem['jockeycode'] = jockeycode

                trainercode_ = tr.xpath('td[10]/a/@href').extract()[0]
                trainercode = re.match(r"^[^\?]+\?trainercode=(?P<code>\w+)'.*",
                    trainercode_).groupdict()['code']
                # todaysTrainers[racenumber].append(trainercode)
                runneritem['trainercode'] = trainercode


                todaysratingchange_ = tr.xpath('td[12]/text()').extract()[0]
                # todaysRatingChanges[racenumber].append(todaysratingchange_)

                #may not exist
                try:
                    horsewt_ = tr.xpath('td[13]/a/@href').extract()[0]

                except IndexError:
                    horsewt_ = 0.0

                todaysHorseWts[horsenumber] = horsewt_
                raceHorseWts[racenumber][horsenumber] = horsewt_
                besttime_ = tr.xpath('td[15]/text()').extract()[0]
                besttime = utils.get_sec(besttime_)
                runneritem['besttime'] = besttime
                raceBestTimes[racenumber][horsenumber] = besttime
                todaysBestTimes[horsenumber]= besttime
                # print(besttime)
                # racebesttimes[horsecode] = besttime
                try:
                    owner_ = tr.xpath('td[22]/text()').extract()[0]
                    runneritem['owner'] = owner_.strip().upper()
                except IndexError:
                    runneritem['owner'] = None

                gear_ = tr.xpath('td[21]/text()').extract()[0]
                gear_ = utils.cleanstring(gear_)
                sire_ = tr.xpath('td[23]/text()').extract()[0]
                runneritem['gear'] = gear_.strip().upper()
                runneritem['sire'] = sire_.strip().upper()
                runneritem['owner'] = owner_.strip().upper()


                seasonstakes_ = tr.xpath('td[19]/text()').extract()[0]
                self.log("seasonstakes %s" % seasonstakes_)
                runneritem['seasonstakes'] = utils.clean_prizemoney(seasonstakes_)
                #use this to work out how to do ranks
                todaysSeasonStakes[horsenumber]= seasonstakes_
                raceSeasonStakes[racenumber][horsenumber] = seasonstakes_
                #rank these

                # raceseasonstakes[horsecode] = seasonstakes_

                priority_ = tr.xpath('td[20]/text()').extract()[0].strip()
                priority_ =utils.get_prio_val(priority_)
                runneritem['priority'] = priority_
                ### DECODE priroty *\xa01 -> *1
                # racepriorities[horsecode] = priority_
                # todaysPriorities[racenumber].append(priority_)
                draw_ = tr.xpath('td[9]//text()[normalize-space()]').extract()[0]
                # draw_ = tr.xpath('td[8]/text()[normalize-space()]').extract()[0]
                draw = draw_.replace(u'\xa0', u'')
                # todaysDraws[racenumber].append(draw_)
                runneritem['draw'] = draw

                importcategory_ = tr.xpath('td[25]/text()').extract()[0].strip()

                runneritem['importcategory'] = importcategory_


                '''
                    ti import trying this
                    mongoimport -d newraceday -c runners --jsonArray < glossary.json OK
                    
                TODO
                change therace or add field raceindex from URL each race gets a raceindex racedateracecourseracenumber
                index on that
                AGG DATA for each horse create metrics then add metrics to horseattrs
                metrics:
                *** MAY 17**
                finish racedayfields + any aggs e.g.
                horsewts rank -- same as sorting
                seasonstakesrank -- same as sorting
                what other information?
                merge later with results
                
                1. MONGO DB PIPELINE
                Race should be done separately
                
                call from NODE which generates all dates and tries
                '''

                # yield runneritem
                horse_items += [runneritem]
        yield scrapy.Request(
            # racedaybeturl,
            jmo_performance_url,
            self.parse_racedaybet,
            dont_filter=True,
            meta={
            'horse_items': horse_items,
            'raceSeasonStakes' :raceSeasonStakes,
            'raceHorseWts' : raceHorseWts,
            'raceBestTimes' : raceBestTimes
        })

    def parse_racedaybet(self, response):
        # jchallenge Points each row is a run ignore next
        # $x("count(//table[@class='bigborder']/tbody/tr[position() >2 and following::td]/td[not(following-sibling::div) and not(following-sibling::font) ])")
        # jchallenges_ = response.xpath("//font[contains(text(), 'Jockey Challenge')]/text()").extract()
        table_rows = response.xpath("//table[@class='bigborder']/tbody/tr[position() >2 and following::td]/td[not(descendant::div) and not(following-sibling::font) ]").extract()
        results = {}
        for tr in table_rows:
            #excluded Jchallenge rows
            _racestats = tr.xpath("td[0]/a/@href/text()") #expath racedate=results.asp?racedate=15/03/2017&raceno=08&venue=HV raceno and venue
            self.log(_racestats)

            
        theracenumber = response.meta['horse_items'][0]['therace']['racenumber']
        raceBestTimes = response.meta['raceBestTimes'][str(theracenumber)]
        d = raceBestTimes
        # float('inf') if x is None else x
        s = sorted(d.items(), key=lambda value: float('inf') if value[1] is None else value[1])
        
        self.log("raceBestTimes : %s" % s)

        horse_items = response.meta['horse_items']
        #loop thru and update
        for x in horse_items:
            x['besttimerank'] =[y[0] for y in s].index(str(x['horsenumber']))
        for i in horse_items:
            yield i

    # def parse_result1(self, response):
    #     #rank seasonStakes self.log("ranks: %s" % list(enumerate(seasonstakes_)))
    #     # #2 results racenet_race_url
    #     # do ranking then return
    #     ss = response.meta['todaysSeasonStakes']
    #     output = [0] * len(ss)
    #     for i, x in enumerate(sorted(range(len(ss)), key=lambda y: ss[y])):
    #         output[x] = i
    #
    #     response.meta['race_prize_ranks'] = output
    #     self.log("ranks: %s" %  output)
    #     return response.meta
