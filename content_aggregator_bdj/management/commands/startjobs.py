import logging
from sched import scheduler
from django.conf import settings
from django.core.management.base import BaseCommand
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from content_aggregator_bdj.models import Episode

logger = logging.getLogger(__name__)
'''
class Command(BaseCommand):
    def handle(self, *args, **options):
        #feed = feedparser.parse("https://straight2l.libsyn.com/rss")
        feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
        podcast_title = feed.channel.title
        podcast_image = feed.channel.image["href"]

        for item in feed.entries:
            if not Episode.objects.filter(guid=item.guid).exists():
                episode = Episode(
                    title=item.title,
                    description=item.description,
                    pub_date=parser.parse(item.published),
                    link=item.link,
                    image=podcast_image,
                    podcast_name=podcast_title,
                    guid=item.guid,
                )
                episode.save()
'''
def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
            if not Episode.objects.filter(guid=item.guid).exists():
                episode = Episode(
                    title=item.title,
                    description=item.description,
                    pub_date=parser.parse(item.published),
                    link=item.link,
                    image=podcast_image,
                    podcast_name=podcast_title,
                    guid=item.guid,
                )
                episode.save()

def fetch_realpython_episodes():
    _feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
    save_new_episodes(_feed)

def fetch_straight2L_episodes():
    _feed = feedparser.parse("https://straight2l.libsyn.com/rss")
    save_new_episodes(_feed)

def fetch_npr_shortwave():
    _feed = feedparser.parse("https://feeds.npr.org/510351/podcast.xml")
    save_new_episodes(_feed)

def delete_old_job_execution(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Run apscheduler."

    def handle(self, *args, **optiions):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_realpython_episodes,
            trigger="interval",
            minutes=2,
            id="The Real Python Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: The Real Python Podcast.")

        scheduler.add_job(
            fetch_straight2L_episodes,
            trigger="interval",
            minutes=2,
            id="Straight 2 L Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Straight 2 L Podcast.")

        scheduler.add_job(
            fetch_npr_shortwave,
            trigger="interval",
            minutes=2,
            id="NPR Shortwave",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: NPR Shortwave.")

        scheduler.add_job(
            delete_old_job_execution,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully")



        
'''
class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_realpython_episodes()
        fetch_straight2L_episodes()
        fetch_npr_shortwave()
'''