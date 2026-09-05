# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Sitemap & Metadata Auditor By Zeeshan Alam SEO Expert", layout="wide")

st.title("Lightweight Sitemap & Metadata Auditor")
st.markdown("Analyze your XML sitemap for status codes, missing title tags, descriptions, and H1 elements instantly.")

sitemap_url = st.text_input("Enter XML Sitemap URL", placeholder="https://example.com/sitemap.xml")

def fetch_sitemap_urls(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Handle standard sitemaps and sitemap indexes
        urls = []
        for elem in root.iter():
            if elem.tag.endswith('loc'):
                if elem.text:
                    urls.append(elem.text.strip())
        return urls
    except Exception as e:
        st.error(f"Error fetching sitemap: {e}")
        return []

def audit_page(url):
    try:
        headers = {'User-Agent': 'SEO-Audit-Bot/1.0'}
        res = requests.get(url, headers=headers, timeout=5)
        status_code = res.status_code
        
        if status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else "Missing Title"
            
            meta_desc = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
            description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else "Missing Description"
            
            h1 = soup.find('h1')
            h1_text = h1.get_text().strip() if h1 else "Missing H1"
        else:
            title, description, h1_text = "N/A", "N/A", "N/A"
            
        return {
            "URL": url,
            "Status": status_code,
            "Title": title,
            "Title Length": len(title) if title != "Missing Title" else 0,
            "Meta Description": description,
            "H1": h1_text
        }
    except Exception as e:
        return {
            "URL": url,
            "Status": "Error",
            "Title": str(e),
            "Title Length": 0,
            "Meta Description": "Error",
            "H1": "Error"
        }

if st.button("Run Audit"):
    if not sitemap_url:
        st.warning("Please enter a valid sitemap URL.")
    else:
        with st.spinner("Fetching sitemap and crawling URLs..."):
            raw_urls = fetch_sitemap_urls(sitemap_url)
            
            if raw_urls:
                # Limit to first 50 URLs for fast Streamlit performance
                max_limit = 50
                urls_to_audit = raw_urls[:max_limit]
                
                if len(raw_urls) > max_limit:
                    st.info(f"Found {len(raw_urls)} URLs. Auditing the first {max_limit} URLs for performance.")
                
                results = []
                progress_bar = st.progress(0)
                
                for i, url in enumerate(urls_to_audit):
                    results.append(audit_page(url))
                    progress_bar.progress((i + 1) / len(urls_to_audit))
                
                df = pd.DataFrame(results)
                
                st.success("Audit Complete!")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Audit Report as CSV",
                    data=csv,
                    file_name="seo_sitemap_audit.csv",
                    mime="text/csv",
                )