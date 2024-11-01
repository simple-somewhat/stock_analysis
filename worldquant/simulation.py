import requests
import json
from os.path import expanduser
from requests.auth import HTTPBasicAuth
from time import sleep
import datetime
import time
import logging

def sign_in():
    with open(expanduser('brain_credentials.txt')) as f:
        credentials = json.load(f)

    username, password = credentials

    sess = requests.Session()

    sess.auth = HTTPBasicAuth(username,password)

    response = sess.post('https://api.worldquantbrain.com/authentication')
    print(response.status_code)
    print(response.json())
    return sess


def get_datafields(s,searchScope,dataset_id:str='',search: str=''):
    import pandas as pd 
    instrument_type = searchScope['instrumentType']
    region = searchScope['region']
    delay = searchScope['delay']
    universe = searchScope['universe']
    if len(search) == 0:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
            f"&instrumentType={instrument_type}" + \
            f"&region={region}&delay={str(delay)}&universe={universe}&dataset.id={dataset_id}&limit=50" +\
            "&offset={x}"
        count = s.get(url_template.format(x=0)).json()['count']
        print("My cc ---" + str(count))
        print("hello my")
    else:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
            f"&instrmentType={instrument_type}" + \
            f"&region={region}&delay={str(delay)}&universe={universe}&limit=50" +\
            f"&search={search}" +\
            "&offset={x}"
        count = 100
    datafields_list = []
    for x in range(0,count,50):
        datafields = s.get(url_template.format(x=x))
        datafields_list.append(datafields.json()['results'])
    datafields_list_flat = [item for sublist in datafields_list for item in sublist]
    datafields_df = pd.DataFrame(datafields_list_flat)
    return datafields_df


def get_field(sess):
    searchScope = {'region': 'USA','delay': '1','universe':'TOP3000','instrumentType':'EQUITY'}
    model38 = get_datafields(s=sess,searchScope=searchScope,dataset_id='fundamental6')
    #print(model38)
    datafields_list_model38 =  model38['id'].values if len(model38)!=0 else []



def create_express(sess):

    alpha_list = []
  
    pvs = ["close","volume","low"]
    day_short = [10,5]
    day_long = [30,15]
    afactor = [0.1,0.2,0.3,0.4]
    markets =  ['MARKET','INDUSTRY','SUBINDUSTRY','SECTOR']

    for mk in markets:
        for pv in pvs:
            for sd in day_short:
                for ld in day_long:
                    for af in afactor:
                        simulation_data = {
                            'type' : 'REGULAR',
                            'settings': {
                                'instrumentType': 'EQUITY',
                                'region': 'USA',
                                'universe': 'TOP3000',
                                'delay': 1,
                                'decay': 0,
                                'neutralization': f"{mk}",
                                'truncation': 0.01,
                                'pasteurization': 'ON',
                                'unitHandling': 'VERIFY',
                                'nanHandling': 'OFF',
                                'language': 'FASTEXPR',
                                'visualization': False
                            },
                            #"regular": "-close/vwap"
                            'regular': f"m_minus=ts_mean({pv},{ld})-ts_mean({pv},{sd});\ndelta=(ts_max(m_minus,{sd})-m_minus)/(ts_max(m_minus,{sd})-ts_min(m_minus,{sd}));\n\
                                        PCY={af}*delta+{(1-af)}*ts_delay(delta,1);\n\
                                        signal=-close/vwap;\n\
                                        trade_when(PCY>ts_delay(PCY,1),signal,-1)"
                        }
                        alpha_list.append(simulation_data)


    # print(len(alpha_list))
    # print(alpha_list[0])
    # sim_resp = sess.post(
    #                 'https://api.worldquantbrain.com/simulations',
    #                 json=alpha_list[0],
    #             )
    # print(sim_resp.status_code)
    # print(sim_resp.headers)
    return alpha_list


def simulation(sess,alpha_list):
    logging.basicConfig(filename="simulation.log",level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
    alpha_fail_attempt_tolerance = 15
    start_time = datetime.datetime.now()

    test_alpha= 0
    pass_alpha= 0

    for alpha in alpha_list:
        pass_alpha += 1
        # if pass_alpha < test_alpha:
        #     continue
        keep_tring = True
        failure_count = 0
        all_count = 0
        while keep_tring:
            #print(alpha)
            try:
                sim_resp = sess.post(
                    'https://api.worldquantbrain.com/simulations',
                    json=alpha,
                )
                #print(sim_resp.headers)
                sim_process_url = sim_resp.headers["Location"]
                logging.info(f'位置是{sim_process_url}')
                all_count += 1
                print(f'位置是{sim_process_url}')
                keep_tring = False
                #print(sim_resp.json)
            except Exception as e:
                logging.error(f"无位置 休息15秒重试 ，错误: {str(e)}")
                print("无位置， 休息 15秒重试")
                sleep(20)
                failure_count += 1
                if failure_count >= alpha_fail_attempt_tolerance:
                    logging.error(f"sigin_in")
                    sess = sign_in()
                    failure_count = 0
                    sim_resp = sess.post(
                    'https://api.worldquantbrain.com/simulations',
                    json=alpha,
                    )  # 多尝试一次
                    logging.error(f"尝试次数过多,无法获取alpha位置,我们将移动到下一个alpha {alpha['regular']}")
                    print(f"尝试次数过多,无法获取alpha位置,我们将移动到下一个alpha {alpha['regular']}")
                    break



if __name__ == '__main__':
    sess = sign_in()
    alpha_list = create_express(sess)
    simulation(sess,alpha_list)