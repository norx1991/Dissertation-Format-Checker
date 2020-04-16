def clean_tail(s):
    return s.rstrip('.').replace(',','').replace('?','').replace(':','').replace(')','').replace(':','')


refdata = open('ref.txt','r').read().split('\n')

print 'Reading reference list'
print 'Number of references',len(refdata)

refs = []

for r in refdata:
    a1, a2 = r.find('. 19'), r.find('. 20')
    l = max(a1,a2)
    if l < 0:
        print '-> No year info found in reference:', r
    else:
        if a1 > 0 and a2 > 0:
            l = min(a1,a2)
        year = r[l+2:].split()[0].rstrip('.')
    authorpart = r[:l+1]
    if ', and' in authorpart:
        authorpart = authorpart.replace(', and',',')
    elif ' and' in authorpart:
        authorpart = authorpart.replace(' and',',')
    a = authorpart.split(',')

    if len(a) == 1:
        print 'Company author:', a
        newrefitem = a[0][:-1] + ' ' + year

    elif len(a) %2 != 0:
        print '-> Wrong author format:', authorpart
        continue
    elif len(a) > 6:
        print '-> Too many authors:', authorpart
        continue
    else:
        if len(a) == 2:
            newrefitem = a[0] + ' ' + year
        if len(a) == 4:
            newrefitem = a[0] + ' and ' + a[2].lstrip(' ') + ' ' + year
        if len(a) == 6:
            newrefitem = a[0] + ' et al.' + ' ' + year

    if r'U.S. Energy Information Administration (EIA)' in newrefitem:
        newrefitem = newrefitem.replace(r'U.S. Energy Information Administration (EIA)','EIA')

    if newrefitem in refs:
        print '-> Duplicate reference item:',newrefitem, r
    refs.append(newrefitem)

print 'Reference list:',refs

hitref = dict(zip(refs,[False]*len(refs)))


print 'Analyzing dissertation content'

figures = []
mentioned_figures = []


data = open('dissertation.txt','r').read().split('\n')

for counter,l in enumerate(data):
    if 'Error! Reference source not found' in l:
        print '-> Critical: Reference source not found error'

    s = l.split()
    if len(s) >=1 and s[0] == 'Where':
        print '-> "Where" after equation',l
    if len(s) >=1 and s[0] == 'where':
        ss = data[counter-1].split()
        if len(ss) >= 2 and ss[-2] != ',':
            print '-> %s before "where"' %data[counter-1].split()[-2],l
    for i, w in enumerate(s):
        if w == 'Figure' or w == 'Table' or w == '(Figure' or w == '(Table':
            w = w.replace('(','')
            if ':' == s[i+1][-1] and s[i+1][-2].isdigit() and w + ' ' + s[i+1][:-1] not in figures:
                figures.append(w + ' ' + s[i+1][:-1])
            else:
                figurenum = clean_tail(s[i+1]).replace('-','')
                for _ in reversed(['a','b','c','d','e','f']):
                    figurenum = figurenum.rstrip(_)
                figurenum = w + ' ' + figurenum
                if figurenum in figures and figurenum not in mentioned_figures:
                    print '-> Figure referenced after the title:', figurenum,l
                if figurenum not in mentioned_figures:
                    mentioned_figures.append(figurenum)
        elif ')' in w or ';' in w:
            if ')' in w:
                index = w.find(')')
            elif ';' in w:
                index = w.find(';')

            additionalnumber = ''
            if w[index-1].isalpha():
                additionalnumber = w[index-1]
                index -= 1


            if (w[index-4:index-2] == '19' or w[index-4:index-2] == '20'):
                try:
                    a = int(w[index-4:index])
                    if 1900 < a < 2019:
                        # print a,l
                        year = str(a) + additionalnumber
                except:
                    continue

                refstring = year
                match = False
                for j in range(1,10):
                    refstring = s[i-j] + ' ' + refstring
                    refstring = refstring.replace('(','')
                    # print refstring
                    if refstring in refs:
                        match = True
                        refstring_match = refstring

                if match:
                    hitref[refstring_match] = True
                if not match:
                    print '-> Reference not found in reference list:',refstring


print 'Mentioned figures:',mentioned_figures
print '  Defined figures:',figures
for i in range(len(mentioned_figures)):
    if mentioned_figures[i] != figures[i]:
        print '-> Difference in figure reference:',mentioned_figures[i],figures[i]
        break


for k,v in hitref.items():
    if v is False:
        print '-> Reference in the list not referenced in the text:',k
