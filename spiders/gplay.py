import scrapy
import json
import csv

count = 0
class QuotesSpider(scrapy.Spider):
    name = "gplay"
    # start_urls = [
    #     '4EezU-E1HL8',
    # ]
    urls = []
    urls_visited = []
    masterjson = {}
    movielist = {}
    def start_requests(self):
        global urls
        global urls_visited
        global count
        global masterjson,movielist
        # urls = ['4EezU-E1HL8']
        # with open('movielist.csv','r') as data_file:
        #     movielist = json.load(data_file)
        with open('mastertree.json','r') as data_file:
            masterjson = json.load(data_file)
        with open('to_crawl.json','r') as data_file:
            urls = json.load(data_file)
        with open('crawled.json','r') as data_file:
            urls_visited = json.load(data_file)    
        
        with open('log.txt','a+') as f:
            f.write("Inside start %s\n" % count)
        yield scrapy.Request(url="https://play.google.com/store/movies/details?id=%s" %urls[0], callback=self.parse)


            
    
    def parse(self, response):

        
        
        global urls_visited
        # global urls
        global masterjson
        global movielist

        page = response.url.split("=")[1]
        moviename = response.xpath('//div[contains(@class, "details-info")][1]/div[2]/div[1]/div/text()').extract_first()
        moviegenre = response.xpath('//a[contains(@class,"document-subtitle")]/span/text()').extract_first()
        if moviegenre is not None:
            moviegenre = moviegenre.encode('utf-8')
        fields = [page.encode('utf-8'),moviename.encode('utf-8'),moviegenre]
        with open('movielist.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
        # if page not in urls_visited:
        urls_visited.append(page.encode('utf-8'))
        
        filename = 'movies/movie-%s.html' % page.encode('utf-8')
        masterjson[page]=[]
        with open(filename, 'wb') as f:
            f.write(response.body)
        with open('log.txt','a') as f:
            f.write("Inside parse->" )    
            f.write('Saved file %s\n' % filename)    

        yield scrapy.Request(url="https://play.google.com/store/movies/similar?id=movie-%s" %page,callback = self.recommend)
        
    def recommend(self, response): 
        with open('log.txt','a') as f:
            f.write("Inside recommend")
        global urls   
        global count
        global urls_visited
        global masterjson,movielist
        parent = urls[0].encode('utf-8')
        urls = urls[1:]
        child = []
        # copyofurls = list(urls)
        recomm = response.css("div.card-content.id-track-click.id-track-impression::attr(data-docid)").extract()
        for x in recomm:
            child.append(x[6:].encode('utf-8'))
            if x[6:] not in urls and x[6:] not in urls_visited:
                urls.append(x[6:].encode('utf-8'))
        # for cards in recomm:
        #     print (cards[6:],count)  
        # urls = urls[1:]        
        masterjson[parent]=child
        # print ("url now")
        
        if len(urls)==0:
            with open('mastertree.json','w') as f:
                json.dump(masterjson,f)
            with open('to_crawl.json', 'w') as f:
                json.dump(urls, f)
            with open('crawled.json','w') as f:
                json.dump(urls_visited,f)    
            with open('log.txt','a') as f:
                f.write("Dumped 20 length = %s\n" %len(urls))
            print "Crawl finished!\n"
            return      

        # parent = response.url[-11:]
        
        # data = {"urls",urls}

        count+=1
        if count==20:
            count=count-20
            with open('mastertree.json','w') as f:
                json.dump(masterjson,f)
            with open('to_crawl.json', 'w') as f:
                json.dump(urls, f)
            with open('crawled.json','w') as f:
                json.dump(urls_visited,f)    
            with open('log.txt','a') as f:
                f.write("Dumped 20 length = %s\n" %len(urls))    
        
        if urls is not None:
            yield scrapy.Request(url="https://play.google.com/store/movies/details?id=%s" %urls[0], callback=self.parse)
        
            
                
        # print "reached here hello"
        # for cards in recomm:
        #     print (cards[6:],count)

        # start_requests(self)    


            # yield scrapy.Request(next_page, callback=self.parse)
