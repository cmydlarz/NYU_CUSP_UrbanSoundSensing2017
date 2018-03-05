from __future__ import print_function
import sys
sys.path.append('../automation') # add the path to sonycstatus
from sonycstatus import data_pull

fqdn = 'sonycnode-b827eb0d8af7.sonyc' # 719 Broadway
how_far_back = sys.argv[1] if len(sys.argv) else 14

datas = list(data_pull.get_status_data(fqdn,
	start_date='now-{}d'.format(int(how_far_back)),
	end_data='now'
))

df = pd.DataFrame(datas)

spl = df[['level_time', 'laeq', 'lceq', 'lzeq']]

print(spl.shape)

spl.to_csv('spl_data.csv', index=False)