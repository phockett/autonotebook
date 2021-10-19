import os
import slack
from pathlib import Path
import inspect
from time import time, sleep
from datetime import datetime
from dotenv import load_dotenv

# nonstandard packages: slackclient, python-dotenv
# requires environment variable file '.env' with Slack token

class slack_client_wrapper():
    def __init__(self,token=None):
        if not token:
            # load Slack token from environment variables
            # env_path = Path('.') / '.env'
            env_path = Path(os.path.dirname(os.path.realpath(__file__))) / '.env'  # Ensure module dir (not cwd)
            load_dotenv(dotenv_path = env_path)
            self.token = os.environ['SLACK_TOKEN']
        else:
            self.token = token
            
        self.client = slack.WebClient(token=self.token)

    def post_message(self,channel,message,attachments=None,thread_ts=None,log_ts=True,log_attachments=True,log_exceptions=True):
        try:

            # post message or reply with attachments
            if attachments is not None:
                filestring = ''
                self.uploaded = []
                for attachment_idx in range(len(attachments)):
                    self.uploaded.append(self.client.files_upload(file=attachments[attachment_idx]))
                    filestring = filestring + '<' + self.uploaded[attachment_idx]['file']['permalink'] + '| >'
                    if log_attachments:
                        log_path = Path('.') / 'slack_attachment_IDs.log'
                        logf = open(log_path, 'a+')
                        logf.write(self.uploaded[attachment_idx]['file']['id'] + '\n')
                if not filestring == '':
                    if thread_ts is not None:
                        response = self.client.chat_postMessage(channel=channel, text=message + '\n' + filestring, thread_ts = thread_ts)
                    else:
                        response = self.client.chat_postMessage(channel=channel, text=message + '\n' + filestring)

            # post message or reply without attachments
            else:
                if thread_ts is not None:
                    response = self.client.chat_postMessage(channel=channel, text=message, thread_ts = thread_ts)
                else:
                    response = self.client.chat_postMessage(channel=channel, text=message)

            # log timestamp
            ts = response.data['ts']
            if log_ts:
                log_path = Path('.') / 'slack_timestamps.log'
                logf = open(log_path, 'a+')
                logf.write(str(ts) + '\n')

        # handle and log exceptions
        except Exception as e:
            timestamp = datetime.fromtimestamp(time()).strftime('%Y%m%d%H%M%S')
            print(timestamp + ': Failed to post message to Slack.')
            if log_exceptions:
                log_path = Path('.') / 'slack_exceptions.log'
                logf = open(log_path, 'a+')
                logf.write('{0}: Failed to post message to Slack\n {1}\n'.format(timestamp, str(e)))
            ts = None
        return ts

    def delete_message(self, channel, ts_list, log_exceptions=True):
        try:
            for ts in ts_list:
                self.client.chat_delete(channel=channel, ts=ts)
        # handle and log exceptions
        except Exception as e:
            timestamp = datetime.fromtimestamp(time()).strftime('%Y%m%d%H%M%S')
            print(timestamp + ': Failed to delete message from Slack.')
            if log_exceptions:
                log_path = Path('.') / 'slack_exceptions.log'
                logf = open(log_path, 'a+')
                logf.write('{0}: Failed to delete message from Slack\n {1}\n'.format(timestamp, str(e)))

    def delete_file(self, file_ID_list, log_exceptions=True):
        try:
            for file_ID in file_ID_list:
                self.client.files_delete(file=file_ID)
        # handle and log exceptions
        except Exception as e:
            timestamp = datetime.fromtimestamp(time()).strftime('%Y%m%d%H%M%S')
            print(timestamp + ': Failed to delete attachment from Slack.')
            if log_exceptions:
                log_path = Path('.') / 'slack_exceptions.log'
                logf = open(log_path, 'a+')
                logf.write('{0}: Failed to delete attachment from Slack\n {1}\n'.format(timestamp, str(e)))

def main():

    channel_ID = 'C02HP5X1F2S'
    slack_client = slack_client_wrapper()

    # # Test exception handling
    # slack_client.post_message(channel='#nonexistant-channel-2648',message='This message should fail.')

    # # Test messages and replies
    # ts = slack_client.post_message(channel=channel_ID,message='Testing longer reply interval.')
    # for k in range(4):
    #     slack_client.post_message(channel=channel_ID,message='Reply #'+str(k+1),thread_ts=ts)
    #     sleep(12)

    # # Test message with reply and attachments
    # directory_path = os.path.dirname(os.path.realpath(__file__))
    # attachment_1_path = os.path.join(directory_path, 'test_figs', '1.jpg')
    # attachment_2_path = os.path.join(directory_path, 'test_figs', '2.jpg')
    # attachment_paths_1 = [attachment_1_path, attachment_2_path]
    # ts = slack_client.post_message(channel=channel_ID,message='Testing messaging, replies, and attachments.',attachments=attachment_paths_1)
    # attachment_3_path = os.path.join(directory_path, 'test_figs', '3.jpg')
    # attachment_4_path = os.path.join(directory_path, 'test_figs', '4.jpg')
    # attachment_5_path = os.path.join(directory_path, 'test_figs', '5.dat')
    # attachment_paths_2 = [attachment_3_path, attachment_4_path, attachment_5_path]
    # slack_client.post_message(channel=channel_ID,message='This reply should have three attachments.',attachments=attachment_paths_2,thread_ts=ts)

    # # Test deleting a message
    # ts_list = ['1634281938.007600', '1634281941.008100']
    # slack_client.delete_message(channel=channel_ID,ts_list=ts_list)

    # # Test deleting an attachment
    # file_ID_list = ['F02HFUUBJTH', 'F02HPTFQYF8']
    # slack_client.delete_file(file_ID_list=file_ID_list)


if __name__ == '__main__':
    main()
