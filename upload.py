import random
import time
from PyQt5.QtCore import *
from requests import Session
import os
import glob
import urllib


class uploadProfiles(QObject):

    sign_exit = pyqtSignal()
    sign_msg = pyqtSignal(int, int, str)

    def __init__(self, listAccounts, timeStart, timeEnd, limit, rmHashtag, rmTitle):
        super().__init__()
        self.listAccounts = listAccounts
        self.timeStart = timeStart
        self.timeEnd= timeEnd
        self.limit = limit
        self.rmHashtag = rmHashtag
        self.rmTitle = rmTitle

        
    def run(self):
        for acc in self.listAccounts:
            cookie = acc['cookie']
            token = acc['token']
            userId = acc['userId']
            userAgent = acc['userAgent']
            video_folder = acc['video_folder']
            row = acc['row']
            self.upload(video_folder=video_folder, token = token, cookie= cookie, userAgent=userAgent, userId=userId, row=row)
        self.sign_exit.emit()
    
    def customDesc(self, video_path):
        f_name, f_ext = os.path.splitext(video_path.split('\\')[-1])
        desc = f_name
        if self.rmHashtag:
            desc = " ".join([x for x in f_name.split(' ') if '#' not in x]) 
        if self.rmTitle:
            desc = ''
        return desc



    def upload(self, video_folder, token, cookie, userId, userAgent, row):
        self.sign_msg.emit(1, int(row), 'Starting ...')
        count = 0
        videos = self.checkVideo(video_folder)
        # print(videos)
        if videos:
            for video in videos:
                self.sign_msg.emit(1, int(row), 'Uploading video %s...' % str(count+1))
                videoLen = self.get_length(video)
                if videoLen < 60:
                    desc = self.customDesc(video)
                    # desc = urllib.parse.quote_plus(desc)
                    result = self.runUpload(cookie=cookie, token=token, userAgent=userAgent, userId=userId, desc=desc, file_path=video)
                    if result:
                        os.remove(video)
                        count += 1
                        if count == self.limit:
                            break
                sleepTime = random.randint(self.timeStart, self.timeEnd)
                self.sign_msg.emit(1, int(row), 'Sleep %ss ...' % str(sleepTime))
                time.sleep(sleepTime)
        self.sign_msg.emit(1, int(row), 'Done')


    def runUpload(self, cookie, token, userAgent, userId, file_path, desc):
        # create session 
        self.sign_msg.emit(2, 0, '>> Create Session Upload <<')
        fileSize = os.path.getsize(file_path)
        _request = Session()
        _request.headers.update({
            'Cookie': cookie,
            'User-Agent': userAgent
        })

        # start upload 
        start_url = f'https://graph-video.facebook.com/v14.0/{userId}/videos'
        data = {
            'access_token': token,
            'upload_phase': "start",
            'file_size': fileSize
        }

        try:
            response = _request.post(start_url, data=data)
            dl = response.json()
            video_id = dl['video_id']
            upload_session_id = dl['upload_session_id']
            start_offset = dl['start_offset']
            end_offset = dl['end_offset']
        except:
            print(dl)
            self.sign_msg.emit(2, 1, '>> Create Session Fail <<')
            return False
        self.sign_msg.emit(2, 0, '>> Transfer Upload <<')
        # transfer upload
        setFlag = 0
        transfer_url = f'https://graph-video.facebook.com/v14.0/{userId}/videos'
        setFlag = 0
        _start_offset = int(start_offset)
        _end_offset = int(end_offset)
        filepath = file_path
        file_size = os.path.getsize(filepath)
        
        f = open(file_path, 'rb')

        while(_start_offset != _end_offset):
            f.seek(_start_offset)
            chunk = f.read(_end_offset - _start_offset)
            data = {
                'access_token': token,
                'upload_phase': 'transfer',
                'start_offset': _start_offset,
                'upload_session_id': upload_session_id,
            }
            files = {
                'video_file_chunk': (
                    os.path.basename(file_path),
                    chunk,
                    
                )
            }
            
            try:
                response = _request.post(transfer_url, data=data, files=files)
                dl = response.json()
                _start_offset = int(dl['start_offset'])
                _end_offset = int(dl['end_offset'])
            except:
                print(dl)
                setFlag = 1
                self.sign_msg.emit(2, 1, '>> Transfer Fail <<')
                break
        f.close()

        if setFlag == 1:
            return False
        self.sign_msg.emit(2, 0, '>> Public Reels <<')
        # public reels 
        public_url =  'https://graph.facebook.com/graphql'
        _request.headers.update({
            "User-Agent":"[FBAN/FB4A;FBAV/357.0.0.23.115;FBBV/"+userId+";FBDM/{density=2.625,width=1080,height=2220};FBLC/vi_Qaau_VN;FBRV/"+userId+";FBCR/;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-G965F;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]",
            "Authorization": "OAuth "+token,
        })
        e = self.getLoggingInteractionKey1()
        data = {
        'method':"post",
        'locate':"vi_VN",
        'pretty':"false",
        'format':"json",
        'client_doc_id':"91093790612417117157594582916",
        'variables':'{"image_low_height":2048,"image_medium_width":540,"automatic_photo_captioning_enabled":"false","angora_attachment_profile_image_size":105,"poll_facepile_size":105,"default_image_scale":"3","image_high_height":2048,"image_large_aspect_height":565,"image_large_aspect_width":1080,"reading_attachment_profile_image_width":236,"image_low_width":360,"media_type":"image/jpeg","input":{"video_start_time_ms":0,"producer_supported_features":["LIGHTWEIGHT_REPLY"],"video_editing_metadata":{"video_editing_data":[{"video_id":"'+video_id+'","original_length":23067,"has_effect":false,"sticker_count":0,"text_count":0,"is_muted":false,"has_doodle":false}]},"tag_expansion_metadata":{"tag_expansion_ids":[]},"place_attachment_setting":"SHOW_ATTACHMENT","past_time":{"time_since_original_post":3},"navigation_data":{"attribution_id_v2":"FbShortsViewerActivity,fb_shorts_viewer_activity,,1646195166.303,26084367,,;FbShortsShareSheetFragment,,,1646195161.54,109378498,,;InspirationCameraActivity,reels_creation,,1646195059.991,32390223,,;FeedFiltersFragment,native_newsfeed,cold_start,1646195049.687,214171736,4748854339,"},"message":{"text":"'+desc+'"},"logging":{"composer_session_id":"'+e+'"},"camera_post_context":{"source":"CAMERA_SYSTEM","platform":"FACEBOOK","deduplication_id":"'+e+'"},"connection_class":"EXCELLENT","is_welcome_to_group_post":false,"is_throwback_post":"NOT_THROWBACK_POST","is_boost_intended":false,"reshare_original_post":"SHARE_LINK_ONLY","idempotence_token":"FEED_'+e+'","inspiration_prompts":[{"prompt_type":"MANUAL","prompt_tracking_string":"0","prompt_id":"1752514608329267"}],"is_tags_user_selected":false,"composer_entry_picker":"camera","fb_shorts":{"remix_status":"NOT_APPLICABLE","is_fb_short":true,"dsc_deal_id":null},"composer_type":"status","composer_source_surface":"short_form_video","implicit_with_tags_ids":[],"composer_entry_point":"tap_creation_button_in_short_form_video_composer_creation_bar","client_mutation_id":"'+self.getLoggingInteractionKey()+'","audiences":[{"undirected":{"privacy":{"tag_expansion_state":"UNSPECIFIED","deny":[],"base_state":"EVERYONE","allow":[]}}}],"source":"MOBILE","actor_id":"'+userId+'","audiences_is_complete":true,"attachments":[{"video":{"unified_stories_media_source":"CAMERA_ROLL","capture_mode":"NORMAL","story_media_audio_data":{"raw_media_type":"VIDEO"},"notify_when_processed":false,"ml_media_tracking_data":{"media_tracking_id":"6'+self.makeNumber(8)+'"},"id":"'+video_id+'"}}],"action_timestamp":'+self.getSpinT()+',"composer_session_events_log":{"number_of_keystrokes":0,"number_of_copy_pastes":0,"composition_duration":0},"looking_for_players":{"selected_game":""},"is_group_linking_post":false},"size_style":"contain-fit","nt_context":{"using_white_navbar":true,"pixel_ratio":3,"styles_id":"d82700195bed991a354f509243d7d19e","bloks_version":"f51c9d91e91f6e9c27f6f24b876c17457bb277986c33ecd69f5544a9cb39cc85"},"image_high_width":1080,"poll_voters_count":5,"action_location":"feed","reading_attachment_profile_image_height":354,"include_image_ranges":true,"profile_image_size":105,"enable_comment_shares":true,"profile_pic_media_type":"image/x-auto","angora_attachment_cover_image_size":1260,"question_poll_count":100,"image_medium_height":2048,"enable_comment_reactions_icons":true,"enable_ranked_replies":"true","fetch_fbc_header":true,"enable_comment_replies_most_recent":"true","fetch_whatsapp_ad_context":true,"enable_comment_reactions":true,"bloks_version":"f51c9d91e91f6e9c27f6f24b876c17457bb277986c33ecd69f5544a9cb39cc85","max_comment_replies":3}',
        'fb_api_analytics_tags':'["nav_attribution_id={\\"0\\":{\\"bookmark_id\\":\\"4748854339\\",\\"session\\":\\"4ef73\\",\\"subsession\\":1,\\"timestamp\\":\\"'+self.getSpinT()+'\\",\\"tap_point\\":\\"cold_start\\",\\"most_recent_tap_point\\":\\"cold_start\\",\\"bookmark_type_name\\":null,\\"fallback\\":false,\\"badging\\":{\\"badge_count\\":0,\\"badge_type\\":\\"num\\"}}}","visitation_id=4748854339:4ef73:1:1646195049.686","surface_hierarchy=FbShortsViewerFragment,null,null;FbShortsViewerActivity,fb_shorts_viewer_activity,null;NewsFeedFragment,native_newsfeed,null;FeedFiltersFragment,native_newsfeed,null;FbChromeFragment,null,cold_start;FbMainTabActivity,unknown,null","session_id=UFS-26716aa1-2000-4b3e-81c0-0c2ebad94832-fg-2","GraphServices"]',
        'fb_api_req_friendly_name':"ComposerStoryCreateMutation",
        'fb_api_caller_class':"graphservice",
        'server_timestamps':"true"

        }

        try:
            response = _request.post(public_url, json=data) 
            dl = response.json()
            store_id = dl['data']['story_create']['story_id']
            self.sign_msg.emit(2, 2, f'<< ID {str(userId)} Uploaded StoryId {str(store_id)} >>')
            return store_id
        except:
            print(dl)
            self.sign_msg.emit(2, 1, '>> Public Fail <<')
            return False
        

    def checkVideo(self, path):
        data = glob.glob(path+'/*.mp4', recursive=True)
        if len(data) > 0:
            return data
        else:
            return []

    def get_length(self, filename):
        import cv2
        video = cv2.VideoCapture(filename)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS) 
        duration = frame_count / fps
        return int(duration)


    def getLoggingInteractionKey1(self):
        import random
        t = [x for x in '"xxxxxxxx-xxxx-1xxx-yxxx-xxxxxxxxxxxx"']	
        for e in range(0, len(t)):
            n = random.randint(0, 16)
            r = t[e]
            if ('1' != r and '-' != r):
                i = n if r == 'x' else 3&n|10
                t[e] = hex(i).replace('0x', '')
        return "".join(t)

    def getLoggingInteractionKey(self):
        import random
        t = [x for x in '"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"']	
        for e in range(0, len(t)):
            n = random.randint(0, 16)
            r = t[e]
            if ('4' != r and '-' != r):
                i = n if r == 'x' else 3&n|10
                t[e] = hex(i).replace('0x', '')
        return "".join(t)

    def getSpinT(self):
        import time 
        return str(time.time()).split(".")[0]

    def makeNumber(self,t):
        import random
        e = ''
        n = '0123456789'
        r = len(n)-1
        for x in range(int(t)):
            e += n[random.randint(0,r)]
        return e


class multiUploadProfiles(QThread):

    sign_exit = pyqtSignal()
    sign_msg = pyqtSignal(int, int, str)

    def __init__(self, x, thread_count, listAccounts, timeStart, timeEnd, limit, rmHashtag, rmTitle):
        QThread.__init__(self)
        self.listAccounts = listAccounts
        self.timeStart = timeStart
        self.timeEnd= timeEnd
        self.limit = limit
        self.rmHashtag = rmHashtag
        self.rmTitle = rmTitle
        self.x = x
        self.thread_count = thread_count

        
    def run(self):
        for y in range(self.x, len(self.listAccounts), self.thread_count):
            acc = self.listAccounts[y]
            cookie = acc['cookie']
            token = acc['token']
            userId = acc['userId']
            userAgent = acc['userAgent']
            video_folder = acc['video_folder']
            row = acc['row']
            self.upload(video_folder=video_folder, token = token, cookie= cookie, userAgent=userAgent, userId=userId, row=row)
        # self.sign_exit.emit()
    
    def customDesc(self, video_path):
        f_name, f_ext = os.path.splitext(video_path.split('\\')[-1])
        desc = f_name
        if self.rmHashtag:
            desc = " ".join([x for x in f_name.split(' ') if '#' not in x]) 
        if self.rmTitle:
            desc = ''
        return desc



    def upload(self, video_folder, token, cookie, userId, userAgent, row):
        self.sign_msg.emit(1, int(row), 'Starting ...')
        count = 0
        videos = self.checkVideo(video_folder)
        # print(videos)
        if videos:
            for video in videos:
                self.sign_msg.emit(1, int(row), 'Uploading video %s...' % str(count+1))
                videoLen = self.get_length(video)
                if videoLen < 60:
                    desc = self.customDesc(video)
                    # desc = urllib.parse.quote_plus(desc)
                    result = self.runUpload(cookie=cookie, token=token, userAgent=userAgent, userId=userId, desc=desc, file_path=video)
                    if result:
                        os.remove(video)
                        count += 1
                        if count == self.limit:
                            break
                    sleepTime = random.randint(self.timeStart, self.timeEnd)
                    self.sign_msg.emit(1, int(row), 'Sleep %ss ...' % str(sleepTime))
                    time.sleep(sleepTime)
                else:
                    self.sign_msg.emit(2, 1, f'{str(userId)}: Video length is more than 60 seconds')
        self.sign_msg.emit(1, int(row), 'Done')


    def runUpload(self, cookie, token, userAgent, userId, file_path, desc):
        # create session 
        self.sign_msg.emit(2, 0, f'{str(userId)}: Create Session Upload ')
        fileSize = os.path.getsize(file_path)
        _request = Session()
        _request.headers.update({
            'Cookie': cookie,
            'User-Agent': userAgent
        })

        # start upload 
        start_url = f'https://graph-video.facebook.com/v14.0/{userId}/videos'
        data = {
            'access_token': token,
            'upload_phase': "start",
            'file_size': fileSize
        }

        try:
            response = _request.post(start_url, data=data)
            dl = response.json()
            video_id = dl['video_id']
            upload_session_id = dl['upload_session_id']
            start_offset = dl['start_offset']
            end_offset = dl['end_offset']
        except:
            print(dl)
            self.sign_msg.emit(2, 1, f'{str(userId)}: Create Session Fail')
            return False
        self.sign_msg.emit(2, 0, f'{str(userId)}: Transfer Upload')
        # transfer upload
        setFlag = 0
        transfer_url = f'https://graph-video.facebook.com/v14.0/{userId}/videos'
        setFlag = 0
        _start_offset = int(start_offset)
        _end_offset = int(end_offset)
        filepath = file_path
        file_size = os.path.getsize(filepath)
        
        f = open(file_path, 'rb')

        while(_start_offset != _end_offset):
            f.seek(_start_offset)
            chunk = f.read(_end_offset - _start_offset)
            data = {
                'access_token': token,
                'upload_phase': 'transfer',
                'start_offset': _start_offset,
                'upload_session_id': upload_session_id,
            }
            files = {
                'video_file_chunk': (
                    os.path.basename(file_path),
                    chunk,
                    
                )
            }
            
            try:
                response = _request.post(transfer_url, data=data, files=files)
                dl = response.json()
                _start_offset = int(dl['start_offset'])
                _end_offset = int(dl['end_offset'])
            except:
                print(dl)
                setFlag = 1
                self.sign_msg.emit(2, 1, f'{str(userId)}: Transfer Fail')
                break
        f.close()

        if setFlag == 1:
            return False
        self.sign_msg.emit(2, 0, f'{str(userId)}: Public Reels ')
        # public reels 
        public_url =  'https://graph.facebook.com/graphql'
        _request.headers.update({
            "User-Agent":"[FBAN/FB4A;FBAV/357.0.0.23.115;FBBV/"+userId+";FBDM/{density=2.625,width=1080,height=2220};FBLC/vi_Qaau_VN;FBRV/"+userId+";FBCR/;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-G965F;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]",
            "Authorization": "OAuth "+token,
        })
        e = self.getLoggingInteractionKey1()
        data = {
        'method':"post",
        'locate':"vi_VN",
        'pretty':"false",
        'format':"json",
        'client_doc_id':"91093790612417117157594582916",
        'variables':'{"image_low_height":2048,"image_medium_width":540,"automatic_photo_captioning_enabled":"false","angora_attachment_profile_image_size":105,"poll_facepile_size":105,"default_image_scale":"3","image_high_height":2048,"image_large_aspect_height":565,"image_large_aspect_width":1080,"reading_attachment_profile_image_width":236,"image_low_width":360,"media_type":"image/jpeg","input":{"video_start_time_ms":0,"producer_supported_features":["LIGHTWEIGHT_REPLY"],"video_editing_metadata":{"video_editing_data":[{"video_id":"'+video_id+'","original_length":23067,"has_effect":false,"sticker_count":0,"text_count":0,"is_muted":false,"has_doodle":false}]},"tag_expansion_metadata":{"tag_expansion_ids":[]},"place_attachment_setting":"SHOW_ATTACHMENT","past_time":{"time_since_original_post":3},"navigation_data":{"attribution_id_v2":"FbShortsViewerActivity,fb_shorts_viewer_activity,,1646195166.303,26084367,,;FbShortsShareSheetFragment,,,1646195161.54,109378498,,;InspirationCameraActivity,reels_creation,,1646195059.991,32390223,,;FeedFiltersFragment,native_newsfeed,cold_start,1646195049.687,214171736,4748854339,"},"message":{"text":"'+desc+'"},"logging":{"composer_session_id":"'+e+'"},"camera_post_context":{"source":"CAMERA_SYSTEM","platform":"FACEBOOK","deduplication_id":"'+e+'"},"connection_class":"EXCELLENT","is_welcome_to_group_post":false,"is_throwback_post":"NOT_THROWBACK_POST","is_boost_intended":false,"reshare_original_post":"SHARE_LINK_ONLY","idempotence_token":"FEED_'+e+'","inspiration_prompts":[{"prompt_type":"MANUAL","prompt_tracking_string":"0","prompt_id":"1752514608329267"}],"is_tags_user_selected":false,"composer_entry_picker":"camera","fb_shorts":{"remix_status":"NOT_APPLICABLE","is_fb_short":true,"dsc_deal_id":null},"composer_type":"status","composer_source_surface":"short_form_video","implicit_with_tags_ids":[],"composer_entry_point":"tap_creation_button_in_short_form_video_composer_creation_bar","client_mutation_id":"'+self.getLoggingInteractionKey()+'","audiences":[{"undirected":{"privacy":{"tag_expansion_state":"UNSPECIFIED","deny":[],"base_state":"EVERYONE","allow":[]}}}],"source":"MOBILE","actor_id":"'+userId+'","audiences_is_complete":true,"attachments":[{"video":{"unified_stories_media_source":"CAMERA_ROLL","capture_mode":"NORMAL","story_media_audio_data":{"raw_media_type":"VIDEO"},"notify_when_processed":false,"ml_media_tracking_data":{"media_tracking_id":"6'+self.makeNumber(8)+'"},"id":"'+video_id+'"}}],"action_timestamp":'+self.getSpinT()+',"composer_session_events_log":{"number_of_keystrokes":0,"number_of_copy_pastes":0,"composition_duration":0},"looking_for_players":{"selected_game":""},"is_group_linking_post":false},"size_style":"contain-fit","nt_context":{"using_white_navbar":true,"pixel_ratio":3,"styles_id":"d82700195bed991a354f509243d7d19e","bloks_version":"f51c9d91e91f6e9c27f6f24b876c17457bb277986c33ecd69f5544a9cb39cc85"},"image_high_width":1080,"poll_voters_count":5,"action_location":"feed","reading_attachment_profile_image_height":354,"include_image_ranges":true,"profile_image_size":105,"enable_comment_shares":true,"profile_pic_media_type":"image/x-auto","angora_attachment_cover_image_size":1260,"question_poll_count":100,"image_medium_height":2048,"enable_comment_reactions_icons":true,"enable_ranked_replies":"true","fetch_fbc_header":true,"enable_comment_replies_most_recent":"true","fetch_whatsapp_ad_context":true,"enable_comment_reactions":true,"bloks_version":"f51c9d91e91f6e9c27f6f24b876c17457bb277986c33ecd69f5544a9cb39cc85","max_comment_replies":3}',
        'fb_api_analytics_tags':'["nav_attribution_id={\\"0\\":{\\"bookmark_id\\":\\"4748854339\\",\\"session\\":\\"4ef73\\",\\"subsession\\":1,\\"timestamp\\":\\"'+self.getSpinT()+'\\",\\"tap_point\\":\\"cold_start\\",\\"most_recent_tap_point\\":\\"cold_start\\",\\"bookmark_type_name\\":null,\\"fallback\\":false,\\"badging\\":{\\"badge_count\\":0,\\"badge_type\\":\\"num\\"}}}","visitation_id=4748854339:4ef73:1:1646195049.686","surface_hierarchy=FbShortsViewerFragment,null,null;FbShortsViewerActivity,fb_shorts_viewer_activity,null;NewsFeedFragment,native_newsfeed,null;FeedFiltersFragment,native_newsfeed,null;FbChromeFragment,null,cold_start;FbMainTabActivity,unknown,null","session_id=UFS-26716aa1-2000-4b3e-81c0-0c2ebad94832-fg-2","GraphServices"]',
        'fb_api_req_friendly_name':"ComposerStoryCreateMutation",
        'fb_api_caller_class':"graphservice",
        'server_timestamps':"true"

        }

        try:
            response = _request.post(public_url, json=data) 
            dl = response.json()
            store_id = dl['data']['story_create']['story_id']
            self.sign_msg.emit(2, 2, f'{str(userId)}: Uploaded StoryId {str(store_id)} ')
            return store_id
        except:
            print(dl)
            self.sign_msg.emit(2, 1, f'{str(userId)}: Public Fail ')
            return False
        

    def checkVideo(self, path):
        data = glob.glob(path+'/*.mp4', recursive=True)
        if len(data) > 0:
            return data
        else:
            return []

    def get_length(self, filename):
        import cv2
        video = cv2.VideoCapture(filename)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS) 
        duration = frame_count / fps
        return int(duration)


    def getLoggingInteractionKey1(self):
        import random
        t = [x for x in '"xxxxxxxx-xxxx-1xxx-yxxx-xxxxxxxxxxxx"']	
        for e in range(0, len(t)):
            n = random.randint(0, 16)
            r = t[e]
            if ('1' != r and '-' != r):
                i = n if r == 'x' else 3&n|10
                t[e] = hex(i).replace('0x', '')
        return "".join(t)

    def getLoggingInteractionKey(self):
        import random
        t = [x for x in '"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"']	
        for e in range(0, len(t)):
            n = random.randint(0, 16)
            r = t[e]
            if ('4' != r and '-' != r):
                i = n if r == 'x' else 3&n|10
                t[e] = hex(i).replace('0x', '')
        return "".join(t)

    def getSpinT(self):
        import time 
        return str(time.time()).split(".")[0]

    def makeNumber(self,t):
        import random
        e = ''
        n = '0123456789'
        r = len(n)-1
        for x in range(int(t)):
            e += n[random.randint(0,r)]
        return e