import requests
import logging
from flask import current_app
from models import Resource, db

class ResourceIntegration:
    """Base class for external resource integrations"""
    
    def __init__(self):
        self.resources = []
    
    def fetch_resources(self):
        """Fetch resources from external source"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def save_to_db(self):
        """Save fetched resources to database"""
        try:
            for resource_data in self.resources:
                # Check if resource already exists (by URL or title)
                existing = Resource.query.filter_by(url=resource_data.get('url')).first()
                if not existing:
                    existing = Resource.query.filter_by(title=resource_data.get('title')).first()
                
                if not existing:
                    # Create new resource
                    resource = Resource(
                        title=resource_data.get('title'),
                        author=resource_data.get('author'),
                        resource_type=resource_data.get('resource_type'),
                        topic=resource_data.get('topic'),
                        description=resource_data.get('description'),
                        content=resource_data.get('content', ''),
                        url=resource_data.get('url', ''),
                        tags=resource_data.get('tags', '')
                    )
                    db.session.add(resource)
            
            db.session.commit()
            return True, f"Successfully added {len(self.resources)} resources"
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving resources: {str(e)}")
            return False, f"Error saving resources: {str(e)}"


class ESwordIntegration(ResourceIntegration):
    """Integration with e-Sword resources"""
    
    def fetch_resources(self, resource_type=None, topic=None):
        """
        Fetch resources from e-Sword compatible libraries
        
        Note: This is a placeholder implementation. Actual implementation would
        require access to e-Sword API or file formats. Currently returns curated
        free resources that are compatible with e-Sword.
        """
        # Curated list of free e-Sword compatible resources
        self.resources = [
            {
                'title': 'Treasury of Scripture Knowledge',
                'author': 'R. A. Torrey',
                'resource_type': 'Commentary',
                'topic': 'Biblical Studies',
                'description': 'A classic Bible cross-reference resource with over 500,000 scripture references.',
                'url': 'https://www.e-sword.net/downloads.html',
                'tags': 'e-sword,cross-reference,public domain'
            },
            {
                'title': 'Matthew Henry\'s Complete Commentary',
                'author': 'Matthew Henry',
                'resource_type': 'Commentary',
                'topic': 'Biblical Studies',
                'description': 'A classic commentary covering the entire Bible, known for its practical and devotional insights.',
                'url': 'https://www.e-sword.net/downloads.html',
                'tags': 'e-sword,commentary,public domain'
            },
            {
                'title': 'Strong\'s Hebrew and Greek Dictionaries',
                'author': 'James Strong',
                'resource_type': 'Dictionary',
                'topic': 'Biblical Languages',
                'description': 'Lexical definitions for Hebrew and Greek words in the Bible.',
                'url': 'https://www.e-sword.net/downloads.html',
                'tags': 'e-sword,lexicon,public domain'
            }
        ]
        
        # Filter by resource type or topic if specified
        if resource_type:
            self.resources = [r for r in self.resources if r['resource_type'] == resource_type]
        if topic:
            self.resources = [r for r in self.resources if r['topic'] == topic]
            
        return self.resources


class LogosIntegration(ResourceIntegration):
    """Integration with Logos Bible Software resources"""
    
    def fetch_resources(self, resource_type=None, topic=None):
        """
        Fetch resources from Logos Bible Software
        
        Note: This is a placeholder implementation. Actual implementation would
        require access to Logos API. Currently returns curated free resources
        that are available in Logos format.
        """
        # Curated list of free Logos compatible resources
        self.resources = [
            {
                'title': 'Lexham Bible Dictionary',
                'author': 'John D. Barry et al.',
                'resource_type': 'Dictionary',
                'topic': 'Biblical Studies',
                'description': 'A comprehensive Bible dictionary with over 7,000 articles on biblical topics.',
                'url': 'https://www.logos.com/product/36564/lexham-bible-dictionary',
                'tags': 'logos,dictionary,free'
            },
            {
                'title': 'Faithlife Study Bible',
                'author': 'Faithlife Corporation',
                'resource_type': 'Study Bible',
                'topic': 'Biblical Studies',
                'description': 'A digital study Bible with notes, articles, and multimedia resources.',
                'url': 'https://www.logos.com/product/36338/faithlife-study-bible',
                'tags': 'logos,study bible,free'
            },
            {
                'title': 'Bible Study Magazine—Issue 1',
                'author': 'Faithlife Corporation',
                'resource_type': 'Magazine',
                'topic': 'Biblical Studies',
                'description': 'First issue of Bible Study Magazine featuring articles on Bible study methods.',
                'url': 'https://www.logos.com/product/5127/bible-study-magazine-issue-1',
                'tags': 'logos,magazine,free'
            }
        ]
        
        # Filter by resource type or topic if specified
        if resource_type:
            self.resources = [r for r in self.resources if r['resource_type'] == resource_type]
        if topic:
            self.resources = [r for r in self.resources if r['topic'] == topic]
            
        return self.resources


class AmillennialResourcesIntegration(ResourceIntegration):
    """Integration specifically for amillennial theological resources"""
    
    def fetch_resources(self, resource_type=None, topic=None):
        """
        Fetch free amillennial resources
        
        This provides a curated list of freely available amillennial resources
        from reputable authors and sources.
        """
        # Curated list of free amillennial resources
        self.resources = [
            {
                'title': 'The Bible and the Future',
                'author': 'Anthony A. Hoekema',
                'resource_type': 'Book',
                'topic': 'Eschatology',
                'description': 'A classic amillennial treatment of biblical eschatology, covering topics such as the kingdom of God, the millennium, and the new earth.',
                'url': 'https://www.monergism.com/topics/eschatology',
                'tags': 'amillennial,eschatology,reformed'
            },
            {
                'title': 'Amillennialism and the Age to Come',
                'author': 'Sam Storms',
                'resource_type': 'Article',
                'topic': 'Eschatology',
                'description': 'An article summarizing the amillennial perspective on the millennium and end times.',
                'url': 'https://www.monergism.com/topics/eschatology/amillennialism',
                'tags': 'amillennial,eschatology,free'
            },
            {
                'title': 'Kingdom Come: The Amillennial Alternative',
                'author': 'Sam Storms',
                'resource_type': 'Book',
                'topic': 'Eschatology',
                'description': 'A thorough examination of amillennial eschatology and a critique of premillennialism.',
                'url': 'https://www.monergism.com/kingdom-come-amillennial-alternative',
                'tags': 'amillennial,eschatology,reformed'
            },
            {
                'title': 'Amillennialism 101',
                'author': 'Kim Riddlebarger',
                'resource_type': 'Article',
                'topic': 'Eschatology',
                'description': 'An introduction to amillennial eschatology, explaining key concepts and biblical support.',
                'url': 'https://www.monergism.com/amillennialism-101',
                'tags': 'amillennial,eschatology,introduction'
            },
            {
                'title': 'A Case for Amillennialism',
                'author': 'Kim Riddlebarger',
                'resource_type': 'Book',
                'topic': 'Eschatology',
                'description': 'A readable defense of amillennialism that explains the viewpoint and responds to common objections.',
                'url': 'https://www.monergism.com/case-amillennialism',
                'tags': 'amillennial,eschatology,reformed'
            },
            {
                'title': 'The Time Is at Hand',
                'author': 'Jay Adams',
                'resource_type': 'Book',
                'topic': 'Eschatology',
                'description': 'An amillennial commentary on the Book of Revelation that emphasizes its relevance for the church throughout history.',
                'url': 'https://www.monergism.com/topics/eschatology/amillennialism',
                'tags': 'amillennial,revelation,commentary'
            },
            {
                'title': 'The Amillennial View of the Kingdom of God',
                'author': 'Anthony Charles',
                'resource_type': 'Article',
                'topic': 'Eschatology',
                'description': 'An article explaining how amillennialists understand the kingdom of God in Scripture.',
                'url': 'https://www.monergism.com/topics/eschatology/amillennialism',
                'tags': 'amillennial,kingdom of god,free'
            }
        ]
        
        # Filter by resource type or topic if specified
        if resource_type:
            self.resources = [r for r in self.resources if r['resource_type'] == resource_type]
        if topic:
            self.resources = [r for r in self.resources if r['topic'] == topic]
            
        return self.resources


def import_external_resources(source="all", resource_type=None, topic=None):
    """
    Import resources from external sources into the database
    
    Args:
        source (str): Source to import from ('esword', 'logos', 'amillennial', or 'all')
        resource_type (str, optional): Filter by resource type
        topic (str, optional): Filter by topic
        
    Returns:
        tuple: (success, message)
    """
    results = []
    
    if source in ['esword', 'all']:
        esword = ESwordIntegration()
        esword.fetch_resources(resource_type, topic)
        success, message = esword.save_to_db()
        results.append(f"e-Sword: {message}")
    
    if source in ['logos', 'all']:
        logos = LogosIntegration()
        logos.fetch_resources(resource_type, topic)
        success, message = logos.save_to_db()
        results.append(f"Logos: {message}")
    
    if source in ['amillennial', 'all']:
        amillennial = AmillennialResourcesIntegration()
        amillennial.fetch_resources(resource_type, topic)
        success, message = amillennial.save_to_db()
        results.append(f"Amillennial: {message}")
    
    return True, "\n".join(results)