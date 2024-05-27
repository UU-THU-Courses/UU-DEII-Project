import os
import requests

class GitHubAPI:
    def __init__(self, access_token, languages = ["Java"], topics = ["maven"], filename = "pom.xml", results_per_page=100) -> None:
        self.parameters = {
            "access_token": access_token,
            "languages": languages,
            "topics": topics,
            "filename": filename,
            "results_per_page": results_per_page,
        }
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_apiurl =  "https://api.github.com/search/repositories"
        self.base_query = self.build_base_query()
    
    def check_rate_limit(self):
        response = requests.get(url="https://api.github.com/rate_limit", headers=self.headers)
        if response.status_code == 200:
            response_dict = response.json()
        return response_dict

    def build_base_query(self):
        query = "?q="

        # Add requested languages to the search query
        if len(self.parameters["languages"]) > 0: query += "language:" + self.parameters["languages"][0]
        for language in self.parameters["languages"][1:]:
            query += f"+language:{language}"

        # Add requested topics to the search query
        if len(self.parameters["topics"]) > 0:
            if len(self.parameters["languages"]) > 0:
                query += "+topic:" + self.parameters["topics"][0]
            else:
                query += "topic:" + self.parameters["topics"][0]
            for topic in self.parameters["topics"][1:]:
                query += f"+topic:{topic}"

        # Only search for public repositories
        if len(self.parameters["languages"]) > 0 or len(self.parameters["topics"]) > 0: query += "+"
        query += "is:public"

        # Only include main repositories
        # excluding any forks
        query += "+-is:fork"

        # Append number of search results
        # per page to the base query
        query += f"&per_page={self.parameters['results_per_page']}"

        return query
    
    def perform_search(self, page_num, sort = None, order = "desc"):
        # Build the sort query
        sort_query = ""
        if sort is not None:
            sort_query = f"&sort={sort}&order={order}"
        
        # Extend the base URL to fetch multiple pages of the search.
        final_url = self.base_apiurl + self.base_query + f"&page={page_num}" + sort_query

        # Query and fetch results
        discovered_repos = []
        response = requests.get(url=final_url, headers=self.headers)
        if response.status_code == 200:
            response_dict = response.json()
            # Use field URL to query if the response
            # repositories contains desired filename
            for repo in response_dict["items"]:
                discovered_repos += [{
                    "reponame": os.path.splitext(os.path.basename(repo["html_url"]))[0],
                    "private": repo["private"],
                    "url": repo["url"],
                    "html_url": repo["html_url"],
                    "fork": repo["fork"],
                    "stargazers_count": repo["stargazers_count"],
                    "language": repo["language"],
                    "topics": repo["topics"],
                    "visibility": repo["visibility"],                   
                }]
        
        # Return final list of repositories
        return discovered_repos
  
    def validity_check(self, url):
        # Make a query to the github api
        response = requests.get(url=url+f"/contents/{self.parameters['filename']}", headers=self.headers)
        if response.status_code == 200: return True    
        return False