# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para piratestreaming
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardarefilm"

host = "http://www.guardarefilm.biz"

headers = [['Referer', host]]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.guardarefilm mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Novita' Al Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/streaming-al-cinema/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]HD[/COLOR]",
                     action="peliculas",
                     url="%s/film-streaming-hd/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Popolari[/COLOR]",
                     action="pelis_top100",
                     url="%s/top100.html" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Animazione[/COLOR]",
                     action="peliculas",
                     url="%s/streaming-cartoni-animati/" % host,
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/serie-tv-streaming/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist


def newest(categoria):
    logger.info("streamondemand.guardarefilm newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://www.guardarefilm.uno/streaming-al-cinema/"
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def categorias(item):
    logger.info("streamondemand.guardarefilm categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="reset dropmenu">(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[guardarefilm.py] " + item.url + " search " + texto)
    section = ""
    if item.extra == "serie":
        section = "0"
    elif item.extra == "movie":
        section = "1"
    item.url = '%s?do=search_advanced&q=%s&section=%s&director=&actor=&year_from=&year_to=' % (host, texto, section)
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.guardarefilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div class="poster"><a href="([^"]+)".*?><img src="([^"]+)".*?><span.*?</div>\s*'
    patron += '<div.*?><a.*?>(.*?)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if item.extra == "serie" else "findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=urlparse.urljoin(host, scrapedthumbnail),
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<div class="pages".*?<span>.*?<a href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def peliculas_tv(item):
    logger.info("streamondemand.guardarefilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div class="poster"><a href="([^"]+)".*?><img src="([^"]+)".*?><span.*?</div>\s*'
    patron += '<div.*?><a.*?>(.*?)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if item.extra == "serie" else "findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=urlparse.urljoin(host, scrapedthumbnail),
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<div class="pages".*?<span>.*?<a href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


def pelis_top100(item):
    logger.info("streamondemand.guardarefilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'<span class="top100_title"><a href="([^"]+)">(.*?\(\d+\))</a>'
    matches = re.compile(patron).findall(data)

    for scrapedurl, scrapedtitle in matches:
        html = httptools.downloadpage(scrapedurl, headers=headers).data
        start = html.find("<div class=\"textwrap\" itemprop=\"description\">")
        end = html.find("</div>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = scrapertools.find_single_match(html, r'class="poster-wrapp"><a href="([^"]+)"')
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios" if item.extra == "serie" else "findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=urlparse.urljoin(host, scrapedthumbnail),
                 plot=scrapedplot,
                 folder=True,
                 fanart=host + scrapedthumbnail))

    return itemlist


def episodios(item):
    logger.info("streamondemand.guardarefilm episodios")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    patron = r'<li id="serie-[^"]+" data-title="Stai guardando: ([^"]+)">'
    patron += r'[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_serie",
                 contentType="episode",
                 title=scrapedtitle,
                 url=item.url,
                 thumbnail=item.thumbnail,
                 extra=scrapedurl,
                 fulltitle=item.fulltitle,
                 show=item.show))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


def findvid_serie(item):
    logger.info("streamondemand.guardarefilm findvideos")

    # Descarga la página
    data = item.extra

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
