import json
import logging
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)

# from requests.auth import HTTPBasicAuth
from requests import get as g
from requests import post as p
from base64 import b64encode

class Kanboard(Extension):

    def __init__(self):
        super(Kanboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        query = event.get_argument() or ""

        items.append(ExtensionResultItem(icon='images/icon.png',
                                            name='Start LaMetric timer',
                                            description='Specify how many minutes or "pause".',
                                            highlightable=False,
                                            on_enter=ExtensionCustomAction(query, keep_app_open=True)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        query = event.get_data()
        setting_host = extension.preferences['setting_host']
        setting_pass = extension.preferences['setting_pass']

        user_pass = b64encode(bytes("dev:" + setting_pass, "utf-8")).decode("ascii")

        headers = {
            'Authorization' : 'Basic %s' %  user_pass,
            'Content-Type': "application/json"
        }

        url = "http://" + setting_host + ":8080/api/v2/device/apps/com.lametric.countdown/widgets/f03ea1ae1ae5f85b390b460f55ba8061/actions"

        if query == "pause":
            payload = "{\"id\":\"countdown.pause\"}"
            r = p(url, data=payload, headers=headers)
            status = "paused"
        elif query == "resume":
            payload = "{\"id\":\"countdown.start\" }"
            r = p(url, data=payload, headers=headers)
            status = "resumed"
        else:
            payload = "{\"id\":\"countdown.reset\"}"
            r = p(url, data=payload, headers=headers)
            status = "started"
            minutes = int(query) * 60
            payload = "{\"id\":\"countdown.configure\", \"params\": { \"duration\": " + str(minutes) +  ", \"start_now\": true }}"
            r = p(url, data=payload, headers=headers)

        if r.status_code == 201:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                                            name="Timer " + status + "!",
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
            return RenderResultListAction(items)
        else:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                                            name="Error connecting to API.",
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
            return RenderResultListAction(items)

if __name__ == '__main__':
    Kanboard().run()
