#!/usr/bin/python
import os
from boto.ec2 import connect_to_region
from boto.ec2.cloudwatch import CloudWatchConnection
from datetime import datetime, timedelta
import time
import json
import sys
import numpy as np

home="/tmp/"
conn = connect_to_region(sys.argv[1])
reservations = conn.get_all_reservations()

def cal(inst_id):
    file = home + inst_id
    main_list = []
    output = []
    config = json.loads(open(file).read())
    if config['Datapoints']:
        for point in config['Datapoints']:
         main_list.append(point["Maximum"])
        numpy_a = np.sort(np.array(main_list))
        output.append(numpy_a.mean())
        output.append(numpy_a.var())
        output.append(np.median(numpy_a))
        output.append(np.percentile(numpy_a, 25))
        output.append(np.percentile(numpy_a, 50))
        output.append(np.percentile(numpy_a, 75))
        output.append(np.percentile(numpy_a, 80))
        output.append(np.percentile(numpy_a, 90))
        output.append(np.percentile(numpy_a, 95))
        output.append(np.percentile(numpy_a, 99))
        return output
    else:
        return "NODATA"

def collect_data():
    for i in reservations:
        for inst in i.instances:
            if inst.state == "running":
                end_date=datetime.now().isoformat()
                start_date= (datetime.now() - timedelta(days=6)).isoformat()
                command= "aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value="+inst.id+" --statistics Maximum --start-time "+start_date+" --end-time "+end_date+" --period 360 >> "+home+inst.id
                os.system(command)
collect_data()

for i in reservations:
    for inst in i.instances:
        if inst.state == "running":
            p = inst.subnet_id
            e = inst.private_ip_address
            r = inst.id
            t = inst.instance_type
            try:
                name = inst.tags["Name"]
            except:
                name = "NO NAME"
            else:
                pass
            u = inst._state
            out = cal(inst.id)
            if out != "NODATA":
                print inst.id, ",",name, ",",inst.private_ip_address, ",",inst.instance_type,",",inst._state, ",",inst.subnet_id, ",", inst.spot_instance_request_id,out[0],out[1],out[2],out[3],out[4],out[5],out[6],out[7],out[8],out[9]
            else:
                print inst.id, ",",name, ",",inst.private_ip_address, ",",inst.instance_type,",",inst._state, ",",inst.subnet_id, ",", inst.spot_instance_request_id,",",out
