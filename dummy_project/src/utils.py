# Utility functions 
"""
Utility functions for Knowledge Repository
This module provides core functionality for managing and accessing knowledge repository data.
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Union

class KnowledgeManager:
    def __init__(self, base_path: str):
        """
        Initialize the KnowledgeManager with the base path for the repository
        
        Args:
            base_path (str): Base directory path for the knowledge repository
        """
        self.base_path = base_path
        self._ensure_directory_structure()

    def _ensure_directory_structure(self) -> None:
        """Create necessary directory structure if it doesn't exist"""
        os.makedirs(os.path.join(self.base_path, "articles"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "metadata"), exist_ok=True)

    def create_article(self, title: str, content: str, tags: List[str]) -> str:
        """
        Create a new article in the repository
        
        Args:
            title (str): Title of the article
            content (str): Content of the article
            tags (List[str]): List of tags for categorization
            
        Returns:
            str: Article ID
        """
        article_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create article file
        article_path = os.path.join(self.base_path, "articles", f"{article_id}.md")
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")
        
        # Create metadata
        metadata = {
            "title": title,
            "created_at": datetime.datetime.now().isoformat(),
            "tags": tags,
            "last_modified": datetime.datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(self.base_path, "metadata", f"{article_id}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        return article_id

    def update_article(self, article_id: str, content: Optional[str] = None, 
                      tags: Optional[List[str]] = None) -> bool:
        """
        Update an existing article
        
        Args:
            article_id (str): ID of the article to update
            content (Optional[str]): New content if provided
            tags (Optional[List[str]]): New tags if provided
            
        Returns:
            bool: Success status
        """
        article_path = os.path.join(self.base_path, "articles", f"{article_id}.md")
        metadata_path = os.path.join(self.base_path, "metadata", f"{article_id}.json")
        
        if not (os.path.exists(article_path) and os.path.exists(metadata_path)):
            return False
            
        # Update content if provided
        if content is not None:
            with open(article_path, "r+", encoding="utf-8") as f:
                lines = f.readlines()
                title_line = lines[0]  # Preserve the title
                with open(article_path, "w", encoding="utf-8") as f2:
                    f2.write(f"{title_line}\n{content}")
        
        # Update metadata if tags provided
        if tags is not None:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata["tags"] = tags
                metadata["last_modified"] = datetime.datetime.now().isoformat()
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
        return True

    def search_articles(self, query: str, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        Search articles by content and/or tags
        
        Args:
            query (str): Search query for content
            tags (Optional[List[str]]): Filter by tags
            
        Returns:
            List[Dict]: List of matching articles with metadata
        """
        results = []
        metadata_dir = os.path.join(self.base_path, "metadata")
        
        for filename in os.listdir(metadata_dir):
            if not filename.endswith(".json"):
                continue
                
            article_id = filename[:-5]
            metadata_path = os.path.join(metadata_dir, filename)
            article_path = os.path.join(self.base_path, "articles", f"{article_id}.md")
            
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                
            with open(article_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if article matches search criteria
            if query.lower() in content.lower():
                if tags is None or any(tag in metadata["tags"] for tag in tags):
                    results.append({
                        "article_id": article_id,
                        "title": metadata["title"],
                        "tags": metadata["tags"],
                        "created_at": metadata["created_at"],
                        "last_modified": metadata["last_modified"]
                    })
        
        return results

    def get_article(self, article_id: str) -> Optional[Dict]:
        """
        Retrieve an article and its metadata
        
        Args:
            article_id (str): ID of the article to retrieve
            
        Returns:
            Optional[Dict]: Article content and metadata if found, None otherwise
        """
        article_path = os.path.join(self.base_path, "articles", f"{article_id}.md")
        metadata_path = os.path.join(self.base_path, "metadata", f"{article_id}.json")
        
        if not (os.path.exists(article_path) and os.path.exists(metadata_path)):
            return None
            
        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        return {
            "content": content,
            "metadata": metadata
        }