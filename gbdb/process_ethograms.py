

if __name__=='__main__':
    file=open('/home/jbonaiuto/Projects/bodb/gestureSED/example_clipdirectory.csv')
    ethograms=[]
    for idx,line in enumerate(file):
        if idx>0:
            cols=line.split('|')
            for i in range(8,13):
                if len(cols[i]) and not cols[i].title() in ethograms:
                    ethograms.append(cols[i].title())

    file.close()

    for idx,ethogram in enumerate(ethograms):
        print('{')
        print('    "model": "gbdb.Ethogram",')
        print('    "pk": %d,' % (idx+1))
        print('    "fields": { ')
        print('        "name": "%s"' % ethogram)
        print('    }')
        print('},')

