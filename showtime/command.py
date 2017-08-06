from ratelimit import rate_limited
from cmd2 import Cmd
from tvmaze.api import Api
from database import Database
from output import Output

class Showtime(Cmd):

    prompt = '(showtime) '

    def __init__(self, api, db):
        Cmd.__init__(self)
        self.api = api
        self.db = db
        self.output = Output(self.poutput)

    def do_search(self, query):
        'Search shows [search Breaking Bad]'
        search_result = api.search.shows(query)
        search_result_tabe = self.output.format_search_results(search_result)
        self.output.poutput(search_result_tabe)

    def do_follow(self, show_id):
        'Follow show by id [follow 3]'
        show = api.show.get(show_id)
        self.db.add(show)
        episodes = self._get_episodes(int(show.id))
        self.db.sync_episodes(show.id, episodes);
        self.output.poutput('Added show: ({id}) {name} - {permiered}'.format(
                id=show.id, name=show.name, permiered=show.premiered))

    def do_episodes(self, show_id):
        show = db.get_show(int(show_id))
        episodes = db.get_episodes(int(show_id))

        episodes_tabe = self.output.format_episodes(show, episodes)
        self.output.poutput(episodes_tabe)

    @rate_limited(20, 10)
    def _get_episodes(self, show_id: int):
        return self.api.show.episodes(show_id)

    def do_sync(self, update):
        self.pfeedback('Syncing shows...')
        shows = self.db.get_active_shows() if update else self.db.get_shows()
        for show in shows:
            self.output.poutput('({id}) {name} - {permiered}'.format(
                id=show['id'], name=show['name'], permiered=show['permiered']))
            episodes = self._get_episodes(int(show['id']))
            self.db.sync_episodes(show['id'], episodes);
        self.pfeedback('Done')

    def do_watched(self, episode_id):
        self.db.mark_watched(int(episode_id))

    def do_unwatched(self, line):
        episodes = self.db.get_unwatched()
        episodes_tabe = self.output.format_unwatched(episodes)
        self.output.poutput(episodes_tabe)

if __name__ == '__main__':
    api = Api()
    db = Database('/tmp/temp.json')
    Showtime(api, db).cmdloop()
