#!/usr/bin/python


from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option('--data_file', 
                      dest= 'in_csv_file', 
                      action='store')
    parser.add_option('--group_by',
                      dest= 'group_varss', 
                      action='store',
                      default='advertiser_id')

    parser.add_option('--delimiter', 
                      dest='in_delim_str', 
                      action='store', 
                      default=',')
    parser.add_option('--out_file',
                       dest='out_file_path',
                       action='store',
                       default='./output.csv')
    parser.add_option('--metrics',
                       dest='metric_list',
                       action='store',
                       default = 'CPM')
    parser.add_option('--out_delim',
                       dest='out_delim_str',
                       action='store',
                       default = ',')
    
    (opts, args) = parser.parse_args()


    in_csv_file = opts.in_csv_file
    in_delim_str = opts.in_delim_str
    
    group_varss = opts.group_varss.split(',')    
    metric_list = opts.metric_list.split(',')

    out_file_path = opts.out_file_path
    out_delim_str = opts.out_delim_str
    

    out_data = csv_reader(in_csv_file, in_delim_str)
    sum_vars_list, summary_dat = aggregator(out_data, group_varss)
    average_final = list_averager_call(summary_dat, sum_vars_list, metric_list=metric_list )
    final_output = dicts_flattener(average_final, group_varss)
    csv_writer(final_output, out_file_path, out_delim_str)
    

    

def csv_reader(csv_file, delim_str):
    '''create a csv reader and 
       parse each row into a dict
    '''
    import csv
    with open(csv_file,'r') as infile:
        reader = csv.DictReader(infile, delimiter = delim_str)
        dat = [row for row in reader]

    return dat


# Grouping function returns summary by group_var       
def aggregator(dict_data, groups_cols):
    #Raise exception  goup_vars NOT in the column names
    group_var = []
    for g_var in groups_cols:
        if g_var not in dict_data[0].keys():
            print 'Grouping Variable: ' + g_var +' not defined in Data'
            pass
        else:
            group_var.append(g_var)
            
    #Cast NULL value into 0 for aggregation and report warnings
    agg = {}
    sum_vars = [x for x in dict_data[0].keys() if x not in group_var]
    
    for row in dict_data:
        # insert by variable into a tuple as the key of dict
        by_var = tuple(row[var] for var in group_var)
        # value pairs as the dict of all other variables not int the group var list
        tmp_sum = {}
        for sum_var in sum_vars:
            # Casting NULL value blank string ('') into 0 for aggregation
            if row[sum_var] == '':
                tmp_sum[sum_var] = 0
            else: 
                tmp_sum[sum_var] = float(row[sum_var]) 
            
        if by_var not in agg.keys():
            agg[by_var] = tmp_sum
        elif by_var in agg.keys():
            agg[by_var] = {x: agg[by_var][x] + tmp_sum[x] for x in tmp_sum.keys()}
    print sum_vars        
    return sum_vars, agg


# Actual averaging function calculate indicators
def averager(agg_dat, num='cost', denom='imps'):
    if num == 'cost' and denom =='imps':
        Avg_type = 'CPM'
    elif num == 'clicks' and denom =='imps':
        Avg_type = 'CTR'
    elif num == 'revenue' and denom =='imps':
        Avg_type = 'RPM'
    '''
    else:
        Avg_type = 'Aggreagation'
    '''
    
    avged = {}
    for x in agg_dat.keys():
        if agg_dat[x]['imps'] == 0:
            print 'Unable to calculate ' + Avg_type + ' for:'
          #  print  str(group_varss) + ' are: \n' + str(x)
            print 'Reason: '+ denom + '= 0 \n'
            pass
        else:
            if Avg_type.upper() in ['CPM', 'RPM']:
                avged[x] = agg_dat[x][num]/agg_dat[x][denom]*1000
            elif Avg_type.upper() in ['CTR']:
                avged[x] = agg_dat[x][num]/agg_dat[x][denom]
            
    return avged

# define caller function parsing different metric into averager
def call_averager(agg_dat, sum_vars_list, metric = 'CPM'):
    
    if not metric.upper() in ['CPM', 'RPM', 'CTR']:
        print 'Unknown Metrics'
        print 'No aggreagation carried out'
        pass
    
    else: 
        if metric.upper() == 'CPM':
            num = 'cost'
            denom ='imps'
            if num in sum_vars_list and denom in sum_vars_list:
                return averager(agg_dat, num=num, denom=denom)
            else:
                print 'Warning: Variable Missing'
                pass
        elif metric.upper() == 'RPM':
            num = 'revenue'
            denom ='imps'
            if num in sum_vars_list and denom in sum_vars_list:
                return averager(agg_dat, num=num, denom=denom)
            else:
                print 'Warning: Variable Missing'
                pass
        else:
            num = 'clicks'
            denom ='imps'
            if num in sum_vars_list and denom in sum_vars_list:
                return averager(agg_dat, num=num, denom=denom)
            else:
                print 'Warning: Variable Missing'
                pass

# Master function calls call_averager and loops through all input_metrics
def list_averager_call(agg_dat, sum_vars_list, metric_list = ['CPM']):
    agged_mertics = []
    success_metircs = []
    for metric in metric_list:
        tmp_dict = call_averager(agg_dat, sum_vars_list, metric)
        if tmp_dict == None:
            print 'Above Metric Not Appliacble, Mertic input: ' + metric + '\n'
            pass
            
        else: 
            agged_mertics.append(tmp_dict)
            success_metircs.append(metric)
    #put all 'APPLIABLE' metrics into dicts
    master = {}
    for i in range(len(agged_mertics)):
        tmp = agged_mertics[i]
        mtc = success_metircs[i]
        for key in tmp.keys():
            if i == 0:
                master[key] = {mtc:tmp[key]}
            else: 
                master[key][mtc] = tmp[key]
        
    return master
    
# Flattens nested objects into a flat dict structure
def dicts_flattener(result, group_varss):    
    container = []
    for group in result.keys():
        tmp_dic = {}
        for n in range(len(group)):
            tmp_dic[group_varss[n]] = group[n]
            for inner_key in result[group].keys():
                tmp_dic[inner_key] = result[group][inner_key]
      
        container.append(tmp_dic)
    return container
    
# outout csv file
def csv_writer(data, out_path, out_delim):
    import csv
    fld_nm = data[0].keys()
    with open(out_path, 'w') as out_file:
        writer = csv.DictWriter(out_file, 
                                fieldnames = fld_nm, 
                                delimiter = out_delim)
        writer.writeheader()
        writer.writerows(data)


if __name__=='__main__':
    main()
