import json
from scrapy import Spider, Request, FormRequest
from ..items import SpidermusicItem


# from scrapy.cmdline import execute
# execute(['scrapy', 'crawl', 'music'])


class MusicSpider(Spider):
    name = 'music'
    allowed_domain = ['music.163.com']
    base_url = 'https://music.163.com'
    ids = ['1001', '1002', '1003', '2001', '2002', '2003', '6001', '6002', '6003', '7001', '7002', '7003', '4001',
           '4002', '4003']
    # ids = ['1001']
    initials = [i for i in range(65, 91)] + [0]

    def start_requests(self):
        for id in self.ids:
            for initial in self.initials:
                url = '{url}/discover/artist/cat?id={id}&initial={initial}'.format(url=self.base_url, id=id,
                                                                                   initial=initial)
                yield Request(url, callback=self.parse_index)

    # abc
    # 歌手url
    def parse_index(self, response):
        artist_id = response.xpath('//*[@id="m-artist-box"]/li[1]/div/a')[0] \
                        .re('href\=\"\/artist\?id\=[(0-9)]{4,9}')[0][17:]
        artist_url = self.base_url + '/artist/album?id=' + artist_id
        artist_suffix = '/artist/album?id=' + artist_id  # 传递歌手第一页url后缀到parse_artist_pre
        yield Request(artist_url, meta={'artist_suffix': artist_suffix}, callback=self.parse_artist_pre,
                      dont_filter=True)

    # 专辑翻页
    def parse_artist_pre(self, response):
        artist_suffix = response.meta['artist_suffix']
        pages = response.xpath('//*[@class="u-page"]/a[@class="zpgi"]/@href').extract()  # 翻页标签
        if pages == []:  # 只有一页
            artist_album_url = self.base_url + artist_suffix
            yield Request(artist_album_url, callback=self.parse_artist)
        else:  # 有多页,获取分页url, 加上第一页url
            pages.append(artist_suffix)
            for page in pages:
                artist_album_url = self.base_url + page
                yield Request(artist_album_url, callback=self.parse_artist)

    # 歌手专辑url
    def parse_artist(self, response):
        albums = response.xpath('//*[@id="m-song-module"]/li/div/a[@class="msk"]/@href').getall()
        for album in albums:
            album_url = self.base_url + album
            yield Request(album_url, callback=self.parse_album)

    # 专辑音乐url
    def parse_album(self, response):
        musics = response.xpath('//ul[@class="f-hide"]/li/a/@href').extract()
        for music in musics:
            music_id = music[9:]
            music_url = self.base_url + music
            yield Request(music_url, meta={'music_id': music_id}, callback=self.parse_music)

    # 音乐信息
    def parse_music(self, response):
        music_id = response.meta["music_id"]
        music = response.xpath('//div[@class="tit"]/em[@class="f-ff2"]/text()').get()
        artist = response.xpath('//div[@class="cnt"]/p[1]/span/a/text()').get()
        album = response.xpath('//div[@class="cnt"]/p[2]/a/text()').get()

        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-length': '664',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': '_iuqxldmzr_=32; _ntes_nnid=04c48f359d53f85abd5324d9f5a5836b,1590128803202; _ntes_nuid=04c48f359d53f85abd5324d9f5a5836b; WM_TID=LAx4ld1of%2B1BFFVUBQYrCVqaQ0RRan8o; mail_psc_fingerprint=df45ee443965bd6b2f1e9e1d87f361ea; P_INFO=dxairopen@163.com|1593403362|0|mail163|00&99|null&null&null#yun&530100#10#0#0|&0||dxairopen@163.com; nts_mail_user=undefined:-1:0; MUSIC_U=5057e34f0e868ba8708b2a8777445dadc4418e8b7f44306f6f296e2956f3052433a649814e309366; __csrf=96374c5de70f258c93ebd41c3432f87d; ntes_kaola_ad=1; WM_NI=CiSCHw2UD%2FKxxaJxTM9tz1o7FXyZSCIrOIbi%2FQgx0N6icmZSDhnw6lBxUjq22B2BFO6OOpKAjSxC5P9oH24TF9whIAOLxVFQjIiEMljW2FMW1LOWY%2BaJfyki0kwGby5iWFA%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea6fb5ab0bdc08fdb3eb68a8bb6c55e839b9aaaf460af9fbba7e15b9599abb0b82af0fea7c3b92a81b79da4cb7df28b8cd0ca74bcbf8699d747fbacb6d2ee3d8688b7bbd2498bae81aae163ed8fa999b346f6b7ad8ed95988b8a298b56882a89b8bf43af29efea3c545f6918191ca4baa8db8a4b85cfbb188d3b76086e7b989cc4b8d94b8b7c55baa97a7a6d068aa89fea7d05df39481b8dc21a396aa9aea63f4b5b9a8e173f7b799a7c437e2a3; JSESSIONID-WYYY=EeDuJXhc2mVm4Tx9SIXkC4J9XE7A2Cf9xGurVDPCQcV8bP2IdTsx14Nr7jznZxusGdlkq1hcqhPAvgnwug7sHQ1M7nDRXn40QD3%2B3ErVNReVbD7k9h%2FaIAKKA8%2B0jQXCN%2FI0IRhpm2je%2FgRpdbRcTjYOQWURhniH0NSfEIQPkD55COhb%3A1594633598263',
            'origin': 'https://music.163.com',
            'referer': self.base_url + '/song?id=' + music_id,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
        }

        data = {
            'csrf_token': '',
            'params': 'ktiZ5z5XZ3O1Eq14bqNApzJl30yT5Znv109VOyum1qnMbR/wuU7UmJ8wSJmjfbifp1Ckk28jLSsteEywSfhrkHxRnD+ldET5VlA8ReAmpvQE9JcsIoCylfcG9UX2DrlrRUlBzOosrjK+esm1solnqgBeqfkVZ8pndew9YYwrA8KBBqwlgjQ+rcWS4dpIXwmknsSyN0X6H147+SNBB4KuMnRTXF4D5/oa0yzPD4E5R3K+RZAX1vc/OK/YVJhmZruUDfNWqiUYJ89pSaXnc4uXemVS1a++AXvlcfCMRPADJcWCOC8aVDcuYw/FMwkTp0ol52igc6gN02ANSX1bR9qKCXjqYQUsJ4mt9wXRZ8zyMG8=',
            'encSecKey': '277e8815a47f1d01942aaf069dc913b6cccf285cfdf84e8752bba472452a7ce425bfe5b5ad74fdbd465cb1b18a4a0a81f65fa1425a9f9647bddd75b502060093e4eccf11ad60395d0f2c74cf1ee578e4479aaf3a779e33ff065f53f6813557b88222769bca51bdb521c48ad16d5744ecd12f15f10d6920eb0676cb021ea19495'
        }

        music_comment = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(music_id)
        yield FormRequest(music_comment, meta={'id': music_id, 'music': music, 'artist': artist, 'album': album}, \
                          callback=self.parse_comment, formdata=data)

    # 获取评论
    def parse_comment(self, response):
        id = response.meta['id']
        music = response.meta['music']
        artist = response.meta['artist']
        album = response.meta['album']
        result = json.loads(response.text)
        comments = []
        if 'hotComments' in result.keys():
            for comment in result.get('hotComments'):
                hotcomment_author = comment['user']['nickname']
                hotcomment = comment['content']
                hotcomment_like = comment['likedCount']
                hotcomment_avatar = comment['user']['avatarUrl']
                data = {
                    'nickname': hotcomment_author,
                    'content': hotcomment,
                    'likedcount': hotcomment_like,
                    'avatarurl': hotcomment_avatar
                }
                comments.append(data)
        item = SpidermusicItem()
        for field in item.fields:
            try:
                item[field] = eval(field)
            except:
                print('Field is not defined', field)
        yield item

