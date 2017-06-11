from newspaper import Article
from application.Connections import Connection
from application.ThreadPool import ThreadPool
from requests import head
from time import gmtime, strftime, time, sleep
from urllib.parse import urlparse
from tldextract import extract
import timeout_decorator
from re import search, IGNORECASE
import sys

def get_next_links_sequence():
    cursor = Connection.Instance().newsPoolDB["counters"].find_and_modify(
            query= { '_id': "link_id" },
            update= { '$inc': { 'seq': 1 } },
            new= True,
            upsert= True
    )
    return cursor['seq']

def unshorten_url(url):
    return head(url, allow_redirects=True).url

@timeout_decorator.timeout(10, use_signals=False)
def linkParser(link):
    try:
        print(link)
        link = unshorten_url(link)
        parsed_uri = urlparse(link)
        source = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        url = link
        article = Article(url)
        article.build()
        image = article.top_image
        keywords = article.keywords
        description = article.summary
        title = article.title

        if image != "" and description != "" and title != "":
            dic = {'url': link, 'im':image, 'title': title, 'description': description, 'keywords': keywords, 'source': source}
            return dic
    except Exception as e:
        print(e, '____parser_____')
        pass

def calculateLinks(alertid):
    alertid = int(alertid)
    b = Connection.Instance().db[str(alertid)].find({{'isClicked': {'$exist': True}, 'isClicked': False})
    print(b.count())
    for tweet in b:
        try:
            print(int(tweet['id_str']))
            Connection.Instance().db[str(alertid)].find_one_and_update({'id_str':tweet['id_str'], {'isClicked': {'$exist': True}, 'isClicked': False}, {'$set': {'isClicked': True}})
            tweet_tuple = {'user_id': tweet['user']['id_str'], 'tweet_id': tweet['id_str'], 'timestamp_ms': int(tweet['timestamp_ms'])}
            for link in tweet['entities']['urls']:
                link = link['expanded_url']
                if link == None:
                    continue
                if search('twitter', link):
                    continue
                try:
                    if len(list(Connection.Instance().newsPoolDB[str(alertid)].find({'url':link}))) != 0:
                        print(alertid, " link var \n", tweet_tuple)
                        Connection.Instance().newsPoolDB[str(alertid)].find_one_and_update({'url': link}, {'$push': {'mentions': tweet_tuple}})
                        continue
                    dic = linkParser(link)
                    if dic != None:
                        if len(list(Connection.Instance().newsPoolDB[str(alertid)].find({'source':dic['source'], 'title':dic['title']}))) != 0:
                            Connection.Instance().newsPoolDB[str(alertid)].find_one_and_update({'source':dic['source'], 'title':dic['title']}, {'$push': {'mentions': tweet_tuple}})

                        else:
                            dic['link_id'] = get_next_links_sequence()
                            dic['mentions']=[tweet_tuple]
                            Connection.Instance().newsPoolDB[str(alertid)].insert_one(dic)
                except Exception as e:
                    print('link: ', link)
                    print(e, '_____calculate_____')
                    pass
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e, '____Genel____')
            pass

def main():
    Connection.Instance().cur.execute("Select alertid from alerts;")
    alertid_list = sorted(list(Connection.Instance().cur.fetchall()), reverse=True)
    alertid_list = [alertid[0] for alertid in alertid_list]
    print(alertid_list)
    alertid_list = [32]
    pool = ThreadPool(1, False)
    pool.map(calculateLinks, alertid_list)
    pool.wait_completion()

if __name__ == '__main__':
    main()
