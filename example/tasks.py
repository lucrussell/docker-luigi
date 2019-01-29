import json
import os
from datetime import date

import luigi
import numpy as np

from example import medium
from example.medium import get_list_of_followings

TARGET_PATH = os.path.join(os.path.dirname(__file__), 'data/{date}'.format(date=date.today()))


class FetchUserList(luigi.Task):
    """
    Fetches a list of users mentioned on the front page of a publication to a JSON file.
    """
    def output(self):
        return get_local_target("user_list.json")

    def run(self):
        with self.output().open('w') as out_file:
            collection_id = get_config_value('collection_id')
            if collection_id:
                j = medium.get_author_list(collection_id)
                json.dump(j, out_file)
            else:
                raise Exception("collection_id must be specified")


class FetchUserProfile(luigi.Task):
    """
    Fetches user profiles to a JSON file.
    """
    file_number = luigi.Parameter()

    def output(self):
        return get_local_target("profiles/{}.json".format(self.file_number))

    def requires(self):
        return FetchUserList()

    # Process only one portion of the input (the input for this task contains _all_ the users)
    def run(self):
        with self.input().open("r") as in_file, self.output().open("w") as out_file:
            output_json = {
                "root": []
            }
            in_json = json.loads(in_file.read())
            lst = get_part_of_list(list(in_json.values()), self.file_number)
            for user in lst.get("root"):
                print("Fetching posts for {0}".format(user["username"]))
                user_summary = {
                    "username": user["username"],
                    "posts": medium.get_user_posts(user["userId"]),
                }
                output_json["root"].append(user_summary)
            json.dump(output_json, out_file)


class ExtractUserMetrics(luigi.Task):
    """
    Extracts some metrics from a user profile file.
    """
    file_number = luigi.Parameter()

    def output(self):
        return get_local_target("metrics/{}.json".format(self.file_number))

    def requires(self):
        return FetchUserProfile(file_number=self.file_number)

    def run(self):
        with self.input().open("r") as in_file, self.output().open('w') as out_file:
            in_json = json.loads(in_file.read())
            output_json = {
                "root": []
            }
            # Extract some details about each of the author's stories
            for user in in_json.get("root"):
                user_report = {
                    "username": user["username"],
                    "posts": []
                }
                for k, v in user["posts"].items():
                    l = v["virtuals"].get("links")
                    if l:
                        link_count = len(l)
                    else:
                        link_count = 0
                    post = {
                        "title": v.get("title"),
                        "word_count": v["virtuals"]["wordCount"],
                        "title_word_count": len(v.get("title").split()),
                        "link_count": link_count,
                        "total_clap_count": v["virtuals"]["totalClapCount"],
                        "tag_count": len(v["virtuals"]["tags"])
                    }
                    user_report["posts"].append(post)
                # Derive some metrics from the extracted story data for a user
                user_report["total_stories"] = len(user_report["posts"])
                user_report["avg_tag_count"] = calc_avg(user_report["posts"], "tag_count")
                user_report["avg_link_count"] = calc_avg(user_report["posts"], "link_count")
                user_report["avg_word_count"] = calc_avg(user_report["posts"], "word_count")
                user_report["avg_title_word_count"] = calc_avg(user_report["posts"], "tag_count")
                user_report["avg_clap_count"] = calc_avg(user_report["posts"], "total_clap_count")
                output_json["root"].append(user_report)
            json.dump(output_json, out_file)


class FetchUserFollowings(luigi.Task):
    """
    Fetches the people followed by a user.
    """
    file_number = luigi.Parameter()

    def requires(self):
        return FetchUserProfile(file_number=self.file_number)

    def output(self):
        return get_local_target("followings/{}.json".format(self.file_number))

    def run(self):
        # Process only a portion of the input
        with self.input().open("r") as in_file, self.output().open("w") as out_file:
            output_json = {
                "root": []
            }
            in_json = json.loads(in_file.read())
            lst = get_part_of_list(list(in_json.values()), self.file_number)
            if lst.get("root"):
                for user in lst.get("root")[0]:
                    f = get_list_of_followings(user.get("username"))
                    output_json["root"].append({
                        "user": user.get("username"),
                        "following_list": f
                    })
                json.dump(output_json, out_file)


class PipelineTask(luigi.WrapperTask):

    def requires(self):
        workers = int(get_config_value('workers', 1))

        base_tasks = [
            FetchUserList()
        ]
        ids = list(range(0, workers))
        fetch_user_profile = [FetchUserProfile(file_number=id) for id in ids]
        extract_user_metrics = [ExtractUserMetrics(file_number=id) for id in ids]
        fetch_user_followings = [FetchUserFollowings(file_number=id) for id in ids]

        return base_tasks + \
               fetch_user_profile + \
               extract_user_metrics + \
               fetch_user_followings

    def run(self):
        with self.output().open('w') as out_file:
            out_file.write("Successfully ran pipeline")

    def output(self):
        return get_local_target("pipeline_complete")


def get_part_files(dir_name):
    followings_dir = os.path.join(TARGET_PATH, dir_name)
    onlyfiles = [f for f in os.listdir(followings_dir) if f.endswith('.json')]
    return onlyfiles


def calc_avg(posts, metric):
    metrics = []
    for post in posts:
        metrics.append(post.get(metric))
    return np.mean(metrics)


def get_part_of_list(lst, chunk_num):
    total_chunks = int(get_config_value("workers", 1))
    chunk = np.array_split(lst, total_chunks)[chunk_num]
    res = {
        "root": []
    }
    res['root'].extend(chunk)
    return res


def get_local_target(path):
    return luigi.LocalTarget(os.path.join(TARGET_PATH, path))


def read_input_files_to_list(input_path, root_node):
    lst = []
    for t in input_path:
        with t.open('r') as in_file:
            lst.extend(json.loads(in_file.read())[root_node])
    return lst


def get_config_value(value, default=None):
    return luigi.configuration.get_config().get('example', value, default)
