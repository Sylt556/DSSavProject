import pandas as pd
from virus_total_apis import PublicApi as VirusTotalPublicApi


def virustotal(hash_value):
    API_KEY = '64e1826d585aece9138dfbc3027fbe62bc7d808d5c4dc6dfb4325e64f7c43f5a'
    vt = VirusTotalPublicApi(API_KEY)
    response = vt.get_file_report(hash_value)
    return response


def virustotal_check(dict_hashes):
    for key in dict_hashes:
        filename = key
        file_hash = dict_hashes[key]
        error = False
        try:
            results = virustotal(file_hash)['results']
            positive = results['positives']
            total = results['total']
            final_results = "{}/{}".format(positive, total)
        except ValueError:
            final_results = "Not_Found"
            error = True
        except KeyError:
            final_results = "RATE_LIMITED"
            error = True
        if not error:
            return "File {} of Hash {} was deemed a virus by {} antiviruses.".format(filename, file_hash, final_results)
        else:
            return "ERROR COMMUNICATING WITH API SERVER"
