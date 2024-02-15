from django.contrib.sitemaps import Sitemap

class ShopSitemap(Sitemap):

    changefreq = "never"
    priority = 0.5
