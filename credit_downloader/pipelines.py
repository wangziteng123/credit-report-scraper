# -*- coding: utf-8 -*-

import logging
import os
from scrapy.pipelines.files import FilesPipeline
from credit_downloader import settings


class CreditDownloaderPipeline(FilesPipeline):
    logger = logging.getLogger()
    storage = os.path.normpath(settings.FILES_STORE)

    # Overriding
    def item_completed(self, results, item, info):
        ''' 把下载文件归类, 并更新 status. 文件存在
         credit_downloader/downloads/<source>/<type>/<filename> '''

        # move file
        source, category = item['source'], item['category']
        for result in [x for ok, x in results if ok]:
            target_path = self.get_target_path(source, category, result)
            dirname = os.path.dirname(target_path)
            tmp_path = os.path.join(self.get_project_dirname(), self.storage, result['path'])

            result['path'] = target_path
            item['files'].append(result)

            os.makedirs(dirname, exist_ok=True)

            try:
                os.rename(tmp_path, target_path)
            except:
                self.logger.error('Unable to move files from %s to %s' , tmp_path, target_path)
                item['status'] = 'move_failed'

        # Update Item json to save download status and paths
        if self.FILES_RESULT_FIELD in item.fields:
            item[self.FILES_RESULT_FIELD] = [x for ok, x in results if ok]
            if item['files'] == []:
                if item['status'] not in ['move_failed', 'missing']:
                    item['status'] = 'download_failed'
            else:
                if item['status'] not in ['move_failed', 'download_failed', 'missing']:
                    item['status'] = 'success'
                item.pop('file_urls', None)
        return item

    def get_target_path(self, src, cat, result):
        name = result['url'].split('/')[-1]
        return os.path.join(self.get_project_dirname(), self.storage, src, cat, name)

    def get_project_dirname(self):
        '''Get the absolute path to project.'''
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
