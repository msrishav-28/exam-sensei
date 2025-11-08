import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models import Exam, Topic
from database import engine

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

class MultiSourceScraper:
    """
    Comprehensive scraper for multiple Indian exam bodies
    """

    SOURCES = {
        "nta": {
            "base_url": "https://nta.ac.in",
            "public_notice_url": "https://nta.ac.in/PublicNotice",
            "exams": ["jee_main", "neet", "cuet", "ugc_net"]
        },
        "upsc": {
            "base_url": "https://upsc.gov.in",
            "exam_calendar_url": "https://upsc.gov.in/examinations/exam-calendar",
            "exams": ["civil_services", "cds", "nda", "ies"]
        },
        "ssc": {
            "base_url": "https://ssc.nic.in",
            "portal_url": "https://ssc.nic.in/Portal/Apply",
            "exams": ["cgl", "chsl", "mts", "stenographer"]
        },
        "ibps": {
            "base_url": "https://www.ibps.in",
            "careers_url": "https://www.ibps.in/Careers/",
            "exams": ["po", "clerk", "rrb"]
        }
    }

    def scrape_all_sources(self):
        """Scrape all configured sources"""
        for source_name, config in self.SOURCES.items():
            print(f"Starting scrape for {source_name}")
            try:
                if source_name == "nta":
                    self.scrape_nta(config)
                elif source_name == "upsc":
                    self.scrape_upsc(config)
                elif source_name == "ssc":
                    self.scrape_ssc(config)
                elif source_name == "ibps":
                    self.scrape_ibps(config)
                print(f"Completed scrape for {source_name}")
            except Exception as e:
                print(f"Error scraping {source_name}: {e}")

    def scrape_nta(self, config):
        """Scrape NTA website"""
        process = CrawlerProcess({
            'USER_AGENT': 'ExamSensei-Bot/1.0 (+https://examsensei.com/bot)',
            'FEEDS': [{'format': 'json', 'name': 'nta_data.json'}],
        })

        process.crawl(NTASpider, config=config)
        process.start()

    def scrape_upsc(self, config):
        """Scrape UPSC website"""
        process = CrawlerProcess({
            'USER_AGENT': 'ExamSensei-Bot/1.0 (+https://examsensei.com/bot)',
            'FEEDS': [{'format': 'json', 'name': 'upsc_data.json'}],
        })

        process.crawl(UPSCSpider, config=config)
        process.start()

    def scrape_ssc(self, config):
        """Scrape SSC website"""
        process = CrawlerProcess({
            'USER_AGENT': 'ExamSensei-Bot/1.0 (+https://examsensei.com/bot)',
            'FEEDS': [{'format': 'json', 'name': 'ssc_data.json'}],
        })

        process.crawl(SSCSpider, config=config)
        process.start()

    def scrape_ibps(self, config):
        """Scrape IBPS website"""
        process = CrawlerProcess({
            'USER_AGENT': 'ExamSensei-Bot/1.0 (+https://examsensei.com/bot)',
            'FEEDS': [{'format': 'json', 'name': 'ibps_data.json'}],
        })

        process.crawl(IBPSSpider, config=config)
        process.start()

    def update_database(self, scraped_data, source_name):
        """Update database with scraped data"""
        for exam_data in scraped_data:
            # Check if exam exists
            exam = db.query(Exam).filter(Exam.code == exam_data.get("code")).first()

            if exam:
                # Update existing exam
                for key, value in exam_data.items():
                    if hasattr(exam, key) and key != "id":
                        if isinstance(value, (dict, list)):
                            setattr(exam, key, json.dumps(value))
                        else:
                            setattr(exam, key, value)
                exam.updated_at = datetime.utcnow()
            else:
                # Create new exam
                exam_dict = exam_data.copy()
                exam_dict["body"] = source_name.upper()

                # Handle JSON fields
                for json_field in ['eligibility', 'fees', 'important_dates', 'pattern', 'centers', 'subjects']:
                    if json_field in exam_dict and isinstance(exam_dict[json_field], dict):
                        exam_dict[json_field] = json.dumps(exam_dict[json_field])

                exam = Exam(**exam_dict)
                db.add(exam)

            db.commit()

            # Update topics if provided
            if "topics" in exam_data:
                self.update_topics(exam.id, exam_data["topics"])

        print(f"Database updated with {len(scraped_data)} exams from {source_name}")

    def update_topics(self, exam_id, topics_data):
        """Update exam topics"""
        for topic_data in topics_data:
            topic = db.query(Topic).filter(
                Topic.exam_id == exam_id,
                Topic.subject == topic_data.get("subject"),
                Topic.name == topic_data.get("name")
            ).first()

            if topic:
                # Update existing topic
                for key, value in topic_data.items():
                    if hasattr(topic, key) and key not in ["id", "exam_id"]:
                        if isinstance(value, (dict, list)):
                            setattr(topic, key, json.dumps(value))
                        else:
                            setattr(topic, key, value)
            else:
                # Create new topic
                topic_dict = topic_data.copy()
                topic_dict["exam_id"] = exam_id

                # Handle JSON fields
                for json_field in ['weightage_history', 'difficulty_distribution', 'correlation_topics', 'previous_patterns']:
                    if json_field in topic_dict and isinstance(topic_dict[json_field], dict):
                        topic_dict[json_field] = json.dumps(topic_dict[json_field])

                topic = Topic(**topic_dict)
                db.add(topic)

        db.commit()


class NTASpider(scrapy.Spider):
    name = "nta_spider"

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config or {}

    def start_requests(self):
        urls = [
            self.config.get("public_notice_url", "https://nta.ac.in/PublicNotice"),
            "https://nta.ac.in/Exam-Calendar",
            "https://nta.ac.in/Information-Bulletin"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract exam information from various NTA pages
        page_title = response.css('title::text').get() or ""

        if "PublicNotice" in response.url:
            yield from self.parse_public_notices(response)
        elif "Exam-Calendar" in response.url:
            yield from self.parse_exam_calendar(response)
        elif "Information-Bulletin" in response.url:
            yield from self.parse_info_bulletin(response)

    def parse_public_notices(self, response):
        notices = response.css('table tbody tr')

        for notice in notices:
            title = notice.css('td:nth-child(2) a::text').get()
            link = notice.css('td:nth-child(2) a::attr(href)').get()
            date = notice.css('td:nth-child(3)::text').get()

            if title and "JEE" in title.upper():
                yield {
                    "code": "jee_main_2025",
                    "name": "JEE Main 2025",
                    "exam_type": "engineering_entrance",
                    "notification_url": response.urljoin(link),
                    "important_dates": {
                        "notification": date.strip() if date else None,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }
            elif title and "NEET" in title.upper():
                yield {
                    "code": "neet_2025",
                    "name": "NEET 2025",
                    "exam_type": "medical_entrance",
                    "notification_url": response.urljoin(link),
                    "important_dates": {
                        "notification": date.strip() if date else None,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }

    def parse_exam_calendar(self, response):
        # Extract exam dates from calendar
        exam_rows = response.css('.exam-calendar table tr')

        for row in exam_rows[1:]:  # Skip header
            cells = row.css('td::text').getall()
            if len(cells) >= 3:
                exam_name = cells[0].strip()
                exam_date = cells[1].strip()

                if "JEE" in exam_name:
                    yield {
                        "code": "jee_main_2025",
                        "important_dates": {
                            "exam_dates": [exam_date],
                            "last_updated": datetime.utcnow().isoformat()
                        }
                    }
                elif "NEET" in exam_name:
                    yield {
                        "code": "neet_2025",
                        "important_dates": {
                            "exam_dates": [exam_date],
                            "last_updated": datetime.utcnow().isoformat()
                        }
                    }

    def parse_info_bulletin(self, response):
        # Extract detailed exam information
        content = response.css('.content-area')

        # JEE Main details
        jee_info = content.css('p:contains("JEE Main")').getall()
        if jee_info:
            yield {
                "code": "jee_main_2025",
                "pattern": {
                    "total_questions": 90,
                    "marks_per_question": 4,
                    "negative_marking": -1,
                    "time": 180
                },
                "eligibility": {
                    "education": "Class 12 pass",
                    "subjects": ["Physics", "Chemistry", "Mathematics"]
                }
            }

        # NEET details
        neet_info = content.css('p:contains("NEET")').getall()
        if neet_info:
            yield {
                "code": "neet_2025",
                "pattern": {
                    "total_questions": 200,
                    "marks_per_question": 4,
                    "negative_marking": -1,
                    "time": 200
                },
                "eligibility": {
                    "education": "Class 12 pass with PCB",
                    "minimum_marks": "50% aggregate"
                }
            }


class UPSCSpider(scrapy.Spider):
    name = "upsc_spider"

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config or {}

    def start_requests(self):
        urls = [
            self.config.get("exam_calendar_url", "https://upsc.gov.in/examinations/exam-calendar"),
            "https://upsc.gov.in/examinations/scheme-of-examination",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if "exam-calendar" in response.url:
            yield from self.parse_exam_calendar(response)
        elif "scheme-of-examination" in response.url:
            yield from self.parse_exam_scheme(response)

    def parse_exam_calendar(self, response):
        # Extract UPSC exam dates
        exam_entries = response.css('.exam-calendar .exam-item')

        for entry in exam_entries:
            exam_name = entry.css('.exam-name::text').get()
            exam_date = entry.css('.exam-date::text').get()

            if exam_name and "Civil Services" in exam_name:
                yield {
                    "code": "upsc_prelims_2025",
                    "name": "UPSC Civil Services Prelims 2025",
                    "exam_type": "civil_services",
                    "important_dates": {
                        "exam_dates": [exam_date.strip()] if exam_date else [],
                        "last_updated": datetime.utcnow().isoformat()
                    },
                    "pattern": {
                        "total_questions": 200,
                        "marks_per_question": 2,
                        "negative_marking": -0.67,
                        "time": 120
                    }
                }

    def parse_exam_scheme(self, response):
        # Extract detailed exam patterns
        yield {
            "code": "upsc_civil_services",
            "syllabus": "Comprehensive syllabus covering history, geography, polity, economy, science, current affairs",
            "pattern": {
                "stages": ["Preliminary", "Mains", "Interview"],
                "subjects": ["General Studies", "CSAT", "Optional Subject"]
            }
        }


class SSCSpider(scrapy.Spider):
    name = "ssc_spider"

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config or {}

    def start_requests(self):
        urls = [
            self.config.get("portal_url", "https://ssc.nic.in/Portal/Apply"),
            "https://ssc.nic.in/Portal/ExamCalendar"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if "ExamCalendar" in response.url:
            yield from self.parse_exam_calendar(response)
        else:
            yield from self.parse_notifications(response)

    def parse_exam_calendar(self, response):
        # Extract SSC exam information
        exam_data = response.css('.exam-calendar table tr')

        for row in exam_data[1:]:  # Skip header
            cells = row.css('td::text').getall()
            if len(cells) >= 2:
                exam_name = cells[0].strip()
                exam_date = cells[1].strip()

                if "CGL" in exam_name.upper():
                    yield {
                        "code": "ssc_cgl_2025",
                        "name": "SSC CGL 2025",
                        "exam_type": "government_job",
                        "important_dates": {
                            "exam_dates": [exam_date],
                            "last_updated": datetime.utcnow().isoformat()
                        }
                    }

    def parse_notifications(self, response):
        # Extract recruitment notifications
        notifications = response.css('.notification-item')

        for notification in notifications:
            title = notification.css('.title::text').get()
            link = notification.css('a::attr(href)').get()

            if title and "CGL" in title.upper():
                yield {
                    "code": "ssc_cgl_2025",
                    "notification_url": response.urljoin(link),
                    "application_url": response.urljoin(link)
                }


class IBPSSpider(scrapy.Spider):
    name = "ibps_spider"

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config or {}

    def start_requests(self):
        urls = [
            self.config.get("careers_url", "https://www.ibps.in/Careers/"),
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract banking exam information
        career_items = response.css('.career-item')

        for item in career_items:
            title = item.css('.title::text').get()
            exam_date = item.css('.exam-date::text').get()

            if title and "PO" in title.upper():
                yield {
                    "code": "ibps_po_2025",
                    "name": "IBPS PO 2025",
                    "exam_type": "banking",
                    "important_dates": {
                        "exam_dates": [exam_date.strip()] if exam_date else [],
                        "last_updated": datetime.utcnow().isoformat()
                    },
                    "pattern": {
                        "stages": ["Preliminary", "Mains", "Interview"],
                        "total_questions": 150,
                        "time": 180
                    }
                }


if __name__ == "__main__":
    scraper = MultiSourceScraper()
    scraper.scrape_all_sources()
