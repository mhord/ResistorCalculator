import argparse
import os.path

E96 = [10.0,	10.2,	10.5,	10.7,	11.0,	11.3,	11.5,	11.8,	12.1,	12.4,	12.7,	13.0,
13.3,	13.7,	14.0,	14.3,	14.7,	15.0,	15.4,	15.8,	16.2,	16.5,	16.9,	17.4,
17.8,	18.2,	18.7,	19.1,	19.6,	20.0,	20.5,	21.0,	21.5,	22.1,	22.6,	23.2,
23.7,	24.3,	24.9,	25.5,	26.1,	26.7,	27.4,	28.0,	28.7,	29.4,	30.1,	30.9,
31.6,	32.4,	33.2,	34.0,	34.8,	35.7,	36.5,	37.4,	38.3,	39.2,	40.2,	41.2,
42.2,	43.2,	44.2,	45.3,	46.4,	47.5,	48.7,	49.9,	51.1,	52.3,	53.6,	54.9,
56.2,	57.6,	59.0,	60.4,	61.9,	63.4,	64.9,	66.5,	68.1,	69.8,	71.5,	73.2,
75.0,	76.8,	78.7,	80.6,	82.5,	84.5,	86.6,	88.7,	90.9,	93.1,	95.3,	97.6]

E24 = [1.0,	1.1,	1.2,	1.3,	1.5,	1.6,	1.8,	2.0,	2.2,	2.4,	2.7,	3.0,
3.3,	3.6,	3.9,	4.3,	4.7,	5.1,	5.6,	6.2,	6.8,	7.5,	8.2,	9.1]

Stack = [[0,0,0,1]]

def r_calc(Vin, Vout, r_list = E96,  r1_mult = 1, r2_mult = 1, o_list = Stack):
    R1 = 0
    R2 = 0
    for i in r_list:
        R1 = i*r1_mult
        for j in r_list:
            R2 = j*r2_mult
            Vtry = (Vin*R2)/(R1 + R2)
            Tryerror = abs((Vtry-Vout)/Vout)
            Try = [R1, R2, Vtry, Tryerror]
            Stack.append(Try)
    return o_list

def vout_err(Vin, Vout, R1Val, R2Val, tol):
    Tryerror = [0,0]
    Vtry = (Vin*(1-tol)*R2Val)/((1+tol)*R1Val + (1-tol)*R2Val)
    Tryerror[0] = (Vtry-Vout)/Vout
    Vtry = (Vin*(1+tol)*R2Val)/((1-tol)*R1Val + (1+tol)*R2Val)
    Tryerror[1] = (Vtry-Vout)/Vout
    return Tryerror

parser = argparse.ArgumentParser(description='Calculate real resistor values to form \
                                  a resistor divider.')
parser.add_argument('Vin', default = 5, type = float, help = "Input voltage.")
parser.add_argument('Vout', default = 3.3, type = float, help = "Desired output voltage.")
parser.add_argument('-f', action = 'store_true', help = "Use input file.") 
parser.add_argument('infile', nargs='?', type = argparse.FileType('r'))
parser.add_argument('-b', action = 'store_true', default = False, help = "Broaden search to 10x normal range.") 
parser.add_argument('-c', action = 'store_true', default = False, help = "Use coarse (E24) values.")
parser.add_argument('-n', default = 5, type = int, help = "Number of results to return.")
args = parser.parse_args()

r_vals = []

if args.f == True:
    for line in args.infile:
        r_vals.append(float(line))
    args.infile.close()
    tol = 0
elif args.c == True:
    r_vals = E24
    tol = .05
else:
    r_vals = E96
    tol = .01

results = r_calc(args.Vin, args.Vout, r_list = r_vals)
if args.b == True:
    if args.f == False:
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = 10, o_list = results)
        r_calc(args.Vin, args.Vout, r_list = r_vals, r2_mult = 10, o_list = results)
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = .1, r2_mult = 10, o_list = results)
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = 10, r2_mult = .1, o_list = results)
sorted_results = sorted(results, key=lambda error: error[3])
print len(sorted_results)
for m in range(args.n):
    tolerance = vout_err(args.Vin, args.Vout, sorted_results[m][0], sorted_results[m][1], tol)
    print 'R1: {:>5} R2: {:>5} Err (nom): {:.2%} Err (act): {:.2%} -> {:.2%} R1||R2= {:.1f}'.format( \
        sorted_results[m][0], \
        sorted_results[m][1], \
        sorted_results[m][3], \
        tolerance[0], \
        tolerance[1], \
        sorted_results[m][0]*sorted_results[m][1]/(sorted_results[m][0]+sorted_results[m][1]))
    
