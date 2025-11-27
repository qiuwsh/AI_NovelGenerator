# epub_exporter.py
# -*- coding: utf-8 -*-
import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

class EPubExporter:
    """
    EPUB格式小说导出器
    """
    
    def __init__(self, novel_title: str, author: str = "AI小说生成器"):
        self.novel_title = novel_title
        self.author = author
        self.chapters = []
        
    def add_chapter(self, chapter_number: int, title: str, content: str):
        """添加章节"""
        self.chapters.append({
            'number': chapter_number,
            'title': title,
            'content': content
        })
        
    def export_to_epub(self, output_path: str) -> bool:
        """
        导出为EPUB文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 创建临时目录结构
            temp_dir = os.path.join(os.path.dirname(output_path), "epub_temp")
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
            
            os.makedirs(temp_dir)
            os.makedirs(os.path.join(temp_dir, "META-INF"))
            os.makedirs(os.path.join(temp_dir, "OEBPS"))
            
            # 创建必需的EPUB文件
            self._create_container_xml(temp_dir)
            self._create_mimetype(temp_dir)
            self._create_content_opf(temp_dir)
            self._create_toc_ncx(temp_dir)
            self._create_chapter_files(temp_dir)
            self._create_cover_page(temp_dir)
            self._create_title_page(temp_dir)
            
            # 打包为EPUB文件
            self._create_epub_archive(temp_dir, output_path)
            
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir)
            
            logging.info(f"EPUB导出成功: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"EPUB导出失败: {e}")
            return False
    
    def _create_container_xml(self, temp_dir: str):
        """创建container.xml文件"""
        container = ET.Element('container', {
            'version': '1.0',
            'xmlns': 'urn:oasis:names:tc:opendocument:xmlns:container'
        })
        
        rootfiles = ET.SubElement(container, 'rootfiles')
        ET.SubElement(rootfiles, 'rootfile', {
            'full-path': 'OEBPS/content.opf',
            'media-type': 'application/oebps-package+xml'
        })
        
        tree = ET.ElementTree(container)
        container_path = os.path.join(temp_dir, "META-INF", "container.xml")
        tree.write(container_path, encoding='utf-8', xml_declaration=True)
        
        # 美化XML格式
        self._prettify_xml(container_path)
    
    def _create_mimetype(self, temp_dir: str):
        """创建mimetype文件"""
        mimetype_path = os.path.join(temp_dir, "mimetype")
        with open(mimetype_path, 'w', encoding='utf-8') as f:
            f.write("application/epub+zip")
    
    def _create_content_opf(self, temp_dir: str):
        """创建content.opf文件"""
        package = ET.Element('package', {
            'version': '2.0',
            'xmlns': 'http://www.idpf.org/2007/opf',
            'unique-identifier': 'bookid'
        })
        
        # 元数据
        metadata = ET.SubElement(package, 'metadata')
        ET.SubElement(metadata, 'dc:title').text = self.novel_title
        ET.SubElement(metadata, 'dc:creator').text = self.author
        ET.SubElement(metadata, 'dc:language').text = 'zh-CN'
        ET.SubElement(metadata, 'dc:identifier', {
            'id': 'bookid'
        }).text = f"urn:uuid:{self._generate_uuid()}"
        ET.SubElement(metadata, 'meta', {
            'name': 'cover',
            'content': 'cover'
        })
        
        # 清单
        manifest = ET.SubElement(package, 'manifest')
        items = [
            ('ncx', 'toc.ncx', 'application/x-dtbncx+xml'),
            ('cover', 'cover.xhtml', 'application/xhtml+xml'),
            ('title', 'title.xhtml', 'application/xhtml+xml')
        ]
        
        for item_id, href, media_type in items:
            ET.SubElement(manifest, 'item', {
                'id': item_id,
                'href': href,
                'media-type': media_type
            })
        
        # 添加章节文件
        for i, chapter in enumerate(self.chapters):
            chapter_id = f'chapter_{chapter["number"]}'
            chapter_file = f'chapter_{chapter["number"]}.xhtml'
            ET.SubElement(manifest, 'item', {
                'id': chapter_id,
                'href': chapter_file,
                'media-type': 'application/xhtml+xml'
            })
        
        # 书脊
        spine = ET.SubElement(package, 'spine', {'toc': 'ncx'})
        ET.SubElement(spine, 'itemref', {'idref': 'cover'})
        ET.SubElement(spine, 'itemref', {'idref': 'title'})
        
        for i, chapter in enumerate(self.chapters):
            chapter_id = f'chapter_{chapter["number"]}'
            ET.SubElement(spine, 'itemref', {'idref': chapter_id})
        
        # 指南
        guide = ET.SubElement(package, 'guide')
        ET.SubElement(guide, 'reference', {
            'type': 'cover',
            'title': '封面',
            'href': 'cover.xhtml'
        })
        
        tree = ET.ElementTree(package)
        content_path = os.path.join(temp_dir, "OEBPS", "content.opf")
        tree.write(content_path, encoding='utf-8', xml_declaration=True)
        
        self._prettify_xml(content_path)
    
    def _create_toc_ncx(self, temp_dir: str):
        """创建toc.ncx文件"""
        ncx = ET.Element('ncx', {
            'version': '2005-1',
            'xmlns': 'http://www.daisy.org/z3986/2005/ncx/'
        })
        
        # 头部
        head = ET.SubElement(ncx, 'head')
        ET.SubElement(head, 'meta', {
            'name': 'dtb:uid',
            'content': f'urn:uuid:{self._generate_uuid()}'
        })
        ET.SubElement(head, 'meta', {
            'name': 'dtb:depth',
            'content': '1'
        })
        ET.SubElement(head, 'meta', {
            'name': 'dtb:totalPageCount',
            'content': '0'
        })
        ET.SubElement(head, 'meta', {
            'name': 'dtb:maxPageNumber',
            'content': '0'
        })
        
        # 文档标题
        doc_title = ET.SubElement(ncx, 'docTitle')
        ET.SubElement(doc_title, 'text').text = self.novel_title
        
        # 导航地图
        nav_map = ET.SubElement(ncx, 'navMap')
        
        # 封面
        nav_point = ET.SubElement(nav_map, 'navPoint', {
            'id': 'cover',
            'playOrder': '1'
        })
        ET.SubElement(nav_point, 'navLabel').text = '封面'
        ET.SubElement(nav_point, 'content', {'src': 'cover.xhtml'})
        
        # 标题页
        nav_point = ET.SubElement(nav_map, 'navPoint', {
            'id': 'title',
            'playOrder': '2'
        })
        ET.SubElement(nav_point, 'navLabel').text = '标题页'
        ET.SubElement(nav_point, 'content', {'src': 'title.xhtml'})
        
        # 章节
        for i, chapter in enumerate(self.chapters):
            nav_point = ET.SubElement(nav_map, 'navPoint', {
                'id': f'chapter_{chapter["number"]}',
                'playOrder': str(i + 3)
            })
            ET.SubElement(nav_point, 'navLabel').text = f"第{chapter['number']}章 {chapter['title']}"
            ET.SubElement(nav_point, 'content', {
                'src': f'chapter_{chapter["number"]}.xhtml'
            })
        
        tree = ET.ElementTree(ncx)
        toc_path = os.path.join(temp_dir, "OEBPS", "toc.ncx")
        tree.write(toc_path, encoding='utf-8', xml_declaration=True)
        
        self._prettify_xml(toc_path)
    
    def _create_chapter_files(self, temp_dir: str):
        """创建章节XHTML文件"""
        for chapter in self.chapters:
            html = ET.Element('html', {
                'xmlns': 'http://www.w3.org/1999/xhtml',
                'xml:lang': 'zh-CN'
            })
            
            head = ET.SubElement(html, 'head')
            ET.SubElement(head, 'title').text = f"第{chapter['number']}章 {chapter['title']}"
            ET.SubElement(head, 'meta', {'charset': 'utf-8'})
            
            style = ET.SubElement(head, 'style')
            style.text = """
                body { font-family: "Microsoft YaHei", serif; margin: 2em; line-height: 1.6; }
                h1 { text-align: center; margin-bottom: 1em; }
                p { text-indent: 2em; margin: 0.5em 0; }
            """
            
            body = ET.SubElement(html, 'body')
            ET.SubElement(body, 'h1').text = f"第{chapter['number']}章 {chapter['title']}"
            
            # 处理内容格式
            content_lines = chapter['content'].split('\n')
            for line in content_lines:
                line = line.strip()
                if line:
                    p = ET.SubElement(body, 'p')
                    p.text = line
            
            tree = ET.ElementTree(html)
            chapter_path = os.path.join(temp_dir, "OEBPS", f"chapter_{chapter['number']}.xhtml")
            tree.write(chapter_path, encoding='utf-8', xml_declaration=True)
            
            self._prettify_xml(chapter_path)
    
    def _create_cover_page(self, temp_dir: str):
        """创建封面页"""
        html = ET.Element('html', {
            'xmlns': 'http://www.w3.org/1999/xhtml',
            'xml:lang': 'zh-CN'
        })
        
        head = ET.SubElement(html, 'head')
        ET.SubElement(head, 'title').text = '封面'
        ET.SubElement(head, 'meta', {'charset': 'utf-8'})
        
        style = ET.SubElement(head, 'style')
        style.text = """
            body { 
                font-family: "Microsoft YaHei", serif; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .cover-content { 
                text-align: center; 
                max-width: 600px;
                padding: 2em;
            }
            h1 { 
                font-size: 2.5em; 
                margin-bottom: 0.5em; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            h2 { 
                font-size: 1.5em; 
                margin-top: 0; 
                font-weight: normal;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
        """
        
        body = ET.SubElement(html, 'body')
        cover_div = ET.SubElement(body, 'div', {'class': 'cover-content'})
        ET.SubElement(cover_div, 'h1').text = self.novel_title
        ET.SubElement(cover_div, 'h2').text = self.author
        
        tree = ET.ElementTree(html)
        cover_path = os.path.join(temp_dir, "OEBPS", "cover.xhtml")
        tree.write(cover_path, encoding='utf-8', xml_declaration=True)
        
        self._prettify_xml(cover_path)
    
    def _create_title_page(self, temp_dir: str):
        """创建标题页"""
        html = ET.Element('html', {
            'xmlns': 'http://www.w3.org/1999/xhtml',
            'xml:lang': 'zh-CN'
        })
        
        head = ET.SubElement(html, 'head')
        ET.SubElement(head, 'title').text = '标题页'
        ET.SubElement(head, 'meta', {'charset': 'utf-8'})
        
        style = ET.SubElement(head, 'style')
        style.text = """
            body { 
                font-family: "Microsoft YaHei", serif; 
                margin: 2em; 
                line-height: 1.6; 
            }
            .title-page { 
                text-align: center; 
                margin-top: 4em;
            }
            h1 { 
                font-size: 2.5em; 
                margin-bottom: 0.5em; 
            }
            h2 { 
                font-size: 1.5em; 
                margin-bottom: 2em; 
                font-weight: normal;
            }
            .info { 
                margin-top: 3em; 
                text-align: left; 
                max-width: 400px; 
                margin-left: auto; 
                margin-right: auto;
            }
        """
        
        body = ET.SubElement(html, 'body')
        title_div = ET.SubElement(body, 'div', {'class': 'title-page'})
        ET.SubElement(title_div, 'h1').text = self.novel_title
        ET.SubElement(title_div, 'h2').text = self.author
        
        info_div = ET.SubElement(body, 'div', {'class': 'info'})
        ET.SubElement(info_div, 'p').text = f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
        ET.SubElement(info_div, 'p').text = f"总章节数: {len(self.chapters)}"
        
        tree = ET.ElementTree(html)
        title_path = os.path.join(temp_dir, "OEBPS", "title.xhtml")
        tree.write(title_path, encoding='utf-8', xml_declaration=True)
        
        self._prettify_xml(title_path)
    
    def _create_epub_archive(self, temp_dir: str, output_path: str):
        """创建EPUB压缩包"""
        import zipfile
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            # 添加mimetype文件（必须第一个且不压缩）
            mimetype_path = os.path.join(temp_dir, "mimetype")
            epub.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
            
            # 添加其他文件
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    
                    # mimetype已经单独处理，跳过
                    if arcname == "mimetype":
                        continue
                    
                    epub.write(file_path, arcname)
    
    def _prettify_xml(self, file_path: str):
        """美化XML文件格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # 解析并重新格式化
            parsed = minidom.parseString(xml_content)
            pretty_xml = parsed.toprettyxml(indent="  ", encoding='utf-8')
            
            # 移除多余的空白行
            pretty_xml_str = pretty_xml.decode('utf-8')
            pretty_xml_str = '\n'.join([line for line in pretty_xml_str.split('\n') 
                                       if line.strip()])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml_str)
                
        except Exception as e:
            logging.warning(f"美化XML失败 {file_path}: {e}")
    
    def _generate_uuid(self) -> str:
        """生成UUID"""
        import uuid
        return str(uuid.uuid4())


def export_novel_to_epub(novel_dir: str, output_path: str, novel_title: str, 
                        author: str = "AI小说生成器") -> bool:
    """
    导出整个小说为EPUB格式
    
    Args:
        novel_dir: 小说目录路径
        output_path: 输出EPUB文件路径
        novel_title: 小说标题
        author: 作者名称
        
    Returns:
        bool: 是否成功
    """
    try:
        chapters_dir = os.path.join(novel_dir, "chapters")
        if not os.path.exists(chapters_dir):
            logging.error(f"章节目录不存在: {chapters_dir}")
            return False
        
        # 创建EPUB导出器
        exporter = EPubExporter(novel_title, author)
        
        # 读取所有章节文件
        chapter_files = []
        for file in os.listdir(chapters_dir):
            if file.startswith("chapter_") and file.endswith(".txt"):
                try:
                    chapter_num = int(file.replace("chapter_", "").replace(".txt", ""))
                    chapter_files.append((chapter_num, file))
                except ValueError:
                    continue
        
        # 按章节号排序
        chapter_files.sort(key=lambda x: x[0])
        
        # 读取章节内容
        for chapter_num, filename in chapter_files:
            chapter_path = os.path.join(chapters_dir, filename)
            
            try:
                with open(chapter_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取章节标题（从内容第一行）
                lines = content.split('\n')
                title = ""
                content_start = 0
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line:
                        # 尝试从第一行提取标题（假设格式为 "第X章 标题"）
                        if line.startswith(f"第{chapter_num}章"):
                            title = line.replace(f"第{chapter_num}章", "").strip()
                            content_start = i + 1
                            break
                        else:
                            # 如果没有找到标准格式，使用第一行作为标题
                            title = line
                            content_start = i + 1
                            break
                
                # 如果没有找到标题，使用默认标题
                if not title:
                    title = f"章节{chapter_num}"
                
                # 重新组合内容（去掉标题行）
                chapter_content = '\n'.join(lines[content_start:])
                
                exporter.add_chapter(chapter_num, title, chapter_content)
                
            except Exception as e:
                logging.warning(f"读取章节失败 {chapter_path}: {e}")
                continue
        
        if not exporter.chapters:
            logging.error("没有找到有效的章节内容")
            return False
        
        # 导出EPUB
        return exporter.export_to_epub(output_path)
        
    except Exception as e:
        logging.error(f"导出小说失败: {e}")
        return False