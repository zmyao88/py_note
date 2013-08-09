in_csv_file = '/home/zaiming/Desktop/data.csv'
in_delim_str = ','

def csv_reader(csv_file, delim_str):
    '''create a csv reader and 
       parse each row into a dict
    '''
    import csv
    with open(csv_file,'r') as infile:
        reader = csv.DictReader(infile, delimiter = delim_str)
        dat = [row for row in reader]

    return dat


# tmp = csv_reader(csv_file)    
# print tmp
           
def aggregator(dict_data, group_var):
    #Raise exception  goup_vars NOT in the column names
    #Cast NULL value into 0 for aggregation and report warnings
    agg = {}
    sum_vars = [x for x in dict_data[0].keys() if x not in group_var]
    
    for row in dict_data:
        # insert by variable into a tuple as the key of dict
        by_var = tuple(row[var] for var in group_var)
        # value pairs as the dict of all other variables not int the group var list
        tmp_sum = {sum_var: float(row[sum_var]) for sum_var in sum_vars}
        if by_var not in agg.keys():
            agg[by_var] = tmp_sum
        elif by_var in agg.keys():
            agg[by_var] = {x: agg[by_var][x] + tmp_sum[x] for x in tmp_sum.keys()}
    print sum_vars        
    return agg


out_data = csv_reader(in_csv_file, in_delim_str)
group_varss = ['campaign_id', 'advertiser_id', 'buyer_member_id']
summary_dat = aggregator(out_data, group_varss)
#print summary_dat

def averager(agg_dat):
    #Raise exception for float/'0'
   # avged = {x: agg_dat[x]['cost']/agg_dat[x]['imps']*1000 for x in agg_dat.keys()}
    avged = {}
    for x in agg_dat.keys():
        if agg_dat[x]['imps'] == 0:
            print 'f\'d up'
            pass
        else:
            avged[x] = agg_dat[x]['cost']/agg_dat[x]['imps']*1000 
            
    return avged

test = averager(summary_dat)
print test
