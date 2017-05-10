#todo

instead of scraping results just scrape
http://www.hkjc.com/english/racing/JockeyPastRec.asp?JockeyCode=MOJ&season=Current





#todo
todo check ranks!

image pipeline to MONGODB?

upsert if any changes DONE

FINISH AGG then DONE

Meteor page will include mongo db for this scrapy raceday run every hour? then more often closer to the time
(BETTER TO HAVE A CALLBACK if data changeson site)
+ results

LOOK HERE
https://github.com/sebdah/scrapy-mongodb/blob/master/scrapy_mongodb.py

https://docs.mongodb.com/manual/reference/method/db.collection.update/


Version 1 only offers

offer yes/no paramutuel bet

paramutuel is a contract where all bets are totaled up and the yes gets 95% of funds split by number of winners

Plus bookmakers offs of a yES based on

(hidden:) JMO wins so far today , JMO_last_3, JMO_Won_last_Race, JMO_pon_last_Race
plus form last 3 meets, 30 days etc,
plus form of horse
Bookmmaker bet is a separate contract with a price


Docker/Meteor Deployment with MONGO DB
scrapy scheduler/api callback

Meteor must have isStarted() callback which will fire if bet site freezes



instead of isFnished look for result from 3 different sources
hkjc.com/results construct from url
+ australian site
+ singapore?


isStartted signal from where?

isFinished = result


todo:

JUST return do not call up results!

check to see if all runner data there

is this correct json?

#then build into app via DB Firebase


#RESULTS CHECKER BUILT INTO JS APP WHICH WILL BE ANGULAR /NODE JS OR EVEN METEOR

what is it ?
a ewb request a la HKODDS

AIM IS TO HAVE THIS WORK AS AN API which can push to an Ethereum contract
How?



#winning J
$x("//tr[@class='trBgGrey' and position()=1]/td[4]/a/text()")
non existent race eg.
empty array

http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/20180305/ST/2

#race started (and ended) but result not released yet

#stewards inquiry


------------------
function update() payable {
    newOraclizeQuery("Oraclize query was sent, standing by for the answer..");
    oraclize_query('URL', 'html(http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/20170305/ST/2).xpath(//tr[@class="trBgGrey" and position()=1]/td[4]/a/text())');
}


##sample contract


   HKJCWinningJock

   This contract keeps in storage a views counter
   for a given Youtube video.

   NEEDS TO TAKE a HK Racecourse, Racedate and Racenumber
   Returns the Winning Jockey if Any (i.e. if valid race, if race has finished
   and result published)
   Can be used for historical races



Results - Contract gets results for a specific event




1 contract checks whether JMO won or not
2 contract checks whether this particular race has started or not


pragma solidity ^0.4.0;
import "github.com/oraclize/ethereum-api/oraclizeAPI.sol";

contract HKJCWinningJock is usingOraclize {

    string public winningJock;

    event newOraclizeQuery(string description);
    event newHKJCWinningJockCall(string winningJock);

    function YoutubeViews() {
        update();
    }

    function __callback(bytes32 myid, string result) {
        if (msg.sender != oraclize_cbAddress()) throw;
        viewsCount = result;
        newYoutubeViewsCount(winningJock);
        // do something with viewsCount. like tipping the author if viewsCount > X?
        //if winningJock LIKE J Morereira (STRING FUNCTION) add PK to winning bets hash
        //get total bets subtract 5%
        //pay out remaining share to PKs in the array
    }

    function update() payable {
        newOraclizeQuery("Oraclize query was sent, standing by for the answer..");
        oraclize_query('URL', 'html(http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/20170305/ST/2).xpath(//tr[@class="trBgGrey" and position()=1]/td[4]/a/text())');
    }

}
