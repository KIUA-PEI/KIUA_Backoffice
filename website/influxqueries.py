from influxdb import InfluxDBClient

#Given a table name generate all qauerys 
def get_querys(tname):
    #Store tags
    tags = []
    #Store tags and it's respective values
    values = []
    #Store fields
    fields = []
    #Store query results

    #Open Client
    client = InfluxDBClient(host='40.68.96.164', port=8086, username="peikpis", password="peikpis_2021")

    #Switch to Metrics database
    client.switch_database('Metrics')

    #Obtain tags
    query = client.query("SHOW TAG KEYS FROM \""+tname+"\"")
    for taglist in query:
        for tag in taglist: 
            tags.append(tag['tagKey'])
    #print(tags)

    #Obtain tag values
    for tag in tags:
        query = client.query("SHOW TAG VALUES FROM \""+tname+"\" WITH KEY="+tag)
        for vlist in query:
            tmp = []
            for value in vlist:
                tmp.append(value['value'])
            values.append((tag, tmp))
    #print(values)

    #Obtain fields
    query = client.query("SHOW FIELD KEYS FROM \""+tname+"\"")
    for flist in query:
        for field in flist:
            fields.append(field['fieldKey'])
    #print(fields)

    result = []
    #Build querys
    for field in fields:
        for tag in values:
            for value in tag[1]:
                result.append(("SELECT "+field+" AS "+"".join(str(value).split())+str(field)+" FROM "+tname+" WHERE "+tag[0]+" = '"+value+"';", field+" from "+value))

    #for r in result:
        #print(r)
    #Close client 
    client.close()
    return result

#print("\n\n\n")
#print(get_querys('parking'))
#print("\n--------\n")
#get_querys('wifiusr')
