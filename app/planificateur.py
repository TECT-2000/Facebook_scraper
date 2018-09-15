import sched, time,os
from spiders.scraper import facebookScraper
from crontab import CronTab


cron = CronTab(user="sentos")
cron.remove_all()
job=cron.new(command="sentos /usr/bin/python /home/sentos/Documents/PycharmProjects/sita_FAA/app/pagination.py > /home/sentos/Documents/PycharmProjects/site_FAA/app/file.log")
job.minute.every(1)
cron.write()
print(cron)

