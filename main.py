import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import sys


class SEOFunctions:
    def __init__(self, initial_url):
        self.initial_url = initial_url
        self.relevant_links = self.fetch_relevant_links()
        self.get_title_and_h1()
        # self.check_link_status()
        self.report_link_status()

    def fetch_relevant_links(self):
        """Fetch SEO-relevant links from an HTML page."""
        logging.info(f"Fetching URLs for {self.initial_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.36'
            }

            response = requests.get(self.initial_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                absolute_url = urljoin(self.initial_url, href)
                anchor_text = a.get_text(strip=True)
                rel = a.get('rel', [])
                links.append({
                    'url': absolute_url,
                    'anchor_text': anchor_text,
                    'rel': rel,
                    'status_response': None,
                    'title': 'not checked',
                    'h1': 'not checked'
                })

            return links
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return []
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return []

    @staticmethod
    def check_link_response(link):
        """Check if the given URL returns the status code."""
        try:
            response = requests.head(link, allow_redirects=True)
            return response.status_code
        except requests.RequestException as e:
            logging.error(f"Error checking {link}: {e}")
        return False

    def check_link_status(self):
        """Main function to process each sitemap and check URLs for 404s."""
        logging.info("Checking response of fetched URLs")
        num_urls = len(self.relevant_links)
        for index, link in enumerate(self.relevant_links):
            link_status = self.check_link_response(link['url'])
            link['status_response'] = link_status
            sys.stdout.write(f"\rChecking URL {index + 1}/{num_urls}: {link['url']} - Status: {link_status}")
            sys.stdout.flush()

            if link_status != 200:
                logging.warning(f"\rNon 200 Response FOUND: {link['url']} with Status: {link_status}")

    def get_title_and_h1(self):
        for link in self.relevant_links:
            response = requests.get(link['url'])
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string if soup.title else None
            link['title'] = title
            h1 = soup.find("h1").text if soup.find("h1") else None
            link['h1'] = h1
            if not title:
                logging.warning(f"No title found for URL {link['url']}")
            if not h1:
                logging.warning(f"No h1 text found for URL {link['url']}")

    def report_link_status(self):
        logging.info(f"\n\nLinks processed for {self.initial_url}")
        for link in self.relevant_links:
            logging.info(f"{link}")

        logging.info(f"\n\nAbnormal link responses:")
        abnormal_links = [link for link in self.relevant_links if (link['status_response']
                          and link['status_response'] != 200)]
        for link in abnormal_links:
            logging.info(f"{link}")

        logging.info(f"\n\nMissing h1 texts:")
        missing_h1_tags = [link for link in self.relevant_links if not link['h1']]
        for link in missing_h1_tags:
            logging.info(f"{link}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    url = "http://www.tourlane.de"
    SEOFunctions(url)
