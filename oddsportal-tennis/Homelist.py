
import json
from bs4 import BeautifulSoup
from os import listdir, altsep, sep, mkdir, getcwd
from selenium import webdriver
import pandas as pd
import datetime
import os
import re
from time import sleep
import shutil


class Homelist():

    def __init__(self, current_set):
        """
        Constructor. Launch the web driver browser, initialize the league
        field by parsing the representative JSON file, and connect to the
        database manager.

        Args:
            league_json (str): JSON string of the league to associate with the
                Homelist.
            initialize_json (bool): Should the database be initialized?
        """

        self.browser = webdriver.Chrome("./chromedriver/chromedriver.exe")
        self.league = self.parse_json(current_set)
        self.league_list = pd.DataFrame(["league","country","url"])
        # self.wholetournamentcol=["year", "month","date","country","league","player1","player2","results"]
        self.wholetournamentcol=["year", "country","league","game"]
        self.wholetournamentrecords = pd.DataFrame(columns=self.wholetournamentcol)
        self.currpath=getcwd()
    def parse_json(self, json_str):
        """
        Parse a JSON string into a dict.

        Args:
            json_str (str): JSON string to parse.

        Returns:
            (dict)
        """

        return json.loads(json_str)

    def scrape_leagues(self, do_verbose_output=False):
        """
        Call the scrape method on every URL in this Scraper's league field, in
        order, then close the browser.
        Args:
            do_verbose_output (bool): True/false do verbose output.
        """
        if do_verbose_output is True:
            output_str = "Start scraping Leagues of the " + self.league["sports"] + "..."
            print(output_str)

        # get all the leagues and url
        leagues_url = self.league["urls"]+sep+self.league["sports"]+sep+"results"
        self.browser.get(leagues_url)
        sleep(1)
        self.browser.find_element_by_class_name('user-header-fakeselect').click()
        sleep(1)
        # find the widget defining the "odds formate"
        # self.browser.find_element_by_link_text("EU Odds").click()
        self.browser.find_element_by_link_text("EU Odds").click()
        sleep(1)

        # league_tbl = self.browser.find_elements_by_class_name("sport")
        # use find_elements_by_css_selector because is not applicable for compound class names
        league_tbl = self.browser.find_element_by_css_selector(".table-main.sport")
        league_tbl_html = league_tbl.get_attribute("innerHTML")
        league_tbl_soup = BeautifulSoup(league_tbl_html, "html.parser")
        # league_tbl_rows = league_tbl_soup.select("tr") # some do not have "class",thus must filtered by "tr", then by "td"
        # league_tbl_rows = league_tbl_soup(self.is_leagues)
        league_tbl_rows=league_tbl_soup.select("td") #  find all "td" directly
        # select rows of leagues and websites
        league_country=[]
        league_name=[]
        league_address=[]
        for row in league_tbl_rows:
            league_name_curr=row.string
            if league_name_curr:
                if (("ATP "in league_name_curr) or ("WTA" in league_name_curr)) and ("Doubles" not in league_name_curr):
                    league_url_curr =row.a.get("href")
                    country = league_url_curr.split("/")[2]
                    league_country.append(country)
                    league_name.append(league_name_curr)
                    league_address.append( self.league["urls"]+league_url_curr)
                    print("...", end="")

        # save name, country, url of every league in csv
        Columslist=["league","country","url"]
        datas={}
        datas[Columslist[0]]=league_name
        datas[Columslist[1]]=league_country
        datas[Columslist[2]]=league_address

        cols = pd.DataFrame(columns = Columslist)
        for id in Columslist:
            cols[id] = datas[id]

        result_dir=self.currpath+sep+"scraping_results"
        if not(os.path.exists(result_dir)):
            os.mkdir(result_dir)
        LeagueList_path=result_dir+sep+'LeagueList.csv'
        lealist=open(LeagueList_path,"w")
        cols.to_csv(LeagueList_path)
        lealist.close()
        self.league_list=cols
        # scrape_gamesofleagues(True)
        Leaguelisttoscape=cols.to_dict(orient='records')
        if do_verbose_output is True:
            print("\n Done scraping the list of leagues. Start scraping tournaments of each league:")
            print("\n There are data of leagues:")
            for i in range(len(Leaguelisttoscape)):
                output_str = str(i+1)+": "+ Leaguelisttoscape[i]['league'] + "; "+Leaguelisttoscape[i]['country']
                print(output_str)

        while True:
            try:
                strinput = int(input("Please select the serial number of league, 0 for all:"))
            except ValueError:
                print("input is incorrect, please input again:")
                continue
            else:
                if strinput not in range(len(Leaguelisttoscape)+1):
                    print("input is incorrect, please input again:")
                    continue
                else:
                    break

        # empty the result folder:
        result_dir=self.currpath+sep+"scraping_results"
        shutil.rmtree(result_dir)
        os.mkdir(result_dir)

        # scape league(s)
        if strinput is 0:
            # scape all leagues
            output_str = "Start scraping All Leagues of the " + self.league["sports"] + "..."
            print(output_str)
            # for row_league_dict in Leaguelisttoscape:
            #     self.scrape_gamesofleagues(row_league_dict, True)
            # test_loop for bug detection, formal code should use the loop shown above
            # for lpindex_Leaguelisttoscape in range(len(Leaguelisttoscape)):
            for lpindex_Leaguelisttoscape in range(100,len(Leaguelisttoscape)):
                self.scrape_gamesofleagues(Leaguelisttoscape[lpindex_Leaguelisttoscape], True,True)
        else:
            # scrape selected league
            output_str = "Selected League to be scraped is " + Leaguelisttoscape[strinput-1]['league']
            print(output_str)
            self.scrape_gamesofleagues(Leaguelisttoscape[strinput-1], True,False)

        if do_verbose_output is True:
            output_str = "Finish scraping all the data."
            print(output_str)
        self.browser.close()

    def scrape_gamesofleagues(self, league_dict, do_verbose_output=False, do_scrape_all=True):
        # get all the games and urls of the league
        if do_verbose_output is True:
            output_str = "Start scraping League " + league_dict["league"] + "..."
            print(output_str)
        # get url of the league
        league_url = league_dict["url"]
        self.browser.get(league_url)
        sleep(1)
        years_tbl = self.browser.find_element_by_css_selector(".main-menu2.main-menu-gray")
        # get each years url
        years_tbl_html = years_tbl.get_attribute("innerHTML")
        years_tbl_soup = BeautifulSoup(years_tbl_html, "html.parser")
        years_tbl_rows=years_tbl_soup.select("a") #  find all "td" directly
        year_index=[]
        year_url=[]
        if do_scrape_all is True:
            # 抓取所有年份
            print("scraping data from 2011")
            year_from = 2010
            year_end = datetime.datetime.now().year
        else:
            # 抓取选定年份
            while True:
                try:
                    year_from = int(input("scrape the data after year: "))
                except ValueError:
                    print("input is incorrect, please input again:")
                    continue
                else:
                    break
            while True:
                try:
                    year_end = int(input("scrape the data no later than year of: "))
                except ValueError:
                    print("input is incorrect, please input again:")
                    continue
                else:
                    if year_end > year_from:
                        break
                    else:
                        print("end year is earlier than the starting year, please input again:")
                        continue
            output_str = "the years to be scraped is from " + str(year_from+1)+ " to " + str(year_end)
            print(output_str)

        # 生成字典链表记录年份信息
        for lpindex_years_tbl_rows in range(len(years_tbl_rows)):
            row=years_tbl_rows[lpindex_years_tbl_rows]
        # for row in years_tbl_rows:
            year_name_curr=row.text
            if year_name_curr!="":
                year_current=int(year_name_curr)
                if year_current>year_from and year_current<=year_end:
                    y_curr=row.get("href")
                    year_url.append(y_curr)
                    year_index.append(year_name_curr)
                    tournament_league=[]
                    tournament_country=[]
                    tournament_date=[]
                    tournament_player1=[]
                    tournament_player2=[]
                    tournament_result=[]
                    tournament_HomeAwayodd01=[]
                    tournament_HomeAwayodd02=[]
                    tournament_AsianHandicapgames=[]
                    tournament_AsianHandicapodd01=[]
                    tournament_AsianHandicapodd02=[]
                    tournament_OverUndergames=[]
                    tournament_OverUnderodd01=[]
                    tournament_OverUnderodd02=[]
                    tournament_url=[]
                    print("...", end="")

                    # scraping games of each year
                    league_url = self.league["urls"]+y_curr
                    self.browser.get(league_url)
                    sleep(1)
                    # how many pages
                    try:
                        self.browser.find_element_by_id("pagination")
                    except:
                        pgnum=1
                    else:
                        pgnum=1
                        pgnum_tbl = self.browser.find_element_by_id("pagination")
                        pgnum_html = pgnum_tbl.get_attribute("innerHTML")
                        pgnum_soup = BeautifulSoup(pgnum_html, "html.parser")
                        pgnum_rows=pgnum_soup.select("a")
                        for row in pgnum_rows:
                            pages=row.get("x-page")
                            pgnum=max(pgnum,int(pages))

                    # get games info on each page:
                    for i in range(1,pgnum+1):
                        if i>1:
                            league_url = self.league["urls"]+y_curr+"#/page/"+str(i)
                            self.browser.get(league_url)
                            sleep(1)

                        tournament_tbl = self.browser.find_element_by_id("tournamentTable")
                        tournament_tbl_html = tournament_tbl.get_attribute("innerHTML")
                        tournament_tbl_soup = BeautifulSoup(tournament_tbl_html, "html.parser")
                        try:
                            significant_rows = tournament_tbl_soup(self.is_tennis_match_or_date)
                        except:
                            break
                        else:
                            current_date_str = None
                            for row in significant_rows:
                                if self.is_date(row) is True:
                                    current_date_str = self.get_date(row)
                                elif self.is_date_string_supported(current_date_str) == False:
                                    # not presently supported 今天昨天等时间变量待识别
                                    continue
                                else:  # is a tennis match
                                    # this_match = TennisMatch()
                                    game_date = self.getmonthdate(current_date_str)    #时间格式考虑修改
                                    participants = self.get_participants(row)
                                    scores = self.get_scores(row)
                                    game_url=row.a.get("href")
                                    odds = self.get_odds(game_url)
                                    tournament_url.append(self.league["urls"]+game_url)
                                    tournament_country.append(league_dict["country"])
                                    tournament_league.append(league_dict["league"])
                                    tournament_date.append(game_date)
                                    tournament_player1.append(participants[0])
                                    tournament_player2.append(participants[1])
                                    tournament_result.append(odds[8])
                                    tournament_HomeAwayodd01.append(odds[0])
                                    tournament_HomeAwayodd02.append(odds[1])
                                    tournament_AsianHandicapgames.append(odds[2])
                                    tournament_AsianHandicapodd01.append(odds[3])
                                    tournament_AsianHandicapodd02.append(odds[4])
                                    tournament_OverUndergames.append(odds[5])
                                    tournament_OverUnderodd01.append(odds[6])
                                    tournament_OverUnderodd02.append(odds[7])
                                    # currenttournamentcol=pd.DataFrame({"year":current_date_str, "country":league_dict["country"],"league":league_dict["league"],"game":game_url})
                                    # currenttournamentcol=pd.DataFrame(data=[current_date_str,league_dict["country"],league_dict["league"],game_url],columns=list["year", "country","league","game"])
                                    # currenttournamentcol=pd.DataFrame(data=[current_date_str,league_dict["country"],league_dict["league"],game_url],columns=["year", "country","league","game"])
                                    # currenttournamentcol=pd.DataFrame("year": current_date_str, "country": league_dict["country"],"league":league_dict["league"], "game": game_url)
                            # currenttournamentcol=pd.DataFrame({"year": [current_date_str], "country": [league_dict["country"]],"league":[league_dict["league"]], "game": [game_url]})
                            # self.wholetournamentrecords =self.wholetournamentrecords.append(currenttournamentcol)
                                    # self.db_manager.add_tennis_match(self.league, url, this_match)

                        # save a whole year's tournaments data
                        Columslist=["League","country","date","player1","player2","result", "HomeAwayodd01","HomeAwayodd02","AHgames" ,"AHodd01","AHodd02","OUgames","OUodds1","OUodds2","tournament_url"]
                        datas={}
                        datas[Columslist[0]]=tournament_league
                        datas[Columslist[1]]=tournament_country
                        datas[Columslist[2]]=tournament_date
                        datas[Columslist[3]]=tournament_player1
                        datas[Columslist[4]]=tournament_player2
                        datas[Columslist[5]]=tournament_result
                        datas[Columslist[6]]=tournament_HomeAwayodd01
                        datas[Columslist[7]]=tournament_HomeAwayodd02
                        datas[Columslist[8]]=tournament_AsianHandicapgames
                        datas[Columslist[9]]=tournament_AsianHandicapodd01
                        datas[Columslist[10]]=tournament_AsianHandicapodd02
                        datas[Columslist[11]]=tournament_OverUndergames
                        datas[Columslist[12]]=tournament_OverUnderodd01
                        datas[Columslist[13]]=tournament_OverUnderodd02
                        datas[Columslist[14]]=tournament_url

                        cols = pd.DataFrame(columns = Columslist)
                        for id in Columslist:
                            cols[id] = datas[id]

                        # save the data in results_folder
                        result_dir=self.currpath+sep+"scraping_results"
                        if not(os.path.exists(result_dir)):
                            os.mkdir(result_dir)
                        tournament_path=result_dir+sep+league_dict["country"]+" "+league_dict["league"]+" "+year_name_curr+' data.csv'
                        tournamentlistcsv=open(tournament_path,"w")
                        cols.to_csv(tournament_path)
                        tournamentlistcsv.close()

        # save the urls of each year for this league.
        Columslist=["year_index","year_url"]
        datas={}
        datas[Columslist[0]]=year_index
        datas[Columslist[1]]=year_url
        cols = pd.DataFrame(columns = Columslist)
        for id in Columslist:
            cols[id] = datas[id]

        # save the data in results_folder
        result_dir=self.currpath+sep+"scraping_results"
        if not(os.path.exists(result_dir)):
            os.mkdir(result_dir)
        LeagueyearList_path=result_dir+sep+"year list of "+league_dict["league"]+'.csv'
        ylist=open(LeagueyearList_path,"w")
        cols.to_csv(LeagueyearList_path)
        ylist.close()
        # self.league_list=cols

        if do_verbose_output is True:
            print("Done scraping all the tournaments of current league, and saving data to .csv file . Scaping the next one")

    def is_leagues(self, tag):
        """
        Determine whether a provided HTML tag is a row for a tennis match or
        date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """
        if tag.name != "tr":
            return False
        elif ("dark" in tag["class"]) or ("center" in tag["class"]):
            return False
        else:
            return True



    def is_country(self, tag):
        """
        Determine whether a provided HTML tag is a row for a date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """
        if "dark" in tag["class"]:
            return False
        if "center" in tag["class"]:
            return True
        else:
            return False

    def get_country(self, tag):
        """
        Extract the date from an HTML tag for a date row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted date string.
        """
        this_country = tag.find(class_="bfl").text
        # if "Today" in this_date:
        #     return "Today"
        # elif this_date.endswith(" - Play Offs"):
        #     this_date = this_date[:-12]
        return this_country

    def get_league(self, tag):
        """
        Extract the date from an HTML tag for a date row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted date string.
        """

        this_league = tag.find().string
        # if "Today" in this_date:
        #     return "Today"
        # elif this_date.endswith(" - Play Offs"):
        #     this_date = this_date[:-12]
        return this_league


######################################################新定义的
    def is_date(self, tag):
        """
        Determine whether a provided HTML tag is a row for a date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """

        return "center" in tag["class"] and "nob-border" in tag["class"]

    def get_date(self, tag):
        """
        Extract the date from an HTML tag for a date row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted date string.
        """

        this_date = tag.find(class_="datet").string
        if "Today" in this_date:
            return "Today"
        if "Yesterday" in this_date:
            return "Yesterday"
        # elif this_date.endswith(" - Play Offs") or this_date.endswith("Qualification"):
        else:
            this_date = this_date[:11]
        return this_date

    def getmonthdate(self,current_date_str ):

        if "Today" in current_date_str:
            date=datetime.datetime.now().date()
        elif "Yesterday" in current_date_str:
            date=datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            date=datetime.datetime.strptime(current_date_str, "%d %b %Y")
        # return [datetime.datetime.strftime(date,'%m'),datetime.datetime.strftime(date,'%d')]
        return datetime.datetime.strftime(date,"%Y-%m-%d")




    def is_date_string_supported(self, date_string):
        """
        Determine whether a given date string is currently supported by this
        software's parsing capabilities.

        Args:
            date_string (str): Date string to assess.

        Returns:
            (bool)
        """

        if date_string is None:
            return False
        elif "Qualification" in date_string:
            return False
        elif "Promotion" in date_string:
            return False
        return True

    def get_participants(self, tag):
        """
       Extract the match's participants from an HTML tag for a tennis match
        row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match participants.
        """

        parsed_strings = tag.find(class_="table-participant").text.split(" - ")
        participants = []
        participants.append(parsed_strings[0])
        participants.append(parsed_strings[-1])
        return participants

    def get_scores(self, tag):
        """
        Extract the scores for each team from an HTML tag for a soccer match
        row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match scores.
        """

        score_str = tag.find(class_="table-score").string
        if self.is_invalid_game_from_score_string(score_str):
            return [-1,-1]
        non_decimal = re.compile(r"[^\d]+")
        score_str = non_decimal.sub(" ", score_str)
        scores = [int(s) for s in score_str.split()]
        return scores


    def is_invalid_game_from_score_string(self, score_str):
        """
        Assess, from the score string extracted from a soccer match row,
        whether a game actually paid out one of the bet outcomes.

        Args:
            score_str (str): Score string to assess.

        Returns:
            (bool)
        """

        if score_str == "postp.":
            return True
        elif score_str == "canc.":
            return True
        return False


    def is_tennis_match_or_date(self, tag):
        """
        Determine whether a provided HTML tag is a row for a soccer match or
        date.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (bool)
        """

        if tag.name != "tr":
            return False
        if "center" in tag["class"] and "nob-border" in tag["class"]:
            return True
        if "deactivate" in tag["class"] and tag.has_attr("xeid"):
            return True
        return False

    def get_odds(self, game_url):

        odds_return=["none","none","none","none","none","none","none","none","none"]
        # [H/A_odd1,H/A_odd1,AH_games,AH_odd1,AH_odd2,O/U_number,O/U_odd1, O/U_odd2,results]
        # Home/Away
        game_url_curr=self.league["urls"]+game_url
        # game_url_curr=self.league["urls"]+sep+game_url+sep+'/#home-away;2'
        self.browser.get(game_url_curr)
        sleep(1)
        # get result
        # result_tbl=self.browser.find_element_by_id("result")
        try:
            result_tbl=self.browser.find_element_by_css_selector(".result")
        except:
            get_results=False
        else:
            get_results=True

        if get_results:
            result_tbl=self.browser.find_element_by_css_selector(".result")
            result_html = result_tbl.get_attribute("innerHTML")
            result_soup = BeautifulSoup(result_html, "html.parser").text
        else:
            result_soup="Canceled"
        odds_return[8]=result_soup
        # scraping the H/A odds
        # odds_tbl=self.browser.find_element_by_id("odds-data-table").find_element_by_partial_link_text("Pinnacle")
        # odds_tbl=self.browser.find_element_by_partial_link_text("Pinnacle")
        haodds_tbl=self.browser.find_element_by_id("odds-data-table")
        haodds_html = haodds_tbl.get_attribute("innerHTML")
        haodds_soup = BeautifulSoup(haodds_html, "html.parser")
        haodds_rows = haodds_soup.select('.lo')
        for row_haodds_rows in haodds_rows:
            td_rows_haodds_rows = row_haodds_rows.select('td')
            if len(td_rows_haodds_rows)!=0:
                # for td_rows_haodds_rows in row_haodds_rows:
                if ("Pinnacle" == td_rows_haodds_rows[0].find_all(class_='name')[0].string) and (td_rows_haodds_rows[3].string!="-"):
                    HAodds_1=td_rows_haodds_rows[1].string
                    HAodds_2=td_rows_haodds_rows[2].string
                    odds_return[0]=HAodds_1
                    odds_return[1]=HAodds_2
                    break

        # Asian Handicap
        # game_url_curr=self.league["urls"]+sep+game_url
        # AHodds_tbl_url_curr=self.league["urls"]+game_url+'#ah;2'
        # self.browser.get(AHodds_tbl_url_curr)
        # Donescraping HA odds, scraping AH
        try:
            self.browser.find_element_by_link_text("AH").click()
        except:
            clicked=False
        else:
            clicked=True
        sleep(1)

        if clicked:
            AHodds_games=self.browser.find_elements_by_partial_link_text(" Games") # located to the inner link item
            # unfold all the "games" tables
            for row_AHodds_games in AHodds_games:
                ahdicap_name=row_AHodds_games.text
                if (" Games" in ahdicap_name) and ("Asian handicap" in ahdicap_name):
                    row_AHodds_games.click()
            sleep(1)

            # find all the "pinnacle" and conpare
            distance=10000000
            ahodds_tbl=self.browser.find_element_by_id("odds-data-table")
            ahodds_html = ahodds_tbl.get_attribute("innerHTML")
            ahodds_soup = BeautifulSoup(ahodds_html, "html.parser")
            ahodds_rows = ahodds_soup.select('.lo')
            for row_ahodds_rows in ahodds_rows: # subwhite tables
                td_row_ahodds_rows = row_ahodds_rows.select('td')
                if len(td_row_ahodds_rows)!=0:
                    if ("Pinnacle" == td_row_ahodds_rows[0].find_all(class_='name')[0].string) and (td_row_ahodds_rows[4].string!="-"):
                        AHodds_1=td_row_ahodds_rows[2].string
                        AHodds_2=td_row_ahodds_rows[3].string
                        currentdistance=(float(AHodds_1)-2)**2+(float(AHodds_2)-2)**2
                        if currentdistance<distance:
                            odds_return[2]=td_row_ahodds_rows[1].string
                            odds_return[3]=AHodds_1
                            odds_return[4]=AHodds_2
                            distance=currentdistance

        # Donescraping AH odds, scraping O/U
        try:
            self.browser.find_element_by_link_text("O/U").click()
        except:
            clicked=False
        else:
            clicked=True
        sleep(1)

        if clicked:
            OUodds_games=self.browser.find_elements_by_partial_link_text(" Games") # located to the inner link item
            # unfold all the "games" tables
            for row_OUodds_games in OUodds_games:
                oudicap_name=row_OUodds_games.text
                if (" Games" in oudicap_name) and ("Over/Under " in oudicap_name):
                    row_OUodds_games.click()
            sleep(1)

            # find all the "pinnacle" and conpare
            distance=10000000
            ouodds_tbl=self.browser.find_element_by_id("odds-data-table")
            ouodds_html = ouodds_tbl.get_attribute("innerHTML")
            ouodds_soup = BeautifulSoup(ouodds_html, "html.parser")
            ouodds_rows = ouodds_soup.select('.lo')
            for row_ouodds_rows in ouodds_rows: # subwhite tables
                td_row_ouodds_rows = row_ouodds_rows.select('td')
                if len(td_row_ouodds_rows)!=0:
                    if ("Pinnacle" == td_row_ouodds_rows[0].find_all(class_='name')[0].string) and (td_row_ouodds_rows[4].string!="-"):
                        OUodds_1=td_row_ouodds_rows[2].string
                        OUodds_2=td_row_ouodds_rows[3].string
                        currentdistance=(float(OUodds_1)-2)**2+(float(OUodds_2)-2)**2
                        if currentdistance<distance:
                            odds_return[5]=td_row_ouodds_rows[1].string
                            odds_return[6]=OUodds_1
                            odds_return[7]=OUodds_2
                            distance=currentdistance


        return odds_return
